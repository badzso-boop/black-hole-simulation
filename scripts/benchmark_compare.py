#!/usr/bin/env python3
"""Két szimuláció összehasonlítása."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def compare(path1: str, path2: str) -> None:
    d1 = json.loads(Path(path1).read_text())
    d2 = json.loads(Path(path2).read_text())
    t1 = d1.get("timeline", [])
    t2 = d2.get("timeline", [])
    print(f"Fájl 1: {path1} ({len(t1)} lépés)")
    print(f"Fájl 2: {path2} ({len(t2)} lépés)")
    if t1 and t2:
        m1 = t1[-1]["mass"]
        m2 = t2[-1]["mass"]
        print(f"Végső tömeg: {m1:.3e} kg vs {m2:.3e} kg")
        print(f"Arány: {m1/m2:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Használat: benchmark_compare.py <fájl1> <fájl2>")
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])
