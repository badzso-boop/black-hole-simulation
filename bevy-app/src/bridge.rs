use std::sync::{Arc, Mutex};
use black_hole_core::{SimulationResults, SimulationConfig};

/// Megosztott szimuláció állapot a Bevy és a core/ között
#[derive(Clone)]
pub struct SimulationState {
    pub results: Option<SimulationResults>,
    pub config: SimulationConfig,
    pub running: bool,
    pub step: usize,
}

impl SimulationState {
    pub fn new() -> Self {
        Self {
            results: None,
            config: SimulationConfig::standard(),
            running: false,
            step: 0,
        }
    }

    pub fn black_hole_mass(&self) -> f64 {
        self.results
            .as_ref()
            .and_then(|r| r.timeline.last())
            .map(|t| t.mass)
            .unwrap_or(self.config.internal_dt * 1e15)
    }
}

impl Default for SimulationState {
    fn default() -> Self {
        Self::new()
    }
}

pub type SharedState = Arc<Mutex<SimulationState>>;
