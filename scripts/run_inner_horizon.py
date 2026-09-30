#!/usr/bin/env python3
"""A belső horizont (S4, Level 1) teljes számolása — docs/inner-horizon-plan.md.

Használat (a repó gyökeréből, `pip install -e '.[dev,thesis]'` után):
    python scripts/run_inner_horizon.py --quick            # gyors próba (~1–2 perc, i5)
    python scripts/run_inner_horizon.py [--jobs 8]         # teljes felbontás-létra (Ryzen)
    python scripts/run_inner_horizon.py --max-n 6400       # + a legnagyobb rács (≈5 GB/futás)

Kimenet: runs/inner-horizon-<id>/
    results.json   minden szám (L1a–L1e, validáció, felbontás-létra)
    SCORECARD.md   validációs kapu + ítéletek a terv §5 szabályai szerint
    figures/*.png, run.log
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

Q_T2 = 0.632455532  # Brady & Smith 1995: e² = 0.4


def ladders(quick: bool, max_n: int) -> dict[str, Any]:
    if quick:
        return {"static_n": [100, 200, 400], "growth_q": [Q_T2], "growth_n": [400, 800],
                "amps": [0.0, 0.1], "late_n": 300}
    growth_n = [n for n in (400, 800, 1600, 3200, 6400) if n <= max_n]
    return {"static_n": [200, 400, 800, 1600],
            "growth_q": [0.5, Q_T2, 0.782, 0.827, 0.907, 0.95],
            "growth_n": growth_n, "amps": [0.0, 0.05, 0.1], "late_n": min(1600, max_n)}


def _task(spec: tuple[Any, ...]) -> tuple[tuple[Any, ...], Any, float]:
    t0 = time.perf_counter()
    kind = spec[0]
    if kind == "l1a":
        from thesis.inflation import Starobinsky, evolve
        from thesis.ori_model import run_l1a

        bg = evolve(Starobinsky(), -1.3, 1)
        out: Any = {"background": {"n_onset": bg.n_onset, "h_onset": bg.h_onset},
                    **run_l1a(bg.n_onset, bg.h_onset or 1e-5)}
    elif kind == "static":
        from thesis.inner_horizon import dn_validation_static

        out = dn_validation_static(spec[1], spec[2])
    elif kind == "growth":
        from thesis.inner_horizon import dn_growth

        out = dn_growth(spec[1], spec[2], spec[3])
    elif kind == "late":
        from thesis.inner_horizon import dn_late_pulse

        out = dn_late_pulse(spec[1], spec[2])
    else:
        raise ValueError(kind)
    return spec, out, time.perf_counter() - t0


def cell_count(spec: tuple[Any, ...]) -> int:
    n = int(spec[2]) if len(spec) > 2 else 1
    if spec[0] in ("growth", "late"):
        return 5 * n * n  # nv = 5·nu
    if spec[0] == "static":
        return n * n
    return 1


def amplitude_analysis(growth: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A numerikus „padló" (amp = 0) és a jel (amp > 0) a felbontás függvényében: feloldott-e a
    fizikai amplitúdó (jel − padló > 3 e-redő a legnagyobb n-nél, és a két legnagyobb n közti
    eltérés < 0.5)?"""
    out = []
    qs = sorted({g["q"] for g in growth})
    for q in qs:
        rows = [g for g in growth if g["q"] == q and g.get("ok")]
        ns = sorted({g["n"] for g in rows})
        amps = sorted({g["amplitude"] for g in rows if g["amplitude"] > 0})
        floor = {g["n"]: g["log_m_end"] for g in rows if g["amplitude"] == 0}
        for amp in amps:
            sig = {g["n"]: g for g in rows if g["amplitude"] == amp}
            n_hi = max(n for n in ns if n in sig)
            gap = sig[n_hi]["log_m_end"] - floor.get(n_hi, float("-inf"))
            conv = (abs(sig[n_hi]["log_m_end"] - sig[sorted(sig)[-2]]["log_m_end"])
                    if len(sig) > 1 else float("inf"))
            resolved = gap > 3 and conv < 0.5
            ln_a = sig[n_hi]["log_m_end"] - sig[n_hi]["kappa_exact"] * sig[n_hi]["v_end"]
            out.append({"q": q, "amplitude": amp, "n_max": n_hi,
                        "log_m_signal": {n: sig[n]["log_m_end"] for n in sorted(sig)},
                        "log_m_floor": {n: floor[n] for n in sorted(floor)},
                        "gap_at_nmax": gap, "change_last_doubling": conv, "resolved": resolved,
                        "kappa_fit_over_exact": sig[n_hi]["kappa_fit"] / sig[n_hi]["kappa_exact"],
                        "ln_A_code_minus_2ln_delta": ln_a - 2 * math.log(amp) if resolved else None})
    return out


