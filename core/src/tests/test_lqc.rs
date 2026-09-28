#[cfg(test)]
mod tests {
    use crate::constants::{RHO_CRIT_LQC, RHO_PLANCK, T_PLANCK};
    use crate::quantum::lqc::LQCEquation;
    use crate::time_evolution::ode::integrate_to;
    use approx::assert_relative_eq;
    use ode_solvers::{System, Vector2};

    #[test]
    fn hubble_vanishes_at_critical_density_not_planck() {
        let lqc = LQCEquation::new();
        assert!(
            lqc.hubble_squared(RHO_CRIT_LQC).unwrap().abs()
                < 1e-6 * lqc.classical_hubble_squared(RHO_CRIT_LQC)
        );
        // ρ_Pl > ρ_c: ott H² < 0 — a Planck-sűrűséget a por sosem éri el
        assert!(lqc.hubble_squared(RHO_PLANCK).unwrap() < 0.0);
        assert!(lqc.bounce_condition_met(RHO_CRIT_LQC));
        assert!(!lqc.bounce_condition_met(0.5 * RHO_CRIT_LQC));
    }

    #[test]
    fn low_density_recovers_friedmann() {
        let lqc = LQCEquation::new();
        let rho = 1e10;
        let rel = (lqc.hubble_squared(rho).unwrap() - lqc.classical_hubble_squared(rho)).abs()
            / lqc.classical_hubble_squared(rho);
        assert!(rel < 1e-80);
    }

    #[test]
    fn max_hubble_rate_is_0926_over_planck_time() {
        let lqc = LQCEquation::new();
        assert_relative_eq!(
            lqc.max_bounce_hubble_rate() * T_PLANCK,
            0.9260,
            max_relative = 1e-3
        );
        // és ez valóban H² maximuma (ρ = ρ_c/2)
        let h2 = lqc.hubble_squared(RHO_CRIT_LQC / 2.0).unwrap();
        assert_relative_eq!(
            h2.sqrt(),
            lqc.max_bounce_hubble_rate(),
            max_relative = 1e-12
        );
        // és a por-megoldás H(τ) maximuma τ = τ_b-nél ugyanez
        assert_relative_eq!(
            lqc.dust_hubble(lqc.bounce_timescale()),
            lqc.max_bounce_hubble_rate(),
            max_relative = 1e-12
        );
    }

    #[test]
    fn analytic_dust_solution_satisfies_effective_friedmann() {
        let lqc = LQCEquation::new();
        let tb = lqc.bounce_timescale();
        for k in [-30.0, -3.0, -1.0, -0.2, 0.3, 2.0, 50.0] {
            let tau = k * tb;
            let rho = lqc.dust_density(tau);
            let h = lqc.dust_hubble(tau);
            assert_relative_eq!(h * h, lqc.hubble_squared(rho).unwrap(), max_relative = 1e-9);
        }
    }

    /// Dimenziótlan (τ/τ_b, ρ/ρ_c, Hτ_b) porrendszer: ρ' = −3Hρ, H' = −(2/3)ρ(1 − 2ρ)
    #[derive(Clone)]
    struct DustBounce;
    impl System<f64, Vector2<f64>> for DustBounce {
        fn system(&self, _t: f64, y: &Vector2<f64>, dy: &mut Vector2<f64>) {
            dy[0] = -3.0 * y[1] * y[0];
            dy[1] = -(2.0 / 3.0) * y[0] * (1.0 - 2.0 * y[0]);
        }
    }

    #[test]
    fn numeric_bounce_matches_analytic() {
        // A Raychaudhuri-egyenlet numerikus integrálása a visszapattanáson át
        // (Dopri5) egyezzen a ρ(τ) = ρ_c/(1+τ²/τ_b²) analitikus megoldással.
        let rho = |t: f64| 1.0 / (1.0 + t * t);
        let h = |t: f64| (2.0 / 3.0) * t / (1.0 + t * t);
        let mut y = Vector2::new(rho(-20.0), h(-20.0));
        let mut t = -20.0;
        for t_next in [-5.0, -1.0, 0.0, 0.5, 3.0, 20.0] {
            y = integrate_to(DustBounce, t, t_next, y, 1e-14).unwrap();
            t = t_next;
            assert_relative_eq!(y[0], rho(t), max_relative = 1e-8);
            assert!(
                (y[1] - h(t)).abs() < 1e-8,
                "H eltérés τ={t}: {} vs {}",
                y[1],
                h(t)
            );
        }
    }
}
