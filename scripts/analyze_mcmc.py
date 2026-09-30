#!/usr/bin/env python3
"""WP5c: a Ryzenes MCMC (scripts/run_mcmc.sh) kiértékelése.

Használat (a repó gyökeréből):
    python scripts/analyze_mcmc.py [--chains chains] [--id AZONOSÍTÓ] [--burn 0.3]

Kimenet: runs/mcmc-<id>/
    RESULTS.md     N_tot poszterior (95% alsó korlát), paraméter-összefoglaló, Δχ²_min
                   (LQC − ΛCDM, a minimize-futásokból), és a következmények a WP3b-re és a
                   WP4b-re (a spin-ablak a CMB N_tot-korlátjánál)
    results.json   ugyanez gépi formában
    n_tot.png, triangle.png
Az ítélet a WP5 előre rögzített szabályával: szignifikáns, ha Δχ²_min < −9.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PARAMS = ["n_tot", "logA", "ns", "tau", "ombh2", "omch2", "H0"]


def read_collection(path: Path) -> dict[str, float] | None:
    """cobaya egypontos kimenet (.bestfit.txt / .minimum.txt): fejléc '#' után, egy sor."""
    if not path.exists():
        return None
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    names = lines[0].lstrip("#").split()
    vals = [float(x) for x in lines[1].split()]
    return dict(zip(names, vals, strict=True))


def find_bestfit(folder: Path) -> dict[str, float] | None:
    """A minimize-kimenet: ignore_prior=True → *.bestfit.txt, különben *.minimum.txt."""
    for pattern in ("*bestfit.txt", "*minimum.txt"):
        hits = sorted(folder.glob(pattern)) if folder.exists() else []
        if hits:
            return read_collection(hits[0])
    return None


def progress_rminus1(prefix: Path) -> float | None:
    p = prefix.parent / (prefix.name + ".progress")
    if not p.exists():
        return None
    rows = [ln.split() for ln in p.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    try:
        return float(rows[-1][3])
    except (IndexError, ValueError):
        return None


def summarize(prefix: Path, burn: float, params: list[str]) -> dict[str, Any]:
    from getdist import loadMCSamples

    s = loadMCSamples(str(prefix), settings={"ignore_rows": burn})
    names = [p.name for p in s.getParamNames().names]
    out: dict[str, Any] = {"n_samples": int(s.numrows), "weight_sum": float(s.norm),
                           "rminus1_last": progress_rminus1(prefix), "params": {}}
    for p in params:
        if p in names:
            out["params"][p] = {"mean": float(s.mean(p)), "std": float(s.std(p))}
    if "n_tot" in names:
        out["n_tot_lower_95"] = float(s.confidence("n_tot", 0.05, upper=False))
        out["n_tot_lower_99"] = float(s.confidence("n_tot", 0.01, upper=False))
    if "chi2" in names:
        out["chi2_min_in_chain"] = float(s.getParams().chi2.min())
    out["_samples"] = s
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default=str(ROOT / "chains"))
    ap.add_argument("--id", default=dt.datetime.now(dt.UTC).date().isoformat())
    ap.add_argument("--burn", type=float, default=0.3)
    args = ap.parse_args()
    chains = Path(args.chains)
    out = ROOT / "runs" / f"mcmc-{args.id}"
    out.mkdir(parents=True, exist_ok=True)

    from thesis import spin
    from thesis.curvature import PARENTS_KG, n_tot_min_edge
    from thesis.verdict import DCHI2_SIGNIFICANT

    lqc = summarize(chains / "lqc" / "lqc", args.burn, PARAMS)
    lcdm = summarize(chains / "lcdm" / "lcdm", args.burn, PARAMS) \
        if (chains / "lcdm").exists() else None
    bf = {m: find_bestfit(chains / f"{m}_bestfit") for m in ("lqc", "lcdm")}
    dchi2 = (bf["lqc"]["chi2"] - bf["lcdm"]["chi2"]) if bf["lqc"] and bf["lcdm"] else None
    n_lo = lqc["n_tot_lower_95"]
    c_fid = spin.profile_coefficient(*spin.FIDUCIAL)
    max_edge = max(n_tot_min_edge(m) for m in PARENTS_KG.values())
    res: dict[str, Any] = {
        "lqc": {k: v for k, v in lqc.items() if k != "_samples"},
        "lcdm": {k: v for k, v in lcdm.items() if k != "_samples"} if lcdm else None,
        "bestfit": bf, "dchi2_min_lqc_minus_lcdm": dchi2,
        "significant": (dchi2 is not None and dchi2 < DCHI2_SIGNIFICANT),
        "consequences": {
            "wp3b_edge_all_parents": n_lo > max_edge, "max_n_tot_min_edge": max_edge,
            "wp4b_a_star_max_at_lower95_fiducial": spin.a_star_max(n_lo, c_fid),
            "wp4b_n_needed_a0.9_fiducial": spin.n_tot_needed(0.9, c_fid),
        },
    }
    if bf["lqc"]:
        res["consequences"]["wp4b_a_star_max_at_bestfit_fiducial"] = spin.a_star_max(
            bf["lqc"]["n_tot"], c_fid)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str))

    # ábrák
    import matplotlib

    matplotlib.use("Agg")
    from getdist import plots

    g = plots.get_single_plotter()
    g.plot_1d(lqc["_samples"], "n_tot")
    g.export(str(out / "n_tot.png"))
    samples = [lqc["_samples"]] + ([lcdm["_samples"]] if lcdm else [])
    try:  # rövid/konvergálatlan láncon a 2D-sűrűség szinguláris lehet — az ábra nem kritikus
        g = plots.get_subplot_plotter()
        g.triangle_plot(samples, ["n_tot", "ns", "logA", "tau"], filled=True,
                        legend_labels=["LQC", "ΛCDM"][: len(samples)])
        g.export(str(out / "triangle.png"))
    except Exception as exc:
        res["triangle_error"] = repr(exc)
        (out / "results.json").write_text(json.dumps(res, indent=1, default=str))

    c = res["consequences"]
    lines = [
        f"# WP5c — teljes Planck-MCMC a hibrid LQC-spektrummal ({args.id})",
        "",
        "Likelihoodok: Planck 2018 alacsony-ℓ TT (Gibbs) és EE, plik-lite TT/TE/EE. "
        "Konfiguráció: `scripts/cobaya/*.yaml`.",
        "",
        f"- LQC-lánc: {lqc['n_samples']} sor (burn-in {args.burn:.0%}), R−1 = {lqc['rminus1_last']}",
        f"- **N_tot > {n_lo:.2f} (95%)**, > {lqc['n_tot_lower_99']:.2f} (99%); a felső határ priorfüggő",
        "- Δχ²_min (LQC − ΛCDM, minimize) = "
        + ("— (nincs minimize-kimenet: futtasd a *_bestfit.yaml-t)" if dchi2 is None else
           f"{dchi2:.2f} → {'SZIGNIFIKÁNS' if res['significant'] else 'nem szignifikáns'} "
           f"(küszöb {DCHI2_SIGNIFICANT})"),
        "",
        "## Következmények",
        "",
        f"- WP3b: a szél minden szülőtömegre a horizonton túl? "
        f"{'igen' if c['wp3b_edge_all_parents'] else 'NEM'} (kell: N_tot > {c['max_n_tot_min_edge']:.1f})",
        f"- WP4b: a spin-ablak felső széle a 95%-os alsó N_tot-nál (fiduciális C): "
        f"a* ≤ {c['wp4b_a_star_max_at_lower95_fiducial']:.2f}; a* = 0.9-hez N_tot ≥ "
        f"{c['wp4b_n_needed_a0.9_fiducial']:.2f} kell",
        "",
        "## Paraméterek (LQC-lánc)",
        "",
        "| paraméter | átlag | szórás |",
        "|---|---|---|",
    ]
    for p, v in lqc["params"].items():
        note = " (priorfüggő: a poszterior ~142 fölött lapos, csak az alsó korlát értelmes)" \
            if p == "n_tot" else ""
        lines.append(f"| {p} | {v['mean']:.5g}{note} | {v['std']:.3g} |")
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"→ {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
