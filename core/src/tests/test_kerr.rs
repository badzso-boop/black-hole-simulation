#[cfg(test)]
mod tests {
    use crate::black_hole::kerr::*;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::BlackHoleTrait;
    use crate::constants::{C, G, M_SUN};
    use approx::assert_relative_eq;

    #[test]
    fn reduces_to_schwarzschild_at_zero_spin() {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        let (rp, rm) = horizons(M_SUN, 0.0);
        assert_relative_eq!(rp, bh.schwarzschild_radius(), max_relative = 1e-14);
        assert_eq!(rm, 0.0);
        assert_relative_eq!(
            hawking_temperature(M_SUN, 0.0),
            bh.hawking_temperature().unwrap(),
            max_relative = 1e-14
        );
        assert_relative_eq!(
            entropy(M_SUN, 0.0),
            bh.bekenstein_entropy(),
            max_relative = 1e-14
        );
        assert_eq!(horizon_angular_velocity(M_SUN, 0.0), 0.0);
    }

    #[test]
    fn extremal_limit() {
        // a* → 1: r+ = r− = m, T → 0, A → 8πm² (fele a Schwarzschild-területnek + ...)
        let m = G * M_SUN / (C * C);
        let (rp, rm) = horizons(M_SUN, 1.0);
        assert_relative_eq!(rp, m, max_relative = 1e-14);
        assert_relative_eq!(rm, m, max_relative = 1e-14);
        assert_eq!(hawking_temperature(M_SUN, 1.0), 0.0);
        assert_relative_eq!(
            horizon_area(M_SUN, 1.0) / horizon_area(M_SUN, 0.0),
            0.5,
            max_relative = 1e-14
        );
        // Ω_H(a*=1) = c/(2m)
        assert_relative_eq!(
            horizon_angular_velocity(M_SUN, 1.0),
            C / (2.0 * m),
            max_relative = 1e-14
        );
    }

    #[test]
    fn temperature_decreases_with_spin() {
        let mut prev = f64::INFINITY;
        for a in [0.0, 0.3, 0.6, 0.9, 0.99, 0.999] {
            let t = hawking_temperature(1e12, a);
            assert!(t < prev);
            prev = t;
        }
    }

    #[test]
    fn isco_known_values() {
        // a* = 0: r = 6m, E = √(8/9), L = 2√3; a* = 1: r = m, E = 1/√3
        assert_relative_eq!(isco_radius_m(0.0), 6.0, max_relative = 1e-12);
        let (e0, l0) = isco_energy_momentum(0.0);
        assert_relative_eq!(e0, (8.0f64 / 9.0).sqrt(), max_relative = 1e-12);
        assert_relative_eq!(l0, 2.0 * 3f64.sqrt(), max_relative = 1e-12);
        assert_relative_eq!(isco_radius_m(1.0), 1.0, max_relative = 1e-9);
        assert_relative_eq!(
            isco_energy_momentum(1.0 - 1e-12).0,
            1.0 / 3f64.sqrt(),
            max_relative = 1e-3
        );
        // a* = 0.5: r_isco ≈ 4.233m (BPT)
        assert_relative_eq!(isco_radius_m(0.5), 4.233, max_relative = 1e-3);
    }

    #[test]
    fn radiative_efficiency_novikov_thorne() {
        assert_relative_eq!(radiative_efficiency(0.0), 0.0572, max_relative = 1e-3);
        let e998 = radiative_efficiency(THORNE_SPIN_LIMIT);
        assert!((0.30..0.33).contains(&e998), "{e998}");
    }

    #[test]
    fn accretion_spins_up_to_thorne_limit_only() {
        assert!(accretion_spin_rate(M_SUN, 0.0, 1.0) > 0.0);
        assert!(accretion_spin_rate(M_SUN, 0.9, 1.0) > 0.0);
        assert_eq!(accretion_spin_rate(M_SUN, THORNE_SPIN_LIMIT, 1.0), 0.0);
        assert_eq!(accretion_spin_rate(M_SUN, 0.5, 0.0), 0.0);
        // Bardeen (1970) zárt alakja a* = 0 kezdetből:
        //   a*(M) = √(2/3)·(M0/M)·[4 − √(18M0²/M² − 2)],  M ≤ √6·M0
        // numerikusan (RK4) da*/d ln M = (L − 2aE)/E, összevetve M/M0 = 2-nél
        let rate = |a: f64| {
            let (e, l) = isco_energy_momentum(a);
            (l - 2.0 * a * e) / e
        };
        let n = 20_000;
        let h = 2f64.ln() / n as f64;
        let mut a = 0.0_f64;
        for _ in 0..n {
            let k1 = rate(a);
            let k2 = rate(a + 0.5 * h * k1);
            let k3 = rate(a + 0.5 * h * k2);
            let k4 = rate(a + h * k3);
            a += h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
        }
        let x: f64 = 0.5; // M0/M
        let bardeen = (2.0f64 / 3.0).sqrt() * x * (4.0 - (18.0 * x * x - 2.0).sqrt());
        assert_relative_eq!(a, bardeen, max_relative = 1e-6);
    }

