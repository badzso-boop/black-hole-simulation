use crate::constants::{G, RHO_PLANCK, PI};
use crate::error::{check_finite, SimulationError};

/// LQCEquation — Loop Quantum Cosmology módosított Friedmann-egyenlet.
/// (ȧ/a)² = (8πG/3) · ρ · (1 - ρ/ρ_P)
#[derive(Debug, Clone)]
pub struct LQCEquation;

impl LQCEquation {
    pub fn new() -> Self {
        Self
    }

    /// LQC módosított Hubble-paraméter négyzete
    /// Ha ρ = ρ_P → H² = 0 (visszapattanás pontja)
    /// Ha ρ > ρ_P → H² < 0 (tágulás megindul)
    pub fn hubble_squared(&self, density: f64) -> Result<f64, SimulationError> {
        if density < 0.0 {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Negatív sűrűség: {density}"),
            });
        }
        let h_sq = (8.0 * PI * G / 3.0) * density * (1.0 - density / RHO_PLANCK);
        check_finite(h_sq, "lqc_hubble_squared")
    }

    /// Klasszikus Friedmann-egyenlet (LQC korrekció nélkül)
    /// (ȧ/a)² = (8πG/3) · ρ
    pub fn classical_hubble_squared(&self, density: f64) -> f64 {
        (8.0 * PI * G / 3.0) * density
    }

    /// Igaz ha a visszapattanás feltétele teljesül (H² ≤ 0)
    pub fn bounce_condition_met(&self, density: f64) -> bool {
        self.hubble_squared(density).map(|h| h <= 0.0).unwrap_or(false)
    }

    /// A tágulási sebesség (ȧ = H · a)
    pub fn expansion_velocity(&self, density: f64, scale_factor: f64) -> Result<f64, SimulationError> {
        let h_sq = self.hubble_squared(density)?;
        let h = if h_sq >= 0.0 { h_sq.sqrt() } else { 0.0 };
        Ok(h * scale_factor)
    }
}

impl Default for LQCEquation {
    fn default() -> Self {
        Self::new()
    }
}
