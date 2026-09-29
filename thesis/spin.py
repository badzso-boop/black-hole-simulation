"""WP4b: a forgó szülő-probléma (docs/spin-plan.md, S1–S6).

**A tengely-menti mag (A út).** Egy forgó csillagban az anyag fajlagos perdülete
j = Ω(r) r² sin²θ; a tengely közelében j → 0. A legkisebb perdületű f tömeghányad
eloszlása kis j-re lineáris (héjankénti forgás, Ω = Ω(r)):
    F(j) = C j / j̄,   C = (1/3) ⟨Ω r²⟩ ⟨1/(Ω r²)⟩   (tömegsúlyozott átlagok, C ≥ 1/3)
Egyenletes, merev gömbre C = 0.6. A j < j_max mag (tömege M_s = fM) a SAJÁT tömege alatt
pattan vissza, ha a centrifugális gát r_b(M_s) alatt van:  j_max² ≤ G M_s r_b(M_s).
j̄ = a* G M/c-vel ez a mag saját spin-paraméterére a*/C-t ad, amiből (Planck-egység,
V_B ≡ √(r_b³/m) = √(3/(4πρ_B)), ρ_B a visszapattanási sűrűség):
    M_s ≤ M_s,max(a*) = C³ V_B / a*³                      (tömegfüggetlen!)
A bébiuniverzum széle a horizontunkon túl (WP3b), ha r_b(M_s) e^{N_tot} > R_obs:
    M_s ≥ M_edge(N_tot) = (4π/3) ρ_B (R_obs e^{−N_tot}/ℓ_P)³
és a LMY tömegrés miatt  M_s ≥ M_gap = 4√α/(3√3) = 0.83 m_P  (alatta nincs csapdázott tartomány).
Megengedett:  M_s,max(a*) ≥ max(M_edge(N_tot), M_gap).  Ebből
    a*_max(N_tot) = C V_B ℓ_P e^{N_tot}/R_obs,   N_needed(a*) = ln(a* R_obs/(C V_B ℓ_P)),
    a*_gap = C (V_B/M_gap)^{1/3}   (N_tot-tól független felső korlát).
Newtoni nagyságrendi becslés; a Kerr-belső relativisztikus részleteit az S4 tárgyalja.
"""
from __future__ import annotations

import itertools
import math
from typing import Any

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
from scipy.stats import beta as beta_dist

from thesis.units import ALPHA_LMY, L_P, M_SUN, PARTICLE_HORIZON_M, RHO_C, RHO_PL, C, G

M_GAP = 4 * math.sqrt(ALPHA_LMY) / (3 * math.sqrt(3))  # 0.83 m_P (LMY 2023)
# Popławski 2010 (arXiv:1007.0587): ε_R = 1.1e116 J/m³ → ρ_T ≈ 237 ρ_Pl
RHO_TORSION = 1.1e116 / C**2 / RHO_PL
N_TOT_LQC_MAX = 145.0  # Linsefors–Barrau 2013 eloszlás csúcsa; a §6 kritérium felső határa
LOG_R_OBS = math.log(PARTICLE_HORIZON_M / L_P)


# ---------------------------------------------------------------------------
# A tengely-menti mag: analitikus relációk
# ---------------------------------------------------------------------------


def v_bounce(rho_b: float = RHO_C) -> float:
    """√(r_b³/m) = √(3/(4πρ_B)) Planck-egységben (LQC-re = √(α/2))."""
    return math.sqrt(3 / (4 * math.pi * rho_b))


def a_star_max(n_tot: float, c_prof: float, rho_b: float = RHO_C) -> float:
    return c_prof * v_bounce(rho_b) * math.exp(n_tot - LOG_R_OBS)


def n_tot_needed(a_star: float, c_prof: float, rho_b: float = RHO_C) -> float:
    return math.log(a_star / (c_prof * v_bounce(rho_b))) + LOG_R_OBS


def seed_mass_max(a_star: float, c_prof: float, rho_b: float = RHO_C) -> float:
    """A legnagyobb visszapattanni képes tengely-mag tömege m_P-ben."""
    return c_prof**3 * v_bounce(rho_b) / a_star**3


