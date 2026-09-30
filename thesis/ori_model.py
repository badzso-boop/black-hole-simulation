"""L1a (+ L1d): az általánosított Ori-modell — tömeg-infláció a belső horizonton.

Carballo-Rubio, Di Filippo, Liberati, Pacilio & Visser 2021 (arXiv:2101.05006), eqs. (4), (10), (32):
    m₋(v) = m₀ + δm(v)                 (a befelé áramló fluxus; klasszikusan Price-farok −β v^−p)
    dR/dv = f₋(m₋(v), R)/2             (a kifelé haladó héj, R → r₀ a belső horizonton)
    (1/f₊) ∂_v M₊ = (1/f₋) ∂_v M₋      (illesztés a héjon; ∂_v rögzített r-nél)
ahol M(m, r) a Misner–Sharp-tömeg és f = 1 − 2M/r. Két alak:
    m-alak:  m₊' = (f₊/f₋)·[∂_m M(m₋,R)/∂_m M(m₊,R)]·m₋'                  (RN, LMYZ)
    M-alak:  M₊' = (f₊/f₋)·∂_m M(m₋,R)·m₋' + ∂_r M|_m(M₊,R)·R'              (Hayward: m₊ ±∞-en megy át)

Numerika: f₋ a késői időkben ~v^−(p+1), R − r₀ ~ v^−p — a kioltás elkerülésére f-et
polinom-osztással számoljuk: f(m₀, r₀+δ) = [N(r₀) + δ·Q(r)]/D(r), ahol N(r₀) a lebegőpontos
gyök pontos maradéka (mpmath), a δm-rész pedig zárt alakban. A változó δR = R − r₀, és a
növekvő tömeget asinh-transzformáltan integráljuk (előjelet vált és exponenciálisan nő).

Metrikák (f = N(m,r)/D(m,r)):
    RN(e):        N = r² − 2mr + e²,     D = r²          M = m − e²/(2r)
    Hayward(ℓ):   N = r³ − 2mr² + 2mℓ²,  D = r³ + 2mℓ²   M = m r³/(r³ + 2mℓ²)
    LMYZ(α):      N = r⁴ − 2mr³ + αm²,   D = r⁴          M = m − αm²/(2r³)
                  (Lewandowski–Ma–Yang–Zhang 2023, α = 16√3πγ³, Planck-egység)
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import mpmath
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

from thesis.units import ALPHA_LMY

mpmath.mp.dps = 50
S_R = 1e-150  # a δR = R − r₀ változó asinh-skálája (előjelet válthat, ha m₋ nő)


# ---------------------------------------------------------------------------
# Metrikák
# ---------------------------------------------------------------------------


@dataclass
class Metric:
    """f = N(m,r)/D(m,r); a leszármazottak adják meg a polinomot és a tömegfüggvényt."""

    name: str = "metric"
    form: str = "m"  # "m" vagy "M" (lásd a modul fejlécét)

    # --- a leszármazottak felüldefiniálják ---
    def n_coeffs(self, m: float) -> list[float]:  # N(m, r) együtthatói, csökkenő fokszám
        raise NotImplementedError

    def d(self, m: float, r: float) -> float:
        raise NotImplementedError

    def dn_dm_diff(self, m0: float, dm: float, r: float) -> float:
        """[N(m0+dm)D(m0) − N(m0)D(m0+dm)] / r-függő rész — pontosan, zárt alakban."""
        raise NotImplementedError

    def mass(self, m: float, r: float) -> float:
        raise NotImplementedError

    def dmass_dm(self, m: float, r: float) -> float:
        raise NotImplementedError

    def dmass_dr_at_M(self, big_m: float, r: float) -> float:  # csak az M-alakhoz
        raise NotImplementedError

    # --- közös ---
    def f(self, m: float, r: float) -> float:
        return float(np.polyval(self.n_coeffs(m), r) / self.d(m, r))

    def inner_horizon(self, m: float) -> float:
        """A legkisebb pozitív gyök, ahol f előjelet vált (− → + befelé)."""
        roots = np.roots(self.n_coeffs(m))
        real = sorted(x.real for x in roots if abs(x.imag) < 1e-9 * abs(x) and x.real > 0)
        if len(real) < 2:
            raise ValueError(f"{self.name}: nincs belső horizont m = {m}-nél")
        r0 = real[0]
        # mpmath-polírozás
        c = [mpmath.mpf(x) for x in self.n_coeffs(m)]
        r0m = mpmath.findroot(lambda x: mpmath.polyval(c, x), mpmath.mpf(r0))
        return float(r0m)

    def outer_horizon(self, m: float) -> float:
        roots = np.roots(self.n_coeffs(m))
        real = sorted(x.real for x in roots if abs(x.imag) < 1e-9 * abs(x) and x.real > 0)
        return float(real[-1])

    def kappa(self, m: float, r0: float) -> float:
        """|κ| = |f'(r0)|/2, numerikus deriválttal (mpmath)."""
        c = [mpmath.mpf(x) for x in self.n_coeffs(m)]

        def ff(x: Any) -> Any:
            return mpmath.polyval(c, x) / self._d_mp(m, x)

        return float(abs(mpmath.diff(ff, mpmath.mpf(r0))) / 2)

    def _d_mp(self, m: float, r: Any) -> Any:
        # a D(m, r) képletek csak aritmetikát használnak → mpmath-számmal is pontosak
        return self.d(m, r)

    def split(self, m0: float, r0: float) -> Callable[[float, float], float]:
        """f(m0+δm, r_true+δ) pontosan: N(r) = (r − r_true)·Q(r), ahol Q együtthatóit a
        mpmath-ban (nagy pontossággal) ismert valódi gyökkel osztjuk ki, így nincs maradék-tag
        és nincs kioltás: f = δ·Q(r)/D(r) + δm-rész. A δ változó a VALÓDI gyöktől mért távolság."""
        coeffs = [mpmath.mpf(x) for x in self.n_coeffs(m0)]
        r_true = mpmath.findroot(lambda x: mpmath.polyval(coeffs, x), mpmath.mpf(r0))
        q_mp = [coeffs[0]]
        for a_k in coeffs[1:-1]:
            q_mp.append(a_k + q_mp[-1] * r_true)
        q = [float(x) for x in q_mp]
        r_base = float(r_true)

        def f_split(dm: float, dr: float) -> float:
            r = r_base + dr
            d0 = self.d(m0, r)
            base = dr * float(np.polyval(q, r)) / d0
            if dm == 0.0:
                return base
            return base + self.dn_dm_diff(m0, dm, r) / (d0 * self.d(m0 + dm, r))

        return f_split


