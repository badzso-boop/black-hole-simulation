#[cfg(test)]
mod tests {
    use crate::black_hole::InteriorModel;
    use crate::constants::{C, M_PLANCK, M_SUN};
    use crate::interior::baby_universe::{baby_universe_states, gibbons_hawking_temperature};
    use crate::interior::collapse::OSCollapse;
    use crate::interior::norbi::NorbiInterior;
    use crate::quantum::lqc::LQCEquation;
    use approx::assert_relative_eq;

    fn states(mass: f64) -> Vec<crate::types::BabyUniverseState> {
        let c = OSCollapse::new(mass, 10.0).unwrap();
        let t = NorbiInterior::new().trajectory(&c, 400);
        baby_universe_states(&c, &t)
    }

    #[test]
    fn no_overflow_at_any_mass() {
        // Korábbi hiba: exp(H·dt) túlcsordult minden M > m_P tömegre
        for mass in [1.0 * M_PLANCK, 2.0 * M_PLANCK, 1.0, 1e12, M_SUN, 1e40] {
            let s = states(mass);
            assert!(!s.is_empty(), "M={mass:e}");
            for b in &s {
                for v in [
                    b.scale_factor,
                    b.efolds,
                    b.hubble,
                    b.density,
                    b.radius,
                    b.total_energy,
                    b.gh_temperature,
                    b.interior_luminosity,
                ] {
                    assert!(
                        v.is_finite() && v >= 0.0,
                        "M={mass:e}: nem véges/negatív érték {v}"
                    );
                }
            }
        }
    }

    #[test]
    fn energy_is_conserved_not_created() {
        for mass in [2.0 * M_PLANCK, 1e12, M_SUN] {
            for b in states(mass) {
                assert_relative_eq!(b.total_energy, mass * C * C, max_relative = 1e-9);
            }
        }
    }

    #[test]
    fn expansion_is_monotonic_from_bounce() {
        let s = states(1e12);
        assert!(s[0].scale_factor >= 1.0);
        for w in s.windows(2) {
            assert!(w[1].scale_factor > w[0].scale_factor);
            assert!(w[1].efolds > w[0].efolds);
        }
        let lqc = LQCEquation::new();
        let h_peak = s.iter().map(|b| b.hubble).fold(0.0, f64::max);
        assert!(h_peak <= lqc.max_bounce_hubble_rate() * (1.0 + 1e-12));
        assert!(h_peak > 0.9 * lqc.max_bounce_hubble_rate());
    }

    #[test]
    fn hubble_peak_resolved_on_interior_grid() {
        // A bébiuniverzum a saját óráján fejlődik; a külső lépésszám nem is bemenete.
        let c = OSCollapse::new(1e12, 10.0).unwrap();
        let a = baby_universe_states(&c, &NorbiInterior::new().trajectory(&c, 401));
        let b = baby_universe_states(&c, &NorbiInterior::new().trajectory(&c, 4001));
        let peak =
            |v: &[crate::types::BabyUniverseState]| v.iter().map(|x| x.hubble).fold(0.0, f64::max);
        // a finomabb rács a H_max csúcsot jobban eltalálja; mindkettő ≤ H_max
        let h_max = LQCEquation::new().max_bounce_hubble_rate();
        assert!(peak(&a) <= h_max && peak(&b) <= h_max);
        assert_relative_eq!(peak(&b), h_max, max_relative = 1e-3);
        assert_relative_eq!(peak(&a), h_max, max_relative = 5e-2);
    }

    #[test]
    fn gibbons_hawking_temperature_formula() {
        // T = ħH/(2πk_B); H = 1/t_P-nél ~ T_P/(2π)
        let t = gibbons_hawking_temperature(1.0 / crate::constants::T_PLANCK);
        assert_relative_eq!(
            t,
            crate::constants::TEMP_PLANCK / (2.0 * std::f64::consts::PI),
            max_relative = 1e-12
        );
    }
}
