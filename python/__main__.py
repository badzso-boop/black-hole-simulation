"""CLI belépési pont: python -m python --mass ... --norbi-mode ... --output ..."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from python.information_packet import InformationPacket
from python.logging_config import init_logging


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fekete Lyuk Szimulátor — CLI")
    p.add_argument(
        "--object",
        default=None,
        help="Valódi fekete lyuk a katalógusból (pl. sgr-a, m87, cyg-x1, gw250114, pbh-today); "
        "a többi kapcsoló felülírja az értékeit",
    )
    p.add_argument("--list-objects", action="store_true", help="A katalógus kilistázása")
    p.add_argument("--mass", type=float, default=None, help="Kezdeti tömeg (kg)")
    p.add_argument(
        "--spin", type=float, default=None, help="Kezdeti spin a* = Jc/(GM²), 0 ≤ a* < 1"
    )
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
        "--cmb-temperature",
        type=float,
        default=None,
        help="Háttérsugárzás (K), alapból 2.7255; 0 = vákuum",
    )
    env.add_argument(
        "--accretion",
        choices=["none", "constant", "bondi"],
        default=None,
        help="alapból none (vagy a katalógus-objektum mért rátája)",
    )
    env.add_argument("--accretion-rate", type=float, default=0.0, help="constant: Ṁ (kg/s)")
    env.add_argument(
        "--gas-density", type=float, default=1.67e-21, help="bondi: ρ_∞ (kg/m³), ISM ≈ 1.67e-21"
    )
    env.add_argument("--sound-speed", type=float, default=1.0e4, help="bondi: c_s (m/s)")
    env.add_argument(
        "--no-eddington-limit", action="store_true", help="bondi: Eddington-korlát nélkül"
    )
    env.add_argument(
        "--radiative-efficiency", type=float, default=None, help="ε (0 ≤ ε < 1), alapból 0.1"
    )
    env.add_argument(
        "--disk-accretion",
        action="store_true",
        help="vékony korong: ε = 1 − E_isco(a*), Bardeen-felpörgetés a Thorne-határig",
    )
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


def build_environment(
    args: argparse.Namespace, base: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Környezet a kapcsolókból; `base` (katalógus) értékeit csak a megadott kapcsolók írják felül."""
    env: dict[str, Any] = dict(base or {})
    env.setdefault("cmb_temperature", 2.7255)
    env.setdefault("accretion", {"type": "none"})
    env.setdefault("radiative_efficiency", 0.1)
    env.setdefault("disk_accretion", False)
    env.setdefault("infall_events", [])
    if args.cmb_temperature is not None:
        env["cmb_temperature"] = args.cmb_temperature
    if args.radiative_efficiency is not None:
        env["radiative_efficiency"] = args.radiative_efficiency
    if args.disk_accretion:
        env["disk_accretion"] = True
    if args.accretion == "constant":
        env["accretion"] = {"type": "constant", "rate": args.accretion_rate}
    elif args.accretion == "bondi":
        env["accretion"] = {
            "type": "bondi",
            "density": args.gas_density,
            "sound_speed": args.sound_speed,
            "eddington_limited": not args.no_eddington_limit,
        }
    elif args.accretion == "none":
        env["accretion"] = {"type": "none"}
    env["infall_events"] = list(env["infall_events"]) + [parse_infall(x) for x in args.infall]
    return env


def list_objects(core: Any) -> None:
    for obj in json.loads(core.catalog_json()):
        dist = f"{obj['distance_pc']:.4g} pc" if obj.get("distance_pc") else "—"
        print(f"{obj['key']:<11} {obj['name']}")
        print(
            f"{'':<11} M = {obj['mass_msun']:.4g} M_☉, a* = {obj['spin']}, D = {dist}, "
            f"Ṁ = {obj['accretion_msun_per_yr']:.2g} M_☉/év"
        )


def print_summary(results: dict[str, Any]) -> None:
    m_sun = 1.98847e30
    year = 3.15576e7
    cfg = results["config"]
    print(f"  kezdőtömeg:   {cfg['mass']:.4e} kg ({cfg['mass'] / m_sun:.4g} M_☉), a* = {cfg['spin']}")
    if results["evaporation_complete"]:
        print(f"  elpárolgott:  {results['end_time']:.4e} s ({results['end_time'] / year / 1e9:.4g} Gyr) alatt")
    else:
        # a pontos változás az energiamérlegből (a tömeg f64-felbontása alatt is)
        e = results["energy"]
        c2 = 299792458.0**2
        dm = (
            e["infall_events"] + e["background_absorbed"] + e["accretion_inflow"]
            - e["accretion_luminosity"] - e["hawking_radiated"]
        ) / c2
        print(
            f"  {results['end_time'] / year / 1e9:.4g} Gyr után: M = {results['end_mass']:.6e} kg "
            f"(ΔM = {dm:+.3e} kg), a* = {results['kerr']['final_spin']:.4f}"
        )
    obj = results.get("object")
    if obj:
        print(f"  objektum:     {obj['name']}")
        if obj.get("assumptions"):
            print(f"  feltevések:   {obj['assumptions']}")
        if obj.get("shadow_diameter_uas"):
            print(f"  árnyék:       {obj['shadow_diameter_uas']:.3g} μas (a* = 0 közelítés)")
        if obj.get("observed_ring_uas"):
            print(
                f"  EHT-gyűrű:    várt {obj['predicted_ring_uas']:.1f} μas, mért "
                f"{obj['observed_ring_uas']} ± {obj['observed_ring_err_uas']} μas "
                f"(δ = {obj['ring_deviation']:+.3f})"
            )
    for w in results.get("warnings", []):
        print(f"  ! {w[:160]}{'…' if len(w) > 160 else ''}")


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

    if args.list_objects:
        list_objects(black_hole_core)
        return 0

    base: dict[str, Any] = {}
    if args.object:
        try:
            base = json.loads(black_hole_core.object_config_json(args.object))
        except ValueError as e:
            print(f"HIBA: {e}", file=sys.stderr)
            return 2
    elif args.mass is None:
        print("HIBA: add meg a --mass vagy az --object kapcsolót", file=sys.stderr)
        return 2

    try:
        environment = build_environment(args, base.get("environment"))
    except ValueError as e:
        print(f"HIBA: {e}", file=sys.stderr)
        return 2
    config: dict[str, Any] = {
        "environment": environment,
        "mass": args.mass if args.mass is not None else base["mass"],
        "spin": args.spin if args.spin is not None else base.get("spin", 0.0),
        "norbi_mode": args.norbi_mode,
        "emission_model": args.emission_model,
        "steps": args.steps,
        "interior_steps": args.interior_steps,
        "initial_radius_rs": args.initial_radius_rs,
    }
    if args.object:
        config["object"] = base["object"]
    if args.max_time is not None:
        config["max_time"] = args.max_time
    elif base.get("max_time") is not None:
        config["max_time"] = base["max_time"]
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
    print_summary(json.loads(result_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
