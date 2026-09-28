"""Végponttól végpontig: Rust mag → Python elemzés (a lefordított kiterjesztés kell hozzá)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("black_hole_core")

from python.__main__ import main
from python.comparator import (
    compare_exterior_spectra,
    compare_information,
    compare_interiors,
)


def _run(tmp_path: Path, norbi: bool, mass: float = 1e12) -> dict[str, Any]:
    out = tmp_path / f"r_{norbi}.json"
    code = main([
        "--mass", str(mass), "--norbi-mode", str(norbi).lower(), "--steps", "40",
        "--interior-steps", "61", "--qubits", "7", "--output", str(out),
        "--payload", '{"uzenet": "teszt"}',
    ])
    assert code == 0
    data: dict[str, Any] = json.loads(out.read_text())
    return data


def test_norbi_and_standard_end_to_end(tmp_path: Path) -> None:
    std = _run(tmp_path, False)
    norbi = _run(tmp_path, True)
    assert std["schema_version"] == norbi["schema_version"] == "3.0"
    assert norbi["payload"] == {"uzenet": "teszt"}

    spectra = compare_exterior_spectra(std, norbi)
    assert not spectra["distinguishable"] and not spectra["norbi_causal_channel_exists"]

    interiors = compare_interiors(std, norbi)
    assert interiors["same_start"] and interiors["norbi_bounce"] is not None

    info = compare_information(std["information"], norbi["information"])
    assert info["norbi_final_mutual_info_bits"] == 0.0
    assert not info["norbi_recovers_message"]
    assert abs(info["unitary_reference_final_mutual_info_bits"] - 2.0) < 1e-9


def test_validator_accepts_output(tmp_path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "validate_results", Path(__file__).parents[2] / "scripts" / "validate_results.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for norbi in (False, True):
        assert mod.validate(_run(tmp_path, norbi, mass=5.1e11)) == []


def test_mass_gap_is_reported(tmp_path: Path) -> None:
    assert main(["--mass", "1e-8", "--output", str(tmp_path / "gap.json")]) == 1
