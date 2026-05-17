use thiserror::Error;

#[derive(Debug, Error)]
pub enum SimulationError {
    #[error("Fekete lyuk tömege nullára csökkent t={time:.3e}s-nél")]
    MassExhausted { time: f64 },

    #[error("Numerikus divergencia: {field} = {value:.3e} t={time:.3e}s-nél")]
    NumericalDivergence { field: String, value: f64, time: f64 },

    #[error("NaN érték keletkezett: {context}")]
    NaNDetected { context: String },

    #[error("Planck-határ elérve r={radius:.3e}m-nél")]
    PlanckBoundaryReached { radius: f64 },

    #[error("Integrálás nem konvergált {max_steps} lépés után")]
    IntegrationFailed { max_steps: usize },

    #[error("Checkpoint hiba: {0}")]
    CheckpointFailed(String),

    #[error("Érvénytelen fizikai állapot: {reason}")]
    InvalidPhysicalState { reason: String },

    #[error("IO hiba: {0}")]
    Io(#[from] std::io::Error),
}

impl From<rmp_serde::encode::Error> for SimulationError {
    fn from(e: rmp_serde::encode::Error) -> Self {
        SimulationError::CheckpointFailed(e.to_string())
    }
}

impl From<rmp_serde::decode::Error> for SimulationError {
    fn from(e: rmp_serde::decode::Error) -> Self {
        SimulationError::CheckpointFailed(e.to_string())
    }
}

pub fn check_finite(value: f64, context: &str) -> Result<f64, SimulationError> {
    if value.is_nan() || value.is_infinite() {
        Err(SimulationError::NaNDetected {
            context: format!("{context} = {value}"),
        })
    } else {
        Ok(value)
    }
}
