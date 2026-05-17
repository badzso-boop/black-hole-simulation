from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA


class ReverseEngineer:
    """Hash visszafejtési kísérlet a Hawking-sugárzás spektrumából."""

    def __init__(
        self,
        spectrum_data: list[float] | NDArray[np.float64],
        original_hash: str,
    ) -> None:
        self.spectrum = np.asarray(spectrum_data, dtype=np.float64)
        self.original_hash = original_hash
        self._pca_result: dict | None = None
        self._fft_result: dict | None = None

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
        peak_idx = int(np.argmax(magnitudes[1:]) + 1)  # DC komponens kihagyva
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
        # Egyszerűsített: a spektrum domináns frekvenciáját kódolja hash-ként
        peak = self._fft_result["peak_frequency"]  # type: ignore[index]
        seed = int(abs(peak * 1e15)) % (2**32)
        import hashlib
        return hashlib.sha3_256(seed.to_bytes(4, "big")).hexdigest()

    def similarity_score(self) -> float:
        """Bit-egyezési arány az eredeti és a rekonstruált hash között."""
        reconstructed = self.reconstruct_hash()
        orig_bits = bin(int(self.original_hash, 16))[2:].zfill(256)
        rec_bits = bin(int(reconstructed, 16))[2:].zfill(256)
        matches = sum(a == b for a, b in zip(orig_bits, rec_bits))
        return matches / 256.0
