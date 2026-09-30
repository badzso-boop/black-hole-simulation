#!/usr/bin/env python3
"""A tézis-terv (docs/thesis-plan.md) hat számolása egyben, pontozólappal.

Használat (a repó gyökeréből, `pip install -e '.[dev,thesis]'` után):
    python scripts/run_thesis.py [--id AZONOSÍTÓ]

Kimenet: runs/thesis-<id>/
    results.json    minden szám (WP1–WP6), a pontozólap és a futási idők
    SCORECARD.md    WP-nként: előre rögzített kritérium → eredmény → indoklás
    figures/*.png   a fő ábrák
    run.log         gép, verziók, futási idők
Az i5-2500S-en ~4–5 perc (a WP-k párhuzamosan futnak).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")


def _timed(name: str) -> tuple[str, Any, float]:
    t0 = time.perf_counter()
    if name == "wp1":
        from thesis import wp1
        out: Any = wp1.run()
    elif name == "wp2":
        from thesis import anisotropy
        out = anisotropy.run()
    elif name == "wp5":
        from thesis import cmb
        out = {**cmb.run(), "baseline_validation": cmb.validate_baseline()}
    elif name == "wp6":
        from thesis import cns
        out = cns.run()
    elif name == "wp4b_s3":
        from thesis import spin
        out = spin.run_shear()
    elif name == "b1a":
        from thesis import inflaton_origin
        out = inflaton_origin.run()
    elif name == "wp1b":
        from thesis import wp1
        out = wp1.run_act()
    elif name == "wp5b":
        from thesis import cmb, cobaya_lqc
        n_own = [139.5, 140.0, 140.25, 140.5, 140.75, 141.0, 141.25, 141.5, 142.0, 143.0, 145.0]
        out = {"own_pipeline": cmb.run_lqc_own(n_own)}
        if cobaya_lqc.available():
            out["official"] = cobaya_lqc.run()
        else:
            out["official"] = None
            out["note"] = ("a Planck-likelihoodok nincsenek telepítve: cobaya-install "
                           "planck_2018_lowl.TT planck_2018_lowl.EE "
                           "planck_2018_highl_plik.TTTEEE_lite_native -p ~/cobaya_packages")
    else:
        raise ValueError(name)
    return name, out, time.perf_counter() - t0


def _dependent(res: dict[str, Any]) -> None:
    """WP3/3b és WP4: a WP1 kimenetére épülnek (gyorsak)."""
    from thesis import curvature, rotation
    from thesis.history import PostInflation

    wp1 = res["wp1"]
    piv = wp1["pivots_consistent"]
    h_inf = math.sqrt(8 * math.pi * piv[0]["V_star"] / 3)
    onsets = [r["n_onset"] for c in wp1["curves"].values() for r in c
              if r["n_infl"] >= 60 and math.isfinite(r["n_onset"]) and r["n_onset"] > 0]
    n_onset = sorted(onsets)[len(onsets) // 2]  # medián (≈ 4.8, alig függ φ_B-től)
    by_treh = {f"{p['t_reh_gev']:.3g} GeV": p["n_post"] for p in piv}
    t0 = time.perf_counter()
    res["wp3"] = curvature.run(n_onset, by_treh, h_inf)
    # WP4 konzervatívan: épp elég infláció, azonnali felmelegedés (a legkevesebb hígulás)
    n_hor = curvature.n_hor(piv[0]["n_post"], h_inf)
    res["wp4"] = rotation.run(curvature.PARENTS_KG, n_onset, h_inf, n_hor,
                              PostInflation(**piv[0]["post"]))
    res["timings_s"]["wp3_wp4"] = time.perf_counter() - t0
    # WP4b (docs/spin-plan.md): a WP1 és a WP5 kimenetére épül
    from thesis import spin

    t0 = time.perf_counter()
    res["wp4b"] = spin.run(wp1, res["wp5"])
    res["timings_s"]["wp4b"] = round(time.perf_counter() - t0, 1)


def figures(res: dict[str, Any], out: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    made = []

    # 1. N_infl(φ_B)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, key, title in zip(axes, ["starobinsky_plus", "starobinsky_minus", "phi2_plus"],
                              ["Starobinsky, φ̇_B > 0", "Starobinsky, φ̇_B < 0", "φ², φ̇_B > 0"],
                              strict=True):
        rows = res["wp1"]["curves"][key]
        ax.plot([r["phi_b"] for r in rows], [min(r["n_infl"], 150) for r in rows], "o-", ms=3)
        for y, ls in ((60, "--"), (68, ":")):
            ax.axhline(y, color="k", ls=ls, lw=0.8)
        ax.set(title=title, xlabel="φ_B [m_Pl]", ylabel="N_infl (plafon 150)")
    fig.tight_layout()
    fig.savefig(out / "wp1_efolds_vs_phiB.png", dpi=120)
    made.append("wp1_efolds_vs_phiB.png")

    # 2. (n_s, r)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axvspan(0.9649 - 2 * 0.0042, 0.9649 + 2 * 0.0042, alpha=0.2, label="Planck 2018 (95%)")
    ax.axvspan(0.974 - 2 * 0.003, 0.974 + 2 * 0.003, alpha=0.2, color="C1", label="ACT DR6 (95%)")
    ax.axhline(0.036, color="k", ls="--", lw=0.8, label="BK18: r < 0.036")
    for p in res["wp1"]["pivots_consistent"]:
        ax.plot(p["n_s"], p["r"], "ko")
        ax.annotate(f"T_reh={p['t_reh_gev']:.0e} GeV", (p["n_s"], p["r"]), fontsize=7)
    ax.set(xlabel="n_s", ylabel="r", yscale="log", title="Starobinsky a visszapattanás után")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "wp1_ns_r.png", dpi=120)
    made.append("wp1_ns_r.png")

    # 3. N_infl(Ω_σ)
    fig, ax = plt.subplots(figsize=(6, 4))
    for key, rows in res["wp2"]["cases"].items():
        ax.plot([max(r["omega_sigma"], 1e-7) for r in rows], [r["n_infl"] for r in rows],
                "o-", label=key)
    ax.axvline(res["wp2"]["omega_sigma_bh"], color="r", ls="--", label="fekete-lyuk nyírás")
    ax.axhline(60, color="k", ls=":", lw=0.8)
    ax.set(xscale="log", xlabel="Ω_σ a visszapattanáskor", ylabel="N_infl",
           title="WP2: a nyírás rövidíti az inflációt")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "wp2_efolds_vs_shear.png", dpi=120)
    made.append("wp2_efolds_vs_shear.png")

    # 4. WP3b: N_min(M) vs N_tot
    rows = [r for r in res["wp3"]["rows"] if r["T_reh"] == next(iter({r["T_reh"] for r in res["wp3"]["rows"]}))]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot([r["mass_kg"] for r in rows], [r["n_tot_min_edge"] for r in rows], "o-",
            label="szükséges: széle a horizonton túl")
    ax.axhline(rows[0]["n_tot_minimal_inflation"], color="C2", ls="--",
               label="a horizont-problémát épp megoldó infláció")
    refs = res["wp3"]["n_tot_references"]
    ax.axhline(refs["zhu2017_lower_95"], color="C1", ls="-.", label="Zhu+ 2017: N_tot > 141 (95%)")
    ax.axhline(res["wp5"]["n_tot_lower_95"], color="C3", ls=":", label="CMB (WP5): 95% alsó korlát")
    ax.set(xscale="log", xlabel="szülő fekete lyuk tömege [kg]", ylabel="N_tot (visszapattanás → ma)",
           title="WP3b: a bébiuniverzum széle")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "wp3b_edge.png", dpi=120)
    made.append("wp3b_edge.png")

    # 5. CMB alacsony ℓ + Δχ²(N_tot)
    c = res["wp5"]["curves"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
    data = c["data"]
    a1.errorbar([d[0] for d in data], [d[1] for d in data],
                yerr=[[d[2] for d in data], [d[3] for d in data]], fmt="k.", label="Planck 2018")
    a1.plot(c["ell"], c["lcdm"], label="ΛCDM")
    a1.plot(c["ell"], c["best_cutoff"], label="LQC-levágás (legjobb)")
    a1.set(xscale="log", xlabel="ℓ", ylabel="D_ℓ^TT [μK²]", title="WP5: alacsony ℓ")
    a1.legend(fontsize=7)
    rr = res["wp5"]["rows"]
    a2.plot([r["n_tot"] for r in rr], [r["dchi2_wishart"] for r in rr], "o-", ms=3)
    a2.axhline(0, color="k", lw=0.8)
    a2.set(ylim=(-3, 15), xlabel="N_tot (k_c-ből)", ylabel="Δχ² (ℓ < 30)",
           title="negatív = jobb, mint ΛCDM")
    fig.tight_layout()
    fig.savefig(out / "wp5_cmb.png", dpi=120)
    made.append("wp5_cmb.png")

    # 6. WP4b: a szükséges N_tot a szülő spinjének függvényében (kulcsábra)
    import numpy as np

    from thesis import spin

    w = res["wp4b"]
    fig = plt.figure(figsize=(13, 6.5))
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 2])
    a1 = fig.add_subplot(gs[0, 0])
    a3 = fig.add_subplot(gs[1, 0], sharex=a1)
    a2 = fig.add_subplot(gs[:, 1])
    aa = np.geomspace(1e-3, 1.0, 200)
    for lab, c in w["c_values"].items():
        a1.plot(aa, [spin.n_tot_needed(a, c) for a in aa], label=f"{lab}")
    a1.axhline(145, color="C1", ls="-.", lw=0.8, label="régi §6 plafon (145 — téves bemenet)")
    a1.axhline(w["n_best_cmb"], color="C3", ls="--", lw=0.8, label="CMB legjobb (WP5)")
    a1.set(xscale="log", ylabel="szükséges N_tot", ylim=(133, 146),
           title="WP4b: tengely-mag — szükséges e-redők")
    a1.legend(fontsize=6, loc="upper left")
    pops = spin.populations()
    for i, (_name, p) in enumerate(pops.items()):
        a3.plot(p["a"], [i] * len(p["a"]), "|", ms=10, color=f"C{i % 10}")
    a3.set_yticks(range(len(pops)), list(pops), fontsize=6)
    a3.set(xscale="log", xlabel="a* (a szülő spinje)", ylim=(-0.7, len(pops) - 0.3))
    for lab, c in w["c_values"].items():
        a2.plot(aa, [spin.seed_mass_max(a, c) for a in aa], label=lab)
    a2.axhline(spin.M_GAP, color="k", ls="--", lw=0.8, label="LMY tömegrés (0.83 m_P)")
    a2.axhline(10, color="k", ls=":", lw=0.8, label="10 m_P")
    a2.set(xscale="log", yscale="log", xlabel="a*", ylabel="a mag max. tömege [m_P]",
           title="a mag tömege (N_tot-tól független)")
    a2.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "wp4b_spin.png", dpi=120)
    made.append("wp4b_spin.png")

    # 7. WP5b: a hibrid LQC-spektrum — Δχ²(N_tot) három módon, és a C_ℓ
    w5b = res["wp5b"]
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(12, 4))
    own = w5b["own_pipeline"]
    b1.plot([r["n_tot"] for r in own["rows"]], [r["dchi2_wishart"] for r in own["rows"]], "o-",
            label="LQC-spektrum, saját Wishart")
    if w5b["official"]:
        rows_o = [r for r in w5b["official"]["low_ell"]["rows"] if np.isfinite(r["dchi2_total"])]
        b1.plot([r["n_tot"] for r in rows_o], [r["dchi2_total"] for r in rows_o], "s-",
                label="LQC-spektrum, hivatalos Planck alacsony-ℓ TT+EE")
    rr = res["wp5"]["rows"]
    b1.plot([r["n_tot"] for r in rr], [r["dchi2_wishart"] for r in rr], ":", label="WP5 levágás-sablon")
    b1.axhline(0, color="k", lw=0.8)
    b1.set(xlim=(139.5, 145), ylim=(-2, 8), xlabel="N_tot", ylabel="Δχ² vs ΛCDM",
           title="WP5b: negatív = jobb, mint ΛCDM")
    b1.legend(fontsize=7)
    c5 = res["wp5"]["curves"]
    data = c5["data"]
    b2.errorbar([d[0] for d in data], [d[1] for d in data],
                yerr=[[d[2] for d in data], [d[3] for d in data]], fmt="k.", label="Planck 2018")
    b2.plot(c5["ell"], c5["lcdm"], label="ΛCDM")
    b2.plot(c5["ell"], own["curve_best"], label=f"hibrid LQC, N_tot = {own['best']['n_tot']}")
    b2.set(xscale="log", xlabel="ℓ", ylabel="D_ℓ^TT [μK²]", title="alacsony ℓ")
    b2.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "wp5b_lqc_spectrum.png", dpi=120)
    made.append("wp5b_lqc_spectrum.png")
    plt.close("all")
    return made


def scorecard_md(res: dict[str, Any]) -> str:
    from thesis.verdict import EXPECTED

    lines = [
        f"# Tézis-számolások — pontozólap ({res['meta']['date']})",
        "",
        "Előre rögzített kritériumok: `docs/thesis-plan.md` §0 (2026-09-28).",
        "Küszöbök, amiket a táblázat nem adott meg számmal: `thesis/verdict.py` fejléce.",
        "",
        "Az utolsó oszlop (A8, docs/upgrade-plan.md): megkülönbözteti-e a sor a fekete-lyuk-eredetet",
        "egy közönséges LQC-visszapattanástól. A „nem” sorok konzisztencia-ellenőrzések, nem bizonyítékok.",
        "",
        "| WP | Eredmény | Várt (§0) | Indoklás | BH-specifikus? |",
        "|---|---|---|---|---|",
    ]
    for row in res["scorecard"]:
        exp = EXPECTED.get(row["wp"], "—")
        lines.append(f"| {row['wp']} | **{row['outcome']}** | {exp} | {row['why']} | "
                     f"{row['discriminates_bh_origin']} |")
    lines += ["", "## Számok", ""]
    for row in res["scorecard"]:
        lines.append(f"### {row['wp']}")
        lines.append("```json")
        lines.append(json.dumps(row["numbers"], indent=1, ensure_ascii=False, default=str))
        lines.append("```")
    from thesis.verdict import EXPECTED_SPIN

    lines += ["", "## WP4b — a forgó szülő (docs/spin-plan.md §6)", "",
              "| Kérdés | Eredmény | Várt (§6) | Indoklás | BH-specifikus? |", "|---|---|---|---|---|"]
    for row in res["spin_scorecard"]:
        lines.append(f"| {row['wp']} | **{row['outcome']}** | "
                     f"{EXPECTED_SPIN.get(row['wp'], '—')} | {row['why']} | "
                     f"{row['discriminates_bh_origin']} |")
    lines += ["", "### WP4b számok", ""]
    for row in res["spin_scorecard"]:
        lines += [f"#### {row['wp']}", "```json",
                  json.dumps(row["numbers"], indent=1, ensure_ascii=False, default=str), "```"]
    lines += ["", "## Kiegészítések: WP1b, WP5b, B1a",
              "", "A WP1b és a WP5b nem előre rögzített; a WP1/WP5 ítéletét nem írják felül, a WP5b a "
              "WP5 szabályát (Δχ² < −9) alkalmazza. A B1a előre rögzítve: docs/upgrade-plan.md.", "",
              "| Kérdés | Eredmény | Indoklás | BH-specifikus? |", "|---|---|---|---|"]
    for row in res["upgrades_scorecard"]:
        lines.append(f"| {row['wp']} | **{row['outcome']}** | {row['why']} | "
                     f"{row['discriminates_bh_origin']} |")
    for row in res["upgrades_scorecard"]:
        lines += [f"#### {row['wp']}", "```json",
                  json.dumps(row["numbers"], indent=1, ensure_ascii=False, default=str), "```"]
    lines += ["", "## Validáció", "",
              f"- CAMB vs Planck minimum-theory (ℓ 2–2500): max eltérés "
              f"{res['wp5']['baseline_validation']['max_rel_dev']:.2%}",
              f"- φ² kudarc-sáv (φ̇_B > 0): {res['wp1']['phi2_fraction']['fail_bands_phidot_pos']} "
              "(Ashtekar–Sloan: [−5.5, 0.94])",
              f"- Bonga–Gupt küszöbök (60 e-redő): {res['wp1']['thresholds']['plus_N60']:.3f} / "
              f"{res['wp1']['thresholds']['minus_N60']:.3f} (cikk: −1.45 / 3.63)",
              "", f"Futási idők (s): {json.dumps(res['timings_s'])}", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", default=dt.datetime.now(dt.UTC).date().isoformat())
    args = ap.parse_args()
    out = ROOT / "runs" / f"thesis-{args.id}"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    res: dict[str, Any] = {"timings_s": {}}
    with ProcessPoolExecutor(max_workers=4) as ex:
        for name, val, secs in ex.map(_timed, ["wp5b", "wp1", "wp5", "wp2", "wp4b_s3", "wp1b", "wp6", "b1a"]):
            res[name] = val
            res["timings_s"][name] = round(secs, 1)
            print(f"[{name}] kész, {secs:.1f} s", flush=True)
    _dependent(res)
    from thesis.verdict import annotate, scorecard, spin_scorecard, upgrades_scorecard

    res["scorecard"] = annotate(scorecard(res))
    res["spin_scorecard"] = annotate(spin_scorecard(res["wp4b"], res["wp4b_s3"]))
    res["upgrades_scorecard"] = annotate(upgrades_scorecard(res))
    import camb
    import numpy
    import scipy

    res["meta"] = {"date": args.id, "python": sys.version.split()[0], "numpy": numpy.__version__,
                   "scipy": scipy.__version__, "camb": camb.__version__,
                   "machine": f"{platform.node()} {platform.machine()} {os.cpu_count()} CPU",
                   "total_s": round(time.perf_counter() - t0, 1)}
    res["timings_s"]["total"] = res["meta"]["total_s"]
    res["figures"] = figures(res, out / "figures")
    (out / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    (out / "SCORECARD.md").write_text(scorecard_md(res))
    log = [f"{k}: {v}" for k, v in res["meta"].items()]
    log += [f"timing {k}: {v} s" for k, v in res["timings_s"].items()]
    (out / "run.log").write_text("\n".join(log) + "\n")
    for row in res["scorecard"] + res["spin_scorecard"] + res["upgrades_scorecard"]:
        print(f"{row['wp']:<26} {row['outcome']}")
    print(f"→ {out.relative_to(ROOT)}  ({res['meta']['total_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
