#[cfg(test)]
mod tests {
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::RadiationEngine;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
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
}
