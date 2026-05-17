#[cfg(test)]
mod tests {
    use crate::black_hole::InteriorModel;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::interior::norbi::NorbiInterior;
    use crate::interior::standard::StandardInterior;
    use crate::types::Particle;

    fn test_bh() -> SchwarzschildBlackHole {
        SchwarzschildBlackHole::new(1e15).unwrap()
    }

    #[test]
    fn test_standard_interior_not_boundary_initially() {
        let interior = StandardInterior::new();
        assert!(!interior.at_physics_boundary());
    }

    #[test]
    fn test_norbi_interior_never_boundary() {
        let interior = NorbiInterior::new();
        assert!(!interior.at_physics_boundary());
    }

    #[test]
    fn test_standard_step_returns_state() {
        let mut interior = StandardInterior::new();
        let bh = test_bh();
        let particle = Particle::test_particle();
        let state = interior.simulate_step(&particle, &bh, 1e-30).unwrap();
        assert!(state.radius >= 0.0);
        assert!(state.density >= 0.0);
    }

    #[test]
    fn test_norbi_step_returns_state() {
        let mut interior = NorbiInterior::new();
        let bh = test_bh();
        let particle = Particle::test_particle();
        let state = interior.simulate_step(&particle, &bh, 1e-30).unwrap();
        assert!(state.radius >= 0.0);
        assert!(!interior.at_physics_boundary());
    }
}
