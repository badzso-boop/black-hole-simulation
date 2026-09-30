"""L1c–L1f: a verseny a belső horizonton (docs/inner-horizon-plan.md).

Kérdés: a csillag anyaga (a „szikra") átjut-e a forgó fekete lyuk belső horizontján, mielőtt az
Planck-görbületűvé válik? Mennyiségek M-egységben (G = c = 1, a lyuk tömege M):

  Planck-görbület a belső horizontnál: K ≈ 48 m²/r₋⁶ = (M/m_P)⁴  →  m_Pl = r₋³ (M/m_P)²/√48
  tömeg-infláció:  ln m(v) = ln A + κ₋ v          (KONZERVATÍV: a klasszikus Price-farok
                   v^−(p+1) elnyomását elhagyjuk — az Ori-modell szerint az csak lassítana)
  → v_Pl = [ln m_Pl − ln A]/κ₋,  A_klasszikus = δ²  (δ: a perturbáció amplitúdója a horizont
    képződésekor; fiduciális δ = 0.1, sáv ×e^±5 — a kettős-null kód a növekedési rátát
    validálja, az amplitúdó a felbontás-létrán dől el), A_kvantum = F/κ₋, F = 4π r₋² ⟨T_vv⟩
  a szikra:  Δv_spark = ∫ v̇/|ṙ| dr  r₊ → r₋ (radiális, E = 1 esés a Kerr-tengelyen)
  torzulás:  D = M/r₋ (Kerr)

A forgás ↔ töltés megfeleltetés κ₋M egyenlőségével (kutatás, D fejezet). A kvantum-fluxus
nagysága: a Kerr a* = 0.8 pólus-érték (Zilberman, Casals, Ori & Ottewill 2022:
⟨T_vv⟩ ≈ 3.0e-5 ħ/M⁴) κ₋²-tel skálázva, ×100 sávval (a v_Pl csak logaritmikusan függ tőle).

Az ítéletek a terv §5 szabályai (előre rögzítve 2026-09-30); a számszerű részletek, amiket a terv
nem adott meg, itt, a futtatás ELŐTT rögzítve: fiduciális M = 10 M☉, δ = 0.1.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

from thesis.units import M_P, M_SUN

FIDUCIAL_MASS_KG = 10 * M_SUN
FIDUCIAL_DELTA = 0.1
AMPLITUDE_BAND_E = 5.0          # ln A bizonytalansága (± e-faktor)
T_VV_KERR_08 = 3.013e-5          # ħ/M⁴, a = 0.8, pólus (arXiv:2203.08502)
QUANTUM_BAND = 100.0
MARGIN_REQUIRED = 10.0           # a terv §5: a szikra legalább 10× korábban lép át
D_MAX = 10.0


# ---------------------------------------------------------------------------
# Kerr- és RN-geometria (M = 1)
# ---------------------------------------------------------------------------


def kerr_horizons(a: float) -> tuple[float, float]:
    d = math.sqrt(1 - a * a)
    return 1 + d, a * a / (1 + d)  # r₋ kioltás nélkül


def kerr_kappa_minus(a: float) -> float:
    rp, rm = kerr_horizons(a)
    return (rp - rm) / (4 * rm)


def rn_kappa_minus(q: float) -> float:
    d = math.sqrt(1 - q * q)
    rp, rm = 1 + d, q * q / (1 + d)
    return (rp - rm) / (2 * rm * rm)


def q_for_kappa(kappa: float) -> float:
    """Az a Q/M, amelynél az RN κ₋M megegyezik a megadottal (κ₋ monoton csökken Q-ban)."""
    return float(brentq(lambda q: rn_kappa_minus(q) - kappa, 1e-9, 1 - 1e-15))


def spark_crossing_dv(a: float) -> float:
    """Δv a Kerr-tengelyen radiálisan (E = 1) eső anyagra r₊-tól r₋-ig (M-egység)."""
    rp, rm = kerr_horizons(a)

    def f(r: float) -> float:
        return (r * r - 2 * r + a * a) / (r * r + a * a)

    def integrand(r: float) -> float:
        ff = f(r)
        s = math.sqrt(max(1 - ff, 0.0))
        vdot = (1 - s) / ff if abs(ff) > 1e-12 else 0.5
        return vdot / s

    return float(quad(integrand, rm, rp, limit=400)[0])


# ---------------------------------------------------------------------------
# A verseny
# ---------------------------------------------------------------------------


def log_m_planck(r_minus: float, mass_kg: float) -> float:
    return 3 * math.log(r_minus) + 2 * math.log(mass_kg / M_P) - 0.5 * math.log(48.0)


def quantum_flux(a: float) -> float:
    """⟨T_vv⟩ a belső horizonton, ħ/M⁴ egységben (a = 0.8-ra kalibrálva, κ₋²-tel skálázva)."""
    return T_VV_KERR_08 * (kerr_kappa_minus(a) / kerr_kappa_minus(0.8)) ** 2


def race(a: float, mass_kg: float = FIDUCIAL_MASS_KG, delta: float = FIDUCIAL_DELTA,
         ln_amp_offset: float = 0.0) -> dict[str, Any]:
    _, rm = kerr_horizons(a)
    k = kerr_kappa_minus(a)
    lmp = log_m_planck(rm, mass_kg)
    ln_a_cl = 2 * math.log(delta) + ln_amp_offset
    hbar = (M_P / mass_kg) ** 2  # ħ M-egységben
    flux = 4 * math.pi * rm * rm * quantum_flux(a) * hbar
    ln_a_q = math.log(flux / k)
    v_cl = (lmp - ln_a_cl) / k
    v_q = (lmp - ln_a_q) / k
    dv = spark_crossing_dv(a)
    return {"a_star": a, "r_minus": rm, "kappa_minus": k, "q_equivalent": q_for_kappa(k),
            "log_m_planck": lmp, "v_planck_classical": v_cl, "v_planck_quantum": v_q,
            "v_planck_quantum_band": [(lmp - ln_a_q - math.log(QUANTUM_BAND)) / k,
                                      (lmp - ln_a_q + math.log(QUANTUM_BAND)) / k],
            "dv_spark": dv, "margin": v_cl / dv, "distortion_D": 1 / rm,
            "passes": float(v_cl / dv >= MARGIN_REQUIRED and 1 / rm <= D_MAX),
            "quantum_first": float(v_q < v_cl),
            "delta_below_which_quantum_first": math.exp(0.5 * ln_a_q)}


def population_race(pops: dict[str, dict[str, Any]], mass_kg: float = FIDUCIAL_MASS_KG,
                    delta: float = FIDUCIAL_DELTA) -> dict[str, Any]:
    out = {}
    for name, p in pops.items():
        rows = [race(max(min(a, 0.9999), 1e-4), mass_kg, delta) for a in p["a"]]
        frac = float(np.mean([r["passes"] for r in rows]))
        lo = float(np.mean([race(max(min(a, 0.9999), 1e-4), mass_kg, delta,
                                 +AMPLITUDE_BAND_E)["passes"] for a in p["a"]]))
        hi = float(np.mean([race(max(min(a, 0.9999), 1e-4), mass_kg, delta,
                                 -AMPLITUDE_BAND_E)["passes"] for a in p["a"]]))
        out[name] = {"fraction_pass": frac, "fraction_pass_band": [lo, hi],
                     "observed": p.get("observed", False),
                     "median_margin": float(np.median([r["margin"] for r in rows])),
                     "median_D": float(np.median([r["distortion_D"] for r in rows]))}
    return out


def spin_scan(mass_kg: float = FIDUCIAL_MASS_KG, delta: float = FIDUCIAL_DELTA) -> list[dict[str, float]]:
    return [race(a, mass_kg, delta) for a in np.geomspace(1e-3, 0.998, 60)]


def mass_scan_quantum(a_values: tuple[float, ...] = (0.1, 0.44, 0.8, 0.95)) -> list[dict[str, Any]]:
    """L1d: tömegenként melyik ér előbb Planck-görbületet — a klasszikus vagy a kvantum?"""
    masses = {"PBH 1e12 kg": 1e12, "PBH 5.1e11 kg": 5.1e11, "10 M_sun": 10 * M_SUN,
              "Sgr A*": 4.3e6 * M_SUN, "M87*": 6.5e9 * M_SUN}
    rows = []
    for label, mk in masses.items():
        for a in a_values:
            r = race(a, mk)
            rows.append({"mass": label, "a_star": a, "v_cl": r["v_planck_classical"],
                         "v_q": r["v_planck_quantum"], "quantum_first": r["quantum_first"],
                         "delta_threshold": r["delta_below_which_quantum_first"],
                         "dv_spark": r["dv_spark"]})
    return rows


def asteroid(mass_kg: float = FIDUCIAL_MASS_KG, delays_s: tuple[float, ...] = (1.0, 86400.0,
             3.156e7), a_values: tuple[float, ...] = (0.01, 0.26, 0.7, 0.97)) -> list[dict[str, Any]]:
    """L1e: egy késői test (aszteroida) a képződés után t késéssel esik be; v_late = t/(GM/c³).
    Ha v_late > v_Pl, a belső horizont tartománya már Planck-görbületű (klasszikusan: a
    Cauchy-horizont tömeg-inflációs szingularitása) — ott ér véget."""
    from thesis.units import C, G

    t_m = G * mass_kg / C**3
    rows = []
    for a in a_values:
        r = race(a, mass_kg)
        for d in delays_s:
            v_late = d / t_m
            rows.append({"a_star": a, "delay_s": d, "v_late": v_late,
                         "v_planck": r["v_planck_classical"],
                         "meets_planckian_inner_horizon": float(v_late > r["v_planck_classical"])})
    return rows


# ---------------------------------------------------------------------------
# A kettős-null kód futtatásai (L1b validáció + L1c amplitúdó-létra)
# ---------------------------------------------------------------------------


def dn_growth(q: float, n: int, amplitude: float, v_max_kappa: float = 90.0,
              width_kappa: float = 4.5, fit_from_kappa: float = 45.0) -> dict[str, Any]:
    """Egy futás: κ-illesztés és ln m a v_max-nál egy belső sugáron; amplitude = 0 a numerikus
    „padló" (a csonkolási hiba mint mag). Az illesztés κ₋v ≥ 45-ön, ahol a tömeg-infláció már
    tisztán exponenciális, és csak ahol r változása feloldható (lásd doublenull.growth_along_ray).
    Q = 0.632-n (Brady–Smith) n = 400 és 800 között a ráta 0.1%-on belül egyezik."""
    from thesis.doublenull import Grid, Influx, growth_along_ray, rn_horizons, solve

    rp, rm = rn_horizons(q)
    km = rn_kappa_minus(q)
    v_max = v_max_kappa / km
    g = Grid(q=q, r_start=rp - 0.05 * (rp - rm), r_end=0.5 * rm, v_max=v_max, nu=n, nv=5 * n,
             influx=Influx(kind="tail" if amplitude else "none", amplitude=amplitude,
                           v_on=0.0, width=width_kappa / km))
    sol = solve(g)
    target = rm + 0.5 * (g.r_start - rm)
    i = int(np.argmin(np.abs(sol.r[:, 0] - target)))
    res = growth_along_ray(sol, i, (fit_from_kappa / km, v_max))
    return {"q": q, "n": n, "amplitude": amplitude, "kappa_exact": km, **res}


def dn_validation_static(q: float, n: int) -> dict[str, Any]:
    """T1: statikus RN — r(u,v) az egzakt dr/dv = f/2 megoldással; másodrendű konvergencia."""
    from scipy.integrate import solve_ivp

    from thesis.doublenull import Grid, Influx, rn_f, rn_horizons, solve

    rp, rm = rn_horizons(q)
    km = rn_kappa_minus(q)
    g = Grid(q=q, r_start=rp - 0.05 * (rp - rm), r_end=0.5 * rm, v_max=min(4.0, 8.0 / km),
             nu=n, nv=n, influx=Influx(kind="none"))
    sol = solve(g)
    err = 0.0
    for i in range(0, n, max(n // 20, 1)):
        ex = solve_ivp(lambda _v, y: [0.5 * rn_f(y[0], q)], (0, g.v_max), [sol.r[i, 0]],
                       t_eval=sol.v, rtol=1e-12, atol=1e-14, method="DOP853").y[0]
        err = max(err, float(np.nanmax(np.abs(sol.r[i] - ex))))
    m = sol.mass()
    return {"q": q, "n": n, "r_plus": rp, "r_minus": rm, "kappa_minus": km,
            "max_abs_r_error": err, "median_abs_mass_error": float(np.nanmedian(np.abs(m - 1)))}


def dn_late_pulse(q: float, n: int, v_late_kappa: float = 50.0) -> dict[str, Any]:
    """L1e a kódban: farok + késői impulzus; a késői befelé-sugár sorsa."""
    from thesis.doublenull import Grid, Influx, ingoing_ray_profile, ray_fates, rn_horizons, solve

    rp, rm = rn_horizons(q)
    km = rn_kappa_minus(q)
    v_max = 90.0 / km
    v_late = v_late_kappa / km
    g = Grid(q=q, r_start=rp - 0.05 * (rp - rm), r_end=0.05 * rm, v_max=v_max, nu=n, nv=5 * n,
             influx=Influx(kind="tail", amplitude=0.1, v_on=0.0, width=4.5 / km,
                           late_pulse_v=v_late, late_pulse_amp=0.05, late_pulse_width=2.0 / km))
    sol = solve(g)
    prof = ingoing_ray_profile(sol, v_late + 1.0 / km)
    fates = ray_fates(sol)
    return {"q": q, "n": n, "v_late": v_late, "ray_max_log10_m": prof["max_log10_m"],
            "ray_reaches_singularity": prof["reaches_singularity"],
            "ray_r_min": float(np.min(prof["r"])) if prof["r"] else float("nan"),
            "n_rays_singular_before_v_max": fates["n_singular_before_v_max"],
            "n_rays": fates["n_rays"]}


def drift_test(t_vv: float = 1e-4, q: float = 0.8) -> dict[str, float]:
    """T10b: a kényszer r_vv − 2σ_v r_v = −4πr T_vv a CH közelében (2σ_v → −κ₋) állandó
    forrással: r_v → −4π(r₋/κ₋)T_vv (Zilberman–Levi–Ori eq. 15)."""
    from scipy.integrate import solve_ivp

    d = math.sqrt(1 - q * q)
    rm = q * q / (1 + d)
    km = rn_kappa_minus(q)

    def rhs(_v: float, y: np.ndarray) -> list[float]:
        return [y[1], -km * y[1] - 4 * math.pi * y[0] * t_vv]

    sol = solve_ivp(rhs, (0, 40 / km), [rm, 0.0], rtol=1e-12, atol=1e-15, method="DOP853")
    return {"r_v_final": float(sol.y[1][-1]), "expected": -4 * math.pi * rm * t_vv / km}
