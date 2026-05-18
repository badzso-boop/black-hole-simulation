from __future__ import annotations
import math
import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA

# Fizikai állandók (SI)
_HBAR = 1.055e-34
_K_B  = 1.381e-23


class ReverseEngineer:
    """Hash visszafejtési kísérlet a Hawking-sugárzás spektrumából."""

    def __init__(
        self,
        spectrum_data: list[float] | NDArray[np.float64],
        original_hash: str,
        frequencies: list[float] | NDArray[np.float64] | None = None,
        temperature: float = 0.0,
        edge_fraction: float = 0.0,
        thermality_score: float = 0.0,
    ) -> None:
        self.spectrum = np.asarray(spectrum_data, dtype=np.float64)
        self.original_hash = original_hash
        self._frequencies: NDArray[np.float64] | None = (
            np.asarray(frequencies, dtype=np.float64) if frequencies is not None else None
        )
        self._temperature = temperature
        self._edge_fraction = edge_fraction
        self._thermality_score = thermality_score
        self._reference_power: float | None = None
        self._pca_result: dict | None = None
        self._fft_result: dict | None = None

    # ------------------------------------------------------------------
    # Meglévő metódusok (nem változnak — 4 teszt megmarad)
    # ------------------------------------------------------------------

    def run_pca(self) -> dict:
        """Főkomponens-analízis a spektrumon."""
        data = self.spectrum.reshape(-1, 1) if self.spectrum.ndim == 1 else self.spectrum
        if data.shape[0] < 2:
            return {"components": [], "explained_variance": []}
        n_components = min(3, data.shape[0], data.shape[1])
        pca = PCA(n_components=n_components)
        transformed = pca.fit_transform(data)
        self._pca_result = {
            "components": pca.components_.tolist(),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
            "transformed": transformed.tolist(),
        }
        return self._pca_result

    def run_fft(self) -> dict:
        """Fourier-transzformáció a spektrumon."""
        fft_vals = np.fft.rfft(self.spectrum)
        freqs = np.fft.rfftfreq(len(self.spectrum))
        magnitudes = np.abs(fft_vals)
        peak_idx = int(np.argmax(magnitudes[1:]) + 1)
        self._fft_result = {
            "frequencies": freqs.tolist(),
            "magnitudes": magnitudes.tolist(),
            "peak_frequency": float(freqs[peak_idx]),
            "peak_magnitude": float(magnitudes[peak_idx]),
        }
        return self._fft_result

    def reconstruct_hash(self) -> str:
        """Hash visszafejtési kísérlet — a spektrum alapján."""
        if self._fft_result is None:
            self.run_fft()
        peak = self._fft_result["peak_frequency"]  # type: ignore[index]
        seed = int(abs(peak * 1e15)) % (2**32)
        import hashlib
        return hashlib.sha3_256(seed.to_bytes(4, "big")).hexdigest()

    # ------------------------------------------------------------------
    # Új metódusok — fizikailag megalapozott információ-mérők
    # ------------------------------------------------------------------

    def extract_spectral_features(self) -> dict:
        """8 fizikailag értelmes jellemző a spektrumból.

        A Standard Hawking-spektrum szinte tökéletesen termális (Planck-szerű),
        ezért ezek az értékek közel vannak a Planck-referenciához.
        Norbi módban az él-sugárzás eltéríti a spektrumot → eltérő jellemzők.
        """
        s = self.spectrum
        total = float(np.sum(s))
        n = len(s)
        if total <= 0.0 or n == 0:
            return {k: 0.0 for k in (
                "peak_freq_normalized", "spectral_width", "spectral_index",
                "tail_fraction", "edge_fraction", "thermality_score",
                "total_power_normalized", "entropy_per_photon",
            )}

        norm = s / total
        idx = np.arange(n, dtype=float)

        # 1. Normalizált csúcsfrekvencia [0, 1]
        peak_bin = int(np.argmax(s))
        peak_freq_normalized = peak_bin / n

        # 2. Spektrális szélesség (szórás)
        mean_bin = float(np.sum(idx * norm))
        spectral_width = float(np.sqrt(np.sum((idx - mean_bin) ** 2 * norm)))

        # 3. Spektrális index (log-log meredekség — Planck-tól való eltérés)
        log_idx = np.log(idx[1:] + 1.0)
        log_s   = np.log(s[1:] + 1e-300)
        spectral_index = float(np.polyfit(log_idx, log_s, 1)[0])

        # 4. Nagy frekvenciás farok aránya (2× csúcs felett)
        two_peak = 2 * peak_bin
        tail_fraction = float(np.sum(s[two_peak:]) / total) if two_peak < n else 0.0

        # 5–6. Rust metaadatok (ha megadták a konstruktorban)
        edge_fraction    = self._edge_fraction
        thermality_score = self._thermality_score

        # 7. Teljesítmény normalizálva (referenciához képest)
        ref = self._reference_power if self._reference_power else total
        total_power_normalized = total / ref if ref > 0 else 1.0

        # 8. Entrópia fotonállapotonként: -sum(p * log(p))
        mask = norm > 1e-300
        entropy_per_photon = float(-np.sum(norm[mask] * np.log(norm[mask])))

        return {
            "peak_freq_normalized":  peak_freq_normalized,
            "spectral_width":        spectral_width,
            "spectral_index":        spectral_index,
            "tail_fraction":         tail_fraction,
            "edge_fraction":         edge_fraction,
            "thermality_score":      thermality_score,
            "total_power_normalized": total_power_normalized,
            "entropy_per_photon":    entropy_per_photon,
        }

    @staticmethod
    def compute_thermality_score(
        spectrum: list[float] | NDArray[np.float64],
        temperature: float,
        frequencies: list[float] | NDArray[np.float64] | None = None,
    ) -> float:
        """KL divergencia a spektrum és a legjobb Planck-illesztés között.

        thermality_score = KL(P || Q)
        ahol P = tényleges normalizált spektrum, Q = Planck(T) normalizálva.
        0 = tökéletesen termális, > 0 = nem-termális komponens van.
        """
        s = np.asarray(spectrum, dtype=np.float64)
        total = float(np.sum(s))
        if total <= 0.0 or temperature <= 0.0:
            return 0.0

        p = s / total
        n = len(s)

        if frequencies is not None:
            f = np.asarray(frequencies, dtype=np.float64)
        else:
            f = np.arange(1, n + 1, dtype=float)

        # Planck-spektrum a megadott hőmérsékleten
        x = _HBAR * 2.0 * math.pi * f / (_K_B * temperature)
        x_clamped = np.clip(x, 0.0, 700.0)
        planck_raw = f ** 3 / (np.exp(x_clamped) - 1.0 + 1e-300)
        sum_q = float(np.sum(planck_raw))
        if sum_q <= 0.0:
            return 0.0
        q = planck_raw / sum_q

        # KL divergencia
        mask = p > 1e-300
        kl = float(np.sum(p[mask] * np.log(p[mask] / q[mask].clip(1e-300))))
        return max(0.0, kl)

    def estimate_information_content(self) -> dict:
        """Visszanyerhető bitek becslése a nem-termális komponensből.

        Fizikai alap:
        - Termális spektrum → maximális entrópia → 0% info visszanyerhető
        - Él-sugárzás komponens → nem-termális → részleges info megőrzés
        - recovered_bits_edge = edge_fraction * log2(N_bins)
        - thermality_capacity = (1 - exp(-thermality)) * log2(N_bins)
        """
        features = self.extract_spectral_features()
        thermality = features["thermality_score"]
        edge_frac  = features["edge_fraction"]

        max_bits = float(np.log2(max(len(self.spectrum), 1)))
        recovered_bits_edge = edge_frac * max_bits
        thermality_capacity = (1.0 - math.exp(-thermality)) * max_bits
        recovery_ratio = max(recovered_bits_edge, thermality_capacity) / max_bits if max_bits > 0 else 0.0

        return {
            "max_possible_bits":        max_bits,
            "recovered_bits_edge":      recovered_bits_edge,
            "thermality_capacity":      thermality_capacity,
            "information_recovery_ratio": float(np.clip(recovery_ratio, 0.0, 1.0)),
        }

    def similarity_score(self) -> float:
        """Fizikailag megalapozott hasonlóság [0, 1].

        Nem hash-bit összehasonlítás (az értelmetlen volt), hanem:
        a spektrum nem-termális komponensének erőssége.
        - Standard: ~0 (tökéletesen termális = teljes info-veszteség)
        - Norbi: > 0 (él-komponens = részleges info megőrzés)
        """
        features = self.extract_spectral_features()
        edge_signal      = float(np.clip(features["edge_fraction"], 0.0, 1.0))
        thermality_signal = float(np.clip(features["thermality_score"], 0.0, 1.0))
        raw = 0.5 * edge_signal + 0.5 * thermality_signal
        return float(np.clip(raw, 0.0, 1.0))
