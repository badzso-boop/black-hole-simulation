"""L1b: gömbszimmetrikus Einstein–Maxwell–skalár kettős-null (karakterisztikus) megoldó.

Metrika:  ds² = −e^{2σ} du dv + r² dΩ²   (G = c = 1, a fekete lyuk tömege M₀ = 1 egység)
Anyag:    semleges, tömeg nélküli skalármező Φ (T_ab = (∇_aΦ∇_bΦ − ½g_ab(∇Φ)²)/4π) és egy
          korábbi, külső héjon ülő állandó Q töltés (Brady–Smith / Burko-féle elrendezés;
          a töltött skalár nincs implementálva — lásd docs/inner-horizon-plan.md §9).
Egyenletek (Burko & Ori 1997, PRD 56, 7820; statikus RN-nel ellenőrizve):
    r_uv = −e^{2σ}(1 − Q²/r²)/(4r) − r_u r_v/r                     ≡ F_r
    σ_uv =  e^{2σ}(1 − 2Q²/r²)/(4r²) + r_u r_v/r² − Φ_u Φ_v         ≡ F_σ
    Φ_uv = −(r_u Φ_v + r_v Φ_u)/r                                   ≡ F_Φ
Kényszerek (csak a kezdőadatra írjuk elő):  r_yy − 2σ_y r_y + r Φ_y² = 0  (y = u, v)
Tömegfüggvény: m = (r/2)(1 + Q²/r² + 4 e^{−2σ} r_u r_v).

Séma: másodrendű "gyémánt" prediktor-korrektor (Burko & Ori 1997): X_N = X_A + X_B − X_S +
ΔuΔv F(cella-közép), a középponti értékek iterálva; menetelés v-ben (külső), u-ban (belső).
A = (u_i, v_{j+1}), B = (u_{i+1}, v_j), S = (u_i, v_j), N = (u_{i+1}, v_{j+1}).
r ≤ r_min vagy nem véges → NaN (a szingularitáson túl), ez tovább terjed.

**Pontossági korlát (2026-09-30, mérve).** A tömegfüggvényhez r-t differenciáljuk; a
Cauchy-horizontnál r_v ~ e^{−κ₋v}, és ha a lépésenkénti Δr a lebegőpontos felbontás
(~1e-16·r) alá esik, a differencia 0 lesz (hamis platók). A növekedési rátát ezért csak ott
illesztjük, ahol |Δr| > 1e-12·r. Egy elsőrendű (Hamadé–Stewart) változatot is kipróbáltunk
(r_u, r_v saját változóként): az ezeken a felbontásokon a Cauchy-horizont közelében nem
konvergált (r_u előjele is hibás lett → negatív tömeg), ezért elvetettük.

Kezdőadat (belső, "adat az eseményhorizonton" jellegű; Brady & Smith 1995 szellemében):
    v = 0 befelé-sugár:   r = r_start − u, σ = ½ ln 2, Φ = ψ = 0, ν = −1, λ = f(r)/2,
                          χ: (rχ)_u = 0                                   (tiszta RN, Eddington-v)
    u = 0 kifelé-sugár:   σ(v) = RN-háttér lapse, Φ(v) = befelé fluxus (farok/impulzus),
                          r(v), λ = r_v a kényszerből; ν, ψ a v-irányú transzport-ODE-kből
ahol r₋ < r_start < r₊ (közvetlenül az eseményhorizont alatt).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp


@njit(cache=True)
def _evolve(r: np.ndarray, s: np.ndarray, p: np.ndarray, du: np.ndarray, dv: np.ndarray,
            q2: float, rmin: float, n_iter: int) -> None:
    nu_, nv_ = r.shape
    for j in range(nv_ - 1):
        dvj = dv[j]
        for i in range(nu_ - 1):
            dui = du[i]
            rS, sS, pS = r[i, j], s[i, j], p[i, j]
            rA, sA, pA = r[i, j + 1], s[i, j + 1], p[i, j + 1]   # ugyanaz az u, új v
            rB, sB, pB = r[i + 1, j], s[i + 1, j], p[i + 1, j]   # új u, régi v
            if not (np.isfinite(rS) and np.isfinite(rA) and np.isfinite(rB)
                    and rA > rmin and rB > rmin and rS > rmin):
                r[i + 1, j + 1] = np.nan
                s[i + 1, j + 1] = np.nan
                p[i + 1, j + 1] = np.nan
                continue
            rN = rA + rB - rS
            sN = sA + sB - sS
            pN = pA + pB - pS
            for _ in range(n_iter):
                rc = 0.25 * (rS + rA + rB + rN)
                sc = 0.25 * (sS + sA + sB + sN)
                if rc <= rmin:
                    break
                ru = ((rB - rS) + (rN - rA)) / (2.0 * dui)
                rv = ((rA - rS) + (rN - rB)) / (2.0 * dvj)
                pu = ((pB - pS) + (pN - pA)) / (2.0 * dui)
                pv = ((pA - pS) + (pN - pB)) / (2.0 * dvj)
                e2s = math.exp(2.0 * sc)
                fr = -e2s * (1.0 - q2 / (rc * rc)) / (4.0 * rc) - ru * rv / rc
                fs = e2s * (1.0 - 2.0 * q2 / (rc * rc)) / (4.0 * rc * rc) + ru * rv / (rc * rc) - pu * pv
                fp = -(ru * pv + rv * pu) / rc
                rN = rA + rB - rS + dui * dvj * fr
                sN = sA + sB - sS + dui * dvj * fs
                pN = pA + pB - pS + dui * dvj * fp
            if not (np.isfinite(rN) and rN > rmin):
                rN = np.nan
                sN = np.nan
                pN = np.nan
            r[i + 1, j + 1] = rN
            s[i + 1, j + 1] = sN
            p[i + 1, j + 1] = pN


def rn_horizons(q: float, m: float = 1.0) -> tuple[float, float]:
    d = math.sqrt(m * m - q * q)
    return m + d, q * q / (m + d)


def rn_kappa(q: float, m: float = 1.0) -> tuple[float, float]:
    rp, rm = rn_horizons(q, m)
    return (rp - rm) / (2 * rp * rp), (rp - rm) / (2 * rm * rm)


def rn_f(r: float, q: float, m: float = 1.0) -> float:
    return 1 - 2 * m / r + q * q / (r * r)


@dataclass
class Influx:
    """A befelé fluxus a kezdeti kifelé-sugáron (u = 0): Φ(v)."""

    kind: str = "tail"          # "tail": δ·(1+v/w)^−3 sin²-bekapcsolással; "pulse": sin²; "none"
    amplitude: float = 0.05
    v_on: float = 0.0           # a farok/impulzus kezdete
    width: float = 1.0          # impulzus szélessége / farok skálája
    late_pulse_v: float | None = None   # L1e: késői "aszteroida"-impulzus középpontja
    late_pulse_amp: float = 0.0
    late_pulse_width: float = 0.2

    def phi(self, v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype=float)
        out = np.zeros_like(v)
        if self.kind == "tail":
            x = np.clip((v - self.v_on) / self.width, 0, None)
            on = np.where(x < 1, np.sin(0.5 * np.pi * np.clip(x, 0, 1)) ** 2, 1.0)
            out = self.amplitude * on * (1 + np.clip(v - self.v_on, 0, None) / self.width) ** (-3.0)
        elif self.kind == "pulse":
            x = (v - self.v_on) / self.width
            out = np.where((x > 0) & (x < 1), self.amplitude * np.sin(np.pi * x) ** 2, 0.0)
        if self.late_pulse_v is not None and self.late_pulse_amp:
            x = (v - self.late_pulse_v) / self.late_pulse_width + 0.5
            out = out + np.where((x > 0) & (x < 1),
                                 self.late_pulse_amp * np.sin(np.pi * x) ** 2, 0.0)
        return np.asarray(out, dtype=float)


@dataclass
class Grid:
    q: float
    r_start: float
    r_end: float
    v_max: float
    nu: int
    nv: int
    influx: Influx = field(default_factory=Influx)
    rmin_frac: float = 0.02   # r ≤ rmin_frac·r₋ → szingulárisnak jelöljük
    n_iter: int = 3

    def axes(self) -> tuple[np.ndarray, np.ndarray]:
        u = np.linspace(0.0, self.r_start - self.r_end, self.nu)
        v = np.linspace(0.0, self.v_max, self.nv)
        return u, v


@dataclass
class Solution:
    grid: Grid
    u: np.ndarray
    v: np.ndarray
    r: np.ndarray
    sigma: np.ndarray
    phi: np.ndarray
    info: dict[str, Any] = field(default_factory=dict)

    def _mass(self, r: np.ndarray, s: np.ndarray, ru: np.ndarray, rv: np.ndarray) -> np.ndarray:
        q2 = self.grid.q**2
        with np.errstate(over="ignore", invalid="ignore"):
            return np.asarray(0.5 * r * (1 + q2 / r**2 + 4 * np.exp(-2 * s) * ru * rv), dtype=float)

    def mass(self) -> np.ndarray:
        ru = np.gradient(self.r, self.u, axis=0)
        rv = np.gradient(self.r, self.v, axis=1)
        return self._mass(self.r, self.sigma, ru, rv)

    def mass_row(self, i: int) -> np.ndarray:
        """m egy kifelé-sugár (rögzített u) mentén — memóriatakarékos (nagy rácsokhoz)."""
        i0, i1 = max(i - 1, 0), min(i + 1, len(self.u) - 1)
        ru = (self.r[i1] - self.r[i0]) / (self.u[i1] - self.u[i0])
        return self._mass(self.r[i], self.sigma[i], ru, np.gradient(self.r[i], self.v))

    def mass_col(self, j: int) -> np.ndarray:
        """m egy befelé-sugár (rögzített v) mentén."""
        j0, j1 = max(j - 1, 0), min(j + 1, len(self.v) - 1)
        rv = (self.r[:, j1] - self.r[:, j0]) / (self.v[j1] - self.v[j0])
        return self._mass(self.r[:, j], self.sigma[:, j], np.gradient(self.r[:, j], self.u), rv)


def initial_data(g: Grid) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    u, v = g.axes()
    q = g.q
    r = np.full((g.nu, g.nv), np.nan)
    s = np.full((g.nu, g.nv), np.nan)
    p = np.full((g.nu, g.nv), np.nan)
    rp, rm = rn_horizons(q)
    # --- v = 0 befelé-sugár: tiszta RN (r = r_start − u, σ = ½ ln 2, Φ = 0) ---
    r[:, 0] = g.r_start - u
    s[:, 0] = 0.5 * math.log(2.0)
    p[:, 0] = 0.0
    # --- u = 0 kifelé-sugár ---
    # háttér-lapse: y = ln(r − r₋), dy/dv = (r − r₊)/(2r²); ln|f| = ln(r₊ − r) + y − 2 ln r
    f0 = rn_f(g.r_start, q)

    def bg(_v: float, y: np.ndarray) -> list[float]:
        rr = rm + math.exp(y[0])
        return [(rr - rp) / (2 * rr * rr)]

    sol_bg = solve_ivp(bg, (0, g.v_max), [math.log(g.r_start - rm)], t_eval=v, rtol=1e-12,
                       atol=1e-12, method="DOP853")
    yb = sol_bg.y[0]
    r_bg = rm + np.exp(yb)
    ln_absf = np.log(rp - r_bg) + yb - 2 * np.log(r_bg)
    sigma_line = 0.5 * math.log(2.0) + 0.5 * (ln_absf - math.log(abs(f0)))
    phi_line = g.influx.phi(v)
    sv = np.gradient(sigma_line, v)
    pv = np.gradient(phi_line, v)

    # kényszer: r_vv = 2σ_v r_v − rΦ_v²; w = ln(−r_v): r' = −e^w, w' = 2σ_v + rΦ_v² e^{−w}
    def rhs(vv: float, y: np.ndarray) -> list[float]:
        sv_i = float(np.interp(vv, v, sv))
        pv_i = float(np.interp(vv, v, pv))
        return [-math.exp(y[1]), 2 * sv_i + y[0] * pv_i**2 * math.exp(-y[1])]

    sol = solve_ivp(rhs, (0, g.v_max), [g.r_start, math.log(-0.5 * f0)], t_eval=v, rtol=1e-11,
                    atol=1e-12, method="DOP853", max_step=(v[1] - v[0]))
    if sol.y.shape[1] != len(v):
        raise RuntimeError(f"a kezdőadat integrálása leállt: {sol.message}")
    r[0, :] = sol.y[0]
    s[0, :] = sigma_line
    p[0, :] = phi_line
    return u, v, r, s, p


def solve(g: Grid) -> Solution:
    u, v, r, s, p = initial_data(g)
    rp, rm = rn_horizons(g.q)
    _evolve(r, s, p, np.diff(u), np.diff(v), g.q**2, g.rmin_frac * rm, g.n_iter)
    kp, km = rn_kappa(g.q)
    return Solution(grid=g, u=u, v=v, r=r, sigma=s, phi=p,
                    info={"r_plus": rp, "r_minus": rm, "kappa_plus": kp, "kappa_minus": km})


# ---------------------------------------------------------------------------
# Elemzés
# ---------------------------------------------------------------------------


def growth_along_ray(sol: Solution, i_ray: int, v_fit: tuple[float, float]) -> dict[str, float]:
    """ln m(v) illesztése egy belső kifelé-sugáron, ahol a tömeg-infláció már elindult (m > 2)
    ÉS r v-menti változása lépésenként még feloldható (|Δr| > 1e-12·r); a leghosszabb
    összefüggő érvényes szakaszon: lineáris (κ) és hatványtagos (ln m = a + κv − q ln v)."""
    m = sol.mass_row(i_ray)
    v = sol.v
    r = sol.r[i_ray]
    resolvable = np.abs(np.gradient(r)) > 1e-12 * np.abs(r)
    sel = (v >= v_fit[0]) & (v <= v_fit[1]) & np.isfinite(m) & (m > 2) & resolvable
    best, cur, best_rng = 0, 0, (0, 0)
    for k, ok in enumerate(sel):
        cur = cur + 1 if ok else 0
        if cur > best:
            best, best_rng = cur, (k - cur + 1, k + 1)
    if best < 10:
        return {"ok": 0.0, "n_points": float(best)}
    x = v[best_rng[0]:best_rng[1]]
    y = np.log(m[best_rng[0]:best_rng[1]])
    a_mat = np.vstack([np.ones_like(x), x, -np.log(x)]).T
    coef, *_ = np.linalg.lstsq(a_mat, y, rcond=None)
    lin = np.polyfit(x, y, 1)
    return {"ok": 1.0, "a": float(coef[0]), "kappa_fit": float(lin[0]), "q_fit": float(coef[2]),
            "kappa_fit_with_powerlaw": float(coef[1]), "n_points": float(best),
            "slope_end": float(np.gradient(y, x)[-1]), "log_m_end": float(y[-1]),
            "v_start": float(x[0]), "v_end": float(x[-1]), "r_ray_end": float(r[best_rng[1] - 1])}


def ray_fates(sol: Solution) -> dict[str, Any]:
    """Minden kifelé-sugárra: véges v-nél szinguláris lesz-e (r → r_min), és a legkisebb r."""
    fin = np.isfinite(sol.r)
    ends_finite_v = ~fin[:, -1]
    r_last = np.array([sol.r[i][fin[i]][-1] if fin[i].any() else np.nan
                       for i in range(sol.r.shape[0])])
    return {"n_rays": int(sol.r.shape[0]), "n_reaching_v_max": int((~ends_finite_v).sum()),
            "n_singular_before_v_max": int(ends_finite_v.sum()), "r_last": r_last}


def ingoing_ray_profile(sol: Solution, v_target: float) -> dict[str, Any]:
    """L1e: a v = v_target befelé-sugár mentén a tömegfüggvény és r (u szerint)."""
    j = int(np.clip(np.searchsorted(sol.v, v_target), 0, len(sol.v) - 1))
    m = sol.mass_col(j)
    r = sol.r[:, j]
    fin = np.isfinite(r) & np.isfinite(m)
    return {"v": float(sol.v[j]), "u": sol.u[fin].tolist(), "r": r[fin].tolist(),
            "m": m[fin].tolist(), "reaches_singularity": bool(not fin[-1]),
            "max_log10_m": float(np.log10(np.nanmax(np.abs(m[fin])))) if fin.any() else float("nan")}
