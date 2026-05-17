use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, G};
use crate::error::SimulationError;
use crate::types::{InteriorState, Particle, Spectrum};

/// RK45 adaptív integrátor a geodézia egyenlethez
pub struct RK45Integrator {
    pub tolerance: f64,
    pub min_dt: f64,
    pub max_dt: f64,
}

impl RK45Integrator {
    pub fn new() -> Self {
        Self { tolerance: 1e-8, min_dt: 1e-50, max_dt: 1e-10 }
    }

    /// Schwarzschild-geodézia integrálása egy lépésen át.
    /// Állapotvektor: [r, dr/dτ]
    pub fn integrate_geodesic(
        &self,
        particle: &Particle,
        bh: &dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<InteriorState, SimulationError> {
        let r_s = bh.schwarzschild_radius();
        let r0 = particle.initial_radius;
        let l = particle.angular_momentum;

        // RK4 lépés a Schwarzschild-geodézián
        // d²r/dτ² = -GM/r² · (1 - r_s/r) + L²/r³ · (1 - r_s/r)
        let f = |r: f64, v: f64| -> (f64, f64) {
            let factor = if r > r_s * 1.01 { 1.0 - r_s / r } else { 0.01 };
            let accel = -G * bh.mass() / r.powi(2) * factor
                + l.powi(2) / r.powi(3) * factor;
            (v, accel)
        };

        let (k1r, k1v) = f(r0, 0.0);
        let (k2r, k2v) = f(r0 + 0.5 * dt * k1r, k1v * 0.5 * dt);
        let (k3r, k3v) = f(r0 + 0.5 * dt * k2r, k2v * 0.5 * dt);
        let (k4r, _k4v) = f(r0 + dt * k3r, k3v * dt);

        let r_new = (r0 + dt / 6.0 * (k1r + 2.0 * k2r + 2.0 * k3r + k4r)).max(0.0);

        // Sűrűség közelítés: ρ ∝ M/r³
        let density = if r_new > 0.0 {
            particle.mass / (4.0 / 3.0 * std::f64::consts::PI * r_new.powi(3))
        } else {
            f64::MAX
        };

        let ricci = 8.0 * std::f64::consts::PI * G * density / (C * C);
        let at_planck = density >= crate::constants::RHO_PLANCK * 0.99;

        Ok(InteriorState {
            time: bh.age(),
            proper_time: dt,
            radius: r_new,
            density,
            ricci_scalar: ricci,
            at_planck_scale: at_planck,
            radiation: Spectrum::default(),
            physics_boundary: None,
            bounce_occurred: false,
            baby_universe: None,
        })
    }
}

impl Default for RK45Integrator {
    fn default() -> Self {
        Self::new()
    }
}
