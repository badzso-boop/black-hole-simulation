use thiserror::Error;

#[derive(Debug, Error)]
pub enum SimulationError {
    #[error("Fekete lyuk tömege nullára csökkent t={time:.3e}s-nél")]
    MassExhausted { time: f64 },

    #[error("Numerikus divergencia: {field} = {value:.3e} t={time:.3e}s-nél")]
    NumericalDivergence {
        field: String,
        value: f64,
        time: f64,
    },

    #[error("NaN érték keletkezett: {context}")]
    NaNDetected { context: String },

    #[error(
        "Tömegrés: M = {mass:.3e} kg < M_min = {m_min:.3e} kg — a kvantum \
         Oppenheimer–Snyder modellben ilyen tömegnél nem alakul ki horizont (LMY 2023)"
    )]
    MassGap { mass: f64, m_min: f64 },

    #[error("Az integrálás sikertelen: {reason}")]
    IntegrationFailed { reason: String },

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
