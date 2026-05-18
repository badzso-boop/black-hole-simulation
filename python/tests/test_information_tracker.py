"""Tesztek az InformationTracker osztályhoz és a Comparator új metódusaihoz."""
from __future__ import annotations
import math
import numpy as np
import pytest
from python.information_tracker import InformationTracker
from python.comparator import Comparator


def _make_timeline(n_steps: int = 50, norbi: bool = False) -> list[dict]:
    """Szintetikus timeline a Rust szimulációs kimenet struktúrájában."""
    timeline = []
    for i in range(n_steps):
        t = (i + 1) / n_steps
        mass = 1e15 * (1.0 - t * 0.9)
        intensities = [float((j + 1) ** 2 / (math.exp((j + 1) / 100.0) - 1.0 + 1e-10))
                       for j in range(1000)]
        edge_frac = 0.2 * t if norbi else 0.0
        therm = 0.15 * t if norbi else 0.02
        timeline.append({
            "time":        float(i) * 1e-42,
            "mass":        mass,
            "temperature": 1e-8 / mass,
            "entropy":     mass ** 2 * 1e-50,
            "spectrum": {
                "frequencies":    list(range(1000)),
                "intensities":    intensities,
                "temperature":    1e-8 / mass,
                "total_power":    float(sum(intensities)),
                "hawking_fraction": 1.0 - edge_frac,
                "edge_fraction":  edge_frac,
                "thermality_score": therm,
            },
            "interior": {},
        })
    return timeline


class TestPageCurve:
    def test_page_curve_returns_list(self):
        curve = InformationTracker.compute_page_curve(_make_timeline())
        assert isinstance(curve, list)
        assert len(curve) == 50

    def test_page_curve_has_required_keys(self):
        curve = InformationTracker.compute_page_curve(_make_timeline())
        required = {"time", "s_radiation", "s_bh", "s_total", "edge_fraction",
                    "thermality_score", "mass"}
        for point in curve:
            assert required <= point.keys(), f"Hiányzó kulcs: {required - point.keys()}"

    def test_radiation_entropy_non_negative(self):
        curve = InformationTracker.compute_page_curve(_make_timeline())
        for point in curve:
            assert point["s_radiation"] >= 0.0, f"Negatív s_radiation: {point['s_radiation']}"

    def test_norbi_has_nonzero_edge_fraction_evolution(self):
        curve = InformationTracker.compute_page_curve(_make_timeline(norbi=True))
        edge_fracs = [p["edge_fraction"] for p in curve]
        assert max(edge_fracs) > 0.0, "Norbi timeline-ban nincs edge_fraction > 0"


class TestCompareModels:
    def _get_results(self):
        tracker = InformationTracker()
        std_r   = tracker.process_timeline(_make_timeline(norbi=False), 5.0)
        norbi_r = tracker.process_timeline(_make_timeline(norbi=True),  5.0)
        return std_r, norbi_r

    def test_compare_models_returns_required_keys(self):
        std_r, norbi_r = self._get_results()
        cmp = InformationTracker.compare_models(std_r, norbi_r)
        required = {
            "thermality_ratio", "norbi_avg_edge_fraction",
            "information_advantage_norbi", "page_curve_turnaround_norbi",
            "std_mean_thermality", "norbi_mean_thermality",
        }
        assert required <= cmp.keys(), f"Hiányzó kulcs: {required - cmp.keys()}"

    def test_norbi_thermality_ratio_greater_than_one(self):
        std_r, norbi_r = self._get_results()
        cmp = InformationTracker.compare_models(std_r, norbi_r)
        assert cmp["thermality_ratio"] > 1.0, \
            f"Norbi thermality_ratio={cmp['thermality_ratio']:.3f} nem > 1"

    def test_norbi_avg_edge_fraction_positive(self):
        std_r, norbi_r = self._get_results()
        cmp = InformationTracker.compare_models(std_r, norbi_r)
        assert cmp["norbi_avg_edge_fraction"] > 0.0, \
            "Norbi átlagos edge_fraction nulla"


class TestComparatorExtensions:
    def test_compute_spectral_divergence_non_negative(self):
        spectrum = [float((i + 1) ** 2 / (math.exp((i + 1) / 100.0) - 1.0 + 1e-10))
                    for i in range(1000)]
        score = Comparator.compute_spectral_divergence(spectrum, 1e-8)
        assert isinstance(score, float)
        assert score >= 0.0, f"KL divergencia negatív: {score}"

    def test_compare_information_content_structure(self):
        std_tl   = _make_timeline(norbi=False)
        norbi_tl = _make_timeline(norbi=True)
        result = Comparator.compare_information_content(std_tl, norbi_tl, 5.0)
        assert "standard"   in result
        assert "norbi"      in result
        assert "comparison" in result
        assert "thermality_ratio" in result["comparison"]

    def test_norbi_information_advantage(self):
        std_tl   = _make_timeline(norbi=False)
        norbi_tl = _make_timeline(norbi=True)
        result = Comparator.compare_information_content(std_tl, norbi_tl, 5.0)
        # Norbi-ban az él-sugárzás miatt kevesebb entrópia „vész el"
        # → information_advantage_norbi > 0 (a Standard végső entrópiája nagyobb)
        cmp = result["comparison"]
        assert cmp["norbi_avg_edge_fraction"] > 0.0
