/// A 7 kötelező validációs teszt — minden ismert analitikus eredmény
/// Ha bármelyik megbukik, a fizikai implementációban hiba van.
#[cfg(test)]
mod validation {
    use approx::assert_relative_eq;
    use crate::black_hole::BlackHoleTrait;
    use crate::black_hole::RadiationEngine;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::constants::{M_SUN, RHO_PLANCK, WIEN_FREQ};
    use crate::quantum::island::{IslandFormula, RadiationState};
    use crate::quantum::lqc::LQCEquation;
    use crate::radiation::hawking_engine::HawkingEngine;

    // VALIDÁCIÓ 1: Schwarzschild-sugár [SCH16]
    #[test]
    fn val_01_schwarzschild_radius_sun() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        assert_relative_eq!(bh.schwarzschild_radius(), 2954.0, epsilon = 5.0);
    }

    // VALIDÁCIÓ 2: Hawking-hőmérséklet [HAW74]
    #[test]
    fn val_02_hawking_temperature_sun() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        assert_relative_eq!(bh.hawking_temperature().unwrap(), 6.17e-8, epsilon = 1e-10);
    }

    // VALIDÁCIÓ 3: Elpárlási idő köbös arány [HAW75]
    #[test]
    fn val_03_evaporation_time_cubic_in_mass() {
        let bh1 = SchwarzschildBlackHole::new(1e10).unwrap();
        let bh2 = SchwarzschildBlackHole::new(2e10).unwrap();
        let ratio = bh2.evaporation_time() / bh1.evaporation_time();
        assert_relative_eq!(ratio, 8.0, epsilon = 0.001);
    }

    // VALIDÁCIÓ 4: Wien-törvény — spektrum csúcs [PLA00]
    #[test]
    fn val_04_spectrum_peak_follows_wien_law() {
        // Tiszta Planck-spektrum (greybody nélkül) — a Wien-törvény pontos tesztje
        let bh = SchwarzschildBlackHole::new(1e10).unwrap();
        let t_h = bh.hawking_temperature().unwrap();
        let engine = HawkingEngine::new();
        let wien_peak = WIEN_FREQ * t_h;

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

        assert!(
            (peak_freq - wien_peak).abs() < 0.01 * wien_peak,
            "Wien csúcs eltér: {peak_freq:.3e} vs {wien_peak:.3e}"
        );
    }

    // VALIDÁCIÓ 5: Entrópia négyzetes arány [BEK73]
    #[test]
    fn val_05_entropy_scales_as_mass_squared() {
        let bh1 = SchwarzschildBlackHole::new(M_SUN).unwrap();
        let bh2 = SchwarzschildBlackHole::new(2.0 * M_SUN).unwrap();
        let ratio = bh2.bekenstein_entropy() / bh1.bekenstein_entropy();
        assert_relative_eq!(ratio, 4.0, epsilon = 0.001);
    }

    // VALIDÁCIÓ 6: Page-görbe alakja [PAG93]
    #[test]
    fn val_06_page_curve_rises_then_falls() {
        let bh_template = SchwarzschildBlackHole::new(1e15).unwrap();
        let island = IslandFormula::new();
        let evap_time = bh_template.evaporation_time();

        let mut timeline: Vec<f64> = Vec::new();
        let mut bh = SchwarzschildBlackHole::new(1e15).unwrap();

        let steps = 200;
        let dt = evap_time / steps as f64;

        let engine = HawkingEngine::new();
        for _ in 0..steps {
            let s = island
                .compute_generalized_entropy(bh.age(), &bh, &RadiationState::default())
                .unwrap();
            timeline.push(s);
            if engine.evolve_step(&mut bh, dt).is_err() {
                break;
            }
        }

        let peak_idx = timeline
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .map(|(i, _)| i)
            .unwrap_or(0);

        // A csúcsnak nem a széleken kell lennie
        assert!(
            peak_idx > 0 && peak_idx < timeline.len() - 1,
            "Page-görbe csúcsának a közepén kell lennie: peak_idx={peak_idx}"
        );
    }

    // VALIDÁCIÓ 7: LQC visszapattanás feltétele [ASH06]
    #[test]
    fn val_07_lqc_hubble_zero_at_planck_density() {
        let lqc = LQCEquation::new();
        let h_sq = lqc.hubble_squared(RHO_PLANCK).unwrap();
        assert!(
            h_sq.abs() < 1e-10,
            "Planck-sűrűségnél H² = {h_sq:.3e}, nullának kellene"
        );
    }
}
