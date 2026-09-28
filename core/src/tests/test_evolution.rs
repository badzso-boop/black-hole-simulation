#[cfg(test)]
mod tests {
    use crate::black_hole::environment::*;
    use crate::black_hole::evaporation::evaporation_history;
    use crate::black_hole::evolution::{evolve_mass, AGE_OF_UNIVERSE};
    use crate::constants::{C, M_MIN_LMY, M_SUN};
    use crate::radiation::emission::EmissionModel;
    use approx::assert_relative_eq;

    const MG: EmissionModel = EmissionModel::MacGibbon;

    fn ledger_error(h: &crate::black_hole::evolution::MassHistory, m0: f64) -> f64 {
        let e = &h.energy;
        let income =
            e.infall_events + e.background_absorbed + e.accretion_inflow - e.accretion_luminosity;
        let lhs = m0 * C * C + income;
        let rhs = h.end_mass * C * C + e.hawking_radiated;
        (lhs - rhs).abs() / (m0 * C * C + income.max(0.0))
    }

    #[test]
    fn vacuum_reproduces_pure_hawking_evaporation() {
        let h = evolve_mass(MG, &Environment::vacuum(), 1e12, 0.0, M_MIN_LMY, None, 150).unwrap();
        let reference = evaporation_history(MG, 1e12, M_MIN_LMY, 150).unwrap();
        assert!(h.evaporated);
        assert_relative_eq!(
            h.end_time,
            reference.samples.last().unwrap().time,
            max_relative = 1e-9
        );
        assert!(ledger_error(&h, 1e12) < 1e-9);
    }

    #[test]
    fn cmb_is_negligible_for_primordial_black_holes() {
        let vac = evolve_mass(
            MG,
            &Environment::vacuum(),
            5.1e11,
            0.0,
            M_MIN_LMY,
            None,
            100,
        )
        .unwrap();
        let cmb = evolve_mass(
            MG,
            &Environment::default(),
            5.1e11,
            0.0,
            M_MIN_LMY,
            None,
            100,
        )
        .unwrap();
        assert!(cmb.evaporated);
        assert_relative_eq!(cmb.end_time, vac.end_time, max_relative = 1e-9);
        assert!(cmb.energy.background_absorbed < 1e-12 * cmb.energy.hawking_radiated);
    }

    #[test]
    fn solar_mass_hole_grows_in_the_cmb_by_a_tiny_exact_amount() {
        // Ṁ = (P_abs − P_H)/c² állandó (a változás 1e-26 relatív): a CMB-ből
        // elnyelt energia ~ P_abs·t_U — M-ben f64-ben nem is látszana, δ-ban igen
        let h = evolve_mass(MG, &Environment::default(), M_SUN, 0.0, M_MIN_LMY, None, 60).unwrap();
        assert!(!h.evaporated);
        assert_relative_eq!(h.end_time, AGE_OF_UNIVERSE, max_relative = 1e-12);
        let p_abs = background_absorption_power(M_SUN, T_CMB_TODAY);
        assert_relative_eq!(
            h.energy.background_absorbed,
            p_abs * AGE_OF_UNIVERSE,
            max_relative = 1e-8
        );
        assert_relative_eq!(
            h.energy.hawking_radiated,
            MG.power(M_SUN) * AGE_OF_UNIVERSE,
            max_relative = 1e-8
        );
        assert!(h
            .samples
            .iter()
            .all(|s| s.time_to_evaporation.is_none() && s.net_mass_rate > 0.0));
        // ~1e4 kg 13.8 Gyr alatt
        let gained = (h.energy.background_absorbed - h.energy.hawking_radiated) / (C * C);
        assert!((1e3..1e5).contains(&gained), "{gained:e} kg");
    }

