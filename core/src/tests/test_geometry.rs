#[cfg(test)]
mod tests {
    use crate::constants::{C, G, M_MIN_LMY, M_PLANCK, M_SUN};
    use crate::geometry::{causal_channel, LmyMetric};
    use approx::assert_relative_eq;

    #[test]
    fn no_horizon_below_mass_gap() {
        assert!(LmyMetric::new(0.99 * M_MIN_LMY).horizons().is_none());
        assert!(LmyMetric::new(1.01 * M_MIN_LMY).horizons().is_some());
        assert!(causal_channel(0.5 * M_MIN_LMY).is_err());
    }

    #[test]
    fn horizons_are_roots_and_ordered() {
        for mass in [
            1.05 * M_MIN_LMY,
            2.0 * M_PLANCK,
            10.0 * M_PLANCK,
            1.0,
            1e12,
            M_SUN,
            1e40,
        ] {
            let met = LmyMetric::new(mass);
            let h = met.horizons().unwrap();
            // r_b < r_−: nagy tömegre csak a kioltásmentes δ_b-ből látszik
            assert!(h.bounce_gap_below_inner_horizon > 0.0, "M={mass:e}");
            assert!(
                h.r_bounce <= h.r_minus && h.r_minus < h.r_plus,
                "M={mass:e}"
            );
            // δ_b ≈ r_b·x_b/6 a kis-ε határesetben (x_b = r_b/m)
            let x_b = h.r_bounce / met.m;
            if x_b < 1e-3 {
                assert_relative_eq!(
                    h.bounce_gap_below_inner_horizon,
                    h.r_bounce * x_b / 6.0,
                    max_relative = 1e-2
                );
            }
            // a külső horizont a Schwarzschild-sugárhoz tart
            if mass > 1.0 {
                assert_relative_eq!(h.r_plus, 2.0 * G * mass / (C * C), max_relative = 1e-12);
            }
        }
    }

    #[test]
    fn f_at_bounce_radius_is_exactly_one() {
        // f(r_b) = 1 analitikusan; a direkt képlet csak ott pontos, ahol nincs
        // nagy kioltás (kis tömeg) — itt ellenőrizzük
        for mass in [1.2 * M_MIN_LMY, 3.0 * M_PLANCK, 30.0 * M_PLANCK] {
            let met = LmyMetric::new(mass);
            assert_relative_eq!(met.f(met.bounce_radius()), 1.0, max_relative = 1e-9);
            let h = met.horizons().unwrap();
            assert!(met.f(h.r_minus).abs() < 1e-9 && met.f(h.r_plus).abs() < 1e-9);
            // κ_− a numerikus deriválttal
            let d = 1e-7 * h.r_minus;
            let fp = (met.f(h.r_minus + d) - met.f(h.r_minus - d)) / (2.0 * d);
            assert_relative_eq!(fp.abs() / 2.0, h.kappa_inner, max_relative = 1e-5);
        }
    }

    #[test]
    fn no_causal_channel_to_exterior_at_any_mass() {
        for mass in [1.05 * M_MIN_LMY, 2.0 * M_PLANCK, 1.0, 5.1e11, M_SUN, 1e40] {
            let ch = causal_channel(mass).unwrap();
            assert!(!ch.exists, "M={mass:e}: {}", ch.reason);
            assert!(ch.edge_ray_final_gap > 0.0);
            assert!(ch.edge_ray_final_gap < ch.horizons.bounce_gap_below_inner_horizon);
        }
    }
}
