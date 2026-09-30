"""WP3 + WP3b: görbület és a bébiuniverzum széle — ugyanaz a geometria.

A szülő fekete lyukat alkotó porgömb (Oppenheimer–Snyder) R0 = n·r_s-ről,
nyugalomból indulva **zárt** (k = +1) Friedmann-tartomány: a felszínén
R = a·sin χ0, és  sin²χ0 = r_s/R0  (marginálisan kötött, R0 → ∞ esetén k = 0).
A visszapattanáskor a gömb sugara r_b(M) (LMY 2023), tehát
    görbületi sugár a visszapattanáskor:  R_c,B = r_b / sin χ0 = r_b·√(R0/r_s)
    a gömb (a „bébiuniverzum") sugara ma: R_ball,0 = r_b · e^{N_tot}
    görbületi sugár ma:                   R_c,0 = R_c,B · e^{N_tot}
    Ω_K,0 = −(c/H0)² / R_c,0²    (zárt: negatív)
ahol N_tot = ln(a_0/a_B) a visszapattanástól a mai napig (Zhu et al. 2017 definíciója).

WP3b feltételei (a bébiuniverzumnak a mi megfigyelhető Univerzumunkat kell tartalmaznia):
    (i)  R_ball,0 > részecskehorizont (14.26 Gpc)
    (ii) |Ω_K,0| a mért határon belül (DESI DR2 + CMB: 0.0023 ± 0.0011)
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

from thesis.lqc import bounce_radius_m
from thesis.units import M_SUN, PARTICLE_HORIZON_M, C, G, hubble0_planck, hubble_radius_m

# DESI DR2 + CMB (68%): Ω_K = 0.0023 ± 0.0011 → zárt esetben 3σ-alsó határ −0.0010
OMEGA_K_DESI = (0.0023, 0.0011)


@dataclass
class ParentGeometry:
    mass_kg: float
    r0_over_rs: float  # float("inf"): marginálisan kötött (lapos)
    r_bounce_m: float
    r_curv_bounce_m: float  # inf, ha lapos

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def parent_geometry(mass_kg: float, r0_over_rs: float) -> ParentGeometry:
    r_b = bounce_radius_m(mass_kg)
    r_c = r_b * math.sqrt(r0_over_rs) if math.isfinite(r0_over_rs) else float("inf")
    return ParentGeometry(mass_kg, r0_over_rs, r_b, r_c)


def schwarzschild_radius_m(mass_kg: float) -> float:
    return 2 * G * mass_kg / C**2


def n_tot_min_edge(mass_kg: float) -> float:
    """(i): a gömb széle a részecskehorizonton túl: N_tot > ln(R_obs/r_b)."""
    return math.log(PARTICLE_HORIZON_M / bounce_radius_m(mass_kg))


def omega_k_today(geo: ParentGeometry, n_tot: float) -> float:
    if not math.isfinite(geo.r_curv_bounce_m):
        return 0.0
    # ln-ben, a túlcsordulás elkerülésére
    ln_ratio = math.log(hubble_radius_m()) - math.log(geo.r_curv_bounce_m) - n_tot
    return -math.exp(2 * ln_ratio)


def n_tot_min_curvature(geo: ParentGeometry, n_sigma: float = 3.0) -> float:
    """(ii): |Ω_K,0| ≤ a DESI-határ n_sigma-n (zárt oldal): N_tot > ln(R_H/(R_c,B √|Ω_lim|))."""
    if not math.isfinite(geo.r_curv_bounce_m):
        return float("-inf")
    mean, sd = OMEGA_K_DESI
    limit = max(-(mean - n_sigma * sd), 1e-12)  # a megengedett legnagyobb |Ω_K| zárt esetben
    return math.log(hubble_radius_m() / (geo.r_curv_bounce_m * math.sqrt(limit)))


def verdict_for(geo: ParentGeometry, n_tot: float) -> dict[str, Any]:
    ok_edge = n_tot > n_tot_min_edge(geo.mass_kg)
    ok_curv = n_tot > n_tot_min_curvature(geo)
    return {
        **geo.as_dict(),
        "n_tot": n_tot,
        "n_tot_min_edge": n_tot_min_edge(geo.mass_kg),
        "n_tot_min_curvature_3sigma": n_tot_min_curvature(geo),
        "omega_k_today": omega_k_today(geo, n_tot),
        "edge_beyond_horizon": ok_edge,
        "curvature_allowed": ok_curv,
    }


# ---------------------------------------------------------------------------
# WP3/WP3b futtatás
# ---------------------------------------------------------------------------

PARENTS_KG = {
    "PBH 5.1e11 kg": 5.1e11,
    "1 M_sun": 1.0 * M_SUN,
    "10 M_sun": 10.0 * M_SUN,
    "Sgr A* (4.3e6 M_sun)": 4.3e6 * M_SUN,
    "M87* (6.5e9 M_sun)": 6.5e9 * M_SUN,
    "Gaztanaga parent (5e22 M_sun)": 5e22 * M_SUN,
}
R0_OVER_RS = [1.0, 10.0, 1e3, 2.3e5]  # 2.3e5: a Nap sugara / r_s(Nap) — nyugalomból induló csillag
# Hivatkozási N_tot-értékek (A2, critical-review.md §3.3). A korábbi „LQC természetes 130–145"
# sáv felső vége a Linsefors–Barrau 2013-féle 145 INFLÁCIÓS e-redő volt, N_tot-nak olvasva.
ZHU_N_TOT_LOWER_95 = 141.0  # Zhu et al. 2017: megfigyelési alsó korlát (nem jóslat)
LB_N_INFL_PEAK = 145.0  # Linsefors & Barrau 2013: N_infl eloszlásának csúcsa (φ², más kezdőállapot)
OMEGA_K_REFERENCE_N_TOT = 130.0  # csak a régi táblázat-oszlop folytonosságáért


def n_hor(n_post: float, h_inf: float) -> float:
    """A horizont-probléma: a mai Hubble-skála (k = a0H0) az infláció alatt lépjen ki.

    N_hor = ln(H_inf/H0) − N_post  (Liddle & Leach 2003 Eq. 6 szerkezete).
    """
    return math.log(h_inf / hubble0_planck()) - n_post


def run(n_onset: float, n_post_by_treh: dict[str, float], h_inf: float) -> dict[str, Any]:
    """n_onset, N_post és H_inf a WP1-ből jön (a futtató adja át)."""
    rows = []
    for label, m in PARENTS_KG.items():
        edge = n_tot_min_edge(m)
        for treh, n_post in n_post_by_treh.items():
            nh = n_hor(n_post, h_inf)
            n_tot_minimal = n_onset + nh + n_post  # épp elég infláció a horizont-problémához
            row: dict[str, Any] = {
                "parent": label, "mass_kg": m, "r_b_m": bounce_radius_m(m),
                "r_s_m": schwarzschild_radius_m(m), "T_reh": treh, "n_post": n_post,
                "n_tot_min_edge": edge,
                "n_infl_needed_for_edge": edge - n_onset - n_post,
                "n_infl_needed_for_horizon_problem": nh,
                "edge_weaker_than_horizon_problem": edge - n_onset - n_post < nh,
                "n_tot_minimal_inflation": n_tot_minimal,
                "by_r0": [],
            }
            for r0 in R0_OVER_RS:
                geo = parent_geometry(m, r0)
                row["by_r0"].append({
                    "r0_over_rs": r0,
                    "n_tot_min_curvature_3sigma": n_tot_min_curvature(geo),
                    "omega_k_at_edge_minimum": omega_k_today(geo, edge),
                    "omega_k_minimal_inflation": omega_k_today(geo, n_tot_minimal),
                    "omega_k_at_n_tot_130": omega_k_today(geo, OMEGA_K_REFERENCE_N_TOT),
                })
            rows.append(row)
    return {
        "rows": rows,
        "n_onset": n_onset,
        "n_tot_references": {
            "zhu2017_lower_95": ZHU_N_TOT_LOWER_95,
            "lb2013_n_infl_peak": LB_N_INFL_PEAK,
            # N_tot = N_onset + N_infl + N_post; N_post a legrövidebb (azonnali felmelegedés)
            # és a leghosszabb felmelegedés közötti sáv
            "lb2013_implied_n_tot": [n_onset + LB_N_INFL_PEAK + min(n_post_by_treh.values()),
                                     n_onset + LB_N_INFL_PEAK + max(n_post_by_treh.values())],
        },
        "omega_k_desi": OMEGA_K_DESI,
        "analytic_note": "a széle-minimumon Ω_K = −(R_H/R_obs)²·r_s/R0 ≈ −0.097·r_s/R0",
        "analytic_coefficient": -((hubble_radius_m() / PARTICLE_HORIZON_M) ** 2),
    }
