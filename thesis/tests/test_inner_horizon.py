"""Belső horizont (S4, Level 1): független ellenőrzések (analitikus törvények, publikált számok)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from thesis import inner_horizon as ih
from thesis import ori_model as om


def test_ori_rn_matches_analytic_law() -> None:
    # Carballo-Rubio+ 2021 Fig. 2: M₊ ∝ e^{κ₀v}/v^{p+1} → d ln M/dv = κ₀ − (p+1)/v
    dm, dmd = om.influx_price(10.0, 1.0, 12.0)
    res = om.integrate(om.RN(e=5.0), 10.0, dm, dmd, 1.0, 25.0, r_i=5.0, m_plus_i=11.0)
    g = om.growth_rate(res, 10.0)
    assert g["slope_end"] == pytest.approx(res.kappa0 - 13.0 / g["v_end"], rel=5e-3)
    assert res.kappa0 == pytest.approx(math.sqrt(75) / (10 - math.sqrt(75)) ** 2, rel=1e-10)


def test_ori_constant_quantum_flux_is_pure_exponential() -> None:
    dm, dmd = om.influx_linear(1e-6)
    res = om.integrate(om.RN(e=5.0), 10.0, dm, dmd, 1.0, 30.0, r_i=5.0, m_plus_i=11.0)
    assert om.growth_rate(res, 10.0)["slope_end"] == pytest.approx(res.kappa0, rel=1e-3)


def test_ori_hayward_turns_polynomial() -> None:
    # Carballo-Rubio+ 2021 eq. (20): késői szakaszban M ∝ v^{p+1}
    hw = om.Hayward(ell=0.5)
    dm, dmd = om.influx_price(10.0, 1.0, 12.0)
    res = om.integrate(hw, 10.0, dm, dmd, 1.0, 400.0, r_i=5.0, big_m_i=hw.mass(11.0, 5.0),
                       n_out=4000)
    assert om.growth_rate(res, 50.0)["loglog_slope_end"] == pytest.approx(13.0, rel=0.05)


def test_lmyz_inner_horizon_geometry() -> None:
    row = om.lmyz_crossing_efolds(1e6)
    # nagy tömegre κ₀ → 3m/r₋², és a r₋ – R_b közötti e-redők → ln 2 (tömegfüggetlen)
    assert row["kappa0"] == pytest.approx(row["kappa0_formula_3m_over_r2"], rel=1e-3)
    assert row["efolds_available"] == pytest.approx(math.log(2), abs=2e-3)
    assert row["R_b"] < row["r_minus"]


def test_charge_spin_mapping_and_published_values() -> None:
    assert ih.rn_kappa_minus(0.92) == pytest.approx(1.06, abs=0.005)       # Eilon & Ori 2016
    assert ih.rn_kappa_minus(0.78 / 0.9) / 0.9 == pytest.approx(2.21, abs=0.01)  # Chesler+ 2020
    for a in (0.3, 0.7, 0.9):
        assert ih.rn_kappa_minus(ih.q_for_kappa(ih.kerr_kappa_minus(a))) == \
            pytest.approx(ih.kerr_kappa_minus(a), rel=1e-9)
    # a Kerr fluxus-előjelváltás κ-illesztéssel az RN-éhez esik (kutatás D fejezet)
    assert ih.q_for_kappa(ih.kerr_kappa_minus(0.862)) == pytest.approx(0.962, abs=0.002)


def test_drift_matches_zilberman_levi_ori() -> None:
    d = ih.drift_test()
    assert d["r_v_final"] == pytest.approx(d["expected"], rel=0.01)


def test_race_logic() -> None:
    fast, slow = ih.race(0.97), ih.race(0.01)
    assert fast["passes"] == 1.0 and slow["passes"] == 0.0
    assert slow["v_planck_classical"] < slow["dv_spark"]
    # 10 M☉-nél a kvantum-fluxus sosem ér előbb Planck-görbületet (δ = 0.1 mellett)
    assert all(r["quantum_first"] == 0.0 for r in ih.mass_scan_quantum())


def test_doublenull_static_rn_second_order() -> None:
    e1 = ih.dn_validation_static(0.92, 100)["max_abs_r_error"]
    e2 = ih.dn_validation_static(0.92, 200)["max_abs_r_error"]
    assert e1 / e2 > 3.0


def test_doublenull_mass_inflation_rate() -> None:
    # Brady & Smith 1995: e² = 0.4 → κ₋ = 15.25; a tömeg-infláció ezzel a rátával nő
    g = ih.dn_growth(0.632455532, 400, 0.1)
    assert g["ok"] == 1.0
    assert g["kappa_fit_with_powerlaw"] == pytest.approx(g["kappa_exact"], rel=0.02)
    assert g["kappa_fit"] == pytest.approx(g["kappa_exact"], rel=0.10)
    assert np.isfinite(g["log_m_end"]) and g["log_m_end"] > 30