def analysis(res: dict[str, Any]) -> None:
    from thesis import inner_horizon as ih
    from thesis import spin
    from thesis.doublenull import rn_horizons, rn_kappa

    pops = {k: v for k, v in spin.populations().items()
            if k in ("natal (theory)", "GW (GWTC-4, Beta fit)")}
    res["race"] = {
        "fiducial_mass_kg": ih.FIDUCIAL_MASS_KG, "fiducial_delta": ih.FIDUCIAL_DELTA,
        "populations": ih.population_race(pops),
        "populations_all": ih.population_race(spin.populations()),
        "spin_scan": ih.spin_scan(), "mass_scan": ih.mass_scan_quantum(),
        "asteroid": ih.asteroid(),
    }
    rp, rm = rn_horizons(0.78)
    res["validation"]["drift_T10b"] = ih.drift_test()
    res["validation"]["t9"] = {"r_minus": rn_horizons(0.78 / 0.9)[1] * 0.9,
                               "kappa_minus": rn_kappa(0.78 / 0.9)[1] / 0.9}
    res["validation"]["ori"] = {"rn": res["l1a"]["rn"], "hayward": res["l1a"]["hayward"]}
    res["amplitude"] = amplitude_analysis(res["growth"])
    del rp, rm


def figures(res: dict[str, Any], out: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out.mkdir(parents=True, exist_ok=True)
    made = []
    # 1. Ori-modell
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
    for key, lab in (("rn", "Reissner–Nordström"), ("hayward", "Hayward")):
        c = res["l1a"][key]["curve"]
        a1.plot(c["v"], c["log_abs_M"], label=lab)
    a1.set(xlabel="v", ylabel="ln |M₊|", title="L1a: tömeg-infláció (Ori-modell)")
    a1.legend(fontsize=8)
    for key in ("hayward",):
        c = res["l1a"][key]["curve"]
        v = np.array(c["v"])
        lm = np.array(c["log_abs_M"])
        a2.plot(v[1:], np.gradient(lm, v)[1:] * v[1:], label="Hayward d ln M / d ln v")
    a2.axhline(13, color="k", ls=":", lw=0.8, label="p+1 = 13 (Carballo-Rubio+ 2021)")
    a2.set(xscale="log", xlabel="v", ylim=(-5, 120), title="exponenciális → polinomiális")
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "l1a_ori.png", dpi=120)
    made.append("l1a_ori.png")
    # 2. felbontás-létra
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for row in res["amplitude"]:
        if abs(row["q"] - Q_T2) > 1e-6:
            continue
        ns = sorted(row["log_m_signal"], key=float)
        ax.plot(ns, [row["log_m_signal"][n] for n in ns], "o-", label=f"δ = {row['amplitude']}")
        nf = sorted(row["log_m_floor"], key=float)
        ax.plot(nf, [row["log_m_floor"][n] for n in nf], "k:", label="numerikus padló (δ = 0)")
    ax.set(xscale="log", xlabel="felbontás n", ylabel="ln m(v_max)",
           title="L1b: a fizikai jel vs a csonkolási padló (Q = 0.632)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "l1b_ladder.png", dpi=120)
    made.append("l1b_ladder.png")
    # 3. a verseny
    ss = res["race"]["spin_scan"]
    a = [r["a_star"] for r in ss]
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(13, 4.5))
    b1.plot(a, [r["v_planck_classical"] for r in ss], label="v_Pl klasszikus (δ = 0.1)")
    b1.plot(a, [r["v_planck_quantum"] for r in ss], label="v_Pl kvantum")
    b1.plot(a, [10 * r["dv_spark"] for r in ss], "k--", label="10 × Δv (szikra átlépése)")
    b1.fill_between(a, 1e-3, 1e5, where=[bool(r["passes"]) for r in ss], alpha=0.15,
                    color="g", label="átjut (margin ≥ 10, D ≤ 10)")
    b1.set(xscale="log", yscale="log", ylim=(1e-3, 1e5), xlabel="a*", ylabel="v (M egységben)",
           title="L1c: a szikra versenye a belső horizonttal (10 M☉)")
    b1.legend(fontsize=7)
    b2.plot(a, [r["distortion_D"] for r in ss])
    b2.axhline(10, color="k", ls=":", lw=0.8)
    b2.set(xscale="log", yscale="log", xlabel="a*", ylabel="D = M/r₋", title="árapály-torzulás")
    fig.tight_layout()
    fig.savefig(out / "l1c_race.png", dpi=120)
    made.append("l1c_race.png")
    plt.close("all")
    return made