@dataclass
class RN(Metric):
    e: float = 5.0
    name: str = "Reissner–Nordström"
    form: str = "m"

    def n_coeffs(self, m: float) -> list[float]:
        return [1.0, -2.0 * m, self.e**2]

    def d(self, m: float, r: float) -> float:
        return r * r

    def dn_dm_diff(self, m0: float, dm: float, r: float) -> float:
        return -2.0 * dm * r * r * r  # (−2 δm r)·r² ; osztva D0·D1 = r⁴ → −2δm/r

    def mass(self, m: float, r: float) -> float:
        return m - self.e**2 / (2 * r)

    def dmass_dm(self, m: float, r: float) -> float:
        return 1.0

    def dmass_dr_at_M(self, big_m: float, r: float) -> float:
        return self.e**2 / (2 * r * r)


@dataclass
class Hayward(Metric):
    ell: float = 0.5
    name: str = "Hayward"
    form: str = "M"

    def n_coeffs(self, m: float) -> list[float]:
        return [1.0, -2.0 * m, 0.0, 2.0 * m * self.ell**2]

    def d(self, m: float, r: float) -> float:
        return r**3 + 2 * m * self.ell**2

    def dn_dm_diff(self, m0: float, dm: float, r: float) -> float:
        return -2.0 * r**5 * dm

    def mass(self, m: float, r: float) -> float:
        return m * r**3 / (r**3 + 2 * m * self.ell**2)

    def dmass_dm(self, m: float, r: float) -> float:
        return r**6 / (r**3 + 2 * m * self.ell**2) ** 2

    def dmass_dr_at_M(self, big_m: float, r: float) -> float:
        return 6 * self.ell**2 * big_m**2 / r**4  # Carballo-Rubio+ 2021 eq. (17)


