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

import itertools
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
                "(Starobinsky), nem a fekete-lyuk eredeté. FELTÉTELES: a számolás ρ_c 100%-át a "
                "skalármezőbe teszi, az összeomló csillag viszont por — a B1a szerint a por mellett "
                "a mezőnek ~99%-ot kellene vinnie; erre nincs mechanizmus (critical-review.md §3.1). "
                "Minden sor, amely a WP1 e-redőit örökli (WP2–WP5), ezt a feltételt is örökli."),
    }


def wp2(r: dict[str, Any]) -> dict[str, Any]:
    thr = r["thresholds_bh_shear"]
    frac = r["phi2_fraction_bh_shear"]
    om_max = r.get("omega_sigma_max_lqc", 0.5625)
    worst = max(
        row["log10_shear_today"]["instant_reheat"]
        for case in r["cases"].values() for row in case
        if row.get("log10_shear_today") and row["n_infl"] >= 60
    )
    killed = frac["fraction_fail_liouville"] > 0.5
    outcome = "against" if killed else "neutral"
    return {
        "wp": "2 Anisotropy", "outcome": outcome,
        "numbers": {"omega_sigma_band": [0.0, om_max],
                    "omega_sigma_classical_extrapolation": r["omega_sigma_bh"],
                    "starobinsky_threshold_plus_N60_at_extrapolation": thr["plus_N60"],
                    "starobinsky_threshold_minus_N60_at_extrapolation": thr["minus_N60"],
                    "phi2_fraction_fail_at_extrapolation": frac["fraction_fail_liouville"],
                    "max_log10_shear_today_with_60_efolds": worst,
                    "limit_log10": -10.33},
        "why": ("A visszapattanáskori nyírás ismeretlen: 0 (a homogén Oppenheimer–Snyder-belső "
                f"pontosan izotróp) és az LQC-plafon Ω_σ = {om_max:.4f} között. A korábbi "
                f"Ω_σ = {r['omega_sigma_bh']:.2f} a klasszikus Kantowski–Sachs-nyírás r_b-re "
                "extrapolálva — de ott a LMYZ-metrikában f(r_b) = 1, a tartomány statikus, tehát "
                "ez nem fizikai érték (critical-review.md §3.4). Az ítélet a sáv egészén áll: a "
                "nyírás rövidíti az inflációt, de nem öli meg (a plafonon is elérhető, WP4b S3; "
                f"Ω_σ = {r['omega_sigma_bh']:.2f}-nél a Starobinsky-küszöb {thr['plus_N60']:.2f}), "
                f"és ma (σ/H)₀ ≤ 10^{worst:.0f} ≪ 4.7e-11 — nem mérhető."),
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
    """A3 (docs/upgrade-plan.md): az ítélet az, amit ténylegesen számolunk — N_edge(M) < N_hor
    minden M-re. Az eredeti §0 szabály („az LQC természetes 130–145 N_tot-ja meghaladja N_min(M)-et")
    téves bemenetre épült (a 145 inflációs e-redő, nem N_tot — critical-review.md §3.3); a régi
    kimenetet mellette megtartjuk (szabály 2c)."""
    rows = r["rows"]
    all_weaker = all(row["edge_weaker_than_horizon_problem"] for row in rows)
    n_min_max = max(row["n_tot_min_edge"] for row in rows)
    old_lo = 130.0  # az eredeti sáv alja (forrás nélküli N_tot-érték)
    old_outcome = "supports" if all_weaker and old_lo > n_min_max else "against"
    outcome = "consistency check: passes" if all_weaker else "against"
    margin = min(row["n_infl_needed_for_horizon_problem"] - row["n_infl_needed_for_edge"]
                 for row in rows)
    refs = r.get("n_tot_references", {})
    return {
        "wp": "3b Edge beyond horizon", "outcome": outcome,
        "numbers": {"max_n_tot_min_edge": n_min_max, "n_tot_references": refs,
                    "n_tot_minimal_inflation": rows[0]["n_tot_minimal_inflation"],
                    "min_margin_efolds": margin, "old_rule_outcome": old_outcome},
        "why": (f"Minden szülőtömegre (5e11 kg … 5e22 M☉) a bébiuniverzum széle a horizontunkon túl "
                f"van, ha N_tot > {n_min_max:.1f}; ezt már a horizont-problémát megoldó infláció is "
                f"biztosítja (legalább {margin:.1f} e-redő ráhagyással). Ez szinte automatikus "
                "(r_b ≫ 1/H a visszapattanáskor), tehát konzisztencia-feltétel, nem bizonyíték. "
                f"A régi szabály szerint „{old_outcome}” — de annak „természetes 130–145” sávja a "
                "Linsefors–Barrau-féle inflációs e-redőt olvasta N_tot-nak."),
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
    loo = r.get("leave_one_out_2Msun", {})
    weakest = min(loo.items(), key=lambda kv: kv[1]["sigma"]) if loo else None
    s24 = r.get("smolin_2_4_reading")
    numbers: dict[str, Any] = {"p_all_below_2Msun": t2012["p_all_below"], "sigma": t2012["sigma"]}
    why = (f"P(minden mért neutroncsillag < 2 M☉) = {t2012['p_all_below']:.1e} "
           f"({t2012['sigma']:.1f}σ, a 2025-ös tömegekkel): Smolin kozmológiai természetes "
           "szelekciója a M_max < 2 M☉ olvasatban erős feszültségben van. ")
    if weakest:
        numbers["leave_one_out_min_sigma"] = {weakest[0]: weakest[1]["sigma"]}
        why += (f"DE az eredményt szinte egyedül a {weakest[0]} viszi: nélküle "
                f"{weakest[1]['sigma']:.1f}σ (a tömege a fűtött kísérő fénygörbe-modelljéből jön). ")
    if s24:
        numbers["smolin_2_4_reading_sigma"] = s24["sigma"]
        why += (f"Smolin 2012 „~2.4 M☉ már ellentmondana” olvasatában nincs feszültség "
                f"({s24['sigma']:.1f}σ). ")
    why += "„Cáfolt” helyett: feszültség. A fekete-lyuk-eredetet ez NEM cáfolja — csak egy javasolt tesztjét."
    return {"wp": "6 Natural selection", "outcome": outcome, "numbers": numbers, "why": why}


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
                 "CMB consistency": "supports",
                 "S7 edge confinement (B3a)": "against (estimated in critical-review §4.1)"}


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
                "populációk kiesnek. FIGYELEM: a 145-ös plafon téves bemenet (Linsefors–Barrau "
                "inflációs e-redője; N_tot-ként "
                f"≈ {w.get('lb_implied_n_tot', float('nan')):.0f} lenne), és a szél-bezártság (S7) "
                "ezt a sort felülírja."),
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
    if "s7" in w:
        rows.append(s7_row(w["s7"]))
    return rows