def seed_mass_edge(n_tot: float, rho_b: float = RHO_C) -> float:
    """A legkisebb mag, amelynek széle N_tot e-redő után a horizontunkon túl van (m_P)."""
    return 4 * math.pi / 3 * rho_b * math.exp(3 * (LOG_R_OBS - n_tot))


def a_star_gap(c_prof: float, m_min: float = M_GAP, rho_b: float = RHO_C) -> float:
    return float(c_prof * (v_bounce(rho_b) / m_min) ** (1 / 3))


def allowed(a_star: float, n_tot: float, c_prof: float, m_min: float = M_GAP,
            rho_b: float = RHO_C) -> bool:
    return seed_mass_max(a_star, c_prof, rho_b) >= max(seed_mass_edge(n_tot, rho_b), m_min)


# ---------------------------------------------------------------------------
# S1: profil-együttható politróp csillagokra
# ---------------------------------------------------------------------------


def lane_emden(n: float) -> tuple[Any, float]:
    """θ'' + 2θ'/ξ + θⁿ = 0; visszaadja a sűrű megoldást és ξ₁-et (θ(ξ₁) = 0)."""
    xi0 = 1e-6
    y0 = [1 - xi0**2 / 6, -xi0 / 3]

    def rhs(xi: float, y: np.ndarray) -> list[float]:
        th = max(y[0], 0.0)
        return [y[1], -(th**n) - 2 * y[1] / xi]

    def surface(_xi: float, y: np.ndarray) -> float:
        return float(y[0])

    surface.terminal = True  # type: ignore[attr-defined]
    sol = solve_ivp(rhs, (xi0, 50.0), y0, method="DOP853", rtol=1e-11, atol=1e-13,
                    events=surface, dense_output=True)
    return sol.sol, float(sol.t_events[0][0])


def profile_coefficient(n: float, beta: float = 0.0) -> float:
    """C = (1/3)⟨r^{2−β}⟩⟨r^{β−2}⟩ egy n indexű politrópra, Ω ∝ r^{−β} forgással."""
    dense, xi1 = lane_emden(n)

    def rho(xi: float) -> float:
        if xi < 1e-6:
            return 1.0
        return float(max(dense(xi)[0], 0.0) ** n) if n > 0 else 1.0

    def moment(k: float) -> float:
        num = quad(lambda x: rho(x) * x ** (2 + k), 0, xi1, limit=400)[0]
        den = quad(lambda x: rho(x) * x**2, 0, xi1, limit=400)[0]
        return float(num / den)

    return moment(2 - beta) * moment(beta - 2) / 3


# ---------------------------------------------------------------------------
# S2: populációk (data/observations.json → 4b_spin)
# ---------------------------------------------------------------------------


def gw_beta_fit(mode: float = 0.12, p90: float = 0.57) -> tuple[float, float]:
    """Béta-eloszlás a GWTC-4 összefoglalóhoz: csúcs 0.01–0.23 (közepe 0.12), 90% < 0.57."""

    def params(al: float) -> tuple[float, float]:
        return al, 1 + (al - 1) * (1 - mode) / mode

    al = brentq(lambda a: float(beta_dist.ppf(0.9, *params(a))) - p90, 1.001, 50.0)
    return params(al)


def heger_a_star(j_cgs: float, m_sun: float) -> float:
    """a* = cJ/(GM²) a Heger, Woosley & Spruit 2005 Table 4 magjaira (M ≈ M_bary)."""
    j_si = j_cgs * 1e-7
    m = m_sun * M_SUN
    return C * j_si / (G * m * m)


