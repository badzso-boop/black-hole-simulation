#[cfg(test)]
mod tests {
    use crate::black_hole::environment::*;
    use crate::constants::{C, G, HBAR, K_B, M_MIN_LMY, M_SUN, PI};
    use crate::radiation::emission::EmissionModel;
    use approx::assert_relative_eq;

    const YEAR: f64 = 3.155_76e7;

    fn stefan_boltzmann() -> f64 {
        PI * PI * K_B.powi(4) / (60.0 * HBAR.powi(3) * C * C)
    }

    #[test]
    fn absorption_reaches_geometric_optics_limit_for_large_holes() {
        // M_☉ a 2.7 K-es CMB-ben: λ ~ mm ≪ r_s ~ km → σ = 27π r_g²
        let r_g = G * M_SUN / (C * C);
        let geometric = 27.0 * PI * r_g * r_g * 4.0 * stefan_boltzmann() * T_CMB_TODAY.powi(4);
        let p = background_absorption_power(M_SUN, T_CMB_TODAY);
        assert_relative_eq!(p, geometric, max_relative = 1e-6);
    }

    #[test]
    fn detailed_balance_with_photon_emission() {
        // T = T_H esetén a foton-elnyelés = foton-kibocsátás (ugyanaz a σ(ν))
        for m in [1e10, 1e12, 1e20] {
            let t_h = crate::radiation::emission::hawking_temperature(m);
            let absorbed = background_absorption_power(m, t_h);
            let model = EmissionModel::PageGammaGraviton;
            let emitted_photons = model.power(m) * model.photon_fraction(m);
            assert_relative_eq!(absorbed, emitted_photons, max_relative = 0.03);
        }
    }

    #[test]
    fn small_holes_barely_absorb_the_cmb() {
        // M = 1e12 kg: r_g ~ fm, a CMB hullámhossza mm → erősen elnyomott
        let r_g = G * 1e12 / (C * C);
        let geometric = 27.0 * PI * r_g * r_g * 4.0 * stefan_boltzmann() * T_CMB_TODAY.powi(4);
        assert!(background_absorption_power(1e12, T_CMB_TODAY) < 1e-6 * geometric);
        assert_eq!(background_absorption_power(M_SUN, 0.0), 0.0);
    }

    #[test]
    fn hawking_temperature_equals_cmb_near_moon_mass() {
        // ismert eredmény: T_H = 2.7 K ↔ M ≈ 4.5e22 kg (~ Hold-tömeg)
        assert_relative_eq!(
            mass_with_hawking_temperature(T_CMB_TODAY),
            4.50e22,
            max_relative = 5e-3
        );
    }

    #[test]
    fn cmb_equilibrium_mass() {
        let env = Environment::default();
        let m_t = mass_with_hawking_temperature(T_CMB_TODAY);
        // foton+graviton: a fotonok részletes egyensúlyban vannak T_H = T_CMB-nél, a
        // gravitonok többlet-kibocsátása miatt kicsit hidegebb (nagyobb) M kell
        let eq = env
            .equilibrium_mass(EmissionModel::PageGammaGraviton, 1e15, 1e30)
            .unwrap();
        assert!(
            eq > m_t && eq < 1.3 * m_t,
            "M_eq = {eq:e}, M(T_H=T_CMB) = {m_t:e}"
        );
        // a teljes SM (a legkönnyebb neutrínóval) még több csatornán sugároz → még nagyobb M_eq
        let eq_mg = env
            .equilibrium_mass(EmissionModel::MacGibbon, 1e15, 1e30)
            .unwrap();
        assert!(
            eq_mg > eq && eq_mg < 3.0 * m_t,
            "M_eq(MacGibbon) = {eq_mg:e}"
        );
        // előjelek: alatta párolog, felette nő
        assert!(env.net_mass_rate(EmissionModel::MacGibbon, 0.5 * eq_mg) < 0.0);
        assert!(env.net_mass_rate(EmissionModel::MacGibbon, 2.0 * eq_mg) > 0.0);
        // vákuumban nincs egyensúly
        assert!(Environment::vacuum()
            .equilibrium_mass(EmissionModel::MacGibbon, M_MIN_LMY * 1.01, 1e45)
            .is_none());
    }

