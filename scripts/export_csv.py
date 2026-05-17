#!/usr/bin/env python3
"""Timeline CSV export."""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path


def export(input_path: str, output_path: str) -> None:
    data = json.loads(Path(input_path).read_text())
    tl = data.get("timeline", [])
    if not tl:
        print("Üres timeline.")
        return
    fields = ["time", "mass", "temperature", "entropy"]
    with open(output_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(tl)
    print(f"Exportálva: {output_path} ({len(tl)} sor)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Használat: export_csv.py <results.json> <output.csv>")
        sys.exit(1)
    export(sys.argv[1], sys.argv[2])
