"""CLI belépési pont: python -m python.main --mass ... --norbi-mode ... --no-ui --output ..."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from python.logging_config import init_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Fekete Lyuk Szimulátor — CLI mód")
    parser.add_argument("--mass", type=float, required=True, help="Fekete lyuk tömege (kg)")
    parser.add_argument("--norbi-mode", type=lambda x: x.lower() == "true", default=True)
    parser.add_argument("--no-ui", action="store_true")
    parser.add_argument("--output", type=str, default="output/results.json")
    args = parser.parse_args()

    init_logging()

    try:
        import black_hole_core  # PyO3 Rust mag
        result_json = black_hole_core.run_simulation_py(
            args.mass, args.norbi_mode, "{}"
        )
    except ImportError:
        print("FIGYELMEZTETÉS: Rust mag nem elérhető, placeholder output", file=sys.stderr)
        result_json = json.dumps({
            "schema_version": "2.0",
            "config": {"norbi_mode": args.norbi_mode, "mode": "Standard"},
            "timeline": [],
            "evaporation_complete": False,
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result_json)
    print(f"Eredmény mentve: {out}")


if __name__ == "__main__":
    main()
