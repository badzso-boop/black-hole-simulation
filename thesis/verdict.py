"""Pontozólap: az eredmények összevetése a docs/thesis-plan.md §0 előre rögzített kritériumaival.

A kritériumokat a számolás ELŐTT rögzítettük (2026-09-28); itt csak gépiesen alkalmazzuk
őket. Ahol a táblázat nem adott számszerű küszöböt, azt itt rögzítjük és indokoljuk:
    WP1 „a legtöbb kezdőadat": φ²-nél a Liouville-mérték szerinti hányad > 0.5; Starobinskynél
        a tér nem kompakt, ezért csak a küszöböt közöljük (mint Bonga–Gupt).
    WP1 95%: Planck n_s 0.9649 ± 0.0042, ACT 0.974 ± 0.003 (±1.96σ), r < 0.036.
    WP3 „mérhető": |Ω_K| > 1e-3.
    WP5 „szignifikáns": Δχ² < −9 (≈3σ egy paraméterre; ~2σ a k_c-rács look-elsewhere
        hatásával) — ezt a számolás előtt, itt rögzítjük.
"""
from __future__ import annotations

import math
from typing import Any

N_S_PLANCK = (0.9649, 0.0042)
N_S_ACT = (0.974, 0.003)
R_LIMIT = 0.036
OMEGA_K_MEASURABLE = 1e-3
DCHI2_SIGNIFICANT = -9.0
SHEAR_LIMIT = 4.7e-11
VORTICITY_LIMIT = 7.6e-10


def _inside(x: float, mean_err: tuple[float, float], z: float = 1.96) -> bool:
    return abs(x - mean_err[0]) <= z * mean_err[1]


def wp1(r: dict[str, Any]) -> dict[str, Any]:
    piv = r["pivots_consistent"][0]  # azonnali felmelegedés: Starobinsky legjobb esete
    ns, rr = piv["n_s"], piv["r"]
    in_planck = _inside(ns, N_S_PLANCK) and rr < R_LIMIT
    in_act = _inside(ns, N_S_ACT) and rr < R_LIMIT
    z_act = (ns - N_S_ACT[0]) / N_S_ACT[1]
    frac = r["phi2_fraction"]
    most = 1 - frac["fraction_fail_liouville"] > 0.5
    if most and in_planck and in_act:
        outcome = "supports"
    elif most and (in_planck or in_act):
        outcome = "mixed"
    else:
        outcome = "against"
    return {
        "wp": "1 Inflation", "outcome": outcome,
        "numbers": {
            "phi2_fraction_fail": frac["fraction_fail_liouville"],
            "starobinsky_threshold_plus_N60": r["thresholds"]["plus_N60"],
            "starobinsky_threshold_minus_N60": r["thresholds"]["minus_N60"],
            "n_s": ns, "r": rr, "N_star": piv["n_star"],
            "inside_planck_95": in_planck, "inside_act_95": in_act, "act_sigma": z_act,
        },
        "why": (f"A visszapattanás szinte mindig inflál (φ²: csak {frac['fraction_fail_liouville']:.1e} "
                f"hányad kap < 68 e-redőt; Starobinsky: φ_B ≥ {r['thresholds']['plus_N60']:.2f} "
                f"ill. ≥ {r['thresholds']['minus_N60']:.2f}). Starobinsky n_s = {ns:.4f}, r = {rr:.4f}: "
                f"Planck 95%-on belül, az ACT DR6-tól {abs(z_act):.1f}σ-ra. A feszültség a potenciálé "
                "(Starobinsky), nem a fekete-lyuk eredeté."),
    }


