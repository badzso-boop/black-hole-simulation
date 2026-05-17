#[cfg(test)]
mod tests {
    use crate::constants::RHO_PLANCK;
    use crate::interior::norbi::NorbiInterior;
    use crate::quantum::lqc::LQCEquation;

    #[test]
    fn test_hubble_zero_at_planck_density() {
        let lqc = LQCEquation::new();
        let h_sq = lqc.hubble_squared(RHO_PLANCK).unwrap();
        assert!(
            h_sq.abs() < 1e-10,
            "Planck-sűrűségnél H² nullának kell lennie, kapott: {h_sq:.3e}"
        );
    }

    #[test]
    fn test_normal_density_recovers_friedmann() {
        let lqc = LQCEquation::new();
        let rho = 1e10_f64;
        let h_sq_lqc = lqc.hubble_squared(rho).unwrap();
        let h_sq_classical = lqc.classical_hubble_squared(rho);
        let rel_diff = (h_sq_lqc - h_sq_classical).abs() / h_sq_classical;
        assert!(
            rel_diff < 1e-6,
            "Kis sűrűségnél LQC ≈ klasszikus Friedmann, eltérés: {rel_diff:.3e}"
        );
    }

    #[test]
    fn test_bounce_triggers_above_planck() {
        let mut interior = NorbiInterior::new();
        let triggered = interior.quantum_bounce(RHO_PLANCK * 1.01);
        assert!(triggered, "Planck-sűrűség felett a visszapattanásnak be kell következni");
    }

    #[test]
    fn test_no_bounce_below_planck() {
        let mut interior = NorbiInterior::new();
        let triggered = interior.quantum_bounce(RHO_PLANCK * 0.5);
        assert!(!triggered, "Planck-sűrűség alatt nem szabad visszapattanás");
    }
}