@dataclass
class LMYZ(Metric):
    alpha: float = ALPHA_LMY
    name: str = "LMYZ (kvantum-OS)"
    form: str = "m"

    def n_coeffs(self, m: float) -> list[float]:
        return [1.0, -2.0 * m, 0.0, 0.0, self.alpha * m * m]

    def d(self, m: float, r: float) -> float:
        return r**4

    def dn_dm_diff(self, m0: float, dm: float, r: float) -> float:
        # [N(m1) − N(m0)]·r⁴  (D nem függ m-től)
        return (-2.0 * dm * r**3 + self.alpha * dm * (2 * m0 + dm)) * r**4

    def mass(self, m: float, r: float) -> float:
        return m - self.alpha * m * m / (2 * r**3)

    def dmass_dm(self, m: float, r: float) -> float:
        return 1.0 - self.alpha * m / r**3

    def bounce_radius(self, m: float) -> float:
        return float((self.alpha * m / 2) ** (1 / 3))


# ---------------------------------------------------------------------------
# Az Ori-modell integrálása
# ---------------------------------------------------------------------------


@dataclass
class OriResult:
    metric: str
    m0: float
    r0: float
    kappa0: float
    v: np.ndarray
    dR: np.ndarray
    big_m: np.ndarray  # M₊ (a Misner–Sharp-tömeg a héj mögött)
    notes: dict[str, Any] = field(default_factory=dict)

    def log_abs_m(self) -> np.ndarray:
        return np.asarray(np.log(np.abs(self.big_m)), dtype=float)


def influx_price(m0: float, beta: float, p: float) -> tuple[Callable[[float], float],
                                                           Callable[[float], float]]:
    """Klasszikus Price-farok: δm = −β v^−p, δm' = pβ v^−(p+1)."""
    return (lambda v: -beta * v ** (-p)), (lambda v: p * beta * v ** (-p - 1))


def influx_linear(flux: float) -> tuple[Callable[[float], float], Callable[[float], float]]:
    """Kvantum-fluxus (L1d): az Eddington-koordinátában véges ⟨T_vv⟩ → dm/dv = 4πr₋²⟨T_vv⟩ = áll."""
    return (lambda v: flux * v), (lambda v: flux)


