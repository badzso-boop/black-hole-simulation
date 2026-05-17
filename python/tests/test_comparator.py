import numpy as np
import pytest
from python.comparator import Comparator


class TestComparator:
    def test_identical_inputs_low_snr(self):
        """Azonos spektrumok: SNR < 1 (nem detektálható különbség)."""
        s = np.ones(1000).tolist()
        result = Comparator.compare_spectra(s, s)
        assert result["snr"] < 1.0
        assert result["detectable"] is False

    def test_detectable_difference(self):
        """100%-os különbség: SNR > 3 (detektálható)."""
        s1 = np.ones(1000).tolist()
        s2 = (np.ones(1000) * 2.0).tolist()
        result = Comparator.compare_spectra(s1, s2)
        assert result["detectable"] is True
        assert result["snr"] > 3.0

    def test_improvement_in_range(self):
        """Javulás [-1, 1] között van."""
        re_std = {"similarity": 0.3}
        re_norbi = {"similarity": 0.5}
        result = Comparator.compare_information_recovery(re_std, re_norbi)
        assert -1.0 <= result["improvement"] <= 1.0
        assert abs(result["improvement"] - 0.2) < 1e-10

    def test_improvement_significant_flag(self):
        """5%-nál nagyobb javulás szignifikáns."""
        result = Comparator.compare_information_recovery(
            {"similarity": 0.4}, {"similarity": 0.5}
        )
        assert result["significant"] is True

    def test_improvement_not_significant_small(self):
        """1%-os javulás nem szignifikáns."""
        result = Comparator.compare_information_recovery(
            {"similarity": 0.40}, {"similarity": 0.41}
        )
        assert result["significant"] is False

    def test_interior_diverges_at_planck(self):
        """Standard megáll, Norbi nem → agree_until_planck = True."""
        std_traj = [
            {"at_planck_scale": False},
            {"at_planck_scale": False},
            {"at_planck_scale": True},
        ]
        norbi_traj = [
            {"at_planck_scale": False},
            {"at_planck_scale": False},
            {"at_planck_scale": False},
        ]
        result = Comparator.compare_interior_evolution(std_traj, norbi_traj)
        assert result["agree_until_planck"] is True