def populations() -> dict[str, dict[str, Any]]:
    al, be = gw_beta_fit()
    gw = beta_dist.ppf((np.arange(200) + 0.5) / 200, al, be)
    refl = [0.97] * 31 + [0.92] * 3 + [0.80] * 2  # Draghis+ 2024: 86% ≥ 0.95, 94% ≥ 0.9, 100% ≥ 0.7
    return {
        "GW (GWTC-4, Beta fit)": {"a": gw.tolist(), "observed": True,
                                  "source": "LVK 2025, arXiv:2508.18083 (Beta fit: mode 0.12, 90% < 0.57)"},
        "X-ray binaries (continuum fitting)": {
            "a": [0.9985, 0.92, 0.84, 0.95, 0.80, 0.70, 0.34, 0.2, 0.12], "observed": True,
            "source": "Zhao+ 2021; McClintock+ 2014 Table 1"},
        "X-ray binaries (reflection, 36)": {"a": refl, "observed": True,
                                            "source": "Draghis+ 2024 (fractions → synthetic sample)"},
        "SMBH (reflection)": {"a": [0.91, 0.97, 0.99, 0.99, 0.99, 0.52], "observed": True,
                              "source": "Reynolds 2021 Table 1 (flux-selected, biased high)"},
        "natal (theory)": {
            "a": [0.01, heger_a_star(7.5e47, 1.47), heger_a_star(4.1e48, 2.30), 1.7e-3, 0.03],
            "observed": False,
            "source": "Fuller & Ma 2019; Heger+ 2005 Table 4; NS birth spin proxy"},
        "PBH radiation era (theory)": {"a": [4e-3, 1e-2], "observed": False,
                                       "source": "De Luca+ 2019; Harada+ 2021"},
        "PBH matter era (theory)": {"a": [0.99], "observed": False, "source": "Harada+ 2017"},
        "supermassive-star collapse": {"a": [0.75], "observed": False,
                                       "source": "Shibata & Shapiro 2002"},
    }


def population_stats(a_vals: list[float], c_prof: float, n_grid: list[float],
                     m_min: float = M_GAP, rho_b: float = RHO_C) -> dict[str, Any]:
    arr = np.asarray(a_vals)
    frac = {f"{n:.1f}": float(np.mean([allowed(a, n, c_prof, m_min, rho_b) for a in arr]))
            for n in n_grid}
    gap_ok = float(np.mean(arr <= a_star_gap(c_prof, m_min, rho_b)))
    med = float(np.median(arr))
    return {"median_a": med, "p90_a": float(np.quantile(arr, 0.9)),
            "n_needed_median": n_tot_needed(med, c_prof, rho_b),
            "fraction_below_gap_limit": gap_ok, "fraction_allowed": frac}


# ---------------------------------------------------------------------------
# S3: a mag nyírása
# ---------------------------------------------------------------------------


def detachment_density_ratio(mass_kg: float, a_star: float) -> float:
    """ρ_det/ρ_c: a szülő átlagsűrűsége a centrifugális sugáron (r_c ≈ a*² GM/c²)."""
    r_c = a_star**2 * G * mass_kg / C**2
    rho_det = mass_kg / (4 * math.pi / 3 * r_c**3)
    return rho_det / (RHO_C * RHO_PL)


def saturating_initial_anisotropy(mass_kg: float, a_star: float) -> float:
    """Klasszikus por-összeomlásban σ/H ∝ (ρ/ρ_det)^{1/2}: ennél nagyobb kezdeti σ/H
    ρ_c-ig telíti az LQC nyírás-korlátot."""
    return math.sqrt(detachment_density_ratio(mass_kg, a_star))


# ---------------------------------------------------------------------------
# S4: a belső horizont átlépése (nagyságrendi)
# ---------------------------------------------------------------------------


def kerr_r_minus(a: float) -> float:
    return 1 - math.sqrt(1 - a * a)  # m egységben


def kappa_minus(a: float) -> float:
    rp, rm = 1 + math.sqrt(1 - a * a), kerr_r_minus(a)
    return (rp - rm) / (2 * (rm * rm + a * a))  # 1/m egységben


def v_planck_over_m(mass_kg: float, a: float, eps: float) -> float:
    """Tömeg-infláció (Ori-típus): m(v) ≈ ε m e^{κ₋ v}; a Planck-görbület (m(v)/r₋³ ~ ℓ_P⁻²)
    késleltetett ideje az m egységében: v_Pl = ln(r₋³/(ε m ℓ_P²))/κ₋."""
    m = G * mass_kg / C**2
    r_m = kerr_r_minus(a) * m
    return math.log(r_m**3 / (eps * m * L_P**2)) / kappa_minus(a)