def integrate(metric: Metric, m0: float, dm_fun: Callable[[float], float],
              dmdot_fun: Callable[[float], float], v_i: float, v_f: float,
              r_i: float | None = None, big_m_i: float | None = None,
              m_plus_i: float | None = None, scale: float = 1.0,
              n_out: int = 2000) -> OriResult:
    """(δR, M₊ vagy m₊) integrálása v_i → v_f. A tömeg-változót asinh(x/scale)-ként integráljuk."""
    r0 = metric.inner_horizon(m0)
    k0 = metric.kappa(m0, r0)
    fs = metric.split(m0, r0)
    dr_i = (r_i - r0) if r_i is not None else 0.1 * r0
    if dr_i <= 0:
        raise ValueError("a héjnak a belső horizont fölött kell indulnia (R > r₀)")

    def f_minus(v: float, dr: float) -> float:
        return fs(dm_fun(v), dr)

    if metric.form == "m":
        m_start = m_plus_i if m_plus_i is not None else m0 + 1.0

        def rhs(v: float, y: np.ndarray) -> list[float]:
            ldr, w = y
            dr = S_R * math.sinh(ldr)
            mp = scale * math.sinh(w)
            r = r0 + dr
            fm = f_minus(v, dr)
            fp = 1.0 - 2.0 * metric.mass(mp, r) / r
            mm = m0 + dm_fun(v)
            dmp = (fp / fm) * (metric.dmass_dm(mm, r) / metric.dmass_dm(mp, r)) * dmdot_fun(v)
            return [0.5 * fm / (S_R * math.cosh(ldr)), dmp / (scale * math.cosh(w))]

        y0 = [math.asinh(dr_i / S_R), math.asinh(m_start / scale)]
    else:
        bm_start = big_m_i if big_m_i is not None else metric.mass(m0 + 1.0, r0 + dr_i)

        def rhs(v: float, y: np.ndarray) -> list[float]:
            ldr, w = y
            dr = S_R * math.sinh(ldr)
            bm = scale * math.sinh(w)
            r = r0 + dr
            fm = f_minus(v, dr)
            fp = 1.0 - 2.0 * bm / r
            mm = m0 + dm_fun(v)
            dbm = (fp / fm) * metric.dmass_dm(mm, r) * dmdot_fun(v) \
                + metric.dmass_dr_at_M(bm, r) * 0.5 * fm
            return [0.5 * fm / (S_R * math.cosh(ldr)), dbm / (scale * math.cosh(w))]

        y0 = [math.asinh(dr_i / S_R), math.asinh(bm_start / scale)]

    def blowup(v: float, y: np.ndarray) -> float:
        return float(690.0 - abs(y[1]))  # |x| ~ scale·e^690 ≈ 1e300·scale … a float határa előtt álljunk meg

    blowup.terminal = True  # type: ignore[attr-defined]

    def ceiling(v: float, y: np.ndarray) -> float:
        """m-alakban ∂_m M(m₊, R) = 0: a Misner–Sharp-tömeg eléri a metrika-család felső
        korlátját (LMYZ: M ≤ R³/(2α), azaz a görbület a beépített Planck-plafonon)."""
        if metric.form != "m":
            return 1.0
        # a szingularitás előtt állunk meg (|∂_m M| < 1e-3): ott m₊' → ∞
        return abs(metric.dmass_dm(scale * math.sinh(y[1]), r0 + S_R * math.sinh(y[0]))) - 1e-3

    ceiling.terminal = True  # type: ignore[attr-defined]
    ts = np.linspace(v_i, v_f, n_out)
    sol = solve_ivp(rhs, (v_i, v_f), y0, method="LSODA", rtol=1e-10, atol=1e-12,
                    t_eval=ts, events=[blowup, ceiling])
    x = scale * np.sinh(sol.y[1])
    dr_arr = S_R * np.sinh(sol.y[0])
    if metric.form == "m":
        r = r0 + dr_arr
        big_m = np.array([metric.mass(mp, rr) for mp, rr in zip(x, r, strict=True)])
    else:
        big_m = x
    notes: dict[str, Any] = {"status": sol.status, "message": sol.message,
                             "blowup_v": sol.t_events[0].tolist(),
                             "ceiling_v": sol.t_events[1].tolist()}
    if sol.t_events[1].size:
        yc = sol.y_events[1][0]
        rc = r0 + S_R * math.sinh(yc[0])
        mc = scale * math.sinh(yc[1])
        notes["ceiling_M"] = metric.mass(mc, rc)
        notes["ceiling_R"] = rc
    return OriResult(metric=metric.name, m0=m0, r0=r0, kappa0=k0, v=sol.t, dR=dr_arr,
                     big_m=big_m, notes=notes)


def growth_rate(res: OriResult, v_min: float) -> dict[str, float]:
    """d ln|M₊ − M₊(∞-háttér)|/dv a késői szakaszon; RN-re az analitikus κ₀ − (p+1)/v."""
    sel = (res.v >= v_min) & np.isfinite(res.big_m) & (np.abs(res.big_m) > 0)
    v = res.v[sel]
    lm = np.log(np.abs(res.big_m[sel]))
    slope = np.gradient(lm, v)
    return {"v_end": float(v[-1]), "slope_end": float(slope[-1]),
            "loglog_slope_end": float(slope[-1] * v[-1]), "log_m_end": float(lm[-1])}


# ---------------------------------------------------------------------------
# L1a: a nem forgó LMYZ-modell saját belső horizontja
# ---------------------------------------------------------------------------