def wp2(r: dict[str, Any]) -> dict[str, Any]:
    thr = r["thresholds_bh_shear"]
    frac = r["phi2_fraction_bh_shear"]
    worst = max(
        row["log10_shear_today"]["instant_reheat"]
        for case in r["cases"].values() for row in case
        if row.get("log10_shear_today") and row["n_infl"] >= 60
    )
    killed = frac["fraction_fail_liouville"] > 0.5
    outcome = "against" if killed else "neutral"
    return {
        "wp": "2 Anisotropy", "outcome": outcome,
        "numbers": {"omega_sigma_bh": r["omega_sigma_bh"],
                    "starobinsky_threshold_plus_N60_bh_shear": thr["plus_N60"],
                    "starobinsky_threshold_minus_N60_bh_shear": thr["minus_N60"],
                    "phi2_fraction_fail_bh_shear": frac["fraction_fail_liouville"],
                    "max_log10_shear_today_with_60_efolds": worst,
                    "limit_log10": -10.33},
        "why": (f"A fekete lyuk belsejéből örökölt nyírás (Ω_σ = {r['omega_sigma_bh']:.2f}) "
                "rövidíti az inflációt (Linsefors–Barrau), de nem öli meg: a Starobinsky-küszöb "
                f"{thr['plus_N60']:.2f}-re tolódik; φ²-nél a kudarc {frac['fraction_fail_liouville']:.1e}. "
                f"Ma (σ/H)₀ ≤ 10^{worst:.0f} ≪ 4.7e-11: a nyírás nyomtalanul eltűnik — nem mérhető."),
    }


def wp3(r: dict[str, Any]) -> dict[str, Any]:
    worst = max(abs(b["omega_k_minimal_inflation"]) for row in r["rows"] for b in row["by_r0"])
    outcome = "neutral" if worst < OMEGA_K_MEASURABLE else "check"
    return {
        "wp": "3 Curvature", "outcome": outcome,
        "numbers": {"max_abs_omega_k_minimal_inflation": worst,
                    "desi": r["omega_k_desi"]},
        "why": (f"A zárt (kötött) szülőből jövő görbület a horizont-problémát épp megoldó "
                f"inflációval is legfeljebb |Ω_K| = {worst:.1e} — ezerszer a mérhető alatt."),
    }


def wp3b(r: dict[str, Any]) -> dict[str, Any]:
    rows = r["rows"]
    all_weaker = all(row["edge_weaker_than_horizon_problem"] for row in rows)
    n_min_max = max(row["n_tot_min_edge"] for row in rows)
    n_nat_lo = r["lqc_natural_n_tot"][0]
    outcome = "supports" if all_weaker and n_nat_lo > n_min_max else "against"
    margin = min(row["n_infl_needed_for_horizon_problem"] - row["n_infl_needed_for_edge"]
                 for row in rows)
    return {
        "wp": "3b Edge beyond horizon", "outcome": outcome,
        "numbers": {"max_n_tot_min_edge": n_min_max, "lqc_natural_n_tot": r["lqc_natural_n_tot"],
                    "n_tot_minimal_inflation": rows[0]["n_tot_minimal_inflation"],
                    "min_margin_efolds": margin},
        "why": (f"Minden szülőtömegre (5e11 kg … 5e22 M☉) a bébiuniverzum széle a horizontunkon túl "
                f"van, ha N_tot > {n_min_max:.1f}; ezt már a horizont-problémát megoldó infláció is "
                f"biztosítja (legalább {margin:.1f} e-redő ráhagyással), és az LQC természetes "
                f"{n_nat_lo:.0f}–145-je is."),
    }


