#!/usr/bin/env python3
"""A `run_campaign.py` kimenetének elemzése.

Használat:  python scripts/analyze_campaign.py runs/<id>

Beolvassa a teljes eredményeket (output/campaign/<id>/*.json), és a
runs/<id>/ mappába írja:
    summary.csv            futásonként egy sor, a fontos skalárokkal
    results_compact.json   ugyanez + idősorok ritkítva (spektrumok nélkül)
    RESULTS.md             automatikusan generált táblázatok és ellenőrzések
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
C2 = 299_792_458.0**2
M_SUN = 1.98847e30
YEAR = 3.15576e7
GYR = 1e9 * YEAR
AGE_UNIVERSE_GYR = 13.787


def extract(run: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    cfg = data["config"]
    env = cfg["environment"]
    tl = data["timeline"]
    e = data["energy"]
    dm = (e["infall_events"] + e["background_absorbed"] + e["accretion_inflow"]
          - e["accretion_luminosity"] - e["hawking_radiated"]) / C2
    info = data.get("information", {})
    active = info.get("curves", {}).get(info.get("active_model", ""), {})
    unitary = info.get("curves", {}).get("unitary", {})
    obj = data.get("object") or {}
    interior = data["interior"]
    bu = data.get("baby_universe") or []
    first = tl[0]
    return {
        "id": run["id"],
        "group": run["group"],
        "name": run["name"],
        "wall_s": run["wall_s"],
        "mass_kg": cfg["mass"],
        "mass_msun": cfg["mass"] / M_SUN,
        "spin0": cfg["spin"],
        "norbi": cfg["norbi_mode"],
        "emission_model": cfg["emission_model"],
        "cmb_K": env["cmb_temperature"],
        "accretion": env["accretion"]["type"],
        "disk": env["disk_accretion"],
        "n_infall": len(env["infall_events"]),
        "steps": len(tl),
        "evaporated": data["evaporation_complete"],
        "end_time_s": data["end_time"],
        "end_time_gyr": data["end_time"] / GYR,
        "end_mass_kg": data["end_mass"],
        "delta_m_kg": dm,
        "delta_m_rel": dm / cfg["mass"],
        "final_spin": data["kerr"]["final_spin"],
        "T_H0_K": first["temperature"],
        "entropy0": first["entropy"],
        "net_rate0_kg_s": first["net_mass_rate"],
        "hawking_J": e["hawking_radiated"],
        "cmb_absorbed_J": e["background_absorbed"],
        "accreted_J": e["accretion_inflow"],
        "accretion_lum_J": e["accretion_luminosity"],
        "ledger_rel_err": e["relative_error"],
        "equilibrium_mass_kg": data.get("equilibrium_mass"),
        "disk_efficiency0": data["kerr"]["disk_efficiency"],
        "r_plus_m": data["kerr"]["r_plus"],
        "horizon_to_end_tau_s": interior["proper_time_horizon_to_end"],
        "bounce_radius_m": (interior.get("bounce") or {}).get("radius"),
        "causal_channel": data["causal_channel"]["exists"],
        "bu_final_efolds": bu[-1]["efolds"] if bu else None,
        "bu_peak_hubble": max((b["hubble"] for b in bu), default=None),
        "nonthermality0": first["spectrum"]["spectral_nonthermality"],
        "info_active_model": info.get("active_model"),
        "info_final_MI_bits": active.get("final_mutual_info"),
        "info_page_turnover": active.get("page_turnover"),
        "info_unitary_MI_bits": unitary.get("final_mutual_info"),
        "object": obj.get("key"),
        "ring_pred_uas": obj.get("predicted_ring_uas"),
        "ring_obs_uas": obj.get("observed_ring_uas"),
        "ring_deviation": obj.get("ring_deviation"),
        "shadow_uas": obj.get("shadow_diameter_uas"),
        "eddington_ratio": obj.get("eddington_ratio"),
        "n_warnings": len(data.get("warnings", [])),
    }


def thin(tl: list[dict[str, Any]], k: int = 25) -> list[dict[str, Any]]:
    idx = sorted(set(round(i * (len(tl) - 1) / (k - 1)) for i in range(k)))
    keys = ["time", "time_to_evaporation", "mass", "spin", "temperature", "net_mass_rate", "after_infall"]
    return [{key: tl[i].get(key) for key in keys if key in tl[i]} for i in idx]


def fmt(x: Any, spec: str = ".3g") -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "igen" if x else "nem"
    if isinstance(x, float):
        return format(x, spec)
    return str(x)


def table(rows: list[dict[str, Any]], cols: list[tuple[str, str, str]]) -> str:
    head = "| " + " | ".join(c[1] for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = ["| " + " | ".join(fmt(r.get(c[0]), c[2]) for c in cols) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def main(run_dir: Path) -> int:
    meta = json.loads((run_dir / "campaign.json").read_text())
    rows, compact = [], []
    for run in meta["runs"]:
        path = ROOT / run["output"]
        if run["exit_code"] != 0 or not path.exists():
            continue
        data = json.loads(path.read_text())
        row = extract(run, data)
        rows.append(row)
        compact.append({**row, "timeline": thin(data["timeline"]), "warnings": data.get("warnings", [])})

    with (run_dir / "summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (run_dir / "results_compact.json").write_text(json.dumps(compact, indent=1, ensure_ascii=False) + "\n")

    by = {r["id"]: r for r in rows}
    g = lambda name: [r for r in rows if r["group"] == name]  # noqa: E731
    out: list[str] = [f"# Kampány-eredmények — {meta['id']}", "",
                      "Automatikusan generálva: `python scripts/analyze_campaign.py "
                      f"runs/{meta['id']}`. Az értelmezés: [ANALYSIS.md](ANALYSIS.md).", ""]

    # --- futtatás ---
    walls = [r["wall_s"] for r in rows]
    out += ["## Futtatás", "", "```", (run_dir / "system.txt").read_text().strip(), "```", "",
            f"- {len(rows)} futás / {len(meta['runs'])} sikeres, {meta['jobs']} párhuzamosan, "
            f"összesen {meta['total_wall_s']:.0f} s",
            f"- futásonként: medián {sorted(walls)[len(walls) // 2]:.2f} s, max {max(walls):.2f} s",
            f"- csúcs-RAM: {meta['peak_rss_mb']} MB",
            f"- energiamérleg legnagyobb relatív hibája: {max(r['ledger_rel_err'] for r in rows):.1e}", ""]

    # --- ellenőrzések ---
    checks: list[tuple[str, str, str, bool]] = []
    pbh = by.get("catalog__pbh-today_norbi-false")
    if pbh:
        checks.append(("Ma elpárolgó PBH élettartama (5.1e11 kg)", f"{pbh['end_time_gyr']:.2f} Gyr",
                       "13.8 Gyr (Carr et al. 2010)", 9.5 < pbh["end_time_gyr"] < 18))
    for key, ref in [("sgr-a", -0.08), ("m87", 0.0)]:
        r = by.get(f"catalog__{key}_norbi-false")
        if r:
            checks.append((f"EHT-gyűrű eltérés δ ({key})", f"{r['ring_deviation']:+.3f}",
                           f"{ref:+.2f} ± 0.09 (EHT)", abs(r["ring_deviation"] - ref) < 0.09))
    s0 = by.get("spin__PageGammaGraviton_a0.0")
    s999 = by.get("spin__PageGammaGraviton_a0.999")
    if s0 and s999:
        ratio = s0["end_time_s"] / s999["end_time_s"]
        checks.append(("Forgó/nem forgó élettartam-faktor (γ+graviton)", f"{ratio:.2f}×",
                       "2.0–2.7× (Page 1976b)", 1.9 < ratio < 3.0))
    disk = by.get("environment__stellar_disk_spinup_from_0")
    if disk:
        x = disk["mass_kg"] / disk["end_mass_kg"]
        bardeen = math.sqrt(2 / 3) * x * (4 - math.sqrt(max(18 * x * x - 2, 0))) if x >= 1 / math.sqrt(6) else 1
        checks.append(("Bardeen-felpörgetés (korong, a*=0-ból)",
                       f"a* = {disk['final_spin']:.4f} @ M/M0 = {1 / x:.3f}",
                       f"a* = {min(bardeen, 0.998):.4f} (Bardeen 1970)", abs(disk["final_spin"] - min(bardeen, 0.998)) < 1e-3))
    edd = by.get("environment__stellar_bondi_eddington_100myr")
    if edd:
        t_s = 0.1 * 6.6524587051e-29 * 299792458.0 / (0.9 * 4 * math.pi * 6.6743e-11 * 1.67262192595e-27)
        expected = math.exp(edd["end_time_s"] / t_s)
        got = edd["end_mass_kg"] / edd["mass_kg"]
        checks.append(("Eddington-korlátos növekedés 100 Myr", f"M/M0 = {got:.4f}",
                       f"e^(t/t_S) = {expected:.4f}", abs(got / expected - 1) < 1e-4))
    conv = sorted(g("convergence"), key=lambda r: r["steps"])
    if conv:
        spread = max(r["end_time_s"] for r in conv) / min(r["end_time_s"] for r in conv) - 1
        checks.append(("Konvergencia (25–1000 lépés), élettartam szórása", f"{spread:.1e}", "< 1e-6", spread < 1e-6))
    out += ["## Ellenőrzések az irodalommal", "",
            "| Ellenőrzés | Szimuláció | Irodalom / elvárt | Rendben |", "|---|---|---|---|",
            *[f"| {a} | {b} | {c} | {'✅' if d else '❌'} |" for a, b, c, d in checks], ""]

    # --- tömeg-scan ---
    cmb = sorted(g("mass_cmb"), key=lambda r: r["mass_kg"])
    vac = {r["mass_kg"]: r for r in g("mass_vacuum")}
    for r in cmb:
        v = vac.get(r["mass_kg"])
        r["vac_time_gyr"] = v["end_time_gyr"] if v else None
        r["fate"] = "elpárolog" if r["evaporated"] else "nő"
    out += ["## Tömeg-scan (mai CMB, 2.7255 K)", "", table(cmb, [
        ("mass_kg", "M (kg)", ".3g"), ("T_H0_K", "T_H (K)", ".3g"), ("fate", "sors", ""),
        ("end_time_gyr", "élettartam / horizont (Gyr)", ".3g"), ("vac_time_gyr", "vákuumban (Gyr)", ".3g"),
        ("net_rate0_kg_s", "dM/dt kezdetben (kg/s)", ".3g"), ("delta_m_kg", "ΔM (kg)", ".3g"),
        ("horizon_to_end_tau_s", "horizont→belső vég τ (s)", ".3g")]), ""]
    eq = next((r["equilibrium_mass_kg"] for r in cmb if r["equilibrium_mass_kg"]), None)
    if eq:
        out += [f"CMB-egyensúlyi tömeg (instabil): **M_eq = {eq:.4g} kg**", ""]

    # --- spin ---
    spin = sorted(g("spin"), key=lambda r: (r["emission_model"], r["spin0"]))
    ref = {r["emission_model"]: r["end_time_s"] for r in spin if r["spin0"] == 0.0}
    for r in spin:
        r["life_ratio"] = r["end_time_s"] / ref[r["emission_model"]]
    out += ["## Spin-scan (M = 1e12 kg, mai CMB — ennél a tömegnél elhanyagolható)", "", table(spin, [
        ("emission_model", "modell", ""), ("spin0", "a*₀", ".3g"), ("T_H0_K", "T_H (K)", ".3g"),
        ("end_time_gyr", "élettartam (Gyr)", ".4g"), ("life_ratio", "τ/τ(a*=0)", ".3f")]), ""]

    # --- emisszió ---
    out += ["## Emissziós modellek (M = 5.1e11 kg)", "", table(g("emission"), [
        ("emission_model", "modell", ""), ("end_time_gyr", "élettartam (Gyr)", ".4g"),
        ("nonthermality0", "spektrális nem-termalitás", ".3f")]), ""]

    # --- környezet ---
    out += ["## Környezet-szcenáriók", "", table(g("environment"), [
        ("name", "szcenárió", ""), ("mass_kg", "M0 (kg)", ".3g"), ("evaporated", "elpárolgott", ""),
        ("end_time_gyr", "idő (Gyr)", ".4g"), ("end_mass_kg", "végtömeg (kg)", ".4g"),
        ("delta_m_kg", "ΔM (kg)", ".3g"), ("final_spin", "a* vég", ".4f"),
        ("ledger_rel_err", "mérleg-hiba", ".1e")]), ""]

    # --- katalógus ---
    cat = sorted(g("catalog"), key=lambda r: (r["object"], r["norbi"]))
    out += ["## Valódi fekete lyukak", "", table([r for r in cat if not r["norbi"]], [
        ("object", "objektum", ""), ("mass_msun", "M (M_☉)", ".4g"), ("spin0", "a*", ".3g"),
        ("T_H0_K", "T_H (K)", ".3g"), ("end_time_gyr", "horizont (Gyr)", ".4g"),
        ("delta_m_kg", "ΔM (kg)", ".3g"), ("delta_m_rel", "ΔM/M", ".2e"), ("final_spin", "a* vég", ".4f"),
        ("shadow_uas", "árnyék (μas)", ".3g"), ("ring_pred_uas", "várt gyűrű (μas)", ".3g"),
        ("ring_obs_uas", "mért gyűrű (μas)", ".3g"), ("ring_deviation", "δ", "+.3f"),
        ("eddington_ratio", "L/L_Edd", ".2e")]), ""]

    # --- Norbi vs Standard ---
    pairs = []
    for r in cat:
        if r["norbi"]:
            continue
        n = by.get(r["id"].replace("norbi-false", "norbi-true"))
        if n:
            s_data = json.loads((ROOT / f"output/campaign/{meta['id']}/{r['id']}.json").read_text())
            n_data = json.loads((ROOT / f"output/campaign/{meta['id']}/{n['id']}.json").read_text())
            same = all(a["spectrum"]["intensities"] == b["spectrum"]["intensities"]
                       for a, b in zip(s_data["timeline"], n_data["timeline"], strict=True))
            pairs.append({"object": r["object"], "same_spectrum": same, "causal": n["causal_channel"],
                          "bu_efolds": n["bu_final_efolds"], "bu_peak_hubble": n["bu_peak_hubble"],
                          "std_MI": r["info_final_MI_bits"], "norbi_MI": n["info_final_MI_bits"],
                          "unitary_MI": n["info_unitary_MI_bits"]})
    out += ["## Norbi vs. Standard", "", table(pairs, [
        ("object", "objektum", ""), ("same_spectrum", "külső spektrum azonos", ""),
        ("causal", "kauzális csatorna", ""), ("bu_efolds", "bébiuniverzum e-redők", ".3g"),
        ("bu_peak_hubble", "H_max (1/s)", ".3g"), ("std_MI", "I(Ref:R) Standard (bit)", ".3g"),
        ("norbi_MI", "I(Ref:R) Norbi (bit)", ".3g"), ("unitary_MI", "I(Ref:R) unitér ref. (bit)", ".3g")]), ""]

    # --- konvergencia ---
    out += ["## Konvergencia a lépésszámban (M = 1e12 kg)", "", table(conv, [
        ("steps", "mintapont", "d"), ("end_time_s", "élettartam (s)", ".12g"),
        ("ledger_rel_err", "mérleg-hiba", ".1e"), ("wall_s", "futási idő (s)", ".2f")]), ""]

    (run_dir / "RESULTS.md").write_text("\n".join(out))
    print(f"Kész: {run_dir / 'RESULTS.md'}, summary.csv, results_compact.json ({len(rows)} futás)")
    print("\n".join(f"  {'OK ' if d else 'HIBA'} {a}: {b} (elvárt {c})" for a, b, c, d in checks))
    return 0 if all(c[3] for c in checks) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
