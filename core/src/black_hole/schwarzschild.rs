use crate::black_hole::evaporation;
use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, G, L_P, PI};
use crate::error::{check_finite, SimulationError};
use crate::radiation::emission::{self, EmissionModel};

#[derive(Debug, Clone)]
pub struct SchwarzschildBlackHole {
    mass: f64,
    initial_mass: f64,
    age: f64,
    emission: EmissionModel,
    lifetime: f64,
}

impl SchwarzschildBlackHole {
    /// Alapértelmezett emissziós modell: MacGibbon (összes SM részecske)
    pub fn new(mass: f64) -> Result<Self, SimulationError> {
        Self::with_emission(mass, EmissionModel::default())
    }

    pub fn with_emission(mass: f64, emission: EmissionModel) -> Result<Self, SimulationError> {
        if !(mass.is_finite() && mass > 0.0) {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Érvénytelen tömeg: {mass}"),
            });
        }
        let lifetime = evaporation::lifetime(emission, mass)?;
        Ok(Self {
            mass,
            initial_mass: mass,
            age: 0.0,
            emission,
            lifetime,
        })
    }
}

impl BlackHoleTrait for SchwarzschildBlackHole {
    fn mass(&self) -> f64 {
        self.mass
    }

    fn initial_mass(&self) -> f64 {
        self.initial_mass
    }

    fn schwarzschild_radius(&self) -> f64 {
        // r_s = 2GM/c²
        2.0 * G * self.mass / (C * C)
    }

    fn hawking_temperature(&self) -> Result<f64, SimulationError> {
        // T_H = ℏc³ / (8πGMk_B)
        check_finite(
            emission::hawking_temperature(self.mass),
            "hawking_temperature",
        )
    }

    fn bekenstein_entropy(&self) -> f64 {
        // S/k_B = A / (4 l_P²), ahol A = 4π r_s²
        let r_s = self.schwarzschild_radius();
        4.0 * PI * r_s.powi(2) / (4.0 * L_P.powi(2))
    }

    fn hawking_power(&self) -> Result<f64, SimulationError> {
        check_finite(self.emission.power(self.mass), "hawking_power")
    }

    fn evaporation_time(&self) -> f64 {
        self.lifetime
    }

    fn age(&self) -> f64 {
        self.age
    }

    fn emission_model(&self) -> EmissionModel {
        self.emission
    }

    fn set_state(&mut self, mass: f64, age: f64) -> Result<(), SimulationError> {
        if !(mass.is_finite() && mass > 0.0) {
            return Err(SimulationError::MassExhausted { time: age });
        }
        self.mass = mass;
        self.age = age;
        Ok(())
    }
}