    #[test]
    fn shadow_diameter_formula() {
        // M87*: 6.5e9 M_☉, 16.8 Mpc → ~40 μas (EHT: 42 ± 3 μas gyűrű)
        let mpc = 3.085_677_581e22;
        let theta = shadow_angular_diameter(6.5e9 * M_SUN, 16.8 * mpc);
        let micro_as = theta * 180.0 / std::f64::consts::PI * 3600.0 * 1e6;
        assert!((38.0..41.0).contains(&micro_as), "{micro_as}");
    }
}

#[cfg(test)]
mod evolution_tests {
    use crate::black_hole::environment::*;
    use crate::black_hole::evolution::evolve_mass;
    use crate::black_hole::kerr::*;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::BlackHoleTrait;
    use crate::constants::{M_MIN_LMY, M_SUN};
    use crate::radiation::emission::EmissionModel;
    use approx::assert_relative_eq;

    const MG: EmissionModel = EmissionModel::MacGibbon;

    fn disk_env(rate: f64) -> Environment {
        Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Constant { rate },
            radiative_efficiency: 0.1,
            disk_accretion: true,
            infall_events: vec![],
        }
    }

    #[test]
    fn kerr_black_hole_equals_schwarzschild_at_zero_spin() {
        let k = KerrBlackHole::new(1e12, 0.0, MG).unwrap();
        let s = SchwarzschildBlackHole::new(1e12).unwrap();
        assert_relative_eq!(
            k.hawking_temperature().unwrap(),
            s.hawking_temperature().unwrap(),
            max_relative = 1e-14
        );
        assert_relative_eq!(
            k.hawking_power().unwrap(),
            s.hawking_power().unwrap(),
            max_relative = 1e-14
        );
        assert_relative_eq!(
            k.bekenstein_entropy(),
            s.bekenstein_entropy(),
            max_relative = 1e-14
        );
        assert!(KerrBlackHole::new(1e12, 1.0, MG).is_err());
    }

    #[test]
    fn disk_accretion_follows_bardeen_and_stops_at_thorne_limit() {
        // Hawking és CMB nélkül a tömeg E_isco·Ṁ₀-lal nő, a spin Bardeen szerint.
        // Ṁ₀ = 1e22 kg/s, M0 = 10 M_☉ → a tömeg ~kétszereződése ~2e9 s alatt
        let env = disk_env(1e22);
        let m0 = 10.0 * M_SUN;
        let t = 1.9e9;
        let h = evolve_mass(MG, &env, m0, 0.0, M_MIN_LMY, Some(t), 200).unwrap();
        let ratio = h.end_mass / m0;
        // Bardeen zárt alakja a* = 0-ból, M ≤ √6·M0
        let x = 1.0 / ratio;
        let bardeen = (2.0f64 / 3.0).sqrt() * x * (4.0 - (18.0 * x * x - 2.0).sqrt());
        assert!(ratio > 1.5 && ratio < 6f64.sqrt(), "ratio = {ratio}");
        assert_relative_eq!(
            h.end_spin,
            bardeen.min(THORNE_SPIN_LIMIT),
            max_relative = 1e-4
        );
        // a spin monoton nő, és sosem lépi át a Thorne-határt
        let long = evolve_mass(MG, &env, m0, 0.0, M_MIN_LMY, Some(10.0 * t), 200).unwrap();
        assert!(long
            .samples
            .iter()
            .all(|s| s.spin <= THORNE_SPIN_LIMIT + 1e-9));
        assert_relative_eq!(long.end_spin, THORNE_SPIN_LIMIT, max_relative = 1e-6);
        // a hatásfok a spinnel nő: a végén ~32%
        let last = long.samples.last().unwrap();
        assert!(last.rates.efficiency > 0.30);
    }

    #[test]
    fn spherical_accretion_and_infall_dilute_spin() {
        // gömbszimmetrikus akkréció: J állandó → a*·M² állandó
        let env = Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Constant { rate: 1e22 },
            radiative_efficiency: 0.1,
            disk_accretion: false,
            infall_events: vec![],
        };
        let m0 = 10.0 * M_SUN;
        let h = evolve_mass(MG, &env, m0, 0.8, M_MIN_LMY, Some(1e9), 100).unwrap();
        assert_relative_eq!(
            h.end_spin * h.end_mass.powi(2),
            0.8 * m0 * m0,
            max_relative = 1e-8
        );
        // radiális beesés: ugyanígy
        let env = Environment {
            infall_events: vec![InfallEvent {
                time: 1.0,
                mass: m0,
                label: "iker".into(),
            }],
            ..Environment::vacuum()
        };
        let h = evolve_mass(MG, &env, m0, 0.8, M_MIN_LMY, Some(10.0), 20).unwrap();
        let a = &h.applied_infalls[0];
        assert_relative_eq!(a.spin_after, 0.2, max_relative = 1e-12);
    }
}

