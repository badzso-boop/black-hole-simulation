"""WP1 (+ WP2 shear): skalármező az LQC-visszapattanáson át az inflációig.

Egyenletek (Planck-egység; Ashtekar & Sloan 2010/2011; Bonga & Gupt 2016):
    ρ = φ̇²/2 + V(φ) + ρ_σ,   ρ_σ = Σ²/(16π a⁶)   (nyírás merev folyadékként, WP2)
    Ḣ = −4π (φ̇² + 2ρ_σ)(1 − 2ρ/ρ_c)         (ρ + P: skalár φ̇², nyírás 2ρ_σ)
    φ̈ + 3Hφ̇ + V′(φ) = 0
    H² = (8π/3) ρ (1 − ρ/ρ_c)   — kényszer, ellenőrzésre (drift)
Kezdőfeltétel a visszapattanáskor (a_B = 1, N = 0): H = 0, ρ = ρ_c,
    ρ_σ,B = Ω_σ ρ_c,   |φ̇_B| = √(2(ρ_c(1 − Ω_σ) − V(φ_B))).

A nyírás merev-folyadék közelítése (σ²/6 = 8πρ_σ/3) a klasszikus Bianchi-I
határesetből jön (Corichi & Singh 2009). A visszapattanásnál a teljes effektív
Bianchi-I dinamika a nyírást σ² ≤ 11.57 ℓ_P⁻²-re korlátozza (Gupt & Singh 2012),
a közelítés 16πρ_c = 20.6-ot enged — Ω_σ > 0.56 ezért a közelítés érvényességén kívül esik.

Szakaszok (ä/a = Ḣ + H² előjele szerint):
    szuperinfláció (Ḣ > 0) → kinetikus lassulás (ä < 0) → lassú gördülés (ä > 0) → vége (ä < 0).
Az idő a visszapattanástól Ḣ = 0-ig kozmikus idő (ott H = 0 szinguláris lenne
N-ben), utána az e-redő N a független változó.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Protocol

import numpy as np
from scipy.integrate import solve_ivp

from thesis.units import RHO_C

RTOL = 1e-10
ATOL = 1e-13


class Potential(Protocol):
    @property
    def name(self) -> str: ...

    def v(self, phi: float) -> float: ...
    def dv(self, phi: float) -> float: ...
    def d2v(self, phi: float) -> float: ...


@dataclass(frozen=True)
class Starobinsky:
    """V = (3M²/32π)(1 − e^{−√(16π/3) φ})²  (m_Pl = 1), M = 2.51e-6 (Bonga & Gupt 2016)."""

    m: float = 2.51e-6
    name: str = "Starobinsky"

    @property
    def k(self) -> float:
        return math.sqrt(16 * math.pi / 3)

    @property
    def v0(self) -> float:
        return 3 * self.m**2 / (32 * math.pi)

    def v(self, phi: float) -> float:
        e = math.exp(-self.k * phi)
        return self.v0 * (1 - e) ** 2

    def dv(self, phi: float) -> float:
        e = math.exp(-self.k * phi)
        return 2 * self.v0 * self.k * e * (1 - e)

    def d2v(self, phi: float) -> float:
        e = math.exp(-self.k * phi)
        return 2 * self.v0 * self.k**2 * e * (2 * e - 1)

    def phi_min_bounce(self) -> float:
        """A legnegatívabb φ_B, ahol V(φ_B) = ρ_c (Bonga–Gupt: −3.47)."""
        return -math.log(1 + math.sqrt(RHO_C / self.v0)) / self.k


@dataclass(frozen=True)
class PolyAttractor:
    """Polinomiális α-attraktor, k = 2 (Kallosh & Linde 2022, arXiv:2202.06492):
    V = V0 φ²/(φ² + μ²) → V0 (1 − μ²/φ² + …) nagy φ-nél; kis μ-re n_s = 1 − 3/(2N) (Eq. 1.5),
    ami N ≈ 55-nél 0.973 — az ACT DR6 értéke. V0-t az A_s normálás rögzíti (`normalized`).
    """

    v0: float = 1e-12
    mu: float = 0.2  # m_Pl egységben (≈ 1 redukált Planck-tömeg)
    name: str = "poly-attractor-k2"

    def v(self, phi: float) -> float:
        return self.v0 * phi * phi / (phi * phi + self.mu**2)

    def dv(self, phi: float) -> float:
        return self.v0 * 2 * phi * self.mu**2 / (phi * phi + self.mu**2) ** 2

    def d2v(self, phi: float) -> float:
        d = phi * phi + self.mu**2
        return self.v0 * 2 * self.mu**2 * (self.mu**2 - 3 * phi * phi) / d**3


@dataclass(frozen=True)
class Quadratic:
    """V = m²φ²/2, m = 1.21e-6 (Ashtekar & Sloan 2011, WMAP-7 normálás)."""

    m: float = 1.21e-6
    name: str = "phi2"

    def v(self, phi: float) -> float:
        return 0.5 * self.m**2 * phi**2

    def dv(self, phi: float) -> float:
        return self.m**2 * phi

    def d2v(self, phi: float) -> float:
        return self.m**2

    def phi_max_bounce(self) -> float:
        return math.sqrt(2 * RHO_C) / self.m


@dataclass
class BounceResult:
    potential: str
    phi_b: float
    phidot_sign: int
    shear_fraction: float
    n_super: float  # e-redők a visszapattanástól Ḣ = 0-ig
    n_onset: float  # a lassú gördülés kezdete (visszapattanástól)
    n_infl: float  # a lassú gördülés hossza (e-redő); ≥ cap, ha capped
    capped: bool
    inflated: bool
    phi_end: float | None
    h_onset: float | None
    v_end: float | None
    log10_shear_over_h_onset: float | None  # log10(σ/H); None, ha nincs nyírás
    log10_shear_over_h_end: float | None
    constraint_drift: float  # a Friedmann-kényszer relatív hibája a szuperinfláció végén

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rho(pot: Potential, phi: float, pi: float, n: float, sigma2_b: float,
         dust_b: float = 0.0) -> tuple[float, float]:
    """(ρ_összes, ρ_σ) — ρ_σ = Σ²/(16π a⁶), Σ² = σ²_B (a_B = 1); por: ρ_d = ρ_d,B a⁻³ (B1)."""
    rho_s = sigma2_b / (16 * math.pi) * math.exp(-6 * n)
    return 0.5 * pi * pi + pot.v(phi) + rho_s + dust_b * math.exp(-3 * n), rho_s


def _hdot(pot: Potential, phi: float, pi: float, n: float, sigma2_b: float,
          dust_b: float = 0.0) -> float:
    rho, rho_s = _rho(pot, phi, pi, n, sigma2_b, dust_b)
    rho_d = dust_b * math.exp(-3 * n)  # por: ρ + P = ρ_d
    return -4 * math.pi * (pi * pi + 2 * rho_s + rho_d) * (1 - 2 * rho / RHO_C)


_rho_mod, _hdot_mod = _rho, _hdot  # az evolve-on belüli, porral lezárt változatokhoz


def evolve(
    pot: Potential,
    phi_b: float,
    phidot_sign: int = 1,
    shear_fraction: float = 0.0,
    n_cap: float = 150.0,
    min_infl: float = 1.0,
    dust_fraction: float = 0.0,
    h_floor: float = 0.0,
) -> BounceResult:
    """Egy trajektória a visszapattanástól az infláció végéig (vagy n_cap e-redőig).

    dust_fraction (B1, docs/upgrade-plan.md): a visszapattanáskori ρ_c pora (a szülő csillag
    anyaga); a skalármező a maradékot kapja. 0 → az eredeti WP1-számolás.
    h_floor: ha H ez alá esik infláció előtt, leállunk („nem inflál"). A B1 ~0.1 m-et ad meg:
    lassú gördüléshez H ≳ m/2 kell (Starobinsky: H_inf ≈ M/2; φ²: H ≳ 0.8 m), alatta a mező a
    minimum körül oszcillál, és az integrálás a sok oszcilláción ragadna.
    """
    kin = RHO_C * (1 - shear_fraction - dust_fraction) - pot.v(phi_b)
    if kin < 0:
        raise ValueError(f"V(φ_B) > ρ_c(1−Ω_σ−f_d) φ_B = {phi_b}")
    sigma2_b = 16 * math.pi * shear_fraction * RHO_C
    dust_b = dust_fraction * RHO_C
    y0 = [0.0, 0.0, phi_b, phidot_sign * math.sqrt(2 * kin)]  # [N, H, φ, φ̇]
    drift = 0.0

    # a belső függvények a por-taggal lezárt változatot használják
    def _rho(pot: Potential, phi: float, pi: float, n: float,
             sigma2_b: float) -> tuple[float, float]:
        return _rho_mod(pot, phi, pi, n, sigma2_b, dust_b)

    def _hdot(pot: Potential, phi: float, pi: float, n: float, sigma2_b: float) -> float:
        return _hdot_mod(pot, phi, pi, n, sigma2_b, dust_b)

    def constraint(n: float, h: float, phi: float, pi: float) -> float:
        rho, _ = _rho(pot, phi, pi, n, sigma2_b)
        target = (8 * math.pi / 3) * rho * (1 - rho / RHO_C)
        return abs(h * h - target) / max(target, h * h, 1e-300)

    # --- 1. szakasz: kozmikus idő, a szuperinfláció végéig (Ḣ = 0) ---
    def rhs_t(_t: float, y: np.ndarray) -> list[float]:
        n, h, phi, pi = y
        return [h, _hdot(pot, phi, pi, n, sigma2_b), pi, -3 * h * pi - pot.dv(phi)]

    def hdot_zero(_t: float, y: np.ndarray) -> float:
        return _hdot(pot, y[2], y[3], y[0], sigma2_b)

    hdot_zero.terminal = True  # type: ignore[attr-defined]
    hdot_zero.direction = -1  # type: ignore[attr-defined]
    # potenciál-dominált visszapattanásnál (V(φ_B) ≈ ρ_c) már a szuperinfláció is
    # gyorsuló és N_cap-nél hosszabb lehet — ekkor nem integrálunk tovább
    def cap_reached(_t: float, y: np.ndarray) -> float:
        return float(y[0] - n_cap)

    cap_reached.terminal = True  # type: ignore[attr-defined]
    sol = solve_ivp(rhs_t, (0.0, 1e12), y0, method="DOP853", rtol=RTOL, atol=ATOL,
                    events=[hdot_zero, cap_reached])
    if sol.t_events[1].size:
        return BounceResult(
            potential=pot.name, phi_b=phi_b, phidot_sign=phidot_sign,
            shear_fraction=shear_fraction, n_super=n_cap, n_onset=0.0, n_infl=n_cap,
            capped=True, inflated=True, phi_end=None, h_onset=None, v_end=None,
            log10_shear_over_h_onset=None, log10_shear_over_h_end=None, constraint_drift=0.0,
        )
    if not sol.t_events[0].size:
        raise RuntimeError(f"a szuperinfláció nem ért véget t < 1e12 alatt (φ_B = {phi_b})")
    n, h, phi, pi = sol.y_events[0][0]
    n_super = n
    drift = max(drift, constraint(n, h, phi, pi))

    # --- 2. szakasz: e-redő a független változó; ä/a = Ḣ + H² előjelváltásai ---
    # H-t itt NEM integráljuk (a Raychaudhuri-egyenlet mint fejlődési egyenlet
    # instabil: a kinetikus szakaszban δH/H ∝ e^{6N} nő), hanem a Friedmann-
    # kényszerből számoljuk, a táguló (H > 0) ágon — Ḣ = 0 után H már nem nullázódik.
    def hubble(nn: float, ph: float, pp: float) -> float:
        rho, _ = _rho(pot, ph, pp, nn, sigma2_b)
        return math.sqrt(max((8 * math.pi / 3) * rho * (1 - rho / RHO_C), 0.0))

    def rhs_n(nn: float, y: np.ndarray) -> list[float]:
        ph, pp = y
        hh = hubble(nn, ph, pp)
        return [pp / hh, (-3 * hh * pp - pot.dv(ph)) / hh]

    def accel(nn: float, y: np.ndarray) -> float:
        hh = hubble(nn, y[0], y[1])
        return _hdot(pot, y[0], y[1], nn, sigma2_b) + hh * hh

    state = np.array([phi, pi])
    accelerating = True  # Ḣ = 0-nál ä/a = H² > 0
    n_start, start_state = n, state.copy()
    n_limit = n + n_cap + 20
    interval: tuple[float, float, np.ndarray, np.ndarray] | None = None
    capped = False
    for _ in range(60):
        direction = -1 if accelerating else 1

        def ev(nn: float, y: np.ndarray) -> float:
            return accel(nn, y)

        ev.terminal = True  # type: ignore[attr-defined]
        ev.direction = direction  # type: ignore[attr-defined]

        def floor(nn: float, y: np.ndarray) -> float:
            return hubble(nn, y[0], y[1]) - h_floor

        floor.terminal = True  # type: ignore[attr-defined]
        floor.direction = -1  # type: ignore[attr-defined]
        sol = solve_ivp(rhs_n, (n, n_limit), state, method="DOP853", rtol=RTOL, atol=ATOL,
                        events=[ev, floor] if h_floor > 0 else ev)
        if h_floor > 0 and sol.t_events[1].size and not sol.t_events[0].size:
            if accelerating and sol.t_events[1][0] - n_start >= min_infl:
                interval = (n_start, float(sol.t_events[1][0]), start_state, sol.y_events[1][0])
            break
        if not sol.t_events[0].size:
            # nincs több előjelváltás a határig
            if accelerating:
                capped = True
                interval = (n_start, float(sol.t[-1]), start_state, sol.y[:, -1])
            break
        n_ev = float(sol.t_events[0][0])
        state = sol.y_events[0][0]
        if accelerating:
            if n_ev - n_start >= min_infl:
                interval = (n_start, n_ev, start_state, state)
                break
        else:
            n_start, start_state = n_ev, state.copy()
        n = n_ev
        accelerating = not accelerating

    def shear_over_h(nn: float, hh: float) -> float | None:
        # log10(σ/H), σ = σ_B e^{-3N}: logaritmusban, mert e^{-3N} N ~ 170-nél alulcsordul
        if sigma2_b <= 0:
            return None
        return (0.5 * math.log(sigma2_b) - 3 * nn - math.log(hh)) / math.log(10)

    if interval is None:
        return BounceResult(
            potential=pot.name, phi_b=phi_b, phidot_sign=phidot_sign,
            shear_fraction=shear_fraction, n_super=n_super, n_onset=float("nan"), n_infl=0.0,
            capped=False, inflated=False, phi_end=None, h_onset=None, v_end=None,
            log10_shear_over_h_onset=None, log10_shear_over_h_end=None, constraint_drift=drift,
        )
    n_onset, n_stop, s_start, s_stop = interval
    n_infl = n_stop - n_onset
    h_start = hubble(n_onset, float(s_start[0]), float(s_start[1]))
    h_stop = hubble(n_stop, float(s_stop[0]), float(s_stop[1]))
    return BounceResult(
        potential=pot.name, phi_b=phi_b, phidot_sign=phidot_sign,
        shear_fraction=shear_fraction, n_super=n_super, n_onset=n_onset, n_infl=n_infl,
        capped=capped or n_infl >= n_cap, inflated=True,
        phi_end=None if capped else float(s_stop[0]),
        h_onset=h_start,
        v_end=None if capped else pot.v(float(s_stop[0])),
        log10_shear_over_h_onset=shear_over_h(n_onset, h_start),
        log10_shear_over_h_end=None if capped else shear_over_h(n_stop, h_stop),
        constraint_drift=drift,
    )


# ---------------------------------------------------------------------------
# Lassú gördülésű megfigyelhetők (a vonzó megoldáson — a visszapattanástól függetlenek)
# ---------------------------------------------------------------------------


def slow_roll_eps(pot: Potential, phi: float) -> float:
    return (pot.dv(phi) / pot.v(phi)) ** 2 / (16 * math.pi)


def slow_roll_eta(pot: Potential, phi: float) -> float:
    return pot.d2v(phi) / pot.v(phi) / (8 * math.pi)


def phi_end_slow_roll(pot: Potential, lo: float, hi: float) -> float:
    """ε_V(φ_end) = 1 biszekcióval (lo-nál ε > 1, hi-nál ε < 1)."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if slow_roll_eps(pot, mid) > 1:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def efolds_slow_roll(pot: Potential, phi_end: float, phi: float) -> float:
    """N(φ) = 8π ∫_{φ_end}^{φ} V/V′ dφ."""
    xs = np.linspace(phi_end, phi, 4001)
    ys = np.array([pot.v(x) / pot.dv(x) for x in xs])
    return float(8 * math.pi * np.trapezoid(ys, xs))


def pivot_observables(pot: Potential, n_star: float, phi_end: float, hi: float) -> dict[str, float]:
    """n_s = 1 − 6ε + 2η, r = 16ε annál a φ*-nál, ahol N(φ*) = n_star.

    N(φ) egyszer, kumulatív trapéz-integrállal [φ_end, hi]-n, majd interpoláció.
    """
    xs = np.linspace(phi_end, hi, 40001)
    ys = np.array([pot.v(x) / pot.dv(x) for x in xs])
    cum = 8 * math.pi * np.concatenate(([0.0], np.cumsum(0.5 * (ys[1:] + ys[:-1]) * np.diff(xs))))
    if n_star > cum[-1]:
        raise ValueError(f"hi = {hi} túl kicsi: N(hi) = {cum[-1]:.1f} < {n_star}")
    phi_star = float(np.interp(n_star, cum, xs))
    eps, eta = slow_roll_eps(pot, phi_star), slow_roll_eta(pot, phi_star)
    # A_s = V/(24π² ε M_Pl⁴), M_Pl⁴ = 1/(64π²) Planck-egységben  →  A_s = (8/3) V/ε
    return {"n_star": n_star, "phi_star": phi_star, "n_s": 1 - 6 * eps + 2 * eta, "r": 16 * eps,
            "V_star": pot.v(phi_star), "A_s": (8 / 3) * pot.v(phi_star) / eps}
