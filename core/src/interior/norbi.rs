use crate::black_hole::{BlackHoleTrait, InteriorModel};
use crate::constants::{C, G, RHO_PLANCK, SPECTRUM_BINS};
use crate::error::SimulationError;
use crate::interior::baby_universe::BabyUniverse;
use crate::quantum::lqc::LQCEquation;
use crate::types::{InteriorState, Particle, Spectrum};

/// NorbiInterior — a Norbi-hipotézis szerinti belső modell.
/// Planck-határnál kvantumvisszapattanás → BabyUniverse születik.
/// at_physics_boundary() mindig false — a szimuláció nem áll le.
#[derive(Debug)]
pub struct NorbiInterior {
    pub baby_universe: Option<BabyUniverse>,
    pub bounce_occurred: bool,
    pub current_radius: f64,
    pub current_density: f64,
    pub proper_time: f64,
    lqc: LQCEquation,
}

impl NorbiInterior {
    pub fn new() -> Self {
        Self {
            baby_universe: None,
            bounce_occurred: false,
            current_radius: 0.0,
            current_density: 0.0,
            proper_time: 0.0,
            lqc: LQCEquation::new(),
        }
    }

    /// LQC feltétel: ρ ≥ ρ_Planck → kvantumvisszapattanás
    pub fn quantum_bounce(&mut self, density: f64) -> bool {
        let h_sq = self.lqc.hubble_squared(density).unwrap_or(1.0);
        if h_sq <= 0.0 {
            self.bounce_occurred = true;
            self.baby_universe = Some(BabyUniverse::new(density));
            true
        } else {
            false
        }
    }
}

impl Default for NorbiInterior {
    fn default() -> Self {
        Self::new()
    }
}

impl InteriorModel for NorbiInterior {
    fn simulate_step(
        &mut self,
        particle: &Particle,
        bh: &dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<InteriorState, SimulationError> {
        let r_s = bh.schwarzschild_radius();

        // Geodézia integráció (azonos a standard modellel Planck előtt)
        let dr = -C * dt * (r_s / (self.current_radius + r_s));
        self.current_radius = (self.current_radius + dr).max(0.0);

        if self.current_radius > 0.0 {
            self.current_density =
                particle.mass / (4.0 / 3.0 * std::f64::consts::PI * self.current_radius.powi(3));
        } else {
            self.current_density = RHO_PLANCK * 1.1; // Planck-határt triggereli
        }

        self.proper_time += dt;

        let ricci = 8.0 * std::f64::consts::PI * G * self.current_density / (C * C);
        let at_planck = self.current_density >= RHO_PLANCK * 0.99;

        // Ha elértük a Planck-sűrűséget és még nem volt visszapattanás
        let mut bounce_now = false;
        if at_planck && !self.bounce_occurred {
            bounce_now = self.quantum_bounce(self.current_density);
        }

        // Ha már van bébiuniverzum: beeső anyag energiáját absorbeálja
        if let Some(ref mut bu) = self.baby_universe {
            bu.absorb_energy(particle.energy);
            bu.evolve(dt);
        }

        let baby_state = self.baby_universe.as_ref().map(|bu| bu.to_state());

        let radiation = if let Some(ref bu) = self.baby_universe {
            let intensities = bu.edge_radiation_spectrum();
            let n = intensities.len();
            Spectrum {
                frequencies: (0..n).map(|i| i as f64 * 1e10).collect(),
                intensities,
                temperature: 0.0,
                total_power: 0.0,
                ..Default::default()
            }
        } else {
            Spectrum::default()
        };

        Ok(InteriorState {
            time: bh.age(),
            proper_time: self.proper_time,
            radius: self.current_radius,
            density: self.current_density,
            ricci_scalar: ricci,
            at_planck_scale: at_planck,
            radiation,
            physics_boundary: None, // Norbi nem áll meg
            bounce_occurred: bounce_now || self.bounce_occurred,
            baby_universe: baby_state,
        })
    }

    fn at_physics_boundary(&self) -> bool {
        false // Norbi folytatja a Planck-határ után is
    }

    fn radiation_spectrum(&self) -> Vec<f64> {
        match &self.baby_universe {
            Some(bu) => bu.edge_radiation_spectrum(),
            None => vec![0.0; SPECTRUM_BINS],
        }
    }
}