def lmyz_crossing_efolds(m: float, alpha: float = ALPHA_LMY) -> dict[str, float]:
    """A porgömb felszíne r₋-től R_b-ig (a visszapattanásig) mennyi befelé-időt (v) tölt,
    κ₀-egységben: ennyi e-redőnyi tömeg-infláció férne bele *legfeljebb*, ha a befelé fluxus
    már ott lenne (de r₋ külső tartománya csak a felszín áthaladása után létezik).
    Marginálisan kötött (E = 1) radiális geodetikus: ṙ² = 1 − f, v̇ = (1 − √(1−f))/f."""
    met = LMYZ(alpha=alpha)
    r0 = met.inner_horizon(m)
    rb = met.bounce_radius(m)
    k0 = met.kappa(m, r0)

    def f(r: float) -> float:
        return 1 - 2 * m / r + alpha * m * m / r**4

    def integrand(r: float) -> float:
        ff = f(r)
        s = math.sqrt(max(1 - ff, 1e-300))
        vdot = (1 - s) / ff if abs(ff) > 1e-12 else 0.5
        return vdot / s

    # R_b-nél ṙ → 0 (fordulópont): integrálható szingularitás (~1/√(r − R_b))
    dv = quad(integrand, rb * (1 + 1e-14), r0, limit=500)[0]
    return {"m": m, "r_minus": r0, "R_b": rb, "gap_rel": (r0 - rb) / rb, "kappa0": k0,
            "kappa0_formula_3m_over_r2": 3 * m / r0**2, "dv_rminus_to_bounce": dv,
            "efolds_available": k0 * dv}


def edge_confinement(eta_total: float, masses_planck: list[float],
                     alpha: float = ALPHA_LMY) -> list[dict[str, float]]:
    """A labda szélén keletkező zavar a visszapattanás után legfeljebb Δχ = η komoving
    távolságra juthat befelé (fénysebesség; a_B = 1). A labda komoving sugara r_b(M)."""
    out = []
    for m in masses_planck:
        rb = (alpha * m / 2) ** (1 / 3)
        out.append({"m_planck": m, "r_b": rb, "eta_over_rb": eta_total / rb})
    return out


def conformal_time_to_end_of_inflation(n_onset: float, h_onset: float) -> dict[str, float]:
    """η = ∫dt/a a visszapattanástól (a_B = 1) az infláció végéig: kinetikus LQC-szakasz
    a(t) = (1 + 24πρ_c t²)^{1/6} a lassú gördülés kezdetéig, utána ≤ 1/(a_on H_on)."""
    from thesis.units import RHO_C

    a_on = math.exp(n_onset)
    t_on = math.sqrt((a_on**6 - 1) / (24 * math.pi * RHO_C))
    eta_kin = quad(lambda t: (1 + 24 * math.pi * RHO_C * t * t) ** (-1 / 6), 0, t_on,
                   limit=500)[0]
    eta_inf = 1 / (a_on * h_onset)
    return {"eta_kinetic": eta_kin, "eta_inflation": eta_inf, "eta_total": eta_kin + eta_inf}


def mass_for_confinement(eta_total: float, ratio: float = 0.1,
                         alpha: float = ALPHA_LMY) -> float:
    """Az a tömeg (m_P), amelynél η/r_b = ratio: e fölött a szél zavara a labda
    legfeljebb `ratio`-ad részéig hatol."""
    return 2 * (eta_total / ratio) ** 3 / alpha