V_SEED_OVER_M = 10.0  # a mag átlépése a horizont képződése után ~ π m; bőkezűen 10 m


def tidal_distortion(a: float) -> float:
    """Összegzett árapály-torzulás r₋-ig: D ~ (m/r₋³)·r₋² = m/r₋."""
    return 1 / kerr_r_minus(a)


# ---------------------------------------------------------------------------
# S5: örökölt forgás
# ---------------------------------------------------------------------------


def log10_omega_over_h_today_seed(n_onset: float, h_onset: float, n_infl: float,
                                  n_reheat: float, n_radiation: float, n_matter: float,
                                  inflation_scaling: str = "dust") -> dict[str, float]:
    """A mag a spin-határon (ω/H)_B ≈ 1-gyel pattan vissza: ω_B ≈ H_max."""
    from thesis.lqc import h_max

    ln = math.log(h_max()) - 2 * n_onset - math.log(h_onset)  # por, ω ∝ a⁻²
    ln += (-2 if inflation_scaling == "dust" else -5) * n_infl
    out = {}
    for carrier, rad in (("dust", 0.0), ("radiation", 1.0)):
        out[carrier] = (ln - 0.5 * n_reheat + rad * n_radiation - 0.5 * n_matter) / math.log(10)
    return out


# ---------------------------------------------------------------------------
# Összesítő futtatás
# ---------------------------------------------------------------------------

PROFILES = [(0.0, 0.0), (1.0, 0.0), (1.5, 0.0), (3.0, 0.0), (3.0, 0.5), (3.0, 1.0), (3.0, -0.5)]
FIDUCIAL = (3.0, 0.0)  # vasmag ≈ n = 3 politróp, mágneses csatolás → közel merev forgás


