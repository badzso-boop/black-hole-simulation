#[cfg(test)]
mod tests {
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
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
        let hist = crate::black_hole::evaporation::evaporation_history(
            crate::radiation::emission::EmissionModel::MacGibbon,
            1e8,
            crate::constants::M_MIN_LMY,
            1000,
        )
        .unwrap();
        assert!(hist
            .samples
            .iter()
            .all(|s| s.mass > 0.0 && s.mass.is_finite()));
    }

    #[test]
    fn test_infinite_mass_returns_error() {
        assert!(SchwarzschildBlackHole::new(f64::INFINITY).is_err());
    }

    #[test]
    fn test_nan_mass_returns_error() {
        let result = SchwarzschildBlackHole::new(f64::NAN);
        assert!(result.is_err(), "NaN tömeg esetén hibát kell adni");
    }

    #[test]
    fn test_zero_frequency_planck_spectrum_is_zero() {
        let val = planck_spectrum(0.0, 1e-8).unwrap();
        assert_eq!(
            val, 0.0,
            "Nulla frekvencián a Planck-spektrum nulla kell legyen"
        );
    }
}