#[cfg(test)]
mod emission_tests {
    use crate::black_hole::environment::Environment;
    use crate::black_hole::evolution::evolve_mass;
    use crate::constants::M_MIN_LMY;
    use crate::radiation::emission::{page_kerr_fg, EmissionModel};
    use approx::assert_relative_eq;

    const PG: EmissionModel = EmissionModel::PageGammaGraviton;

    #[test]
    fn page_1976b_enhancement_factors_at_maximal_spin() {
        // Page absztraktja: 13.35 (ν), 107.5 (γ), 26 380 (graviton)
        let ratio = |col| page_kerr_fg(col, 1.0).0 / page_kerr_fg(col, 0.0).0;
        assert_relative_eq!(ratio(1), 13.35, max_relative = 2e-3);
        assert_relative_eq!(ratio(2), 107.5, max_relative = 5e-3);
        assert_relative_eq!(ratio(3), 26_380.0, max_relative = 5e-3);
    }

    #[test]
    fn spin_down_index_h() {
        // Page-készlet (2 ν-íz + γ + graviton): h(0) = g/f − 2 ≈ 7.04
        let (f12, g12) = page_kerr_fg(1, 0.0);
        let (f1, g1) = page_kerr_fg(2, 0.0);
        let (f2, g2) = page_kerr_fg(3, 0.0);
        let h = (2.0 * g12 + g1 + g2) / (2.0 * f12 + f1 + f2) - 2.0;
        assert_relative_eq!(h, 7.04, max_relative = 5e-3);
        // a modellen át (γ + graviton): h(0.5) ≈ 5.99, h(0.9) ≈ 1.72
        assert_relative_eq!(PG.kerr_factors(1e12, 0.5).h, 5.99, max_relative = 2e-2);
        assert_relative_eq!(PG.kerr_factors(1e12, 0.9).h, 1.72, max_relative = 2e-2);
        assert_eq!(PG.kerr_factors(1e12, 0.0).power_ratio, 1.0);
        // a forgás a gravitonok miatt erősen növeli a teljesítményt
        assert!(PG.kerr_factors(1e12, 0.9).power_ratio > 100.0);
    }

    #[test]
    fn rotating_hole_spins_down_before_losing_half_its_mass() {
        // Page 1976b: „a gyorsan forgó fekete lyuk közel nem forgó állapotba
        // lassul, mielőtt tömegének nagy részét leadná" — γ+graviton esetén
        // a* = 0.1 kb. M/M0 ≈ 0.65-nél (a kutatási jelentés integrálása)
        let h = evolve_mass(
            PG,
            &Environment::vacuum(),
            1e12,
            0.9999,
            M_MIN_LMY,
            None,
            400,
        )
        .unwrap();
        assert!(h.evaporated);
        let cross = h.samples.iter().find(|s| s.spin < 0.1).unwrap();
        let ratio = cross.mass / 1e12;
        assert!((0.58..0.72).contains(&ratio), "a* = 0.1 at M/M0 = {ratio}");
        let near_zero = h.samples.iter().find(|s| s.spin < 0.01).unwrap();
        assert!(near_zero.mass / 1e12 > 0.45, "{}", near_zero.mass / 1e12);
        // a spin monoton csökken
        assert!(h.samples.windows(2).all(|w| w[1].spin <= w[0].spin + 1e-12));
    }

    #[test]
    fn rotating_hole_lives_shorter_by_page_factor() {
        // Page 1976b: az élettartam a kezdeti spintől 2.0–2.7-szeres faktorral függ;
        // γ + graviton készletre τ(a*≈1)/τ(0) ≈ 0.38
        let spin = evolve_mass(
            PG,
            &Environment::vacuum(),
            1e12,
            0.9999,
            M_MIN_LMY,
            None,
            400,
        )
        .unwrap();
        let still =
            evolve_mass(PG, &Environment::vacuum(), 1e12, 0.0, M_MIN_LMY, None, 400).unwrap();
        let r = spin.end_time / still.end_time;
        assert!((0.33..0.45).contains(&r), "τ(a*≈1)/τ(0) = {r}");
        assert!(spin.energy.hawking_radiated > 0.0);
    }
}
