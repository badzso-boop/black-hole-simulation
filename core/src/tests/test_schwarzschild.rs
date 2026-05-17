#[cfg(test)]
mod tests {
    use approx::assert_relative_eq;
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::constants::M_SUN;

    #[test]
    fn test_schwarzschild_radius_sun() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        assert_relative_eq!(bh.schwarzschild_radius(), 2954.0, epsilon = 5.0);
    }

    #[test]
    fn test_hawking_temperature_sun() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        assert_relative_eq!(bh.hawking_temperature().unwrap(), 6.17e-8, epsilon = 1e-10);
    }

    #[test]
    fn test_bekenstein_entropy_positive() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        assert!(bh.bekenstein_entropy() > 0.0);
    }

    #[test]
    fn test_entropy_scales_with_mass_squared() {
        let bh1 = SchwarzschildBlackHole::new(M_SUN).unwrap();
        let bh2 = SchwarzschildBlackHole::new(2.0 * M_SUN).unwrap();
        let ratio = bh2.bekenstein_entropy() / bh1.bekenstein_entropy();
        assert_relative_eq!(ratio, 4.0, epsilon = 0.001);
    }

    #[test]
    fn test_evaporation_time_cubic_mass() {
        let bh1 = SchwarzschildBlackHole::new(1e10).unwrap();
        let bh2 = SchwarzschildBlackHole::new(2e10).unwrap();
        let ratio = bh2.evaporation_time() / bh1.evaporation_time();
        assert_relative_eq!(ratio, 8.0, epsilon = 0.001);
    }

    #[test]
    fn test_larger_mass_colder() {
        let bh_small = SchwarzschildBlackHole::new(1e10).unwrap();
        let bh_large = SchwarzschildBlackHole::new(1e20).unwrap();
        assert!(
            bh_large.hawking_temperature().unwrap() < bh_small.hawking_temperature().unwrap()
        );
    }
}
