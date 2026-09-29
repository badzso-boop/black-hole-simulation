"""WP4b: a forgó szülő — analitikus relációk független ellenőrzése."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.special import sici
from scipy.stats import beta as beta_dist

from thesis import spin
from thesis.lqc import bounce_radius_m
from thesis.units import ALPHA_LMY, M_P, M_SUN, RHO_C, C, G


def test_profile_coefficient_analytic() -> None:
    # egyenletes gömb: C = (1/3)(3/5)(3) = 0.6
    assert spin.profile_coefficient(0.0) == pytest.approx(0.6, rel=1e-6)
    # n = 1: θ = sin ξ/ξ, ξ₁ = π → ⟨r²⟩ = (π² − 6)/π², ⟨r⁻²⟩ = π Si(π)
    si_pi = sici(math.pi)[0]
    expect = (math.pi**2 - 6) / math.pi**2 * (math.pi * si_pi) / 3
    assert spin.profile_coefficient(1.0) == pytest.approx(expect, rel=1e-5)
    # Cauchy–Schwarz: C ≥ 1/3, és a koncentráltabb n = 3 nagyobb, mint az egyenletes
    assert spin.profile_coefficient(3.0) > spin.profile_coefficient(0.0) > 1 / 3


def test_axial_seed_brute_force() -> None:
    """Az analitikus M_s,max-t közvetlenül a j_max² ≤ G M_s r_b(M_s) feltételből ellenőrizzük."""
    c_prof = 0.6
    for mass in (1.0 * M_SUN, 4.3e6 * M_SUN):
        for a in (0.05, 0.5):
            j_mean = a * G * mass / C

            def ok(f: float, m: float = mass, jm: float = j_mean) -> bool:
                j_max = f * jm / c_prof  # F(j) = C j/j̄ inverze
                return j_max**2 <= G * f * m * bounce_radius_m(f * m)

            fs = np.geomspace(1e-60, 1e-20, 4001)
            f_max = max(f for f in fs if ok(float(f)))
            assert f_max * mass / M_P == pytest.approx(spin.seed_mass_max(a, c_prof), rel=0.03)


def test_mass_independent_limit_matches_plan() -> None:
    # a terv első becslése: C = 0.6, N_tot = 130.9 → a*_max ≈ 1.2e-5; a* = 0.998 → 142.2
    assert spin.a_star_max(130.9, 0.6) == pytest.approx(1.2e-5, rel=0.02)
    assert spin.n_tot_needed(0.998, 0.6) == pytest.approx(142.2, abs=0.05)
    assert spin.v_bounce() == pytest.approx(math.sqrt(ALPHA_LMY / 2), rel=1e-12)
    # az él-feltétel és a spin-feltétel a*_max-nál egybeesik
    a = spin.a_star_max(141.0, 1.2)
    assert spin.seed_mass_max(a, 1.2) == pytest.approx(spin.seed_mass_edge(141.0), rel=1e-9)


def test_mass_gap_value() -> None:
    assert spin.M_GAP == pytest.approx(0.83, abs=0.01)  # LMY 2023


def test_kerr_inner_horizon() -> None:
    a = 1e-3
    assert spin.kerr_r_minus(a) == pytest.approx(a * a / 2, rel=1e-3)
    assert spin.kappa_minus(0.7) > 0
    # r_c ≈ 2 r₋ kis spinnél (a terv §1 geometriai azonossága)
    assert (a * a) / spin.kerr_r_minus(a) == pytest.approx(2.0, rel=1e-3)
    assert spin.tidal_distortion(0.9) == pytest.approx(1 / (1 - math.sqrt(0.19)), rel=1e-12)


def test_gw_fit_reproduces_summary() -> None:
    al, be = spin.gw_beta_fit()
    assert beta_dist.ppf(0.9, al, be) == pytest.approx(0.57, abs=1e-6)
    assert (al - 1) / (al + be - 2) == pytest.approx(0.12, abs=1e-9)


def test_heger_spin_from_table() -> None:
    # Heger+ 2005 Table 4: 15 M☉ mag, J = 7.5e47 g cm²/s, 1.47 M☉ → a* ≈ 0.04
    assert spin.heger_a_star(7.5e47, 1.47) == pytest.approx(0.0394, abs=5e-4)


def test_torsion_needs_more_efolds() -> None:
    extra = spin.n_tot_needed(0.5, 1.0, spin.RHO_TORSION) - spin.n_tot_needed(0.5, 1.0)
    assert extra == pytest.approx(0.5 * math.log(spin.RHO_TORSION / RHO_C), rel=1e-12)
    assert spin.RHO_TORSION == pytest.approx(237, rel=0.01)


def test_detachment_density_tiny() -> None:
    # r_c ≫ r_b → a leválási sűrűség sok nagyságrenddel ρ_c alatt
    assert spin.detachment_density_ratio(10 * M_SUN, 0.1) < 1e-60