def s7_row(s7: dict[str, Any]) -> dict[str, Any]:
    """B3a (docs/upgrade-plan.md, előre rögzítve 2026-09-30; nem vak — a becslés a
    critical-review.md §4.1-ben már szerepelt)."""
    observed = ("GW (GWTC-4, Beta fit)", "X-ray binaries (continuum fitting)",
                "X-ray binaries (reflection, 36)", "SMBH (reflection)")
    e1 = s7["by_eps"]["1"]
    fr = {k: e1["fraction_allowed"][k] for k in observed if k in e1["fraction_allowed"]}
    if all(v >= 0.5 for v in fr.values()):
        outcome = "passes"
    elif not any(v >= 0.5 for v in fr.values()):
        outcome = "against (unless the disturbance amplitude is ≪ 1, B3b)"
    else:
        outcome = "mixed"
    e01 = s7["by_eps"]["0.1"]
    return {
        "wp": "S7 edge confinement (B3a)", "outcome": outcome,
        "numbers": {"eta_lP": s7["eta"]["eta_total"], "a_star_max_eps1": e1["a_star_max"],
                    "a_star_max_eps0.1": e01["a_star_max"], "m_conf_kg_eps1": e1["m_conf_kg"],
                    "fraction_allowed_eps1": fr},
        "why": (f"A labda szélén keletkező zavar a visszapattanástól az infláció végéig "
                f"η ≈ {s7['eta']['eta_total']:.2g} ℓ_P-ig hatol befelé. A mag csak akkor maradhat "
                f"érintetlen, ha nagyobb ennél: M_s ≳ {e1['m_conf_kg']:.1g} kg, ami a WP4b "
                f"magtömeg-korlátjával a* ≲ {e1['a_star_max']:.1e} spint enged (ε = 0.1-gyel "
                f"{e01['a_star_max']:.1e}). Egyetlen megfigyelt populáció sem fér bele: a "
                "spin-út csak akkor él, ha a zavar amplitúdója ≪ 1 (B3b, még nincs számolva)."),
    }


