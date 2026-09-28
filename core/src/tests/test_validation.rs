/// A 7 kötelező validációs teszt — minden ismert analitikus eredmény
/// Ha bármelyik megbukik, a fizikai implementációban hiba van.
#[cfg(test)]
mod validation {
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::BlackHoleTrait;
    use crate::constants::{M_SUN, WIEN_FREQ};
    use crate::quantum::lqc::LQCEquation;
    use crate::radiation::hawking_engine::HawkingEngine;
    use approx::assert_relative_eq;

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
        // A tiszta M³ skálázás csak tömegfüggetlen α-ra igaz (a teljes SM
        // f(M)-mel nem) — ezért itt a tankönyvi foton-fekete-test modell
        use crate::radiation::emission::EmissionModel::PhotonBlackbody;
        let bh1 = SchwarzschildBlackHole::with_emission(1e10, PhotonBlackbody).unwrap();
        let bh2 = SchwarzschildBlackHole::with_emission(2e10, PhotonBlackbody).unwrap();
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

    // VALIDÁCIÓ 7: LQC visszapattanás feltétele [ASH06, LMY23] — ρ_c ≈ 0.41 ρ_Pl-nél
    #[test]
    fn val_07_lqc_hubble_zero_at_critical_density() {
        let lqc = LQCEquation::new();
        let rho_c = crate::constants::RHO_CRIT_LQC;
        let h_sq = lqc.hubble_squared(rho_c).unwrap();
        assert!(
            h_sq.abs() < 1e-6 * lqc.classical_hubble_squared(rho_c),
            "H² = {h_sq:.3e}"
        );
    }
}
