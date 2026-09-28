#!/usr/bin/env python3
"""CI validátor — szimulációs eredmények (schema 3.2) ellenőrzése."""
from __future__ import annotations

import json
import math
import sys
from itertools import pairwise
from pathlib import Path
from typing import Any

SCHEMA = "3.2"
RHO_CRIT_LQC = 2.1102600051408844e96


def _walk_numbers(obj: Any, path: str, errors: list[str]) -> None:
    if obj is None:
        errors.append(f"HIBA: null érték: {path}")
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            errors.append(f"HIBA: NaN/Inf: {path}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _walk_numbers(v, f"{path}.{k}", errors)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_numbers(v, f"{path}[{i}]", errors)


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA:
        errors.append(f"HIBA: váratlan schema: {data.get('schema_version')} (várt: {SCHEMA})")
        return errors

    _walk_numbers(data, "$", errors)
    if len(errors) > 20:
        return [*errors[:20], f"... és még {len(errors) - 20} hiba"]

    tl = data.get("timeline", [])
    if not tl:
        return [*errors, "HIBA: üres timeline"]

    # A tömeg a beesések között monoton, a dM/dt előjelének megfelelően
    for i, (a, b) in enumerate(pairwise(tl)):
        if b.get("after_infall"):
            if b["mass"] <= a["mass"]:
                errors.append(f"HIBA: a {i + 1}. pontnál a beesés nem növelte a tömeget")
            continue
        grows = a["net_mass_rate"] > 0
        if (grows and b["mass"] < a["mass"]) or (not grows and b["mass"] >= a["mass"]):
            errors.append(f"HIBA: a tömeg változása a {i + 1}. pontnál ellentmond dM/dt előjelének")
            break
    if any(b["time"] < a["time"] for a, b in pairwise(tl)):
        errors.append("HIBA: az idő csökkent")
    if any(s["entropy"] < 0 for s in tl):
        errors.append("HIBA: negatív entrópia")
    if any(not (0.0 <= s["spin"] < 1.0) for s in tl):
        errors.append("HIBA: a spin kívül esik a [0, 1) tartományon")

    if data.get("evaporation_complete"):
        # az utolsó beesés utáni párolgó szakaszon a hátralévő idő szigorúan csökken
        last_jump = max((i for i, s in enumerate(tl) if s.get("after_infall")), default=0)
        rem = [s.get("time_to_evaporation") for s in tl[last_jump:]]
        if any(r is None for r in rem):
            errors.append("HIBA: elpárolgott fekete lyuknál hiányzik a hátralévő idő")
        elif any(b >= a for a, b in pairwise(rem)):
            errors.append("HIBA: a hátralévő idő nem szigorúan csökkenő")
        if rem and rem[-1] != 0.0:
            errors.append("HIBA: a párolgás végén a hátralévő idő nem 0")

    # Az energiamérleg tételei ugyanabban az ODE-ben integráltak: a hiba ~1e-9
    energy = data.get("energy", {})
    if energy.get("relative_error", 1.0) > 1e-6:
        errors.append(f"HIBA: energiamérleg eltérés {energy.get('relative_error'):.3e} > 1e-6")
    feeding = data.get("interior_feeding", {})
    expected = energy.get("infall_events", 0.0) + feeding.get("continuous_inflow_energy", 0.0)
    total = feeding.get("total_infallen_energy", 0.0)
    if abs(total - expected) > 1e-9 * max(abs(expected), 1.0):
        errors.append("HIBA: interior_feeding összege nem egyezik az energiamérleggel")

    interior = data.get("interior", {})
    samples = interior.get("samples", [])
    if not samples:
        errors.append("HIBA: üres belső trajektória")
    elif samples[0].get("phase") != "infall":
        errors.append("HIBA: a belső trajektória nem a horizonton kívülről indul")
    if any(s["density"] > RHO_CRIT_LQC * (1 + 1e-9) for s in samples):
        errors.append("HIBA: a sűrűség meghaladja az LQC kritikus sűrűséget")

    norbi = data.get("config", {}).get("norbi_mode", False)
    bounce = interior.get("bounce")
    if norbi:
        if bounce is None:
            errors.append("HIBA: Norbi módban nincs visszapattanás")
        elif abs(bounce["density"] / RHO_CRIT_LQC - 1) > 1e-9:
            errors.append("HIBA: a visszapattanás nem ρ_c-nél történt")
        if not data.get("baby_universe"):
            errors.append("HIBA: Norbi módban üres a bébiuniverzum")
    elif interior.get("physics_boundary") is None:
        errors.append("HIBA: Standard módban nincs fizikai határ")

    return errors


def main(paths: list[str]) -> int:
    all_errors: list[str] = []
    for path in paths:
        errs = validate(json.loads(Path(path).read_text()))
        print(f"{path}: {'OK' if not errs else f'{len(errs)} HIBA'}")
        for e in errs:
            print(f"  {e}")
        all_errors.extend(errs)
    return 1 if all_errors else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: validate_results.py <results.json> [...]")
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
