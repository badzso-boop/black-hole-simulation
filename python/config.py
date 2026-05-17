from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from enum import Enum


class SimMode(str, Enum):
    LITE = "Lite"
    STANDARD = "Standard"
    RESEARCH = "Research"


@dataclass
class SimulationConfig:
    mode: SimMode = SimMode.STANDARD
    max_external_objects: int = 100
    max_internal_objects: int = 200
    internal_dt: float = 1e-11
    external_dt: float = 1e5
    norbi_mode: bool = True
    gravitational_softening: float = 0.001

    @classmethod
    def lite(cls) -> SimulationConfig:
        return cls(
            mode=SimMode.LITE,
            max_external_objects=10,
            max_internal_objects=20,
            internal_dt=1e-10,
            external_dt=1e6,
        )

    @classmethod
    def standard(cls) -> SimulationConfig:
        return cls()

    @classmethod
    def research(cls) -> SimulationConfig:
        return cls(
            mode=SimMode.RESEARCH,
            max_external_objects=1000,
            max_internal_objects=5000,
            internal_dt=1e-12,
            external_dt=1e4,
        )

    def to_json(self) -> str:
        d = asdict(self)
        d["mode"] = self.mode.value
        return json.dumps(d)

    @classmethod
    def from_json(cls, s: str) -> SimulationConfig:
        d = json.loads(s)
        d["mode"] = SimMode(d["mode"])
        return cls(**d)
