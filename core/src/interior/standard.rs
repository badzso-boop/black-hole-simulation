use crate::black_hole::{BlackHoleTrait, InteriorModel};
use crate::constants::{C, G, RHO_PLANCK, SPECTRUM_BINS};
use crate::error::SimulationError;
use crate::types::{InteriorState, Particle, PhysicsBoundary, Spectrum};

/// StandardInterior — a standard kvantummechanikai modell.
/// A Planck-határon megáll (at_physics_boundary = true).
#[derive(Debug, Clone, Default)]
pub struct StandardInterior {
    pub current_radius: f64,
    pub current_density: f64,
    pub proper_time: f64,
    pub hit_boundary: bool,
}

impl StandardInterior {
    pub fn new() -> Self {
        Self::default()
    }
}

impl InteriorModel for StandardInterior {
    fn simulate_step(
        &mut self,
        particle: &Particle,
        bh: &dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<InteriorState, SimulationError> {
        if self.hit_boundary {
            return Ok(InteriorState {
                at_planck_scale: true,
                physics_boundary: Some(PhysicsBoundary {
                    radius: self.current_radius,
                    density: self.current_density,
                    time: self.proper_time,
                }),
                ..Default::default()
            });
        }

        let r_s = bh.schwarzschild_radius();
        // Egyszerűsített geodézia: a részecske befelé esik
        let dr = -C * dt * (r_s / (self.current_radius + r_s));
        self.current_radius = (self.current_radius + dr).max(0.0);

        // Sűrűség növekszik ahogy összehúzódik: ρ ∝ r⁻³
        if self.current_radius > 0.0 {
            self.current_density = particle.mass / (4.0 / 3.0 * std::f64::consts::PI * self.current_radius.powi(3));
        } else {
            self.current_density = f64::MAX;
        }

        self.proper_time += dt;

        // Ricci-skaláris közelítés: R ∝ G·ρ/c²
        let ricci = 8.0 * std::f64::consts::PI * G * self.current_density / (C * C);
        let at_planck = self.current_density >= RHO_PLANCK * 0.99;

        if at_planck {
            self.hit_boundary = true;
        }

        let physics_boundary = if at_planck {
            Some(PhysicsBoundary {
                radius: self.current_radius,
                density: self.current_density,
                time: self.proper_time,
            })
        } else {
            None
        };

        Ok(InteriorState {
            time: bh.age(),
            proper_time: self.proper_time,
            radius: self.current_radius,
            density: self.current_density,
            ricci_scalar: ricci,
            at_planck_scale: at_planck,
            radiation: Spectrum::default(),
            physics_boundary,
            bounce_occurred: false,
            baby_universe: None,
        })
    }

    fn at_physics_boundary(&self) -> bool {
        self.hit_boundary
    }

    fn radiation_spectrum(&self) -> Vec<f64> {
        vec![0.0; SPECTRUM_BINS]
    }
}
