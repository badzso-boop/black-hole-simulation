use crate::error::SimulationError;
use crate::radiation::emission::EmissionModel;
use crate::types::{InteriorState, Particle, Spectrum};

pub mod evaporation;
pub mod schwarzschild;
pub mod thermodynamics;

// ---------------------------------------------------------------------------
// Trait-ek — OOP interfészek Rust módra
// ---------------------------------------------------------------------------

/// Minden fekete lyuk típus ezt implementálja
pub trait BlackHoleTrait: Send + Sync {
    fn mass(&self) -> f64;
    fn initial_mass(&self) -> f64;
    fn schwarzschild_radius(&self) -> f64;
    fn hawking_temperature(&self) -> Result<f64, SimulationError>;
    /// Bekenstein–Hawking entrópia k_B egységben: S = A/(4ℓ_P²)
    fn bekenstein_entropy(&self) -> f64;
    /// Teljes kisugárzott teljesítmény az emissziós modell szerint (W)
    fn hawking_power(&self) -> Result<f64, SimulationError>;
    /// Teljes élettartam a kezdeti tömegből (s)
    fn evaporation_time(&self) -> f64;
    fn age(&self) -> f64;
    fn emission_model(&self) -> EmissionModel;
    /// Állapot beállítása a párolgási történet egy mintapontjára
    fn set_state(&mut self, mass: f64, age: f64) -> Result<(), SimulationError>;
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
}