# ---------------------------------------------------------------------------
# Kiegészítések (nem előre rögzítettek): WP1b és WP5b
# ---------------------------------------------------------------------------


def b1a_row(r: dict[str, Any]) -> dict[str, Any]:
    """B1a (docs/upgrade-plan.md, előre rögzítve 2026-09-30): against, ha f_φ,min ≥ 0.5 (vagy nincs
    ilyen); open, ha kisebb (mechanizmus nélkül „supports" nem érhető el)."""
    pots = r["potentials"]
    f = {k: v["f_field_min"] for k, v in pots.items()}
    worst = [v for v in f.values() if v is None or v >= 0.5]
    outcome = "against" if len(worst) == len(f) else ("open" if not worst else "mixed")
    star = pots.get("Starobinsky", {})
    return {
        "wp": "B1a inflaton origin (dust + field)", "outcome": outcome,
        "numbers": {"f_field_min": f,
                    "r_freeze_required": {k: v["r_freeze_required"] for k, v in pots.items()},
                    "amplification": {k: v["amplification_rho_c_over_rho_freeze"]
                                      for k, v in pots.items()},
                    "validation_pure_dust_inflated": r["validation_pure_dust_inflated"]},
        "why": ("Ha a mező a vákuum-minimumában indul (φ_B = 0) a csillag pora mellett, ≥ 60 e-redőhöz "
                f"Starobinskynél a ρ_c legalább {f.get('Starobinsky') or float('nan'):.2%}-át a mezőnek "
                "kell vinnie (a por legfeljebb ~1%), φ²-nél még 100% sem elég. A mező energiája az "
                "összeomlásban a porhoz képest ρ_c/ρ_freeze ≈ "
                f"{star.get('amplification_rho_c_over_rho_freeze', float('nan')):.1e}-szeresére nő, így "
                "ehhez a H = m pillanatban a por energiájának "
                f"{star.get('r_freeze_required') or float('nan'):.1e}-ét kellene koherens, homogén "
                "inflaton-sebességként hordoznia — a csillag anyagában ilyen mechanizmus nincs "
                "(B1b). A WP1 „szinte biztos infláció”-ja tehát a fekete-lyuk belsejére nem vihető át."),
    }


# A8: megkülönbözteti-e a sor a fekete-lyuk-eredetet egy közönséges LQC-visszapattanástól?
DISCRIMINATES = {
    "1 Inflation": "no: a property of LQC + inflaton",
    "2 Anisotropy": "partly: the initial shear is BH-specific, but inflation erases it",
    "3 Curvature": "partly: closedness is BH-specific, but unmeasurably small",
    "3b Edge beyond horizon": "no: automatic once inflation solves the horizon problem",
    "4 Parent spin": "yes: only a BH parent spins",
    "5 CMB imprint": "no: any LQC bounce",
    "6 Natural selection": "yes: tests Smolin's extension",
    "S1+S2 observed spins": "yes", "S3 axial core inflates": "partly",
    "S4 crossing r_-": "yes", "S5 rotation today": "yes", "CMB consistency": "no",
    "S6 torsion (info)": "n/a", "S7 edge confinement (B3a)": "yes",
    "1b ACT-compatible potential": "no: a property of the potential",
    "5b CMB with hybrid LQC spectrum": "no: any LQC bounce (vacuum initial state)",
    "B1a inflaton origin (dust + field)": "yes: asks whether a BH interior can supply the inflaton",
    "L1b validation gate": "n/a", "L1a star's own bounce vs inner horizon": "yes",
    "L1c the spark crosses r_-": "yes", "L1d quantum vs classical": "n/a",
    "L1e the asteroid": "yes (Norbi's feeding claim)",
}


def annotate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for row in rows:
        row["discriminates_bh_origin"] = DISCRIMINATES.get(row["wp"], "—")
    return rows


