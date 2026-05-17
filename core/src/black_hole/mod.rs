use crate::error::SimulationError;
use crate::types::{InteriorState, Particle, Spectrum};

pub mod schwarzschild;
pub mod thermodynamics;
pub mod kerr;

// ---------------------------------------------------------------------------
// Trait-ek — OOP interfészek Rust módra
// ---------------------------------------------------------------------------

/// Minden fekete lyuk típus ezt implementálja
pub trait BlackHoleTrait: Send + Sync {
    fn mass(&self) -> f64;
    fn schwarzschild_radius(&self) -> f64;
    fn hawking_temperature(&self) -> Result<f64, SimulationError>;
    fn bekenstein_entropy(&self) -> f64;
    fn hawking_power(&self) -> Result<f64, SimulationError>;
    fn evaporation_time(&self) -> f64;
    fn update_mass(&mut self, delta_m: f64) -> Result<(), SimulationError>;
    fn age(&self) -> f64;
    fn advance_time(&mut self, dt: f64);
}

/// Belső modell — Standard és Norbi egyaránt implementálja
pub trait InteriorModel: Send + Sync {
    fn simulate_step(
        &mut self,
        particle: &Particle,
        bh: &dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<InteriorState, SimulationError>;

    fn at_physics_boundary(&self) -> bool;
    fn radiation_spectrum(&self) -> Vec<f64>;
}

/// Sugárzási motor
pub trait RadiationEngine: Send + Sync {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError>;
    fn energy_loss_rate(&self, bh: &dyn BlackHoleTrait) -> Result<f64, SimulationError>;
    fn evolve_step(
        &self,
        bh: &mut dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<f64, SimulationError>;
    fn greybody_factor(&self, freq: f64, bh: &dyn BlackHoleTrait) -> f64;
}
