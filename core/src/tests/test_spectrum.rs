#[cfg(test)]
mod tests {
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::RadiationEngine;
    use crate::radiation::hawking_engine::HawkingEngine;
    use crate::radiation::spectrum::planck_spectrum;

    #[test]
    fn test_planck_spectrum_zero_at_zero_freq() {
        let val = planck_spectrum(0.0, 1e-8).unwrap();
        assert_eq!(val, 0.0);
    }

    #[test]
    fn test_planck_spectrum_positive_for_valid_input() {
        let val = planck_spectrum(1e10, 1e-8).unwrap();
        assert!(val >= 0.0);
    }

    #[test]
    fn test_spectrum_has_correct_bin_count() {
        let bh = SchwarzschildBlackHole::new(1e10).unwrap();
        let engine = HawkingEngine::new();
        let spectrum = engine.compute_spectrum(&bh).unwrap();
        assert_eq!(spectrum.frequencies.len(), crate::constants::SPECTRUM_BINS);
        assert_eq!(spectrum.intensities.len(), crate::constants::SPECTRUM_BINS);
    }

    #[test]
    fn test_spectrum_temperature_stored_correctly() {
        let bh = SchwarzschildBlackHole::new(1e10).unwrap();
        let engine = HawkingEngine::new();
        let t_h = bh.hawking_temperature().unwrap();
        let spectrum = engine.compute_spectrum(&bh).unwrap();
        assert!((spectrum.temperature - t_h).abs() < 1e-20);
    }

    #[test]
    fn test_spectrum_intensities_non_negative() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        let spectrum = engine.compute_spectrum(&bh).unwrap();
        assert!(spectrum.intensities.iter().all(|&v| v >= 0.0));
    }

    /// Abszolút normálás: π∫B_ν dν = σ_SB·T⁴ (Stefan–Boltzmann).
    /// A korábbi prefaktor 4π²-szer túl nagy volt — ez a teszt azt fogta volna meg.
    #[test]
    fn test_planck_spectrum_integrates_to_stefan_boltzmann() {
        use crate::constants::{C, HBAR, K_B, PI, WIEN_FREQ};
        let t = 5000.0;
        let n = 200_000;
        let nu_max = 30.0 * WIEN_FREQ * t;
        let dnu = nu_max / n as f64;
        let integral: f64 = (0..n)
            .map(|i| planck_spectrum((i as f64 + 0.5) * dnu, t).unwrap() * dnu)
            .sum();
        let sigma = PI * PI * K_B.powi(4) / (60.0 * HBAR.powi(3) * C * C);
        let rel = (PI * integral - sigma * t.powi(4)).abs() / (sigma * t.powi(4));
        assert!(rel < 1e-6, "Stefan–Boltzmann eltérés: {rel:e}");
    }
}
