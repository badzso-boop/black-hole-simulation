"""WP2–WP6: analitikus határesetek és a pontozólap logikája."""
from __future__ import annotations

import math

import pytest

from thesis import cns
from thesis.anisotropy import OMEGA_SIGMA_MAX, bh_shear_fraction, kantowski_sachs_shear
from thesis.curvature import (
    n_tot_min_edge,
    omega_k_today,
    parent_geometry,
)
from thesis.history import max_reheat_temperature_gev, post_inflation
from thesis.inflation import Starobinsky, evolve
from thesis.rotation import a_star_max
from thesis.units import M_SUN, PARTICLE_HORIZON_M, hubble_radius_m


def test_kantowski_sachs_vacuum() -> None:
    k = kantowski_sachs_shear(1e-4)
    assert k["H2"] == pytest.approx(k["sigma2"] / 6, rel=1e-3)  # vákuum: H² = σ²/6
    assert k["sigma2"] * 1e-12 == pytest.approx(3.0, rel=1e-3)  # σ² → 3m/r³
    assert bh_shear_fraction() == pytest.approx(0.2)
    assert bh_shear_fraction() < OMEGA_SIGMA_MAX == pytest.approx(0.5625, abs=1e-3)


def test_shear_isotropic_limit_and_shortening() -> None:
    star = Starobinsky()
    iso = evolve(star, -1.3, 1)
    tiny = evolve(star, -1.3, 1, shear_fraction=1e-12)
    bh = evolve(star, -1.3, 1, shear_fraction=bh_shear_fraction())
    assert tiny.n_infl == pytest.approx(iso.n_infl, abs=1e-4)
    assert bh.n_infl < iso.n_infl


def test_post_inflation_entropy() -> None:
    rho_end = 8.1e-14
    inst = post_inflation(rho_end, max_reheat_temperature_gev(rho_end))
    assert inst.n_reheat == pytest.approx(0.0, abs=1e-6)
    assert inst.n_matter == pytest.approx(math.log(3403))
    late = post_inflation(rho_end, 4e-3)
    # w = 0 felmelegedés: minél később, annál több e-redő utána
    assert late.n_post > inst.n_post


def test_curvature_edge_relation() -> None:
    # a széle-minimumon Ω_K = −(R_H/R_obs)² r_s/R0 — tömegfüggetlen
    for m in (1e12, M_SUN, 1e9 * M_SUN):
        for r0 in (10.0, 1e4):
            geo = parent_geometry(m, r0)
            ok = omega_k_today(geo, n_tot_min_edge(m))
            assert ok == pytest.approx(-(hubble_radius_m() / PARTICLE_HORIZON_M) ** 2 / r0, rel=1e-9)
    assert n_tot_min_edge(5.1e11) == pytest.approx(126.8, abs=0.2)


def test_spin_limit_tiny() -> None:
    amax = a_star_max(M_SUN)
    assert amax["hubble_criterion"] < 1e-12
    assert amax["centrifugal_criterion"] < 1e-12


def test_natural_selection_numbers() -> None:
    d = cns.run()
    assert d["two_heaviest_p_below_2"] == pytest.approx(0.0025, rel=0.02)
    t2012 = next(t for t in d["tests"] if t["prediction"] == "Smolin 2012")
    assert t2012["sigma"] > 3


def test_cmb_baseline_matches_planck() -> None:
    pytest.importorskip("camb")
    from thesis.cmb import n_tot_from_kc, validate_baseline

    v = validate_baseline()
    assert v["max_rel_dev"] < 0.01
    assert v["table_vs_param_max_rel"] < 1e-3
    assert n_tot_from_kc(3.6e-4) == pytest.approx(141.0, abs=0.1)  # Ashtekar+ 2020 / Zhu+ 2017
