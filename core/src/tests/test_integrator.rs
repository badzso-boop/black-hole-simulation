#[cfg(test)]
mod tests {
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::time_evolution::integrator::RK45Integrator;
    use crate::types::Particle;

    #[test]
    fn test_integrator_returns_valid_state() {
        let integrator = RK45Integrator::new();
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let particle = Particle::test_particle();
        let state = integrator.integrate_geodesic(&particle, &bh, 1e-30).unwrap();
        assert!(state.radius >= 0.0);
        assert!(!state.radius.is_nan());
        assert!(!state.density.is_nan());
    }

    #[test]
    fn test_integrator_accel_directed_inward() {
        // A gravitációs gyorsulás befelé mutat (negatív dr irány)
        // Elegendő dt-vel a sugár csökken
        let integrator = RK45Integrator::new();
        // Nagy tömegű BH (1e30 kg), részecske r0 = 1e6 m-en
        let bh = SchwarzschildBlackHole::new(1e30).unwrap();
        let particle = Particle {
            angular_momentum: 0.0,
            initial_radius: 1e6,
            ..Particle::test_particle()
        };
        // Nagy dt → érzékelhető elmozdulás
        let state = integrator.integrate_geodesic(&particle, &bh, 1e3).unwrap();
        assert!(state.radius < particle.initial_radius || state.radius == 0.0,
            "Radiális esés: r = {:.3e} >= r0 = {:.3e}", state.radius, particle.initial_radius);
    }
}
