use crate::constants::{G, PI, RHO_CRIT_LQC};
use crate::error::{check_finite, SimulationError};

/// LQCEquation — Loop Quantum Cosmology effektív dinamika.
///
/// Módosított Friedmann-egyenlet:   H² = (8πG/3)·ρ·(1 − ρ/ρ_c)
/// Módosított Raychaudhuri (por):   dH/dτ = −4πGρ·(1 − 2ρ/ρ_c)
///
/// ρ_c ≈ 0.409 ρ_Pl (γ = 0.2375) — nem a Planck-sűrűség; ez volt a korábbi hiba.
/// Porra (Oppenheimer–Snyder) az analitikus megoldás, τ a visszapattanástól mérve:
///   ρ(τ) = ρ_c / (1 + τ²/τ_b²),   τ_b = 1/√(6πGρ_c)
///   a(τ) ∝ (1 + τ²/τ_b²)^(1/3),   H(τ) = (2/3)·τ/(τ_b² + τ²)
/// [Kelly–Santacruz–Wilson-Ewing 2020, arXiv:2006.09325; LMY 2023, arXiv:2210.02253]
#[derive(Debug, Clone)]
pub struct LQCEquation {
    rho_c: f64,
}

impl LQCEquation {
    pub fn new() -> Self {
        Self {
            rho_c: RHO_CRIT_LQC,
        }
    }

    pub fn critical_density(&self) -> f64 {
        self.rho_c
    }

    /// H² az effektív Friedmann-egyenletből
    pub fn hubble_squared(&self, density: f64) -> Result<f64, SimulationError> {
        if density < 0.0 {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Negatív sűrűség: {density}"),
            });
        }
        let h_sq = (8.0 * PI * G / 3.0) * density * (1.0 - density / self.rho_c);
        check_finite(h_sq, "lqc_hubble_squared")
    }

    /// Klasszikus Friedmann-egyenlet: H² = (8πG/3)·ρ
    pub fn classical_hubble_squared(&self, density: f64) -> f64 {
        (8.0 * PI * G / 3.0) * density
    }

    /// dH/dτ porra (effektív Raychaudhuri-egyenlet)
    pub fn raychaudhuri_dust(&self, density: f64) -> f64 {
        -4.0 * PI * G * density * (1.0 - 2.0 * density / self.rho_c)
    }

    /// A visszapattanás feltétele: ρ elérte ρ_c-t (itt H² = 0)
    pub fn bounce_condition_met(&self, density: f64) -> bool {
        density >= self.rho_c
    }

    /// H² maximuma ρ = ρ_c/2-nél: H_max = √(2πGρ_c/3) ≈ 0.926/t_P
    pub fn max_bounce_hubble_rate(&self) -> f64 {
        (2.0 * PI * G * self.rho_c / 3.0).sqrt()
    }

    /// A visszapattanás időskálája τ_b = 1/√(6πGρ_c)
    pub fn bounce_timescale(&self) -> f64 {
        1.0 / (6.0 * PI * G * self.rho_c).sqrt()
    }

    /// Por analitikus sűrűsége a visszapattanástól mért τ sajátidőben
    pub fn dust_density(&self, tau: f64) -> f64 {
        let tb = self.bounce_timescale();
        self.rho_c / (1.0 + (tau / tb).powi(2))
    }

    /// Por analitikus Hubble-rátája (τ < 0: összehúzódás, τ > 0: tágulás)
    pub fn dust_hubble(&self, tau: f64) -> f64 {
        let tb = self.bounce_timescale();
        (2.0 / 3.0) * tau / (tb * tb + tau * tau)
    }

    /// Az a τ < 0 sajátidő, amikor a (visszapattanás előtti) sűrűség `density`
    pub fn dust_tau_at_density(&self, density: f64) -> f64 {
        let tb = self.bounce_timescale();
        -tb * (self.rho_c / density - 1.0).max(0.0).sqrt()
    }
}

impl Default for LQCEquation {
    fn default() -> Self {
        Self::new()
    }
}
