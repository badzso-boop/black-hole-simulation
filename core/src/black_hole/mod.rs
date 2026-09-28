use crate::error::SimulationError;
use crate::interior::collapse::OSCollapse;
use crate::radiation::emission::EmissionModel;
use crate::types::{InteriorKind, InteriorTrajectory, Spectrum};

pub mod environment;
pub mod evaporation;
pub mod evolution;
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

/// Belső modell — Standard és Norbi egyaránt implementálja.
/// A belső dinamika saját ideje (τ) független a külső párolgási időtől.
pub trait InteriorModel: Send + Sync {
    fn kind(&self) -> InteriorKind;
    /// Folytatódik-e a leírás a kritikus sűrűségen túl
    fn continues_through_bounce(&self) -> bool;
    fn trajectory(&self, collapse: &OSCollapse, n_samples: usize) -> InteriorTrajectory {
        collapse.trajectory(self.kind(), n_samples)
    }
}

/// Sugárzási motor
pub trait RadiationEngine: Send + Sync {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError>;
    fn energy_loss_rate(&self, bh: &dyn BlackHoleTrait) -> Result<f64, SimulationError>;
}
