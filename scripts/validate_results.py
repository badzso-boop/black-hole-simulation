#!/usr/bin/env python3
"""CI validátor — szimulációs eredmények ellenőrzése."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def validate(path: str) -> list[str]:
    errors: list[str] = []
    data = json.loads(Path(path).read_text())
    tl = data.get("timeline", [])

    if not tl:
        errors.append("HIBA: Üres timeline")
        return errors

    # 1. Tömeg monoton csökkenő
    masses = [s["mass"] for s in tl]
    for i in range(1, len(masses)):
        if masses[i] > masses[i - 1] * (1 + 1e-10):
            errors.append(f"HIBA: A tömeg nőtt {i}. lépésnél: {masses[i-1]:.3e} → {masses[i]:.3e}")
            break

    # 2. Entrópia nem negatív
    for s in tl:
        if s.get("entropy", 0) < 0:
            errors.append(f"HIBA: Negatív entrópia t={s['time']:.3e}s-nél")
            break

    # 3. Hőmérséklet monoton növekvő
    temps = [s["temperature"] for s in tl]
    for i in range(1, len(temps)):
        if temps[i] < temps[i - 1] * (1 - 1e-10):
            errors.append(f"HIBA: Hőmérséklet csökkent {i}. lépésnél")
            break

    # 4. NaN / Inf ellenőrzés
    for s in tl:
        for k, v in s.items():
            if isinstance(v, float) and (v != v or abs(v) == float("inf")):
                errors.append(f"HIBA: NaN/Inf: {k} t={s.get('time', '?'):.3e}s")

    # 5. Schema verzió
    if data.get("schema_version") != "2.0":
        errors.append(f"HIBA: Váratlan schema: {data.get('schema_version')}")

    return errors


if __name__ == "__main__":
    all_errors: list[str] = []
    for path in sys.argv[1:]:
        errs = validate(path)
        status = "OK" if not errs else f"{len(errs)} HIBA"
        print(f"{path}: {status}")
        for e in errs:
            print(f"  {e}")
        all_errors.extend(errs)
    sys.exit(1 if all_errors else 0)
