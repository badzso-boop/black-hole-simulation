"""WP1: a visszapattanás utáni infláció — literatúra-reprodukciók."""
from __future__ import annotations

import pytest

from thesis.inflation import Quadratic, Starobinsky, evolve, phi_end_slow_roll, pivot_observables
from thesis.wp1 import threshold_phi_b


def test_friedmann_constraint_preserved() -> None:
    r = evolve(Starobinsky(), -1.3, 1)
    assert r.constraint_drift < 1e-8


def test_bonga_gupt_thresholds() -> None:
    star = Starobinsky()
    assert star.phi_min_bounce() == pytest.approx(-3.47, abs=0.01)
    assert threshold_phi_b(star, 1, 60.0, -1.8, -1.0, tol=1e-3) == pytest.approx(-1.45, abs=0.03)
    assert threshold_phi_b(star, -1, 60.0, 3.3, 4.0, tol=1e-3) == pytest.approx(3.63, abs=0.03)


def test_ashtekar_sloan_band_edges() -> None:
    # AS 2011 Eq. 4.25: 68 e-redő alatt csak φ_B ∈ [−5.5, 0.94] (φ̇_B > 0)
    q = Quadratic()
    assert evolve(q, -5.6, 1).n_infl >= 68
    assert evolve(q, -5.3, 1).n_infl < 68
    assert evolve(q, 0.8, 1).n_infl < 68
    assert evolve(q, 1.2, 1).n_infl >= 68
    # mindkét irányban szimmetrikus a potenciál
    assert evolve(q, 0.5, 1).n_infl == pytest.approx(evolve(q, -0.5, -1).n_infl, rel=1e-6)


def test_starobinsky_slow_roll_observables() -> None:
    pot = Starobinsky()
    phi_end = phi_end_slow_roll(pot, 0.01, 3.0)
    for n in (50.0, 60.0):
        obs = pivot_observables(pot, n, phi_end, 12.0)
        assert obs["n_s"] == pytest.approx(1 - 2 / n, abs=2e-3)
        assert obs["r"] == pytest.approx(12 / n**2, rel=0.2)
    obs = pivot_observables(pot, 55.0, phi_end, 12.0)
    assert obs["A_s"] == pytest.approx(2.1e-9, rel=0.1)