def scorecard_md(res: dict[str, Any]) -> str:
    from thesis.verdict import EXPECTED_INNER

    lines = [f"# Belső horizont (S4, Level 1) — pontozólap ({res['meta']['date']})", "",
             "Előre rögzített kritériumok: `docs/inner-horizon-plan.md` §5 (2026-09-30); a "
             "számszerű részletek a `thesis/verdict.py` belső-horizont szakaszában.", "",
             "| Kérdés | Eredmény | Várt (§5) | Indoklás |", "|---|---|---|---|"]
    for row in res["scorecard"]:
        lines.append(f"| {row['wp']} | **{row['outcome']}** | {EXPECTED_INNER.get(row['wp'], '—')} "
                     f"| {row['why']} |")
    lines += ["", "## Számok", ""]
    for row in res["scorecard"]:
        lines += [f"### {row['wp']}", "```json",
                  json.dumps(row["numbers"], indent=1, ensure_ascii=False, default=str), "```"]
    lines += ["", "## Az amplitúdó feloldása (felbontás-létra)", "",
              "| Q | δ | n_max | jel − padló | változás az utolsó duplázáskor | feloldva | κ_fit/κ₋ |",
              "|---|---|---|---|---|---|---|"]
    for r in res["amplitude"]:
        lines.append(f"| {r['q']:.3f} | {r['amplitude']} | {r['n_max']} | {r['gap_at_nmax']:.2f} | "
                     f"{r['change_last_doubling']:.2f} | {r['resolved']} | "
                     f"{r['kappa_fit_over_exact']:.4f} |")
    lines += ["", f"Futási idők (s): {json.dumps(res['timings_s'])}", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", default=dt.datetime.now(dt.UTC).date().isoformat())
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, (os.cpu_count() or 2) // 2)))
    ap.add_argument("--max-n", type=int, default=3200)
    args = ap.parse_args()
    tag = f"inner-horizon-{args.id}" + ("-quick" if args.quick else "")
    out = ROOT / "runs" / tag
    out.mkdir(parents=True, exist_ok=True)
    lad = ladders(args.quick, args.max_n)
    specs: list[tuple[Any, ...]] = [("l1a",)]
    specs += [("static", q, n) for q in (0.5, 0.92, 0.95) for n in lad["static_n"]]
    specs += [("growth", q, n, amp) for q in lad["growth_q"] for n in lad["growth_n"]
              for amp in lad["amps"]]
    specs += [("late", 0.782, lad["late_n"])]
    small = [s for s in specs if cell_count(s) < 5 * 6400**2]
    big = [s for s in specs if cell_count(s) >= 5 * 6400**2]
    res: dict[str, Any] = {"validation": {"static": {}, "growth_T2": []}, "growth": [],
                           "timings_s": {}, "ladders": lad}
    t0 = time.perf_counter()

    def collect(spec: tuple[Any, ...], val: Any, secs: float) -> None:
        name = "/".join(str(x) for x in spec)
        res["timings_s"][name] = round(secs, 1)
        print(f"[{name}] kész, {secs:.1f} s", flush=True)
        if spec[0] == "l1a":
            res["l1a"] = val
        elif spec[0] == "static":
            res["validation"]["static"].setdefault(str(spec[1]), []).append(val)
        elif spec[0] == "growth":
            res["growth"].append(val)
            if abs(spec[1] - Q_T2) < 1e-6 and spec[3] > 0:
                res["validation"]["growth_T2"].append(val)
        elif spec[0] == "late":
            res["late_pulse"] = val

    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for spec, val, secs in ex.map(_task, sorted(small, key=cell_count, reverse=True)):
            collect(spec, val, secs)
    if big:
        with ProcessPoolExecutor(max_workers=max(1, args.jobs // 4)) as ex:
            for spec, val, secs in ex.map(_task, big):
                collect(spec, val, secs)
    analysis(res)
    from thesis.verdict import inner_horizon_scorecard

    res["scorecard"] = inner_horizon_scorecard(res)
    import numpy

    res["meta"] = {"date": args.id, "quick": args.quick, "python": sys.version.split()[0],
                   "numpy": numpy.__version__,
                   "machine": f"{platform.node()} {platform.machine()} {os.cpu_count()} CPU",
                   "jobs": args.jobs, "total_s": round(time.perf_counter() - t0, 1)}
    res["figures"] = figures(res, out / "figures")
    (out / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    (out / "SCORECARD.md").write_text(scorecard_md(res))
    (out / "run.log").write_text("\n".join(f"{k}: {v}" for k, v in res["meta"].items()) + "\n")
    for row in res["scorecard"]:
        print(f"{row['wp']:<42} {row['outcome']}")
    print(f"→ {out.relative_to(ROOT)}  ({res['meta']['total_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
