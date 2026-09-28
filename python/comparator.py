"""Standard vs. Norbi összehasonlítás a (schema 3.0) szimulációs eredményekből."""
from __future__ import annotations

from typing import Any

import numpy as np


def compare_exterior_spectra(std: dict[str, Any], norbi: dict[str, Any]) -> dict[str, Any]:
    """A külső megfigyelő szemszögéből: különbözik-e a két modell spektruma?

    Relatív L1-eltérés lépésenként; 0 = megkülönböztethetetlen.
    """
    diffs: list[float] = []
    for a, b in zip(std.get("timeline", []), norbi.get("timeline", []), strict=True):
        ia = np.asarray(a["spectrum"]["intensities"], dtype=np.float64)
        ib = np.asarray(b["spectrum"]["intensities"], dtype=np.float64)
        denom = float(np.sum(np.abs(ia))) or 1.0
        diffs.append(float(np.sum(np.abs(ia - ib)) / denom))
    max_diff = max(diffs) if diffs else 0.0
    return {
        "max_relative_l1_difference": max_diff,
        "distinguishable": max_diff > 1e-9,
        "norbi_causal_channel_exists": bool(norbi.get("causal_channel", {}).get("exists", False)),
    }


def compare_interiors(std: dict[str, Any], norbi: dict[str, Any]) -> dict[str, Any]:
    """Hol válik szét a két belső leírás? (a klasszikus határ / visszapattanás)"""
    si, ni = std.get("interior", {}), norbi.get("interior", {})
    return {
        "standard_physics_boundary": si.get("physics_boundary"),
        "norbi_bounce": ni.get("bounce"),
        "same_start": abs(si.get("tau_start", 0.0) - ni.get("tau_start", 0.0))
        <= 1e-9 * abs(si.get("tau_start", 1.0)),
        "baby_universe_final_efolds": (norbi.get("baby_universe") or [{}])[-1].get("efolds"),
    }


def compare_information(std_info: dict[str, Any], norbi_info: dict[str, Any]) -> dict[str, Any]:
    """Az információs görbék (quantum_info.analyze kimenete) összevetése."""
    s = std_info["curves"][std_info["active_model"]]
    n = norbi_info["curves"][norbi_info["active_model"]]
    u = norbi_info["curves"]["unitary"]
    return {
        "standard_final_mutual_info_bits": s["final_mutual_info"],
        "norbi_final_mutual_info_bits": n["final_mutual_info"],
        "unitary_reference_final_mutual_info_bits": u["final_mutual_info"],
        "norbi_recovers_message": n["message_recoverable"],
        "norbi_page_turnover": n["page_turnover"],
    }
