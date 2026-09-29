"""WP1: elég inflációt ad-e a visszapattanás, és jó-e az (n_s, r)?

Minden itt az `inflation.evolve` trajektóriáira épül:
    scan_phi_b          N_infl(φ_B) rács mindkét φ̇_B előjellel
    threshold_phi_b     az a φ_B, ahol N_infl = N_cél (biszekció) — Bonga–Gupt küszöbei
    phi2_fraction       φ²: a |φ_B| ≤ φ_max tartomány mekkora hányada ad ≥ 68 e-redőt
                        (egyenletes mérték φ_B-ben, Ashtekar–Sloan 2011)
    pivot_consistent    N* önkonzisztensen a felmelegedési hőmérsékletből (k* = 0.05/Mpc)
    energy_budget       a szülő tömegéből mennyi energia lesz az infláció végére
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from thesis.history import max_reheat_temperature_gev, post_inflation
from thesis.inflation import (
    Potential,
    Quadratic,
    Starobinsky,
    evolve,
    phi_end_slow_roll,
    pivot_observables,
)
from thesis.lqc import bounce_radius_m
from thesis.units import H0_KM_S_MPC, L_P, M_P, M_SUN, MPC, RHO_C, C, G, hubble0_planck

K_PIVOT_MPC = 0.05  # Planck pivot, Mpc⁻¹


def scan_phi_b(pot: Potential, phis: np.ndarray, sign: int, n_cap: float = 150.0) -> list[dict[str, Any]]:
    out = []
    for phi in phis:
        r = evolve(pot, float(phi), sign, n_cap=n_cap)
        out.append({"phi_b": float(phi), "sign": sign, "n_infl": r.n_infl, "n_onset": r.n_onset,
                    "capped": r.capped, "drift": r.constraint_drift})
    return out


def threshold_phi_b(pot: Potential, sign: int, n_target: float, lo: float, hi: float,
                    tol: float = 1e-4, shear_fraction: float = 0.0) -> float:
    """φ_B, ahol N_infl = n_target; lo-nál kevesebb, hi-nál több infláció legyen."""

    def f(phi: float) -> float:
        return evolve(pot, phi, sign, shear_fraction=shear_fraction).n_infl - n_target

    f_lo = f(lo)
    f_hi = f(hi)
    if f_lo * f_hi > 0:
        raise ValueError(f"nincs előjelváltás [{lo}, {hi}] között")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if f(mid) * f_lo > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def phi2_fraction(n_required: float = 68.0, inner: float = 15.0, step: float = 0.05,
                  shear_fraction: float = 0.0) -> dict[str, Any]:
    """Ashtekar–Sloan 2011 (§IV D): a φ² bounce-adatok mekkora hányada ad < n_required e-redőt.

    V szimmetrikus, így (φ_B, +φ̇) és (−φ_B, −φ̇) ugyanaz a megoldás: elég φ̇_B > 0.
    A kudarc-sávokat `step` rácson keressük meg |φ_B| ≤ inner-ben, a széleket
    biszekcióval finomítjuk; a sávon kívül logaritmikus mintákkal ellenőrizzük, hogy
    mindenhol teljesül. Két mérték:
      egyenletes φ_B-ben:      P = Σ szélesség / (2 φ_max)
      Liouville (AS Eq. 4.26):  P = Σ [g(f_hi) − g(f_lo)] / π,  g(f) = f√(1−f²) + arcsin f
    (Az AS cikk a [−5.5, 0.94] sávra 2.74e-6-ot közöl; a saját Eq. 4.26-juk ≈ 5.5e-6-ot ad —
    kettes faktor eltérés a cikkben; mindkettő „néhány milliomod".)
    """
    pot = Quadratic()
    phi_max = pot.phi_max_bounce() * math.sqrt(1 - shear_fraction)

    def fails(phi: float) -> bool:
        return evolve(pot, phi, 1, shear_fraction=shear_fraction).n_infl < n_required

    grid = np.arange(-inner, inner + step / 2, step)
    flags = [fails(float(p)) for p in grid]
    bands: list[list[float]] = []
    for i in range(1, len(grid)):
        if flags[i] != flags[i - 1]:
            lo, hi = float(grid[i - 1]), float(grid[i])
            for _ in range(20):
                mid = 0.5 * (lo + hi)
                if fails(mid) == flags[i - 1]:
                    lo = mid
                else:
                    hi = mid
            edge = 0.5 * (lo + hi)
            if flags[i]:
                bands.append([edge, float("nan")])
            else:
                bands[-1][1] = edge
    if flags[0] or flags[-1]:
        raise RuntimeError("a kudarc-sáv eléri a rács szélét — növeld az `inner`-t")
    outer_failures = [
        {"phi_b": float(ph), "n_infl": evolve(pot, float(ph), 1, shear_fraction=shear_fraction).n_infl}
        for mag in np.geomspace(inner, 0.999 * phi_max, 12) for ph in (mag, -mag) if fails(float(ph))
    ]

    def g(f: float) -> float:
        return f * math.sqrt(1 - f * f) + math.asin(f)

    width = sum(hi - lo for lo, hi in bands)
    p_uniform = width / (2 * phi_max)
    p_liouville = sum(g(hi / phi_max) - g(lo / phi_max) for lo, hi in bands) / math.pi
    return {"n_required": n_required, "shear_fraction": shear_fraction, "phi_max": phi_max,
            "fail_bands_phidot_pos": bands, "fail_width_mPl": width,
            "fraction_fail_uniform": p_uniform, "fraction_fail_liouville": p_liouville,
            "ashtekar_sloan_band": [-5.5, 0.94], "ashtekar_sloan_quoted": 2.74e-6,
            "outer_failures": outer_failures}


def n_star_consistent(pot: Potential, phi_end: float, hi: float, rho_end: float,
                      t_reh_gev: float) -> dict[str, Any]:
    """N* = ln(H*/H0) − N_post − ln(k*/(a0 H0)), iterálva (N* függ V*-tól)."""
    ln_k = math.log(K_PIVOT_MPC / (H0_KM_S_MPC / (C / 1e3)))  # k*/(a0H0), a0H0 = H0/c Mpc⁻¹-ben
    post = post_inflation(rho_end, t_reh_gev)
    n_star = 55.0
    for _ in range(30):
        obs = pivot_observables(pot, n_star, phi_end, hi)
        h_star = math.sqrt(8 * math.pi * obs["V_star"] / 3)
        new = math.log(h_star / hubble0_planck()) - post.n_post - ln_k
        if abs(new - n_star) < 1e-6:
            break
        n_star = new
    obs = pivot_observables(pot, n_star, phi_end, hi)
    return {**obs, "t_reh_gev": t_reh_gev, "n_post": post.n_post, "post": post.as_dict()}


def starobinsky_end() -> tuple[Starobinsky, float, float]:
    pot = Starobinsky()
    phi_end = phi_end_slow_roll(pot, 0.01, 3.0)
    return pot, phi_end, 1.5 * pot.v(phi_end)


def energy_budget(mass_kg: float, n_onset: float, n_infl: float, rho_inf: float) -> dict[str, float]:
    """A labda energiája az infláció végén vs a szülő tömege; Hubble-térfogat tömege ma.

    Energia nem globálisan megmaradó táguló téridőben: inflációkor ρ ≈ állandó, a térfogat
    e^{3N}-nel nő, így az energia is (Guth „ingyen ebédje").
    """
    r_b = bounce_radius_m(mass_kg) / L_P  # Planck-egységben
    ln_e_end = math.log(rho_inf * 4 * math.pi / 3 * r_b**3) + 3 * (n_onset + n_infl)
    ln_m_parent = math.log(mass_kg / M_P)
    h0 = H0_KM_S_MPC * 1e3 / MPC
    m_hubble_kg = 4 / 3 * math.pi * (C / h0) ** 3 * 3 * h0**2 / (8 * math.pi * G)
    return {
        "check_parent_mass_equals_rho_c_volume": RHO_C * 4 * math.pi / 3 * r_b**3 / (mass_kg / M_P),
        "ln_energy_gain": ln_e_end - ln_m_parent,
        "n_infl_to_hubble_mass": (math.log(m_hubble_kg / mass_kg)
                                  - math.log(rho_inf / RHO_C)) / 3 - n_onset,
        "m_hubble_kg": m_hubble_kg,
    }


def run() -> dict[str, Any]:
    """A WP1 teljes számolása (a futtató szkript hívja)."""
    star = Starobinsky()
    quad = Quadratic()
    # 1. N_infl(φ_B) görbék
    curves = {
        "starobinsky_plus": scan_phi_b(star, np.linspace(star.phi_min_bounce() + 1e-3, 1.0, 60), 1),
        "starobinsky_minus": scan_phi_b(star, np.linspace(1.0, 4.2, 60), -1),
        "phi2_plus": scan_phi_b(quad, np.linspace(-12, 6, 73), 1),
    }
    # 2. Bonga–Gupt küszöbök (60 e-redőre, a literatúra lassú gördülési kritériuma szerint)
    thresholds = {}
    for n_t in (60.0, 68.0):
        thresholds[f"plus_N{int(n_t)}"] = threshold_phi_b(star, 1, n_t, -1.8, -1.0)
        thresholds[f"minus_N{int(n_t)}"] = threshold_phi_b(star, -1, n_t, 3.3, 4.0)
    # 3. φ² mérték
    frac = phi2_fraction()
    # 4. (n_s, r): önkonzisztens N* a felmelegedési hőmérséklet függvényében
    pot, phi_end, rho_end = starobinsky_end()
    t_max = max_reheat_temperature_gev(rho_end)
    pivots = [n_star_consistent(pot, phi_end, 12.0, rho_end, t)
              for t in (t_max, 1e9, 1e3, 4e-3)]
    fixed = [pivot_observables(pot, n, phi_end, 12.0) for n in (50.0, 55.0, 60.0)]
    # 5. energiamérleg: 1 M_☉ szülő, 60 e-redő, Starobinsky (ρ_inf ≈ V(φ*) a pivotnál)
    budget = energy_budget(M_SUN, 4.5, 60.0, pivots[0]["V_star"])
    return {"curves": curves, "thresholds": thresholds, "phi2_fraction": frac,
            "phi_end_starobinsky": phi_end, "rho_end_starobinsky": rho_end,
            "t_reh_max_gev": t_max, "pivots_consistent": pivots, "pivots_fixed": fixed,
            "energy_budget_1msun": budget}
