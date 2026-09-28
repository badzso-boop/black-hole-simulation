#[cfg(test)]
mod tests {
    use crate::black_hole::evaporation::{
        evaporation_history, lifetime, lifetime_constant_alpha, mass_at_time_constant_alpha,
    };
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::{BlackHoleTrait, RadiationEngine};
    use crate::constants::{C, M_MIN_LMY, WIEN_FREQ};
    use crate::radiation::emission::{EmissionModel, ALPHA_PAGE_GAMMA_GRAVITON};
    use crate::radiation::hawking_engine::HawkingEngine;
    use approx::assert_relative_eq;

    const GYR: f64 = 3.155_76e16;

    #[test]
    fn photon_blackbody_lifetime_matches_textbook_formula() {
        // τ = 5120πG²M³/(ħc⁴) ≈ 8.41e-17 (M/kg)³ s
        let bh =
            SchwarzschildBlackHole::with_emission(1e10, EmissionModel::PhotonBlackbody).unwrap();
        assert_relative_eq!(bh.evaporation_time() / 1e30, 8.41e-17, max_relative = 2e-3);
    }

    #[test]
    fn page_gamma_graviton_lifetime() {
        // Page 2013: τ ≈ 8895 M³ (Planck-egység) = 4.65e-17 (M/kg)³ s
        let t = lifetime(EmissionModel::PageGammaGraviton, 1.0).unwrap();
        assert_relative_eq!(t, 4.65e-17, max_relative = 5e-3);
    }

    #[test]
    fn macgibbon_species_factor_anchors() {
        // f(M ≫ 1e17 g) ≈ 1 (foton + graviton + 3 neutrínó)
        assert_relative_eq!(EmissionModel::macgibbon_f(1e16), 1.016, max_relative = 1e-3);
        // Carr et al. 2010: f(M*) ≈ 1.9 a ma elpárolgó M* ≈ 5.1e11 kg-ra
        let f_star = EmissionModel::macgibbon_f(5.1e11);
        assert!((1.7..2.2).contains(&f_star), "f(M*) = {f_star}");
        // Foton+graviton részhalmaz = Page 2013 α (a normálás konzisztens)
        let alpha_gg =
            EmissionModel::MacGibbon.alpha(1e16) * (0.134 / EmissionModel::macgibbon_f(1e16));
        assert_relative_eq!(alpha_gg, ALPHA_PAGE_GAMMA_GRAVITON, max_relative = 5e-3);
    }

    #[test]
    fn black_hole_evaporating_today_has_universe_age_lifetime() {
        // Carr et al. 2010/2021: M* ≈ 5.1e11 kg párolog el éppen most (13.8 Gyr).
        // A közelítő fajta-küszöbökkel ±30% pontosság várható.
        let t = lifetime(EmissionModel::MacGibbon, 5.1e11).unwrap() / GYR;
        assert!((9.5..18.0).contains(&t), "τ(M*) = {t:.2} Gyr");
    }

    #[test]
    fn dopri_history_matches_analytic_where_alpha_is_constant() {
        // 1e20 → 1e17 kg: T_H < 1e-4 MeV, minden tömeges fajta lekapcsolva,
        // tehát a MacGibbon α itt állandó — a numerikus (Dopri5) ágnak ekkor
        // az analitikus t(M) = (M0³ − M³)/(3Kα) megoldást kell adnia.
        let model = EmissionModel::MacGibbon;
        let m0 = 1e20;
        let alpha = model.alpha(m0);
        let hist = evaporation_history(model, m0, 1e17, 200).unwrap();
        for s in &hist.samples {
            let t = lifetime_constant_alpha(alpha, m0) - lifetime_constant_alpha(alpha, s.mass);
            assert_relative_eq!(s.time, t, max_relative = 1e-8, epsilon = 1e-30);
        }
        // és az analitikus M(t) inverz is konzisztens
        let mid = &hist.samples[10];
        assert_relative_eq!(
            mass_at_time_constant_alpha(alpha, m0, mid.time),
            mid.mass,
            max_relative = 1e-6
        );
    }

