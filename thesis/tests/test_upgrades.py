"""A 2026-09-30-i kritikai áttekintés utáni javítások (docs/upgrade-plan.md A és B fázis)."""
from __future__ import annotations

import math
from typing import Any

import pytest

from thesis import inflaton_origin as io
from thesis import spin
from thesis.inflation import Quadratic, Starobinsky, evolve
from thesis.units import ALPHA_LMY, RHO_C

# --- B1a: por + mező ------------------------------------------------------------------


def test_b1a_zero_dust_reproduces_wp1() -> None:
    """f_d = 0: pontosan a WP1-számolás (ugyanaz a trajektória)."""
    star = Starobinsky()
    assert evolve(star, -1.3, 1, dust_fraction=0.0).n_infl == pytest.approx(
        evolve(star, -1.3, 1).n_infl, rel=1e-12)


def test_b1a_pure_dust_does_not_inflate() -> None:
    """Tiszta por, a mező nyugalomban a minimumában: nincs infláció (analitikus: V ≡ 0)."""
    assert not evolve(Starobinsky(), 0.0, 1, dust_fraction=1.0).inflated


def test_b1a_dust_bounce_density() -> None:
    """A tiszta por-visszapattanás Friedmann-kényszere: H² = (8π/3)ρ(1 − ρ/ρ_c), ρ = ρ_c e^{−3N}
    — az első szakasz végén (Ḣ = 0) ρ = ρ_c/2, azaz N = ln 2 / 3 (analitikus)."""
    r = evolve(Starobinsky(), 0.0, 1, dust_fraction=1.0)
    assert r.n_super == pytest.approx(math.log(2) / 3, rel=1e-6)


def test_b1a_amplification_is_analytic() -> None:
    """ρ_c/ρ_freeze = 8πρ_c/(3m²); Starobinsky m = M = 2.51e-6 (V″(0) = M²)."""
    star = Starobinsky()
    assert io.inflaton_mass(star) == pytest.approx(2.51e-6, rel=1e-9)
    assert RHO_C / io.rho_freeze(star) == pytest.approx(8 * math.pi * RHO_C / (3 * 2.51e-6**2))
    assert io.inflaton_mass(Quadratic()) == pytest.approx(1.21e-6, rel=1e-9)


def test_b1a_phi2_at_vacuum_fails_even_without_dust() -> None:
    """Ashtekar–Sloan: φ̇_B > 0-nál a φ_B ∈ [−5.5, 0.94] sáv < 68 e-redőt ad — φ_B = 0 benne van."""
    assert io.n_infl_at_vacuum(Quadratic(), 1.0) < 60


def test_b1a_field_must_dominate() -> None:
    f = io.min_field_fraction(Starobinsky(), iters=20)
    assert f is not None and 0.5 < f < 1.0
    assert io.min_field_fraction(Quadratic()) is None


# --- B3a: szél-bezártság --------------------------------------------------------------


def test_b3a_confinement_mass_and_spin_scaling() -> None:
    """M_conf = 2(η/ε)³/α és a*_max = C (√(α/2)/M_conf)^{1/3} ∝ ε — kézi képletből."""
    eta, c = 9553.68, 1.2255540597751917
    m1 = spin.confinement_mass(eta, 1.0)
    assert m1 == pytest.approx(2 * eta**3 / ALPHA_LMY, rel=1e-12)
    a1 = spin.a_star_gap(c, m1)
    assert a1 == pytest.approx(c * (math.sqrt(ALPHA_LMY / 2) / m1) ** (1 / 3), rel=1e-12)
    assert spin.a_star_gap(c, spin.confinement_mass(eta, 0.1)) == pytest.approx(a1 / 10, rel=1e-12)
    assert 5e-5 < a1 < 2e-4


def test_b3a_no_observed_population_survives() -> None:
    s7 = spin.edge_confinement_bounds(1.2255540597751917, spin.populations())
    assert s7["eta"]["eta_total"] == pytest.approx(
        s7["eta"]["eta_kinetic"] + s7["eta"]["eta_inflation"])
    assert all(v == 0.0 for v in s7["by_eps"]["1"]["fraction_allowed"].values())


# --- A3, A4: ítélet-logika ------------------------------------------------------------


def test_a4_l1e_planck_curvature_is_neutral(monkeypatch: pytest.MonkeyPatch) -> None:
    """A terv §5: ha a sors a kvantumgravitáción múlik → neutral (nem against)."""
    from thesis import verdict

    res: dict[str, Any] = {"validation": {}, "l1a": {"crossing": [{"efolds_available": 0.69}], "lmyz": [],
                                          "edge_confinement": []},
           "race": {"populations": {"GW": {"fraction_pass": 0.22, "fraction_pass_band": [0, 1]}},
                    "spin_scan": [{"passes": 1.0, "a_star": 0.44}], "mass_scan": [],
                    "fiducial_mass_kg": 1.0, "fiducial_delta": 0.1,
                    "asteroid": [{"delay_s": 86400.0, "meets_planckian_inner_horizon": 1.0}]}}
    monkeypatch.setattr(verdict, "inner_horizon_gate", lambda _v: {"passed": True, "checks": {}})
    rows = {r["wp"]: r["outcome"] for r in verdict.inner_horizon_scorecard(res)}
    assert rows["L1e the asteroid"].startswith("neutral")


def test_a3_wp3b_is_consistency_check() -> None:
    from thesis.verdict import wp3b

    rows = [{"edge_weaker_than_horizon_problem": True, "n_tot_min_edge": 126.8,
             "n_infl_needed_for_horizon_problem": 60.0, "n_infl_needed_for_edge": 55.0,
             "n_tot_minimal_inflation": 130.9}]
    out = wp3b({"rows": rows})
    assert out["outcome"] == "consistency check: passes"
    assert out["numbers"]["old_rule_outcome"] == "supports"
