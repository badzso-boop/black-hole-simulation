"""A Rust `SimulationConfig` tükre (core/src/types.rs)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

EmissionModel = Literal["MacGibbon", "PageGammaGraviton", "PhotonBlackbody"]

T_CMB_TODAY = 2.7255


@dataclass
class InfallEvent:
    """Egy objektum beesése: t (s) időpontban m (kg) tömeg."""

    time: float
    mass: float
    label: str = ""


@dataclass
class Environment:
    """A Rust `Environment` tükre (core/src/black_hole/environment.rs).

    accretion: {"type": "none"} | {"type": "constant", "rate": kg/s}
             | {"type": "bondi", "density": kg/m³, "sound_speed": m/s,
                "eddington_limited": bool}
    """

    cmb_temperature: float = T_CMB_TODAY
    accretion: dict[str, Any] = field(default_factory=lambda: {"type": "none"})
    radiative_efficiency: float = 0.1
    disk_accretion: bool = False
    infall_events: list[InfallEvent] = field(default_factory=list)



@dataclass
class SimulationConfig:
    mass: float = 1e12
    spin: float = 0.0
    norbi_mode: bool = False
    emission_model: EmissionModel = "MacGibbon"
    steps: int = 100
    interior_steps: int = 201
    initial_radius_rs: float = 10.0
    environment: Environment = field(default_factory=lambda: Environment())
    max_time: float | None = None
    object: str | None = None

    def to_json(self) -> str:
        d = asdict(self)
        for k in ("max_time", "object"):
            if d[k] is None:
                del d[k]
        return json.dumps(d)

    @classmethod
    def from_json(cls, s: str) -> SimulationConfig:
        d = json.loads(s)
        env = d.pop("environment", {})
        infalls = [InfallEvent(**e) for e in env.pop("infall_events", [])]
        return cls(**d, environment=Environment(**env, infall_events=infalls))
