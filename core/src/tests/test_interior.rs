#[cfg(test)]
mod tests {
    use crate::black_hole::InteriorModel;
    use crate::constants::{C, G, M_MIN_LMY, M_PLANCK, M_SUN, RHO_CRIT_LQC};
    use crate::error::SimulationError;
    use crate::interior::collapse::OSCollapse;
    use crate::interior::norbi::NorbiInterior;
    use crate::interior::standard::StandardInterior;
    use crate::types::{CollapsePhase, InteriorKind};
    use approx::assert_relative_eq;

    #[test]
    fn bounce_is_not_at_the_first_step_and_infall_starts_outside() {
        // Korábbi hiba: current_radius = 0 → visszapattanás mindig a 0. lépésben
        for mass in [2.0 * M_PLANCK, 1.0, 1e12, M_SUN] {
            let c = OSCollapse::new(mass, 10.0).unwrap();
            let traj = NorbiInterior::new().trajectory(&c, 200);
            let first = &traj.samples[0];
            assert_eq!(first.phase, CollapsePhase::Infall, "M={mass:e}");
            assert_relative_eq!(first.radius, c.initial_radius, max_relative = 1e-6);
            let bounce_idx = traj.samples.iter().position(|s| s.tau > 0.0).unwrap();
            assert!(bounce_idx > 50, "M={mass:e}: bounce_idx={bounce_idx}");
            // minden fázis előfordul, sorrendben
            let phases: Vec<_> = traj.samples.iter().map(|s| s.phase).collect();
            for p in [
                CollapsePhase::Trapped,
                CollapsePhase::InnerRegion,
                CollapsePhase::PostBounce,
            ] {
                assert!(phases.contains(&p), "M={mass:e}: hiányzó fázis {p:?}");
            }
        }
    }

    #[test]
    fn initial_radius_is_used() {
        let near = OSCollapse::new(1e12, 2.0).unwrap();
        let far = OSCollapse::new(1e12, 100.0).unwrap();
        let t_near = NorbiInterior::new().trajectory(&near, 50).tau_start;
        let t_far = NorbiInterior::new().trajectory(&far, 50).tau_start;
        assert!(t_far < t_near && t_near < 0.0);
        // klasszikus szabadesés: |τ| ∝ R^(3/2)
        assert_relative_eq!(t_far / t_near, 50f64.powf(1.5), max_relative = 1e-6);
    }

    #[test]
    fn density_never_exceeds_critical_and_bounce_radius_matches_lmy() {
        let c = OSCollapse::new(1e12, 10.0).unwrap();
        let traj = NorbiInterior::new().trajectory(&c, 400);
        assert!(traj
            .samples
            .iter()
            .all(|s| s.density <= RHO_CRIT_LQC * (1.0 + 1e-12)));
        let b = traj.bounce.as_ref().unwrap();
        // R(ρ_c) = (3M/4πρ_c)^(1/3) = r_b = (αm/2)^(1/3) — két független képlet
        assert_relative_eq!(
            c.radius_at_density(RHO_CRIT_LQC),
            b.radius,
            max_relative = 1e-10
        );
        assert!(traj
            .samples
            .iter()
            .all(|s| s.radius >= b.radius * (1.0 - 1e-10)));
    }

    #[test]
    fn standard_stops_at_critical_density() {
        let c = OSCollapse::new(1e12, 10.0).unwrap();
        let traj = StandardInterior::new().trajectory(&c, 200);
        assert_eq!(traj.kind, InteriorKind::Standard);
        assert!(traj.bounce.is_none());
        let pb = traj.physics_boundary.as_ref().unwrap();
        assert_relative_eq!(pb.density, RHO_CRIT_LQC);
        let last = traj.samples.last().unwrap();
        assert_relative_eq!(last.density, RHO_CRIT_LQC, max_relative = 1e-9);
        assert!(traj.samples.iter().all(|s| s.tau < 0.0));
    }

    #[test]
    fn horizon_to_end_proper_time_is_4gm_over_3c3() {
        // Klasszikus marginálisan kötött OS: a horizonttól a szingularitásig 4GM/(3c³)
        let m = M_SUN;
        let c = OSCollapse::new(m, 10.0).unwrap();
        let traj = StandardInterior::new().trajectory(&c, 50);
        assert_relative_eq!(
            traj.proper_time_horizon_to_end,
            4.0 * G * m / (3.0 * C.powi(3)),
            max_relative = 1e-6
        );
    }

    #[test]
    fn standard_and_norbi_agree_far_from_bounce() {
        let c = OSCollapse::new(1e12, 10.0).unwrap();
        let s = StandardInterior::new().trajectory(&c, 100);
        let n = NorbiInterior::new().trajectory(&c, 100);
        assert_relative_eq!(
            s.samples[0].density,
            n.samples[0].density,
            max_relative = 1e-12
        );
        assert_relative_eq!(s.tau_start, n.tau_start, max_relative = 1e-12);
    }

    #[test]
    fn mass_gap_and_start_inside_horizon_are_errors() {
        assert!(matches!(
            OSCollapse::new(0.5 * M_MIN_LMY, 10.0),
            Err(SimulationError::MassGap { .. })
        ));
        assert!(OSCollapse::new(1e12, 0.9).is_err());
    }
}