def run(wp1: dict[str, Any], wp5: dict[str, Any]) -> dict[str, Any]:
    """S1, S2, S4, S5, S6 (gyors). Az S3 inflációs része a `run_shear`-ben (lassabb)."""
    # S1
    profiles = [{"n": n, "beta": b, "C": profile_coefficient(n, b)} for n, b in PROFILES]
    c_fid = next(p["C"] for p in profiles if (p["n"], p["beta"]) == FIDUCIAL)
    c_values = {"uniform rigid (C=0.6)": 0.6, "n=3 rigid (fiducial)": c_fid,
                "min over profiles": min(p["C"] for p in profiles),
                "max over profiles": max(p["C"] for p in profiles)}
    # S2
    n_best = wp5["best"]["n_tot"]
    n_grid = [wp5["n_tot_lower_95"], n_best, 142.0, N_TOT_LQC_MAX]
    pops = populations()
    stats = {name: {"observed": p["observed"], "source": p["source"],
                    "by_C": {lab: population_stats(p["a"], c, n_grid) for lab, c in c_values.items()}}
             for name, p in pops.items()}
    relations = {lab: {"a_star_gap": a_star_gap(c), "a_star_gap_10mP": a_star_gap(c, 10.0),
                       "a_star_max_at_best": a_star_max(n_best, c),
                       "seed_mass_max_a0.1": seed_mass_max(0.1, c),
                       "seed_mass_max_a0.9": seed_mass_max(0.9, c)}
                 for lab, c in c_values.items()}
    # S3 (analitikus rész)
    s3_rows = []
    for label, m, a in (("10 M_sun", 10 * M_SUN, 0.1), ("10 M_sun", 10 * M_SUN, 0.7),
                        ("Sgr A*", 4.3e6 * M_SUN, 0.9), ("M87*", 6.5e9 * M_SUN, 0.9),
                        ("PBH 5.1e11 kg", 5.1e11, 0.01)):
        s3_rows.append({"parent": label, "a": a,
                        "rho_det_over_rho_c": detachment_density_ratio(m, a),
                        "saturating_sigma_over_h": saturating_initial_anisotropy(m, a)})
    # S4
    s4_rows = []
    for label, m, a in (("PBH 5.1e11 kg", 5.1e11, 0.01), ("10 M_sun natal", 10 * M_SUN, 0.01),
                        ("10 M_sun GW median", 10 * M_SUN, float(stats["GW (GWTC-4, Beta fit)"]
                                                             ["by_C"]["n=3 rigid (fiducial)"]["median_a"])),
                        ("10 M_sun XRB", 10 * M_SUN, 0.97), ("Sgr A*", 4.3e6 * M_SUN, 0.9),
                        ("M87*", 6.5e9 * M_SUN, 0.9)):
        v_lo = v_planck_over_m(m, a, 1e-2)
        v_hi = v_planck_over_m(m, a, 1e-20)
        s4_rows.append({"case": label, "a": a, "r_minus_over_m": kerr_r_minus(a),
                        "kappa_minus_m": kappa_minus(a), "v_planck_over_m": [v_lo, v_hi],
                        "v_seed_over_m": V_SEED_OVER_M, "planck_first": v_lo < V_SEED_OVER_M,
                        "tidal_distortion": tidal_distortion(a)})
    # S5
    piv = wp1["pivots_consistent"][0]
    h_inf = math.sqrt(8 * math.pi * piv["V_star"] / 3)
    onsets = [r["n_onset"] for c in wp1["curves"].values() for r in c
              if r["n_infl"] >= 60 and math.isfinite(r["n_onset"]) and r["n_onset"] > 0]
    n_onset = sorted(onsets)[len(onsets) // 2]
    post = piv["post"]
    n_infl_min = 130.925 - n_onset - post["n_post"]
    s5 = {sc: log10_omega_over_h_today_seed(n_onset, h_inf, n_infl_min, post["n_reheat"],
                                            post["n_radiation"], post["n_matter"], sc)
          for sc in ("dust", "perfect_fluid")}
    # S6
    s6 = {"rho_torsion_over_rho_pl": RHO_TORSION,
          "extra_efolds_vs_lqc": math.log(v_bounce(RHO_C) / v_bounce(RHO_TORSION)),
          "a_star_gap_fiducial": a_star_gap(c_fid, 1.0, RHO_TORSION),
          "n_needed_a0.9_fiducial": n_tot_needed(0.9, c_fid, RHO_TORSION),
          "n_needed_a0.9_lqc_fiducial": n_tot_needed(0.9, c_fid)}
    return {"m_gap": M_GAP, "profiles": profiles, "c_values": c_values, "c_fiducial": c_fid,
            "n_grid": n_grid, "n_best_cmb": n_best, "populations": stats,
            "relations": relations, "s3_detachment": s3_rows, "s4": s4_rows,
            "s5": s5, "s5_n_infl": n_infl_min, "s6": s6}


def run_shear() -> dict[str, Any]:
    """S3: infláció a maximális LQC-nyírással (Ω_σ = 0.5625, σ² = 11.57 ℓ_P⁻²)."""
    from thesis.anisotropy import OMEGA_SIGMA_MAX
    from thesis.inflation import Starobinsky, evolve
    from thesis.wp1 import phi2_fraction, threshold_phi_b

    star = Starobinsky()
    om = OMEGA_SIGMA_MAX * (1 - 1e-9)
    scan = []
    for sign, grid in ((1, np.linspace(-1.5, 3.0, 19)), (-1, np.linspace(1.0, 4.0, 13))):
        for phi in grid:
            r = evolve(star, float(phi), sign, shear_fraction=om)
            scan.append({"phi_b": float(phi), "sign": sign, "n_infl": r.n_infl})
    thresholds: dict[str, float | None] = {}
    for sign in (1, -1):
        rows = [r for r in scan if r["sign"] == sign]
        pair = next(((a, b) for a, b in itertools.pairwise(rows)
                     if a["n_infl"] < 60 <= b["n_infl"]), None)
        thresholds["plus_N60" if sign == 1 else "minus_N60"] = (
            threshold_phi_b(star, sign, 60.0, pair[0]["phi_b"], pair[1]["phi_b"],
                            shear_fraction=om) if pair else None)
    frac = phi2_fraction(shear_fraction=om)
    return {"omega_sigma": om, "scan": scan, "thresholds_N60": thresholds,
            "phi2_fraction": frac}