    #[test]
    fn constant_accretion_adds_mass_linearly() {
        let env = Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Constant { rate: 1e10 },
            radiative_efficiency: 0.1,
            disk_accretion: false,
            infall_events: vec![],
        };
        let t = 1e10;
        let h = evolve_mass(MG, &env, 1e30, 0.0, M_MIN_LMY, Some(t), 50).unwrap();
        assert_relative_eq!(h.end_mass - 1e30, 0.9 * 1e10 * t, max_relative = 1e-6);
        assert_relative_eq!(
            h.energy.accretion_luminosity,
            0.1 * 1e10 * t * C * C,
            max_relative = 1e-8
        );
        assert!(ledger_error(&h, 1e30) < 1e-9);
    }

    #[test]
    fn eddington_limited_growth_is_exponential_with_salpeter_time() {
        let env = Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Bondi {
                density: 1e-8,
                sound_speed: 1e4,
                eddington_limited: true,
            },
            radiative_efficiency: 0.1,
            disk_accretion: false,
            infall_events: vec![],
        };
        let t_s = salpeter_time(0.1);
        let m0 = 10.0 * M_SUN;
        let h = evolve_mass(MG, &env, m0, 0.0, M_MIN_LMY, Some(5.0 * t_s), 80).unwrap();
        assert_relative_eq!(h.end_mass, m0 * 5f64.exp(), max_relative = 1e-7);
        assert!(ledger_error(&h, m0) < 1e-8);
    }

    #[test]
    fn unlimited_bondi_runaway_is_reported() {
        let env = Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Bondi {
                density: 1e-8,
                sound_speed: 1e4,
                eddington_limited: false,
            },
            radiative_efficiency: 0.0,
            disk_accretion: false,
            infall_events: vec![],
        };
        let err = evolve_mass(
            MG,
            &env,
            10.0 * M_SUN,
            0.0,
            M_MIN_LMY,
            Some(AGE_OF_UNIVERSE),
            50,
        )
        .unwrap_err();
        assert!(err.to_string().contains("divergál"), "{err}");
    }

    #[test]
    fn infall_event_makes_the_hole_heavier_and_longer_lived() {
        let vac = evolve_mass(MG, &Environment::vacuum(), 1e12, 0.0, M_MIN_LMY, None, 100).unwrap();
        let env = Environment {
            infall_events: vec![InfallEvent {
                time: 1e17,
                mass: 1e12,
                label: "aszteroida".into(),
            }],
            ..Environment::vacuum()
        };
        let h = evolve_mass(MG, &env, 1e12, 0.0, M_MIN_LMY, None, 100).unwrap();
        assert!(h.evaporated);
        assert_eq!(h.applied_infalls.len(), 1);
        let a = &h.applied_infalls[0];
        assert_relative_eq!(a.mass_after - a.mass_before, 1e12, max_relative = 1e-12);
        let jump = h
            .samples
            .iter()
            .position(|s| s.after_infall.as_deref() == Some("aszteroida"))
            .unwrap();
        assert_eq!(h.samples[jump].time, 1e17);
        assert!(h.samples[jump].mass > h.samples[jump - 1].mass);
        assert!(h.end_time > vac.end_time);
        assert_relative_eq!(h.energy.infall_events, 1e12 * C * C);
        assert!(ledger_error(&h, 1e12) < 1e-9);
        // a tömeg a beesésen kívül mindenhol csökken (párolgó ág)
        for (i, w) in h.samples.windows(2).enumerate() {
            if i + 1 != jump {
                assert!(w[1].mass < w[0].mass, "i = {i}");
            }
        }
    }

    #[test]
    fn infall_after_evaporation_is_skipped() {
        let env = Environment {
            infall_events: vec![InfallEvent {
                time: 1e30,
                mass: 1.0,
                label: String::new(),
            }],
            ..Environment::vacuum()
        };
        let h = evolve_mass(MG, &env, 1e9, 0.0, M_MIN_LMY, None, 50).unwrap();
        assert!(h.evaporated);
        assert!(h.applied_infalls.is_empty());
        assert_eq!(h.skipped_infalls.len(), 1);
    }

    #[test]
    fn max_time_truncates_evaporation_consistently() {
        let full =
            evolve_mass(MG, &Environment::vacuum(), 1e12, 0.0, M_MIN_LMY, None, 100).unwrap();
        let t_max = 0.5 * full.end_time;
        let h = evolve_mass(
            MG,
            &Environment::vacuum(),
            1e12,
            0.0,
            M_MIN_LMY,
            Some(t_max),
            100,
        )
        .unwrap();
        assert!(!h.evaporated);
        assert_relative_eq!(h.end_time, t_max, max_relative = 1e-12);
        let last = h.samples.last().unwrap();
        assert_relative_eq!(
            last.time_to_evaporation.unwrap(),
            full.end_time - t_max,
            max_relative = 1e-8
        );
        // a félidős tömeg egyezik a teljes futás interpolációjával: M³ ∝ hátralévő idő (közel)
        assert!(last.mass < 1e12 && last.mass > 0.5e12);
    }
}
