#[cfg(test)]
mod tests {
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::RadiationEngine;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::radiation::hawking_engine::HawkingEngine;
    use crate::radiation::spectrum::planck_spectrum;

    #[test]
    fn test_zero_mass_returns_error() {
        let result = SchwarzschildBlackHole::new(0.0);
        assert!(result.is_err(), "Nulla tömeg esetén hibát kell adni");
    }

    #[test]
    fn test_negative_mass_returns_error() {
        let result = SchwarzschildBlackHole::new(-1e10);
        assert!(result.is_err(), "Negatív tömeg esetén hibát kell adni");
    }

    #[test]
    fn test_mass_never_negative_during_evaporation() {
        let mut bh = SchwarzschildBlackHole::new(1e8).unwrap();
        let engine = HawkingEngine::new();
        for _ in 0..10000 {
            if engine.evolve_step(&mut bh, 1.0).is_err() {
                break;
            }
            assert!(bh.mass() > 0.0, "A tömeg negatívra csökkent!");
        }
    }

    #[test]
    fn test_nan_mass_returns_error() {
        let result = SchwarzschildBlackHole::new(f64::NAN);
        assert!(result.is_err(), "NaN tömeg esetén hibát kell adni");
    }

    #[test]
    fn test_zero_frequency_planck_spectrum_is_zero() {
        let val = planck_spectrum(0.0, 1e-8).unwrap();
        assert_eq!(val, 0.0, "Nulla frekvencián a Planck-spektrum nulla kell legyen");
    }
}
