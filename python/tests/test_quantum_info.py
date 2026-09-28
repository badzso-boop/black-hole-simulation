"""A kvantuminformációs toy modell validálása ismert eredményeken."""
from __future__ import annotations

import math
from itertools import pairwise

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from python.information_packet import InformationPacket
from python.quantum_info import (
    emission_times,
    entropy_bits_from_matrix,
    haar_isometry_columns,
    norbi_curve,
    page_average_entropy_bits,
    semiclassical_curve,
    unitary_curve,
)


def test_entropy_of_product_and_bell_states() -> None:
    product = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128)
    assert abs(entropy_bits_from_matrix(product)) < 1e-12
    bell = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128) / math.sqrt(2)
    assert abs(entropy_bits_from_matrix(bell) - 1.0) < 1e-12


def test_page_formula_known_value() -> None:
    # S_{2,2} = 1/3 + 1/4 − 1/4 = 1/3 nat
    assert abs(page_average_entropy_bits(2, 2) - (1 / 3) / math.log(2)) < 1e-12
    # nagy n-re S ≈ ln m − m/(2n)
    m, n = 8, 4096
    approx = (math.log(m) - m / (2 * n)) / math.log(2)
    assert abs(page_average_entropy_bits(m, n) - approx) < 1e-3


def test_page_formula_matches_haar_monte_carlo() -> None:
    rng = np.random.default_rng(1)
    m, n = 4, 16
    samples = []
    for _ in range(400):
        psi = haar_isometry_columns(m * n, 1, rng)[:, 0].reshape(m, n)
        samples.append(entropy_bits_from_matrix(psi))
    assert abs(float(np.mean(samples)) - page_average_entropy_bits(m, n)) < 0.02


def test_haar_columns_are_orthonormal() -> None:
    cols = haar_isometry_columns(64, 4, np.random.default_rng(2))
    assert np.allclose(cols.conj().T @ cols, np.eye(4), atol=1e-12)


def test_unitary_page_curve_turns_over_and_returns_message() -> None:
    curve = unitary_curve(n_bh=9, k_msg=1, rng=np.random.default_rng(3))
    s = [p.s_radiation for p in curve.points]
    mi = [p.mutual_info_ref_radiation for p in curve.points]
    assert curve.page_turnover
    # Page-csúcs a felénél, a Page-átlag közelében
    n_sys = 10
    assert abs(int(np.argmax(s)) - n_sys // 2) <= 1
    assert abs(max(s) - page_average_entropy_bits(2**5, 2**6)) < 0.4
    # a végén a teljes rendszer tiszta a referenciával: S(R) = k, I = 2k
    assert abs(s[-1] - 1.0) < 1e-9
    assert abs(mi[-1] - 2.0) < 1e-9
    # korán nincs információ a sugárzásban
    assert mi[2] < 0.1


def test_hayden_preskill_recovery_soon_after_page_time() -> None:
    n_bh, k = 11, 1
    curve = unitary_curve(n_bh, k, np.random.default_rng(4))
    n_sys = n_bh + k
    j_recover = next(p.emitted for p in curve.points if p.mutual_info_ref_radiation > 2 * k - 0.1)
    # a Page-idő (n/2) után néhány qubittel visszanyerhető
    assert n_sys // 2 < j_recover <= n_sys // 2 + k + 4


def test_semiclassical_hawking_loses_information() -> None:
    curve = semiclassical_curve(n_bh=9, k_msg=1)
    assert [p.s_radiation for p in curve.points] == [float(j) for j in range(11)]
    assert all(p.mutual_info_ref_radiation == 0.0 for p in curve.points)
    assert not curve.page_turnover


def test_norbi_follows_causal_channel() -> None:
    disconnected = norbi_curve(8, 1, causal_channel_exists=False, rng=np.random.default_rng(5))
    assert disconnected.final_mutual_info == 0.0 and not disconnected.page_turnover
    connected = norbi_curve(8, 1, causal_channel_exists=True, rng=np.random.default_rng(5))
    assert abs(connected.final_mutual_info - 2.0) < 1e-9 and connected.page_turnover


@settings(max_examples=40, deadline=None)
@given(n_a=st.integers(1, 4), n_b=st.integers(1, 4), seed=st.integers(0, 2**32 - 1))
def test_entropy_bounds(n_a: int, n_b: int, seed: int) -> None:
    psi = haar_isometry_columns(2 ** (n_a + n_b), 1, np.random.default_rng(seed))[:, 0]
    s = entropy_bits_from_matrix(psi.reshape(2**n_a, 2**n_b))
    assert -1e-9 <= s <= min(n_a, n_b) + 1e-9


def test_emission_times_are_monotonic_and_span_lifetime() -> None:
    # szintetikus idővonal állandó α-val: t_h ∝ M³
    m0, tau = 1e12, 1e17
    masses = m0 * np.exp(-np.linspace(0, 40, 80))
    timeline = [
        {"mass": float(m), "time_to_evaporation": tau * (m / m0) ** 3, "time": tau * (1 - (m / m0) ** 3)}
        for m in masses
    ]
    times = emission_times(timeline, 10)
    rem = [t["time_to_evaporation"] for t in times]
    assert all(b <= a for a, b in pairwise(rem))
    # a j. qubit akkor megy ki, amikor 1 − (M/M0)² = j/n → t_h/τ = (1 − j/n)^(3/2)
    for j in (2, 5, 8):
        assert abs(rem[j] / tau - (1 - j / 10) ** 1.5) < 0.02


def test_information_packet_is_deterministic() -> None:
    a = InformationPacket({"uzenet": "szia", "n": 1})
    b = InformationPacket({"n": 1, "uzenet": "szia"})
    assert a.hash_sha3 == b.hash_sha3 and a.seed == b.seed
    assert InformationPacket({"x": 2}).seed != a.seed
    assert len(a.message_bits(5)) == 5 and set(a.message_bits(5)) <= {0, 1}


def test_config_roundtrip_with_environment() -> None:
    from python.config import Environment, InfallEvent, SimulationConfig

    cfg = SimulationConfig(
        mass=1e12,
        environment=Environment(
            accretion={"type": "constant", "rate": 1.0},
            infall_events=[InfallEvent(time=1.0, mass=2.0, label="x")],
        ),
        max_time=10.0,
    )
    back = SimulationConfig.from_json(cfg.to_json())
    assert back == cfg
    assert "max_time" not in SimulationConfig().to_json()


def test_emission_times_empty_for_non_evaporating_timeline() -> None:
    timeline = [{"mass": 1.0, "time": 0.0}, {"mass": 1.1, "time": 1.0}]
    assert emission_times(timeline, 4) == []
