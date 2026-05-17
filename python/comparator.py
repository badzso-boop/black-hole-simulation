from __future__ import annotations
import numpy as np
from numpy.typing import NDArray


class Comparator:
    """Két szimulációs mód (Standard vs Norbi) összehasonlítása."""

    @staticmethod
    def compare_spectra(
        s1: list[float] | NDArray[np.float64],
        s2: list[float] | NDArray[np.float64],
    ) -> dict:
        """Spektrum-különbség és SNR számítása."""
        a1 = np.asarray(s1, dtype=np.float64)
        a2 = np.asarray(s2, dtype=np.float64)
        delta = a2 - a1
        raw_std = float(np.std(a1))
        # Ha a jel konstans (std=0), a zajszint a jel átlagának 10%-a
        noise_std = raw_std if raw_std > 1e-12 else max(float(np.mean(np.abs(a1))) * 0.1, 1e-10)
        snr = float(np.sqrt(np.mean(delta**2)) / noise_std)
        return {
            "delta_spectrum": delta.tolist(),
            "snr": snr,
            "detectable": snr > 3.0,
            "rms_diff": float(np.sqrt(np.mean(delta**2))),
        }

    @staticmethod
    def compare_information_recovery(
        re_standard: dict,
        re_norbi: dict,
    ) -> dict:
        """Információ visszanyerési javulás."""
        sim_std = float(re_standard.get("similarity", 0.0))
        sim_norbi = float(re_norbi.get("similarity", 0.0))
        improvement = sim_norbi - sim_std
        return {
            "similarity_standard": sim_std,
            "similarity_norbi": sim_norbi,
            "improvement": float(np.clip(improvement, -1.0, 1.0)),
            "significant": abs(improvement) > 0.05,
        }

    @staticmethod
    def compare_interior_evolution(
        standard_trajectory: list[dict],
        norbi_trajectory: list[dict],
    ) -> dict:
        """Belső evolúció összehasonlítása — mikor válnak szét a modellek?"""
        agreed_until = 0
        for i, (s, n) in enumerate(zip(standard_trajectory, norbi_trajectory)):
            s_at_planck = s.get("at_planck_scale", False)
            n_at_planck = n.get("at_planck_scale", False)
            if s_at_planck != n_at_planck:
                agreed_until = i
                break
            agreed_until = i + 1

        return {
            "agree_until_planck": agreed_until > 0,
            "agreement_steps": agreed_until,
            "diverge_at_step": agreed_until if agreed_until < len(standard_trajectory) else -1,
        }
