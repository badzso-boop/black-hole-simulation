"""A Rust `SimulationConfig` tükre (core/src/types.rs)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Literal

EmissionModel = Literal["MacGibbon", "PageGammaGraviton", "PhotonBlackbody"]


@dataclass
class SimulationConfig:
    mass: float = 1e12
    norbi_mode: bool = False
    emission_model: EmissionModel = "MacGibbon"
    steps: int = 100
    interior_steps: int = 201
    initial_radius_rs: float = 10.0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, s: str) -> SimulationConfig:
        return cls(**json.loads(s))
