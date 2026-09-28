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
    p.add_argument(
        "--max-time",
        type=float,
        default=None,
        help="Szimulációs horizont (s); alapból a párolgás végéig, ill. ha nő, 13.787 Gyr",
    )
    env = p.add_argument_group("környezet (ami a keletkezés után beleesik)")
    env.add_argument(
        "--cmb-temperature", type=float, default=2.7255, help="Háttérsugárzás (K); 0 = vákuum"
    )
    env.add_argument("--accretion", choices=["none", "constant", "bondi"], default="none")
    env.add_argument("--accretion-rate", type=float, default=0.0, help="constant: Ṁ (kg/s)")
    env.add_argument(
        "--gas-density", type=float, default=1.67e-21, help="bondi: ρ_∞ (kg/m³), ISM ≈ 1.67e-21"
    )
    env.add_argument("--sound-speed", type=float, default=1.0e4, help="bondi: c_s (m/s)")
    env.add_argument(
        "--no-eddington-limit", action="store_true", help="bondi: Eddington-korlát nélkül"
    )
    env.add_argument("--radiative-efficiency", type=float, default=0.1, help="ε (0 ≤ ε < 1)")
    env.add_argument(
        "--infall",
        action="append",
        default=[],
        metavar="IDŐ:TÖMEG[:CÍMKE]",
        help="Beesés: pl. 1e17:5.97e24:Föld (ismételhető)",
    )
    p.add_argument("--payload", type=str, default="{}", help="Bemeneti üzenet (JSON)")
    p.add_argument("--qubits", type=int, default=12, help="Toy modell: fekete lyuk qubitjei")
    p.add_argument("--message-qubits", type=int, default=1, help="Toy modell: üzenet-qubitek")
    p.add_argument("--no-info", action="store_true", help="Kvantuminformációs elemzés kihagyása")
    p.add_argument("--no-ui", action="store_true", help="(kompatibilitás; nincs UI)")
    p.add_argument("--output", type=str, default="output/results.json")
    return p


def parse_infall(spec: str) -> dict[str, object]:
    """'IDŐ:TÖMEG[:CÍMKE]' → {"time", "mass", "label"}"""
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"A --infall formátuma IDŐ:TÖMEG[:CÍMKE], kapott: {spec!r}")
    return {
        "time": float(parts[0]),
        "mass": float(parts[1]),
        "label": parts[2] if len(parts) > 2 else "",
    }


def build_environment(args: argparse.Namespace) -> dict[str, object]:
    accretion: dict[str, object]
    if args.accretion == "constant":
        accretion = {"type": "constant", "rate": args.accretion_rate}
    elif args.accretion == "bondi":
        accretion = {
            "type": "bondi",
            "density": args.gas_density,
            "sound_speed": args.sound_speed,
            "eddington_limited": not args.no_eddington_limit,
        }
    else:
        accretion = {"type": "none"}
    return {
        "cmb_temperature": args.cmb_temperature,
        "accretion": accretion,
        "radiative_efficiency": args.radiative_efficiency,
        "infall_events": [parse_infall(x) for x in args.infall],
    }


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

    try:
        environment = build_environment(args)
    except ValueError as e:
        print(f"HIBA: {e}", file=sys.stderr)
        return 2
    config: dict[str, object] = {
        "environment": environment,
        "mass": args.mass,
        "norbi_mode": args.norbi_mode,
        "emission_model": args.emission_model,
        "steps": args.steps,
        "interior_steps": args.interior_steps,
        "initial_radius_rs": args.initial_radius_rs,
    }
    if args.max_time is not None:
        config["max_time"] = args.max_time
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