def upgrades_scorecard(res: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    act = res["wp1b"]
    piv = act["pivots_consistent"][0]
    ns, rr = piv["n_s"], piv["r"]
    in_p = _inside(ns, N_S_PLANCK) and rr < R_LIMIT
    in_a = _inside(ns, N_S_ACT) and rr < R_LIMIT
    bands = act["fail_bands_N60_phidot_pos"]
    rows.append({
        "wp": "1b ACT-compatible potential", "outcome": "supports" if in_p and in_a else "mixed",
        "numbers": {"potential": act["potential"], "mu": act["mu"], "n_s": ns, "r": rr,
                    "N_star": piv["n_star"], "planck_sigma": (ns - N_S_PLANCK[0]) / N_S_PLANCK[1],
                    "act_sigma": (ns - N_S_ACT[0]) / N_S_ACT[1], "fail_bands_N60": bands},
        "why": (f"Polinomiális α-attraktorral (k = 2, μ = {act['mu']} m_Pl) n_s = {ns:.4f}, "
                f"r = {rr:.4f}: Planck-tól {abs(ns - N_S_PLANCK[0]) / N_S_PLANCK[1]:.1f}σ, "
                f"ACT-tól {abs(ns - N_S_ACT[0]) / N_S_ACT[1]:.1f}σ — mindkettő 95%-án belül. "
                f"A visszapattanás a φ_B ∈ {[[round(x, 2) for x in b] for b in bands]} sávon "
                "kívül mindig ≥ 60 e-redőt ad. Az ACT-feszültség tehát a potenciálé volt."),
    })
    w = res["wp5b"]
    off = w.get("official")
    src = off if off else None
    if src:
        best, lo95 = src["best"], src["n_tot_lower_95"]
        dchi2 = best["dchi2_total"]
        n_best = best["n_tot"]
        which = "hivatalos Planck alacsony-ℓ TT+EE"
    else:
        best = w["own_pipeline"]["best"]
        dchi2, n_best, lo95 = best["dchi2_wishart"], best["n_tot"], None
        which = "saját Wishart (a Planck-likelihoodok nincsenek telepítve)"
    edge = res["wp3"]["rows"]
    max_edge = max(r["n_tot_min_edge"] for r in edge)
    consistent = lo95 is None or lo95 > max_edge
    outcome = "against" if not consistent else ("supports" if dchi2 < DCHI2_SIGNIFICANT
                                                 else "neutral")
    own = w["own_pipeline"]["best"]
    rows.append({
        "wp": "5b CMB with hybrid LQC spectrum", "outcome": outcome,
        "numbers": {"likelihood": which, "best_n_tot": n_best, "dchi2": dchi2,
                    "n_tot_lower_95": lo95,
                    "full_likelihood_check": off["full_check"]["rows"] if off else None,
                    "own_pipeline_best": own},
        "why": (f"A Guillén et al. 2026-féle hibrid LQC-spektrummal ({which}) a legjobb "
                f"N_tot = {n_best:.2f}, Δχ² = {dchi2:.2f} — nem szignifikáns (küszöb −9). "
                + (f"95%-os alsó korlát N_tot > {lo95:.2f}; " if lo95 else "")
                + f"a saját csővezeték ugyanitt {own['dchi2_wishart']:.2f}-t ad, S₁/₂ = "
                f"{own['S_half']:.0f} μK⁴. A magas ℓ nem változik (plik-lite Δχ² ≈ 0)."),
    })
    if "b1a" in res:
        rows.append(b1a_row(res["b1a"]))
    return rows


# ---------------------------------------------------------------------------
# Belső horizont (S4, Level 1): docs/inner-horizon-plan.md §5, rögzítve 2026-09-30.
# Részletek, amiket a §5 nem adott meg számmal (a futtatás ELŐTT rögzítve):
#   validációs kapu: T1 másodrendű konvergencia (hibaarány ≥ 3 duplázásonként), T2 |κ_fit/κ₋ − 1|
#   ≤ 0.10 és a két legfinomabb rács κ_fit-je 5%-on belül (utóbbit az implementáció közben
#   tettük hozzá, szigorítás), T10b ≤ 1%, Ori-modell: RN meredekség ≤ 1%, Hayward késői log-log meredekség p+1-től
#   ≤ 5%; L1a „mielőtt nőhetne" = a r₋ és R_b közé férő e-redők < 1; L1c zöm = ≥ 50%;
#   L1e „késői" = ≥ 1 nap a képződés után.
# ---------------------------------------------------------------------------

EXPECTED_INNER = {"L1a star's own bounce vs inner horizon": "supports",
                  "L1c the spark crosses r_-": "open (depends on spin)",
                  "L1d quantum vs classical": "info (classical first for stellar masses)",
                  "L1e the asteroid": "against (plan §5 expectation; the §5 rule itself gives "
                                      "neutral for Planck curvature)"}


def inner_horizon_gate(val: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    for q, rows in val["static"].items():
        rows = sorted(rows, key=lambda r: r["n"])
        ratios = [a["max_abs_r_error"] / b["max_abs_r_error"] for a, b in itertools.pairwise(rows)]
        checks[f"T1 static RN Q={q} (2nd order)"] = bool(ratios) and min(ratios) >= 3.0
    g2 = sorted([r for r in val["growth_T2"] if r.get("ok")], key=lambda r: r["n"])
    g = g2[-1] if g2 else {"kappa_fit": float("nan"), "kappa_exact": 1.0}
    checks["T2 mass-inflation rate κ₋ (Brady–Smith e²=0.4)"] = \
        abs(g["kappa_fit"] / g["kappa_exact"] - 1) <= 0.10
    checks["T2 rate converged (two finest grids within 5%)"] = len(g2) >= 2 and \
        abs(g2[-1]["kappa_fit"] / g2[-2]["kappa_fit"] - 1) <= 0.05
    d = val["drift_T10b"]
    checks["T10b semiclassical drift (ZLO eq. 15)"] = abs(d["r_v_final"] / d["expected"] - 1) <= 0.01
    o = val["ori"]
    checks["Ori RN slope vs analytic"] = abs(o["rn"]["slope_end"] / o["rn"]["analytic_slope_end"] - 1) <= 0.01
    checks["Ori Hayward late polynomial (p+1)"] = \
        abs(o["hayward"]["loglog_slope_end"] / o["hayward"]["expected_late_loglog_slope"] - 1) <= 0.05
    checks["T9 Chesler r₋, κ₋ (analytic)"] = abs(val["t9"]["r_minus"] - 0.451) < 0.002 and \
        abs(val["t9"]["kappa_minus"] - 2.207) < 0.005
    return {"passed": all(checks.values()), "checks": checks}


def inner_horizon_scorecard(res: dict[str, Any]) -> list[dict[str, Any]]:
    gate = inner_horizon_gate(res["validation"])
    rows: list[dict[str, Any]] = [{
        "wp": "L1b validation gate", "outcome": "passed" if gate["passed"] else "FAILED",
        "numbers": gate["checks"],
        "why": "A fizikai ítéletek csak akkor számítanak, ha a kód minden ellenőrzésen átment.",
    }]
    invalid = not gate["passed"]
    l1a = res["l1a"]
    eff = max(c["efolds_available"] for c in l1a["crossing"])
    rows.append({
        "wp": "L1a star's own bounce vs inner horizon",
        "outcome": "invalid" if invalid else ("supports" if eff < 1 else "against"),
        "numbers": {"max_efolds_between_r_minus_and_bounce": eff,
                    "lmyz_ori": [{k: r[k] for k in ("m0", "shell_jump_sign", "outcome",
                                                     "efolds_to_ceiling", "median_growth_over_kappa")}
                                 for r in l1a["lmyz"]],
                    "edge_confinement": l1a["edge_confinement"]},
        "why": (f"A csillag saját anyaga a nem forgó (LMYZ) modell belső horizontját átlépve legfeljebb "
                f"{eff:.2f} e-redőnyi tömeg-infláció idején belül visszapattan (tömegfüggetlenül ≈ ln 2), "
                "és a külső r₋-tartomány csak a felszín áthaladása után létezik: a visszapattanás "
                "megelőzi az instabilitást. Maga az LMYZ belső horizont instabil (Ori-modell: a "
                "tömeg a héj előjelétől függően −∞-be fut vagy a beépített görbületi plafont éri el) — "
                "ez a visszapattant labda SZÉLÉT érinti; a szél zavara csillag-tömegnél a labda "
                "10⁻⁹-éig hatol, de Planck-tömegű magnál (WP4b) az egészig."),
    })
    pops = res["race"]["populations"]
    fr = {k: v["fraction_pass"] for k, v in pops.items()}
    any_pass = any(r["passes"] for r in res["race"]["spin_scan"])
    bulk = all(v >= 0.5 for v in fr.values())
    rows.append({
        "wp": "L1c the spark crosses r_-",
        "outcome": "invalid" if invalid else ("supports" if bulk else
                                             ("against" if not any_pass else "open (mixed)")),
        "numbers": {"fraction_pass": fr, "band": {k: v["fraction_pass_band"] for k, v in pops.items()},
                    "window": [r["a_star"] for r in res["race"]["spin_scan"] if r["passes"]][:1],
                    "fiducial": {"mass_kg": res["race"]["fiducial_mass_kg"],
                                 "delta": res["race"]["fiducial_delta"]}},
        "why": ("A szikra (a csillag tengely-menti magja) akkor jut át, ha legalább 10×-rel a belső "
                "horizont Planck-görbületűvé válása előtt lép át, és a torzulás D = M/r₋ ≤ 10. "
                + ", ".join(f"{k}: {v:.0%}" for k, v in fr.items())
                + ". Gyors spinnél átjut, lassúnál (születési ~0.01) nem."),
    })
    ms = res["race"]["mass_scan"]
    q_first = [r for r in ms if r["quantum_first"]]
    q_before_spark = [r for r in ms if r["v_q"] < r["dv_spark"]]
    rows.append({
        "wp": "L1d quantum vs classical",
        "outcome": "invalid" if invalid else ("against" if q_before_spark else "info"),
        "numbers": {"quantum_first_cases": len(q_first), "cases": len(ms),
                    "delta_thresholds": {f"{r['mass']} a={r['a_star']}": r["delta_threshold"]
                                         for r in ms}},
        "why": ("A kvantum-fluxus csak akkor érne előbb Planck-görbületet, ha a klasszikus perturbáció "
                "amplitúdója δ kisebb a táblázatbeli küszöbnél (~(m_P/M)-szerű, csillag-tömegnél "
                "~10⁻³⁸ körül): minden valós tömegnél a klasszikus tömeg-infláció nyer. A kvantum-tag "
                "nem lassul hatványszerűen (Ori-modell: tiszta e^{κv}), így v → ∞-ben ő dominál — de "
                "addigra a tartomány már rég Planck-görbületű."),
    })
    ast = res["race"]["asteroid"]
    late = [r for r in ast if r["delay_s"] >= 86400.0]
    all_meet = all(r["meets_planckian_inner_horizon"] for r in late)
    lp = res.get("late_pulse", {})
    # A4 (hibajavítás, docs/upgrade-plan.md; critical-review.md §4.3): a terv §5 szerint „against"
    # csak akkor, ha a héj a Cauchy-horizont szingularitásán, a sokkon vagy r = 0-n ér véget;
    # ha a sorsa a nem modellezett kvantumgravitáción múlik, az „neutral". A Planck-görbület
    # elérése pontosan ez utóbbi — korábban a kód ezt tévesen „against"-nek vette. „against"
    # csak akkor, ha egy klasszikus futás a Planck-görbület ELŐTT mutatna véget (ends_sub_planck).
    ends_sub_planck = bool(lp.get("ends_sub_planck", False)) if isinstance(lp, dict) else False
    if invalid:
        l1e = "invalid"
    elif ends_sub_planck:
        l1e = "against"
    elif all_meet:
        l1e = "neutral (quantum-gravity dependent)"
    else:
        l1e = "open"
    rows.append({
        "wp": "L1e the asteroid",
        "outcome": l1e,
        "numbers": {"late_cases_meeting_planckian_IH": sum(r["meets_planckian_inner_horizon"]
                                                           for r in late),
                    "late_cases": len(late), "code_late_pulse": lp},
        "why": ("Egy napnál később beeső test (aszteroida, bolygó) minden spinnél olyan belső horizontot "
                "talál, amely már Planck-görbületű (klasszikusan: a Cauchy-horizont tömeg-inflációs "
                "szingularitása). Az eredeti Norbi-„táplálás”-nak tehát nincs klasszikus útja; hogy a "
                "kvantumgravitáció ott visszapattanást csinál-e, azt ez a számolás nem dönti el — "
                "a terv §5 szerint ez „neutral”, nem „against” (2026-09-30-i szabály-alkalmazási "
                "hibajavítás)."),
    })
    return rows
