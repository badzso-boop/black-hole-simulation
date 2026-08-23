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

    /// A módosított Friedmann-egyenlet H²(ρ) = (8πG/3)·ρ·(1-ρ/ρ_P) analitikus maximuma.
    /// dH²/dρ = 0 ⟹ 1 - 2ρ/ρ_P = 0 ⟹ ρ_max = ρ_P/2, ahol
    /// H²_max = (8πG/3)·(ρ_P/2)·(1/2) = classical_hubble_squared(ρ_P) / 4.
    ///
    /// Ez a bébiuniverzum visszapattanás utáni inflációs Hubble-rátája (H_inf):
    /// a visszapattanás pillanatában (ρ=ρ_P) H=0, utána a sűrűség csökkenni kezd,
    /// és H a fenti maximumon át tér vissza a klasszikus tágulásba. Ez a maximum
    /// magából a mozgásegyenletből adódik, nem szabadon választott konstans.
    pub fn max_bounce_hubble_rate(&self) -> f64 {
        (self.classical_hubble_squared(RHO_PLANCK) / 4.0).sqrt()
    }
}

impl Default for LQCEquation {
    fn default() -> Self {
        Self::new()
    }
}
