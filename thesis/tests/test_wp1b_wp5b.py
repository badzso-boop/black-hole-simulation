"""WP1b (ACT-kompatibilis potenciál) és WP5b (hibrid LQC-spektrum) — független ellenőrzések."""
from __future__ import annotations

import math

import numpy as np
import pytest

from thesis import lqc_spectrum as lqs
from thesis.inflation import PolyAttractor, phi_end_slow_roll, pivot_observables
from thesis.units import L_P, MPC, RHO_C


def test_poly_attractor_matches_kallosh_linde() -> None:
    # Kallosh & Linde 2022 Eq. 1.5, k = 2, kis μ: n_s = 1 − 3/(2N)
    pot = PolyAttractor(mu=0.02)
    phi_end = phi_end_slow_roll(pot, 1e-4, 50.0)
    for n in (50.0, 60.0):
        assert pivot_observables(pot, n, phi_end, 60.0)["n_s"] == pytest.approx(1 - 1.5 / n, abs=2e-4)


def test_background_matches_paper() -> None:
    bg = lqs.background()
    assert bg["a0"] == pytest.approx((1 + 24 * math.pi * RHO_C * 0.16) ** (1 / 6), rel=1e-12)
    assert bg["eta0"] == pytest.approx(0.35, abs=0.01)  # Guillén+ 2026: η0 ≃ 0.35 (hibrid)
    assert bg["k0"] == pytest.approx(1.0, abs=0.05)  # „k0 ~ 1 Planck-egységben"
    assert math.cosh(bg["alpha"] * bg["eta0"]) == pytest.approx(bg["a0"] ** 2, rel=1e-12)


def test_poschl_teller_exact_scattering() -> None:
    for k in (0.3, 1.0, 3.0):
        assert lqs.pt_numeric_beta2(k) == pytest.approx(lqs.pt_exact_beta2(k), rel=1e-6)


def test_bogoliubov_normalisation_and_limits() -> None:
    for k in (1e-3, 0.1, 1.0, 10.0):
        a, b = lqs.bogoliubov(k)
        assert a * a - b * b == pytest.approx(1.0, abs=1e-6)
    assert lqs.suppression(30.0) > 0.9999  # UV: a ΛCDM-spektrum
    assert lqs.suppression(0.01) < 1e-3  # IR: erős elnyomás
    assert lqs.suppression(100.0) == pytest.approx(1.0, abs=1e-6)


def test_today_mapping() -> None:
    n = 141.0
    k_mpc = 1.0 / (math.exp(n) * L_P / MPC)  # ennél a mai k-nál k_Planck = 1
    assert float(lqs.suppression_today(np.array([k_mpc]), n)[0]) == pytest.approx(lqs.suppression(1.0),
                                                                          rel=1e-3)


def test_cobaya_plugin_reduces_to_lcdm() -> None:
    pytest.importorskip("cobaya")
    from thesis import cobaya_lqc

    if not cobaya_lqc.available():
        pytest.skip("Planck-likelihood adatok nincsenek telepítve")
    d = cobaya_lqc.grid_scan([150.0], cobaya_lqc.LOW_ELL)
    assert d["rows"][0]["dchi2_total"] == pytest.approx(0.0, abs=1e-3)