    #[test]
    fn evaporation_reaches_mass_gap_and_is_monotonic() {
        let hist = evaporation_history(EmissionModel::MacGibbon, 1e12, M_MIN_LMY, 150).unwrap();
        assert!(hist.reached_end_mass);
        let last = hist.samples.last().unwrap();
        assert_relative_eq!(last.mass, M_MIN_LMY, max_relative = 1e-9);
        for w in hist.samples.windows(2) {
            // a tömeg és a hátralévő idő szigorúan csökken; a kezdettől mért idő
            // a végfázisban f64-felbontás alatt változik, ezért csak nem csökkenő
            assert!(w[1].mass < w[0].mass);
            assert!(w[1].remaining < w[0].remaining);
            assert!(w[1].time >= w[0].time);
        }
        assert_eq!(last.remaining, 0.0);
        let tau = lifetime(EmissionModel::MacGibbon, 1e12).unwrap();
        assert_relative_eq!(last.time, tau, max_relative = 1e-6);
    }

    #[test]
    fn history_is_independent_of_sample_count() {
        // A korábbi fix-dt Euler eredménye a lépésszámtól függött.
        let coarse = evaporation_history(EmissionModel::MacGibbon, 1e9, M_MIN_LMY, 50).unwrap();
        let fine = evaporation_history(EmissionModel::MacGibbon, 1e9, M_MIN_LMY, 5000).unwrap();
        assert_relative_eq!(
            coarse.samples.last().unwrap().time,
            fine.samples.last().unwrap().time,
            max_relative = 1e-8
        );
    }

    #[test]
    fn energy_is_conserved_along_history() {
        // E_rad(t) = ∫P dt  vs  (M0 − M(t))c² — trapéz-integrál a sűrű rácson
        let model = EmissionModel::MacGibbon;
        let hist = evaporation_history(model, 1e11, 1e8, 4000).unwrap();
        let mut e_rad = 0.0;
        for w in hist.samples.windows(2) {
            let p0 = model.power(w[0].mass);
            let p1 = model.power(w[1].mass);
            e_rad += 0.5 * (p0 + p1) * (w[1].time - w[0].time);
        }
        let de = (1e11 - hist.samples.last().unwrap().mass) * C * C;
        assert_relative_eq!(e_rad, de, max_relative = 1e-3);
    }

    #[test]
    fn photon_greybody_fit_consistent_with_page_photon_rate() {
        // A σ(ν)-ból integrált nyers foton-teljesítmény egyezzen az irodalmi
        // foton-rátával (2·0.060·Carr) — erre kalibráltuk az x_c átmenetet.
        let m = 1e12;
        let raw = HawkingEngine::unnormalized_photon_power(m);
        let lit = EmissionModel::PageGammaGraviton.power(m)
            * EmissionModel::PageGammaGraviton.photon_fraction(m);
        let ratio = raw / lit;
        assert!((0.97..1.03).contains(&ratio), "nyers/irodalmi = {ratio:.3}");
    }

    #[test]
    fn spectrum_integrates_to_photon_power() {
        let bh = SchwarzschildBlackHole::new(1e12).unwrap();
        let s = HawkingEngine::new().compute_spectrum(&bh).unwrap();
        let df = s.frequencies[1] - s.frequencies[0];
        let integral: f64 = s.intensities.iter().sum::<f64>() * df;
        assert_relative_eq!(integral, s.photon_power, max_relative = 1e-10);
        assert!(s.photon_power < s.total_power);
    }

    #[test]
    fn greybody_shifts_peak_above_wien_and_is_nonthermal() {
        let bh = SchwarzschildBlackHole::new(1e12).unwrap();
        let s = HawkingEngine::new().compute_spectrum(&bh).unwrap();
        assert!(s.peak_frequency() > WIEN_FREQ * s.temperature);
        // greybody-torzítás: > 0 nem-termalitás információ nélkül is
        assert!(s.spectral_nonthermality > 0.0);
        assert!(s.fit_temperature > s.temperature);
    }

    #[test]
    fn lifetime_scales_cubically_for_constant_alpha() {
        let a = EmissionModel::PhotonBlackbody.alpha(1.0);
        assert_relative_eq!(
            lifetime_constant_alpha(a, 2e10) / lifetime_constant_alpha(a, 1e10),
            8.0,
            max_relative = 1e-12
        );
    }
}
