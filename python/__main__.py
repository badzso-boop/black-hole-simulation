"""CLI belépési pont: python -m python --mass ... --norbi-mode ... --output ..."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from python.information_packet import InformationPacket
from python.logging_config import init_logging


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fekete Lyuk Szimulátor — CLI")
    p.add_argument("--mass", type=float, required=True, help="Kezdeti tömeg (kg)")
    p.add_argument(
        "--norbi-mode",
        type=lambda x: x.lower() in ("true", "1", "igen", "yes"),
        default=False,
        help="true: LQC visszapattanás + bébiuniverzum a belsőben",
    )
    p.add_argument(
        "--emission-model",
        choices=["MacGibbon", "PageGammaGraviton", "PhotonBlackbody"],
        default="MacGibbon",
    )
    p.add_argument("--steps", type=int, default=100, help="Külső idővonal mintapontjai")
    p.add_argument("--interior-steps", type=int, default=201)
    p.add_argument("--initial-radius-rs", type=float, default=10.0)
    p.add_argument("--payload", type=str, default="{}", help="Bemeneti üzenet (JSON)")
    p.add_argument("--qubits", type=int, default=12, help="Toy modell: fekete lyuk qubitjei")
    p.add_argument("--message-qubits", type=int, default=1, help="Toy modell: üzenet-qubitek")
    p.add_argument("--no-info", action="store_true", help="Kvantuminformációs elemzés kihagyása")
    p.add_argument("--no-ui", action="store_true", help="(kompatibilitás; nincs UI)")
    p.add_argument("--output", type=str, default="output/results.json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    init_logging()

    try:
        import black_hole_core  # PyO3 Rust mag
    except ImportError:
        print(
            "HIBA: a Rust mag (black_hole_core) nincs telepítve — futtasd: pip install -e '.[dev]'",
            file=sys.stderr,
        )
        return 2

    config = {
        "mass": args.mass,
        "norbi_mode": args.norbi_mode,
        "emission_model": args.emission_model,
        "steps": args.steps,
        "interior_steps": args.interior_steps,
        "initial_radius_rs": args.initial_radius_rs,
    }
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"HIBA: a --payload nem érvényes JSON: {e}", file=sys.stderr)
        return 2

    try:
        result_json = black_hole_core.run_simulation_py(json.dumps(config), json.dumps(payload))
    except (RuntimeError, ValueError) as e:
        print(f"HIBA: {e}", file=sys.stderr)
        return 1

    if not args.no_info:
        from python.quantum_info import analyze

        results = json.loads(result_json)
        packet = InformationPacket(payload)
        info = analyze(results, n_bh=args.qubits, k_msg=args.message_qubits, seed=packet.seed)
        info["payload_sha3"] = packet.hash_sha3
        results["information"] = info
        result_json = json.dumps(results)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result_json)
    print(f"Eredmény mentve: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
