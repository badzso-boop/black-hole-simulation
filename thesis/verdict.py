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


# ---------------------------------------------------------------------------
# WP4b: a forgó szülő (docs/spin-plan.md §6, rögzítve 2026-09-29 a számolás előtt).
# Rögzített részletek, amiket a §6 táblázat nem adott meg számmal:
#   „a populáció zöme" = ≥ 50%-a; a profil-együttható fiduciális értéke az n = 3 merev
#   politróp (vasmag); „O(1) torzulás" = D ≤ 10; a mag átlépési ideje v_seed = 10 m.
#   Utólag hozzáadott érvényességi feltétel (az implementáció közben levezetve, a
#   hipotézis ELLEN hat): a mag tömege ≥ a LMY tömegrés (0.83 m_P).
# ---------------------------------------------------------------------------

EXPECTED_SPIN = {"S1+S2 observed spins": "supports", "S3 axial core inflates": "open",
                 "S4 crossing r_-": "open", "S5 rotation today": "neutral",
                 "CMB consistency": "supports"}


def spin_scorecard(w: dict[str, Any], s3: dict[str, Any]) -> list[dict[str, Any]]:
    fid = "n=3 rigid (fiducial)"
    obs = {k: v for k, v in w["populations"].items() if v["observed"]}
    n145, n142 = f"{w['n_grid'][3]:.1f}", f"{w['n_grid'][2]:.1f}"
    gw = obs["GW (GWTC-4, Beta fit)"]["by_C"][fid]["fraction_allowed"]
    bulk = {k: v["by_C"][fid]["fraction_allowed"][n145] >= 0.5 for k, v in obs.items()}
    if all(bulk.values()) and gw[n142] >= 0.5:
        o12 = "supports"
    elif gw[n145] < 0.5:
        o12 = "against"
    else:
        o12 = "mixed"
    pess = {k: v["by_C"]["min over profiles"]["fraction_allowed"][n145] for k, v in obs.items()}
    rel = w["relations"][fid]
    rows = [{
        "wp": "S1+S2 observed spins", "outcome": o12,
        "numbers": {"C_fiducial": w["c_fiducial"], "C_range": [w["c_values"]["min over profiles"],
                                                                w["c_values"]["max over profiles"]],
                    "a_star_gap_fiducial": rel["a_star_gap"],
                    "a_star_semiclassical_10mP_fiducial": rel["a_star_gap_10mP"],
                    "seed_mass_max_a0.9_mP": rel["seed_mass_max_a0.9"],
                    "fraction_allowed_N145_fiducial": {k: v["by_C"][fid]["fraction_allowed"][n145]
                                                       for k, v in obs.items()},
                    "fraction_allowed_N145_pessimistic_C": pess,
                    "gw_fraction_allowed_N142": gw[n142]},
        "why": (f"Reális (n = 3) magprofillal C = {w['c_fiducial']:.2f}: minden megfigyelt "
                f"populáció zöme belefér N_tot ≤ 145-be, a GW-populáció {gw[n142]:.0%}-a már "
                f"N_tot ≤ 142-nél. A tömegrés-korlát a* ≤ {rel['a_star_gap']:.2f} — de a mag "
                f"a* = 0.9-nél csak {rel['seed_mass_max_a0.9']:.1f} m_P: Planck-méretű, ahol az "
                "effektív LQC a határán van. Legpesszimistább profillal (C = "
                f"{w['c_values']['min over profiles']:.2f}) a gyorsan forgó (röntgen, SMBH) "
                "populációk kiesnek."),
    }]
    thr = s3["thresholds_N60"]
    reachable = any(v is not None for v in thr.values())
    rows.append({
        "wp": "S3 axial core inflates", "outcome": "supports" if reachable else "against",
        "numbers": {"omega_sigma": s3["omega_sigma"], "thresholds_N60": thr,
                    "phi2_fraction_fail": s3["phi2_fraction"]["fraction_fail_liouville"],
                    "saturating_sigma_over_h": [r["saturating_sigma_over_h"]
                                                for r in w["s3_detachment"]]},
        "why": ("Klasszikusan bármely σ/H > 10⁻¹⁴…10⁻⁴⁸ kezdeti anizotrópia ρ_c-ig telíti az LQC "
                "nyírás-korlátot, ezért a legrosszabb esetet (σ² = 11.57, Ω_σ = 0.5625) számoltuk: "
                f"az infláció így is elérhető (Starobinsky φ̇ > 0: φ_B ≥ {thr['plus_N60']:.2f}; "
                f"φ²: kudarc {s3['phi2_fraction']['fraction_fail_liouville']:.1e}). A merev-folyadék "
                "közelítés itt a határán van."),
    })
    s4 = w["s4"]
    ok = [(not r["planck_first"]) and r["tidal_distortion"] <= 10 for r in s4]
    o4 = "supports" if all(ok) else ("against" if all(r["planck_first"] for r in s4) else "open")
    rows.append({
        "wp": "S4 crossing r_-", "outcome": o4,
        "numbers": {r["case"]: {"a": r["a"], "v_planck_over_m": r["v_planck_over_m"],
                                "planck_first": r["planck_first"], "D": r["tidal_distortion"]}
                    for r in s4},
        "why": ("Gyors spinnél (a* ≥ 0.9) a tengely-mag ~50–140-szer hamarabb lépi át r₋-t, mint "
                "ahogy a tömeg-infláció Planck-görbületet ér el, és a torzulás O(1) (1.3–1.8). "
                "Lassú spinnél (a* ~ 0.01) r₋ apró, a Planck-görbület előbb alakul ki "
                "(D ~ 2·10⁴); a GW-medián (0.26) határeset. Rendkívül durva becslés: a forgó "
                "összeomlás kvantumos számolása hiányzik az irodalomból."),
    })
    worst = max(max(v.values()) for v in w["s5"].values())
    rows.append({
        "wp": "S5 rotation today", "outcome": "against" if worst > math.log10(VORTICITY_LIMIT)
        else "neutral",
        "numbers": {"max_log10_omega_over_h_today": worst, "n_infl_used": w["s5_n_infl"]},
        "why": f"(ω/H)₀ ≤ 10^{worst:.0f} ≪ 7.6e-10 — nincs mérhető forgás, tengely sem.",
    })
    gw_best = obs["GW (GWTC-4, Beta fit)"]["by_C"][fid]["fraction_allowed"][f"{w['n_best_cmb']:.1f}"]
    rows.append({
        "wp": "CMB consistency", "outcome": "supports" if gw_best >= 0.5 else "open",
        "numbers": {"n_best": w["n_best_cmb"], "a_star_max_at_best_fiducial": rel["a_star_max_at_best"],
                    "gw_fraction_allowed_at_best": gw_best},
        "why": (f"Ha az alacsony-ℓ hiány a visszapattanás (N_tot = {w['n_best_cmb']:.1f}), a szülő "
                f"spinje a* ≲ {rel['a_star_max_at_best']:.2f} (fiduciális C) — ez a GW-populáció "
                f"{gw_best:.0%}-ára igaz. Gyorsabb szülőnél a nyom ℓ ≲ 2-n van, láthatatlan."),
    })
    rows.append({
        "wp": "S6 torsion (info)", "outcome": "info",
        "numbers": w["s6"],
        "why": (f"Popławski-torzió (ρ ≈ {w['s6']['rho_torsion_over_rho_pl']:.0f} ρ_Pl): ugyanahhoz a "
                f"spinhez {w['s6']['extra_efolds_vs_lqc']:.1f} e-redővel több kell, és a tömegrés-"
                f"szerű korlát (1 m_P) a* ≤ {w['s6']['a_star_gap_fiducial']:.2f}: a torzió rosszabb, "
                "nem jobb."),
    })
    return rows
