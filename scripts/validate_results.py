#!/usr/bin/env python3
"""CI validátor — szimulációs eredmények (schema 3.0) ellenőrzése."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

SCHEMA = "3.0"
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
        return errors[:20] + [f"... és még {len(errors) - 20} hiba"]

    tl = data.get("timeline", [])
    if not tl:
        return errors + ["HIBA: üres timeline"]

    masses = [s["mass"] for s in tl]
    if any(b >= a for a, b in zip(masses, masses[1:])):
        errors.append("HIBA: a tömeg nem szigorúan csökkenő")
    rem = [s["time_to_evaporation"] for s in tl]
    if any(b >= a for a, b in zip(rem, rem[1:])):
        errors.append("HIBA: a hátralévő idő nem szigorúan csökkenő")
    temps = [s["temperature"] for s in tl]
    if any(b < a for a, b in zip(temps, temps[1:])):
        errors.append("HIBA: a hőmérséklet csökkent")
    if any(s["entropy"] < 0 for s in tl):
        errors.append("HIBA: negatív entrópia")

    if not data.get("evaporation_complete"):
        errors.append("HIBA: a párolgás nem futott le a végtömegig")

    # A mérleg kvadratúrája másodrendű a log-tömegrácson: a tűrés (100/steps)²-tel skálázódik
    energy = data.get("energy", {})
    steps = max(int(data.get("config", {}).get("steps", 100)), 2)
    tol = 0.01 * (100 / steps) ** 2
    if energy.get("relative_error", 1.0) > tol:
        errors.append(f"HIBA: energiamérleg eltérés {energy.get('relative_error'):.3e} > {tol:.1e}")

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