def run_l1a(n_onset: float, h_onset: float) -> dict[str, Any]:
    """L1a: validáció (RN exponenciális, Hayward polinomiális), LMYZ tömeg-infláció,
    időzítés, és a szél-bezártság (edge confinement)."""
    beta, p = 1.0, 12.0
    out: dict[str, Any] = {}
    # 1. RN — Carballo-Rubio+ 2021 Fig. 2 paraméterei; analitikus: d ln M/dv = κ₀ − (p+1)/v
    rn = RN(e=5.0)
    dm, dmd = influx_price(10.0, beta, p)
    res = integrate(rn, 10.0, dm, dmd, 1.0, 25.0, r_i=5.0, m_plus_i=11.0)
    g = growth_rate(res, 10.0)
    out["rn"] = {"kappa0": res.kappa0, **g,
                 "analytic_slope_end": res.kappa0 - (p + 1) / g["v_end"],
                 "curve": {"v": res.v[::20].tolist(), "log_abs_M": res.log_abs_m()[::20].tolist()}}
    # 2. Hayward — előbb exponenciális, utána polinomiális (d ln M/d ln v → p+1)
    hw = Hayward(ell=0.5)
    res = integrate(hw, 10.0, dm, dmd, 1.0, 400.0, r_i=5.0,
                    big_m_i=hw.mass(11.0, 5.0), n_out=4000)
    g = growth_rate(res, 50.0)
    out["hayward"] = {"kappa0": res.kappa0, **g, "expected_late_loglog_slope": p + 1,
                      "curve": {"v": res.v[::40].tolist(),
                                "log_abs_M": res.log_abs_m()[::40].tolist()}}
    # 3. LMYZ — Planck-egységben; késői szakasz (kis perturbáció), mindkét előjelű héj-ugrással
    lm = LMYZ()
    lmyz_rows = []
    for m0 in (10.0, 1e3):
        r0 = lm.inner_horizon(m0)
        rbr = (lm.alpha * m0) ** (1 / 3)  # itt ∂_m M = 0: ágváltás
        dm0, dmd0 = influx_price(m0, beta, p)
        v_i = 10.0
        r_i = r0 + 1e-3 * (rbr - r0)
        big_m_minus = lm.mass(m0 + dm0(v_i), r_i)
        for sign in (1, -1):
            big_m_plus = big_m_minus + sign * 1e-6
            m_plus = (r_i**3 / lm.alpha) * (1 + math.sqrt(max(1 - 2 * lm.alpha * big_m_plus / r_i**3, 0)))
            res = integrate(lm, m0, dm0, dmd0, v_i, v_i + 30.0, r_i=r_i, m_plus_i=m_plus, n_out=1500)
            cv = res.notes["ceiling_v"]
            stop = cv[0] if cv else res.v[-1]
            sel = res.v < stop - 1e-9
            dev = np.abs(res.big_m[sel] - big_m_minus)
            ok = dev > 0
            slope = np.gradient(np.log(dev[ok]), res.v[sel][ok])
            fin = res.big_m[np.isfinite(res.big_m)]
            last = float(fin[-1]) if fin.size else float("nan")
            lmyz_rows.append({
                "m0": m0, "shell_jump_sign": sign, "r_minus": r0, "R_b": lm.bounce_radius(m0),
                "kappa0": res.kappa0, "kappa0_formula_3m_over_r2": 3 * m0 / r0**2,
                "ceiling_reached_v": cv[0] if cv else None,
                "efolds_to_ceiling": (cv[0] - v_i) * res.kappa0 if cv else None,
                "ceiling_M": res.notes.get("ceiling_M"), "M_end_last_finite": last,
                "median_growth_over_kappa": float(np.median(slope[len(slope) // 4:])) / res.kappa0,
                "outcome": ("reaches the curvature ceiling R³/(2α)" if cv else
                            ("M₊ → −∞ (unbounded, exponential)" if last < 0
                             else "M₊ → +∞ (unbounded, exponential)")),
            })
    out["lmyz"] = lmyz_rows
    # 4. időzítés: hány e-redő férne bele r₋ és R_b között (több tömegre)
    out["crossing"] = [lmyz_crossing_efolds(m) for m in (10.0, 1e3, 1e6)]
    # 5. a szél-bezártság
    eta = conformal_time_to_end_of_inflation(n_onset, h_onset)
    from thesis.units import M_P, M_SUN
    masses = {"seed 1 m_P": 1.0, "seed 100 m_P": 100.0, "PBH 5.1e11 kg": 5.1e11 / M_P,
              "1 M_sun": M_SUN / M_P, "Sgr A*": 4.3e6 * M_SUN / M_P}
    conf = edge_confinement(eta["eta_total"], list(masses.values()))
    out["edge_confinement"] = {"eta": eta, "rows": [{"label": k, **c} for k, c
                                                    in zip(masses, conf, strict=True)],
                               "m_min_for_10pct_planck": mass_for_confinement(eta["eta_total"]),
                               "m_min_for_10pct_kg": mass_for_confinement(eta["eta_total"]) * M_P}
    return out


def brentq_safe(fun: Callable[[float], float], lo: float, hi: float) -> float | None:
    try:
        return float(brentq(fun, lo, hi))
    except ValueError:
        return None