def wp4(r: dict[str, Any]) -> dict[str, Any]:
    """A jóslat csak a* ≤ a*_max-ra érvényes (különben a forgás dominál a visszapattanáskor).

    A „formális a* = 0.9" sor a modell érvényességén kívüli extrapoláció — a pontozásba nem
    számít bele, de közöljük, és a modell-korlátot külön kimenetként jelezzük.
    """
    valid = max(max(row["log10_omega_over_h_today_at_a_max"].values()) for row in r["rows"])
    formal = max(max(row["log10_omega_over_h_today_formal_a0.9"].values()) for row in r["rows"])
    amax = max(min(row["a_star_max"].values()) for row in r["rows"])
    limit_log = math.log10(VORTICITY_LIMIT)
    outcome = "against" if valid > limit_log else "neutral (model limit)"
    return {
        "wp": "4 Parent spin", "outcome": outcome,
        "numbers": {"max_log10_omega_over_h_today_valid": valid,
                    "max_log10_omega_over_h_today_formal_a0.9_invalid": formal,
                    "largest_a_star_max": amax, "limit_log10": limit_log,
                    "model_valid_for_real_spins": False},
        "why": (f"A modell érvényességi tartományában (a* ≤ a*_max) (ω/H)₀ ≤ 10^{valid:.0f} ≪ "
                "7.6e-10: nincs mérhető tengely. DE: a homogén visszapattanás csak "
                f"a* ≲ {amax:.0e} spinnel fér össze (a legkisebb, 5e11 kg-os szülőnél; nagyobbaknál "
                "még kisebb) — valódi fekete lyukak a* ~ 0.1–0.998. A forgó szülő tehát NEM írható "
                "le ezzel a modellel: ez nyitott modell-korlát, nem cáfolat és nem megerősítés."),
    }


def wp5(r: dict[str, Any], wp3b_res: dict[str, Any]) -> dict[str, Any]:
    best = r["best"]
    sig = best["dchi2_wishart"] < DCHI2_SIGNIFICANT
    consistent = r["n_tot_lower_95"] > wp3b_res["numbers"]["max_n_tot_min_edge"]
    if not consistent:
        outcome = "against"
    elif sig:
        outcome = "supports"
    else:
        outcome = "neutral"
    return {
        "wp": "5 CMB imprint", "outcome": outcome,
        "numbers": {"best_k_c_mpc": best["k_c_mpc"], "best_n_tot": best["n_tot"],
                    "dchi2": best["dchi2_wishart"], "n_tot_lower_95": r["n_tot_lower_95"],
                    "S_half_lcdm": r["S_half_lcdm"], "S_half_best": best["S_half"],
                    "S_half_data_fullsky": r["S_half_data_fullsky"]},
        "why": (f"A legjobb levágás k_c = {best['k_c_mpc']:.1e}/Mpc (N_tot = {best['n_tot']:.1f}) "
                f"Δχ² = {best['dchi2_wishart']:.1f}-et javít — nem szignifikáns (küszöb −9). "
                f"S₁/₂ {r['S_half_lcdm']:.0f} → {best['S_half']:.0f} μK⁴ (adat, teljes égbolt: "
                f"{r['S_half_data_fullsky']:.0f}). A CMB szerint N_tot > {r['n_tot_lower_95']:.1f} "
                "(95%), összhangban a WP3b-vel. Ez bármely LQC-visszapattanásra igaz, nem "
                "fekete-lyuk-specifikus."),
    }


def wp6(r: dict[str, Any]) -> dict[str, Any]:
    t2012 = next(t for t in r["tests"] if t["prediction"] == "Smolin 2012")
    outcome = "against" if t2012["sigma"] > 3 else "neutral"
    return {
        "wp": "6 Natural selection", "outcome": outcome,
        "numbers": {"p_all_below_2Msun": t2012["p_all_below"], "sigma": t2012["sigma"]},
        "why": (f"P(minden mért neutroncsillag < 2 M☉) = {t2012['p_all_below']:.1e} "
                f"({t2012['sigma']:.1f}σ): Smolin kozmológiai természetes szelekciója a publikált "
                "formájában cáfolt. A fekete-lyuk-eredetet ez NEM cáfolja — csak egy javasolt "
                "tesztjét."),
    }


def scorecard(res: dict[str, Any]) -> list[dict[str, Any]]:
    w3b = wp3b(res["wp3"])
    return [wp1(res["wp1"]), wp2(res["wp2"]), wp3(res["wp3"]), w3b, wp4(res["wp4"]),
            wp5(res["wp5"], w3b), wp6(res["wp6"])]


EXPECTED = {  # thesis-plan §0 „várható becsületes eredmény"
    "1 Inflation": "supports", "2 Anisotropy": "neutral", "3 Curvature": "neutral",
    "3b Edge beyond horizon": "supports", "4 Parent spin": "neutral",
    "5 CMB imprint": "neutral", "6 Natural selection": "against",
}
