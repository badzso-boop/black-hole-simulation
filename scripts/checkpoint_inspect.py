#!/usr/bin/env python3
"""Checkpoint tartalmának megtekintése."""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import msgpack  # type: ignore[import]
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False


def inspect(path: str) -> None:
    data = Path(path).read_bytes()
    if HAS_MSGPACK:
        unpacked = msgpack.unpackb(data, raw=False)
        print(f"Schema: {unpacked.get('schema_version', '?')}")
        print(f"ID: {unpacked.get('simulation_id', '?')}")
        results = unpacked.get("results", {})
        cfg = results.get("config", {})
        print(f"Kezdőtömeg: {cfg.get('mass', 0):.3e} kg, Norbi-mód: {cfg.get('norbi_mode')}")
        tl = results.get("timeline", [])
        print(f"Timeline lépések: {len(tl)}")
        print(f"Párolgás lefutott: {results.get('evaporation_complete')}")
    else:
        print(f"Checkpoint mérete: {len(data)} byte")
        print("(msgpack csomag szükséges a tartalom megtekintéséhez)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: checkpoint_inspect.py <checkpoint.bhs>")
        sys.exit(1)
    inspect(sys.argv[1])