    #[test]
    fn massive_neutrinos_switch_off_for_cold_holes() {
        // f(M ≫) = foton 0.12 + graviton 0.014 + ν1 (tömegtelen) 2·0.147 = 0.428
        assert_relative_eq!(EmissionModel::macgibbon_f(1e25), 0.428, max_relative = 1e-3);
        // melegebb lyukra (T_H ≫ 0.05 eV) mindhárom aktív: 1.016
        assert_relative_eq!(EmissionModel::macgibbon_f(1e16), 1.016, max_relative = 1e-3);
    }

    #[test]
    fn bondi_rate_value_and_scaling() {
        // Ṁ = π (GM)² ρ / c_s³ (λ = 1/4); csillagközi közeg, 1 M_☉
        let rho = 1.67e-21;
        let cs: f64 = 1.0e4;
        let expected = PI * (G * M_SUN).powi(2) * rho / cs.powi(3);
        assert_relative_eq!(bondi_rate(M_SUN, rho, cs), expected, max_relative = 1e-12);
        assert_relative_eq!(
            bondi_rate(2.0 * M_SUN, rho, cs) / bondi_rate(M_SUN, rho, cs),
            4.0
        );
        // ~1e-15 M_☉/év nagyságrend
        let msun_per_yr = expected * YEAR / M_SUN;
        assert!((1e-16..1e-14).contains(&msun_per_yr), "{msun_per_yr:e}");
    }

    #[test]
    fn eddington_and_salpeter_times() {
        // L_Edd = 1.26e31 W · (M/M_☉)
        let l_edd = 0.1 * eddington_rate(M_SUN, 0.1) * C * C;
        assert_relative_eq!(l_edd, 1.257e31, max_relative = 5e-3);
        // Eddington-idő σ_T c/(4πG m_p) ≈ 450 Myr; Salpeter-idő ε = 0.1-re ≈ 50 Myr
        let t_edd = salpeter_time(0.5); // ε/(1−ε) = 1
        assert_relative_eq!(t_edd / YEAR, 4.505e8, max_relative = 5e-3);
        assert_relative_eq!(
            salpeter_time(0.1) / YEAR,
            4.505e8 / 9.0,
            max_relative = 5e-3
        );
    }

    #[test]
    fn eddington_limit_caps_bondi() {
        let env = Environment {
            cmb_temperature: 0.0,
            accretion: AccretionModel::Bondi {
                density: 1e-10,
                sound_speed: 1e4,
                eddington_limited: true,
            },
            radiative_efficiency: 0.1,
            disk_accretion: false,
            infall_events: vec![],
        };
        let m = 10.0 * M_SUN;
        assert!(bondi_rate(m, 1e-10, 1e4) > eddington_rate(m, 0.1));
        assert_relative_eq!(env.accretion_inflow(m), eddington_rate(m, 0.1));
    }

    #[test]
    fn invalid_environments_are_rejected() {
        let bad = [
            Environment {
                cmb_temperature: -1.0,
                ..Environment::default()
            },
            Environment {
                radiative_efficiency: 1.0,
                ..Environment::default()
            },
            Environment {
                accretion: AccretionModel::Constant { rate: -1.0 },
                ..Environment::default()
            },
            Environment {
                infall_events: vec![InfallEvent {
                    time: -1.0,
                    mass: 1.0,
                    label: String::new(),
                }],
                ..Environment::default()
            },
        ];
        for env in bad {
            assert!(env.validate().is_err(), "{env:?}");
        }
        assert!(Environment::default().validate().is_ok());
    }
}
