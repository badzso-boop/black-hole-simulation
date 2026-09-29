"""WP0: a Python LQC-háttér reprodukálja a Rust mag (és a literatúra) értékeit."""
from __future__ import annotations

import json
import math

import pytest

from thesis.lqc import bounce_radius_m, dust_density, h_max, hubble_squared
from thesis.units import RHO_C, RHO_PL, T_P


def test_critical_density() -> None:
    assert RHO_C == pytest.approx(math.sqrt(3) / (32 * math.pi**2 * 0.2375**3), rel=1e-14)
    assert RHO_C == pytest.approx(0.4094, abs=1e-4)


def test_h_max_is_maximum_of_friedmann() -> None:
    assert h_max() == pytest.approx(0.926, abs=1e-3)
    assert hubble_squared(RHO_C / 2) == pytest.approx(h_max() ** 2, rel=1e-14)
    assert hubble_squared(RHO_C) == 0.0


def test_dust_bounce_solves_friedmann() -> None:
    # ρ(τ) analitikus: H = ȧ/a = −ρ̇/(3ρ) és H² = (8π/3)ρ(1−ρ/ρ_c)
    for tau in (0.1, 0.7, 3.0):
        eps = 1e-6
        rho = dust_density(tau)
        h = -(dust_density(tau + eps) - dust_density(tau - eps)) / (2 * eps) / (3 * rho)
        assert h * h == pytest.approx(hubble_squared(rho), rel=1e-8)


def test_matches_rust_core() -> None:
    core = pytest.importorskip("black_hole_core")
    out = json.loads(core.run_simulation_py(json.dumps({"mass": 1e3, "norbi_mode": True}), "{}"))
    b = out["interior"]["bounce"]
    assert b["radius"] == pytest.approx(bounce_radius_m(1e3), rel=1e-12)
    assert b["max_hubble_rate"] == pytest.approx(h_max() / T_P, rel=1e-12)
    assert b["density"] == pytest.approx(RHO_C * RHO_PL, rel=1e-6)
