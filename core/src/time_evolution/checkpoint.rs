use std::fs;
use std::path::Path;

use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::SimulationError;
use crate::types::{SimulationResults, SCHEMA_VERSION};

/// Szimulációs eredmény mentése MessagePack formátumban (atomikus írás).
#[derive(Debug, Serialize, Deserialize)]
pub struct Checkpoint {
    pub schema_version: String,
    pub simulation_id: String,
    pub created_at: u64,
    pub results: SimulationResults,
}

impl Checkpoint {
    pub fn new(results: SimulationResults) -> Self {
        Self {
            schema_version: SCHEMA_VERSION.to_string(),
            simulation_id: Uuid::new_v4().to_string(),
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0),
            results,
        }
    }

    /// Atomikus mentés: tmp fájlba ír, majd átnevezi
    pub fn save(&self, path: &Path) -> Result<(), SimulationError> {
        let bytes = rmp_serde::to_vec_named(self)?;
        let tmp = path.with_extension("tmp");
        fs::write(&tmp, &bytes)?;
        fs::rename(&tmp, path)?;
        Ok(())
    }

    pub fn load(path: &Path) -> Result<Self, SimulationError> {
        let bytes = fs::read(path)?;
        let cp: Self = rmp_serde::from_slice(&bytes)?;
        if cp.schema_version != SCHEMA_VERSION {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Ismeretlen checkpoint verzió: {}", cp.schema_version),
            });
        }
        Ok(cp)
    }
}
