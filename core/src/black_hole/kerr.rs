// v3 placeholder — Kerr (forgó fekete lyuk) metrika
// Implementálva a v3.0-ban

use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, G};
use crate::error::SimulationError;

#[allow(dead_code)]
pub struct KerrBlackHole {
    mass: f64,
    spin: f64, // a = J/(Mc), dimenzió nélküli [0, 1]
    initial_mass: f64,
    age: f64,
}

impl KerrBlackHole {
    #[allow(dead_code)]
    pub fn new(mass: f64, spin: f64) -> Result<Self, SimulationError> {
        if mass <= 0.0 {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Érvénytelen tömeg: {mass}"),
            });
        }
        if !(0.0..=1.0).contains(&spin) {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Spin kívül [0,1]: {spin}"),
            });
        }
        Ok(Self { mass, spin, initial_mass: mass, age: 0.0 })
    }
}

// v3.0-ban kerül implementálásra
impl BlackHoleTrait for KerrBlackHole {
    fn mass(&self) -> f64 { self.mass }
    fn schwarzschild_radius(&self) -> f64 { 2.0 * G * self.mass / (C * C) }
    fn hawking_temperature(&self) -> Result<f64, SimulationError> {
        Err(SimulationError::InvalidPhysicalState {
            reason: "Kerr nem implementált (v3)".to_string(),
        })
    }
    fn bekenstein_entropy(&self) -> f64 { 0.0 }
    fn hawking_power(&self) -> Result<f64, SimulationError> {
        Err(SimulationError::InvalidPhysicalState {
            reason: "Kerr nem implementált (v3)".to_string(),
        })
    }
    fn evaporation_time(&self) -> f64 { 0.0 }
    fn update_mass(&mut self, delta_m: f64) -> Result<(), SimulationError> {
        self.mass += delta_m;
        Ok(())
    }
    fn age(&self) -> f64 { self.age }
    fn advance_time(&mut self, dt: f64) { self.age += dt; }
}
