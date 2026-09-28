"""Kvantuminformációs toy modell a fekete lyuk párolgásához.

Ez váltja fel a korábbi "visszanyert bitek" metrikát, ami valójában
``edge_fraction · log2(1000 bin)`` volt (a 9.97 bit = log2(1000)), és a
"Page-görbét", ami egy 1000 bines hisztogram Shannon-entrópiája volt. Az
információ a kisugárzott kvantumok közti *korrelációkban* van, nem a spektrum
alakjában (Page 1993b; Almheiri et al., Rev. Mod. Phys. 93, 035002, 2021) — ezért
itt a sugárzás összefonódási entrópiáját és a kölcsönös információt számoljuk.

Modellek (egységesen bitben):

``unitary`` — Page (1993) / Hayden–Preskill (2007):
    A fekete lyuk n qubitje + k üzenet-qubit (mindegyik maximálisan
    összefonódva egy külső referencia-qubittel) egy Haar-véletlen unitérrel
    összekeveredik, majd a qubitek egyenként kisugárzódnak. S(R) a Page-görbét
    követi (emelkedik, majd a felénél visszafordul), I(Ref:R) → 2k bit a végére:
    az üzenet a sugárzásból visszanyerhető.

``semiclassical`` — Hawking (1976):
    Minden kisugárzott qubit egy Bell-pár fele, amelynek párja a belsőben marad.
    A (Ref, R) redukált állapot egzaktul ρ_Ref ⊗ (I/2)^j, így S(R) = j bit
    (monoton nő), I(Ref:R) = 0: az információ nem jön ki.

``norbi`` — a Rust mag kauzalitás-eredményéből származtatva:
    ha a bébiuniverzum széle kauzálisan le van választva (causal_channel.exists
    = false — az LMY-geometriában minden M > M_min tömegre ez a helyzet), a
    beeső üzenet a bébiuniverzumba kerül, a külső sugárzás a horizont
    Hawking-sugárzása → ugyanaz, mint a ``semiclassical``. Kauzális csatorna
    esetén ``unitary`` lenne (ezt a jelenlegi geometria nem engedi).

A Haar-unitér pontos: csak a |b⟩|0…0⟩ bemenetek 2^k oszlopára van szükség,
ami egy (2^N × 2^k) komplex Gauss-mátrix QR-felbontása — ez N ≈ 20 qubitig olcsó.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

MAX_QUBITS = 20

ComplexArray = NDArray[np.complex128]


# ---------------------------------------------------------------------------
# Alapműveletek
# ---------------------------------------------------------------------------


def entropy_bits_from_matrix(psi_matrix: ComplexArray) -> float:
    """Neumann-entrópia (bit) a sorindexekhez tartozó részrendszerre,
    ahol ``psi_matrix[a, b]`` a tiszta állapot amplitúdója (Schmidt-felbontás)."""
    s = np.linalg.svd(psi_matrix, compute_uv=False)
    p = s.real**2
    p = p[p > 1e-15]
    return max(0.0, float(-np.sum(p * np.log2(p))))


def page_average_entropy_bits(m: int, n: int) -> float:
    """Page (1993) formula: egy m·n dimenziós Haar-véletlen tiszta állapot m
    dimenziós részrendszerének átlagos entrópiája (m ≤ n), bitben:
        S_{m,n} = Σ_{k=n+1}^{mn} 1/k − (m−1)/(2n)   [nat]
    """
    if m > n:
        m, n = n, m
    harmonic = float(np.sum(1.0 / np.arange(n + 1, m * n + 1))) if m * n > n else 0.0
    return (harmonic - (m - 1) / (2 * n)) / math.log(2)


def haar_isometry_columns(dim: int, n_cols: int, rng: np.random.Generator) -> ComplexArray:
    """Egy Haar-véletlen U ∈ U(dim) első ``n_cols`` oszlopa (Mezzadri 2007:
    komplex Gauss-mátrix QR-je, R átlójának fázisával korrigálva)."""
    z = (rng.standard_normal((dim, n_cols)) + 1j * rng.standard_normal((dim, n_cols))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    phases = d / np.abs(d)
    return np.asarray(q * phases, dtype=np.complex128)


# ---------------------------------------------------------------------------
# Párolgási toy modell
# ---------------------------------------------------------------------------


@dataclass
class InfoPoint:
    """Egy kisugárzási lépés utáni állapot (bitben)."""

    emitted: int
    emitted_fraction: float
    s_radiation: float
    mutual_info_ref_radiation: float


@dataclass
class InfoCurve:
    model: str
    n_black_hole_qubits: int
    n_message_qubits: int
    points: list[InfoPoint] = field(default_factory=list)

    @property
    def final_mutual_info(self) -> float:
        return self.points[-1].mutual_info_ref_radiation if self.points else 0.0

    @property
    def page_turnover(self) -> bool:
        """Visszafordul-e S(R) (a csúcs nem az utolsó pont)?"""
        s = [p.s_radiation for p in self.points]
        if len(s) < 3:
            return False
        peak = int(np.argmax(s))
        return 0 < peak < len(s) - 1 and s[-1] < s[peak] - 0.5

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["final_mutual_info"] = self.final_mutual_info
        d["page_turnover"] = self.page_turnover
        d["message_recoverable"] = self.final_mutual_info > 2 * self.n_message_qubits - 0.5
        return d


def unitary_curve(n_bh: int, k_msg: int, rng: np.random.Generator) -> InfoCurve:
    """Page/Hayden–Preskill: Haar-összekeverés után qubitenkénti kisugárzás.

    Qubit-sorrend az állapotvektorban: [Ref (k) | kisugárzandó qubitek (n+k)].
    A fekete lyuk kezdetben n qubit |0⟩ + k üzenet-qubit, ahol az üzenet
    maximálisan összefonódott Ref-fel: |Φ⟩ = 2^(−k/2) Σ_b |b⟩_Ref |b⟩_msg.
    (I ⊗ U)|Φ⟩|0⟩ = 2^(−k/2) Σ_b |b⟩_Ref ⊗ U|b, 0⟩ — U-nak csak 2^k oszlopa kell.
    """
    n_sys = n_bh + k_msg
    if n_sys + k_msg > MAX_QUBITS:
        raise ValueError(f"Túl sok qubit ({n_sys + k_msg} > {MAX_QUBITS})")
    dim_sys = 2**n_sys
    dim_ref = 2**k_msg
    # U|b,0…0⟩ oszlopok: a bemeneti bázisállapot indexe b·2^n (üzenet a legfelső bitek)
    cols = haar_isometry_columns(dim_sys, dim_ref, rng)  # (dim_sys, dim_ref)
    psi = (cols.T / math.sqrt(dim_ref)).reshape(dim_ref, dim_sys)  # [Ref, Sys]

    curve = InfoCurve("unitary", n_bh, k_msg)
    s_ref = float(k_msg)
    for j in range(n_sys + 1):
        dim_r = 2**j
        dim_rest = dim_sys // dim_r
        t = psi.reshape(dim_ref, dim_r, dim_rest)
        s_r = entropy_bits_from_matrix(t.transpose(1, 0, 2).reshape(dim_r, dim_ref * dim_rest))
        s_ref_r = entropy_bits_from_matrix(t.reshape(dim_ref * dim_r, dim_rest))
        curve.points.append(
            InfoPoint(j, j / n_sys, s_r, max(0.0, s_ref + s_r - s_ref_r))
        )
    return curve


def semiclassical_curve(n_bh: int, k_msg: int) -> InfoCurve:
    """Hawking (1976): ρ_{Ref,R} = ρ_Ref ⊗ (I/2)^j egzaktul → S(R) = j, I = 0."""
    n_sys = n_bh + k_msg
    curve = InfoCurve("semiclassical", n_bh, k_msg)
    for j in range(n_sys + 1):
        curve.points.append(InfoPoint(j, j / n_sys, float(j), 0.0))
    return curve


def norbi_curve(n_bh: int, k_msg: int, causal_channel_exists: bool, rng: np.random.Generator) -> InfoCurve:
    """A Norbi-forgatókönyv a Rust mag kauzalitás-eredménye alapján."""
    base = unitary_curve(n_bh, k_msg, rng) if causal_channel_exists else semiclassical_curve(n_bh, k_msg)
    base.model = "norbi"
    return base


# ---------------------------------------------------------------------------
# Összekötés a Rust szimulációval
# ---------------------------------------------------------------------------


def emission_times(timeline: list[dict[str, Any]], n_total: int) -> list[dict[str, float]]:
    """A j. qubit kisugárzásának ideje: amikor a Bekenstein–Hawking-entrópia
    j/n részét elvesztette, azaz M_j = M0·√(1 − j/n). A hátralévő időt a
    tömegben log-log interpoláljuk (állandó α-ra t_h ∝ M³ hatványfüggvény),
    mert a végfázisban ez a pontos mennyiség (a kezdettől mért idő ott már
    f64-felbontás alatt változik)."""
    if not timeline:
        return []
    masses = np.array([float(s["mass"]) for s in timeline])
    rem = np.array([float(s["time_to_evaporation"]) for s in timeline])
    t_total = float(timeline[-1]["time"])
    m0 = masses[0]
    out: list[dict[str, float]] = []
    for j in range(n_total + 1):
        m_j = m0 * math.sqrt(max(0.0, 1.0 - j / n_total))
        # a tömeg csökkenő: az első index, ahol masses <= m_j
        idx = int(np.argmax(masses <= m_j)) if np.any(masses <= m_j) else len(masses)
        if idx == 0:
            r = float(rem[0])
        elif idx >= len(masses) or m_j <= 0.0:
            r = float(rem[-1])
        else:
            m_a, m_b = masses[idx - 1], masses[idx]
            r_a, r_b = rem[idx - 1], rem[idx]
            w = math.log(m_a / m_j) / math.log(m_a / m_b)
            r = float(r_a * (r_b / r_a) ** w) if r_b > 0 else float(r_a * (1 - w))
        out.append({"time": max(0.0, t_total - r), "time_to_evaporation": r})
    return out


def analyze(
    results: dict[str, Any],
    n_bh: int = 12,
    k_msg: int = 1,
    seed: int = 0,
) -> dict[str, Any]:
    """A Rust szimuláció eredményéhez tartozó információs görbék (bitben).

    Mindhárom modellt kiszámolja; a ``norbi`` a ``causal_channel.exists``-ből jön.
    A toy modell qubitszáma (n) nem a valódi S_BH (az ~10⁴⁰ bit lenne), hanem
    egy leskálázott érték; az időtengely a valódi párolgásból származik.
    """
    rng = np.random.default_rng(seed)
    causal = bool(results.get("causal_channel", {}).get("exists", False))
    n_total = n_bh + k_msg
    times = emission_times(results.get("timeline", []), n_total)

    curves = {
        "unitary": unitary_curve(n_bh, k_msg, rng),
        "semiclassical": semiclassical_curve(n_bh, k_msg),
        "norbi": norbi_curve(n_bh, k_msg, causal, rng),
    }
    out: dict[str, Any] = {
        "units": "bit",
        "n_black_hole_qubits": n_bh,
        "n_message_qubits": k_msg,
        "seed": seed,
        "causal_channel_exists": causal,
        "emission_times": times,
        "page_average_entropy_half": page_average_entropy_bits(2 ** (n_total // 2), 2 ** (n_total - n_total // 2)),
        "curves": {name: c.to_dict() for name, c in curves.items()},
    }
    active = "norbi" if results.get("config", {}).get("norbi_mode") else "semiclassical"
    out["active_model"] = active
    out["message_recoverable"] = out["curves"][active]["message_recoverable"]
    return out
