#[cfg(test)]
mod tests {
    use approx::assert_relative_eq;
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::radiation::hawking_engine::HawkingEngine;
    use crate::black_hole::RadiationEngine;

    #[test]
    fn test_mass_decreases_over_time() {
        // 1e3 kg-os mini fekete lyuk: rövid idő alatt mérhető tömegvesztés
        let mut bh = SchwarzschildBlackHole::new(1e3).unwrap();
        let engine = HawkingEngine::new();
        let m_before = bh.mass();
        engine.evolve_step(&mut bh, 1e-10).unwrap();
        assert!(bh.mass() < m_before, "A tömegnek csökkenie kell");
    }

    #[test]
    fn test_energy_conservation() {
        let mut bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        let m_before = bh.mass();
        let emitted = engine.evolve_step(&mut bh, 1.0).unwrap();
        let delta_e = (m_before - bh.mass()) * crate::constants::C * crate::constants::C;
        assert_relative_eq!(emitted, delta_e, epsilon = delta_e * 1e-10 + 1e-100);
    }

    #[test]
    fn test_spectrum_peak_matches_temperature() {
        // Pure Planck-spektrum tesztelése greybody nélkül (Wien-törvény pontos)
        let bh = SchwarzschildBlackHole::new(1e10).unwrap();
        let t_h = bh.hawking_temperature().unwrap();
        let engine = HawkingEngine::new();
        let wien_peak = crate::constants::WIEN_FREQ * t_h;

        // Manuálisan keressük a Planck-spektrum csúcsát (greybody nélkül)
        let freq_max = wien_peak * 5.0;
        let df = freq_max / 10_000.0;
        let (peak_freq, _) = (0..10_000usize)
            .map(|i| {
                let f = (i as f64 + 0.5) * df;
                let p = engine.planck_spectrum(f, t_h).unwrap_or(0.0);
                (f, p)
            })
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or((0.0, 0.0));

        // 1% tolerancia (finom grid)
        assert!(
            (peak_freq - wien_peak).abs() < 0.01 * wien_peak,
            "Wien csúcs eltér: {peak_freq:.3e} vs {wien_peak:.3e}"
        );
    }

    #[test]
    fn test_greybody_factor_bounds() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        for freq in [1e10_f64, 1e11, 1e12, 1e13] {
            let gamma = engine.greybody_factor(freq, &bh);
            assert!(
                gamma >= 0.0 && gamma <= 1.0,
                "Greybody faktor {freq:.2e} Hz-en kívül [0,1]: {gamma}"
            );
        }
    }
}
