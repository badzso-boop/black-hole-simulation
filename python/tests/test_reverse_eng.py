import numpy as np
import pytest
from python.reverse_engineer import ReverseEngineer


class TestReverseEngineer:
    def make_spectrum(self, n: int = 100) -> list[float]:
        freqs = np.linspace(0, 1e10, n)
        return (freqs**3 / (np.exp(freqs / 1e9 + 1e-10) - 1 + 1e-10)).tolist()

    def test_pca_returns_components(self):
        """PCA fut és visszaad főkomponenseket."""
        spectrum = self.make_spectrum(100)
        re = ReverseEngineer(spectrum, "a" * 64)
        result = re.run_pca()
        assert "components" in result
        assert "explained_variance" in result

    def test_fft_returns_peak(self):
        """FFT csúcs frekvenciát ad vissza."""
        spectrum = self.make_spectrum(1000)
        re = ReverseEngineer(spectrum, "b" * 64)
        result = re.run_fft()
        assert "peak_frequency" in result
        assert "magnitudes" in result
        assert len(result["magnitudes"]) > 0

    def test_similarity_score_in_range(self):
        """Hasonlóság [0, 1] között van."""
        spectrum = self.make_spectrum(200)
        original_hash = "a" * 64
        re = ReverseEngineer(spectrum, original_hash)
        score = re.similarity_score()
        assert 0.0 <= score <= 1.0

    def test_reconstruct_hash_length(self):
        """A rekonstruált hash 64 hex karakter."""
        re = ReverseEngineer([1.0] * 100, "c" * 64)
        h = re.reconstruct_hash()
        assert len(h) == 64
