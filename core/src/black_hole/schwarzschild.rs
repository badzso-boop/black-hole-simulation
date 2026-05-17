use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, G, HBAR, K_B, L_P, PI};
use crate::error::{check_finite, SimulationError};

#[derive(Debug, Clone)]
pub struct SchwarzschildBlackHole {
    mass: f64,
    initial_mass: f64,
    age: f64,
}

impl SchwarzschildBlackHole {
    pub fn new(mass: f64) -> Result<Self, SimulationError> {
        if mass <= 0.0 || mass.is_nan() {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Érvénytelen tömeg: {mass}"),
            });
        }
        Ok(Self { mass, initial_mass: mass, age: 0.0 })
    }
}

impl BlackHoleTrait for SchwarzschildBlackHole {
    fn mass(&self) -> f64 {
        self.mass
    }

    fn schwarzschild_radius(&self) -> f64 {
        // r_s = 2GM/c²
        2.0 * G * self.mass / (C * C)
    }

    fn hawking_temperature(&self) -> Result<f64, SimulationError> {
        // T_H = ℏc³ / (8πGMk_B)
        let t = (HBAR * C.powi(3)) / (8.0 * PI * G * self.mass * K_B);
        check_finite(t, "hawking_temperature")
    }

    fn bekenstein_entropy(&self) -> f64 {
        // S = A / (4 l_P²), ahol A = 4π r_s²
        let r_s = self.schwarzschild_radius();
        let area = 4.0 * PI * r_s.powi(2);
        area / (4.0 * L_P.powi(2))
    }

    fn hawking_power(&self) -> Result<f64, SimulationError> {
        // P = ℏc⁶ / (15360π G² M²)
        let p = (HBAR * C.powi(6)) / (15360.0 * PI * G.powi(2) * self.mass.powi(2));
        check_finite(p, "hawking_power")
    }

    fn evaporation_time(&self) -> f64 {
        // t = 5120π G² M₀³ / (ℏ c⁴)
        5120.0 * PI * G.powi(2) * self.initial_mass.powi(3) / (HBAR * C.powi(4))
    }

    fn update_mass(&mut self, delta_m: f64) -> Result<(), SimulationError> {
        let new_mass = self.mass + delta_m;
        if new_mass <= 0.0 {
            return Err(SimulationError::MassExhausted { time: self.age });
        }
        if new_mass.is_nan() {
            return Err(SimulationError::NaNDetected {
                context: format!("update_mass: delta_m={delta_m}"),
            });
        }
        self.mass = new_mass;
        Ok(())
    }

    fn age(&self) -> f64 {
        self.age
    }

    fn advance_time(&mut self, dt: f64) {
        self.age += dt;
    }
}
