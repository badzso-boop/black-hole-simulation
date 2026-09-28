#[cfg(test)]
mod model_comparison {
    use crate::constants::{M_MIN_LMY, M_PLANCK, M_SUN};
    use crate::error::SimulationError;
    use crate::run_simulation;
    use crate::types::SimulationConfig;
    use approx::assert_relative_eq;

    fn cfg(mass: f64, norbi: bool) -> SimulationConfig {
        SimulationConfig {
            mass,
            norbi_mode: norbi,
            ..Default::default()
        }
    }

    #[test]
    fn mass_scan_has_no_nan_inf_or_null() {
        for mass in [2.0 * M_PLANCK, 1e-6, 1.0, 5.1e11, 1e12, M_SUN] {
            for norbi in [false, true] {
                let r = run_simulation(&cfg(mass, norbi), serde_json::json!({})).unwrap();
                let txt = serde_json::to_string(&r).unwrap();
                assert!(!txt.contains("null"), "M={mass:e} norbi={norbi}");
                assert!(r.evaporation_complete);
                assert_relative_eq!(r.end_mass, M_MIN_LMY);
            }
        }
    }

    #[test]
    fn exterior_is_identical_because_interior_is_causally_disconnected() {
        let s = run_simulation(&cfg(1e12, false), serde_json::json!({})).unwrap();
        let n = run_simulation(&cfg(1e12, true), serde_json::json!({})).unwrap();
        assert!(!n.causal_channel.exists);
        assert_eq!(s.timeline.len(), n.timeline.len());
        for (a, b) in s.timeline.iter().zip(&n.timeline) {
            assert_eq!(a.spectrum.intensities, b.spectrum.intensities);
        }
        assert!(s.baby_universe.is_empty() && !n.baby_universe.is_empty());
        assert!(s.interior.physics_boundary.is_some() && n.interior.bounce.is_some());
        assert!(n.warnings.iter().any(|w| w.contains("kauzálisan")));
    }

    #[test]
    fn converged_in_step_count() {
        let a = run_simulation(
            &SimulationConfig {
                steps: 100,
                ..cfg(1e12, true)
            },
            serde_json::json!({}),
        )
        .unwrap();
        let b = run_simulation(
            &SimulationConfig {
                steps: 1000,
                ..cfg(1e12, true)
            },
            serde_json::json!({}),
        )
        .unwrap();
        assert_relative_eq!(
            a.timeline.last().unwrap().time,
            b.timeline.last().unwrap().time,
            max_relative = 1e-8
        );
        assert_relative_eq!(
            a.timeline[0].time_to_evaporation,
            b.timeline[0].time_to_evaporation,
            max_relative = 1e-8
        );
    }

    #[test]
    fn energy_ledger_is_consistent() {
        let r = run_simulation(
            &SimulationConfig {
                steps: 2000,
                ..cfg(1e12, false)
            },
            serde_json::json!({}),
        )
        .unwrap();
        assert!(
            r.energy.relative_error < 1e-3,
            "{}",
            r.energy.relative_error
        );
        let r = run_simulation(&cfg(1e12, false), serde_json::json!({})).unwrap();
        assert!(
            r.energy.relative_error < 1e-2,
            "{}",
            r.energy.relative_error
        );
    }

    #[test]
    fn payload_passes_through_and_mass_gap_is_error() {
        let r = run_simulation(&cfg(1e12, true), serde_json::json!({"uzenet": "szia"})).unwrap();
        assert_eq!(r.payload["uzenet"], "szia");
        assert_eq!(r.schema_version, "3.0");
        assert!(matches!(
            run_simulation(&cfg(0.5 * M_PLANCK, true), serde_json::json!({})),
            Err(SimulationError::MassGap { .. })
        ));
    }
}
