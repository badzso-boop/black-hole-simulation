use crate::constants::{C, G, L_P, SPECTRUM_BINS};
use crate::types::{BabyUniverseState, BreakupEvent, InternalObjectData};

const H_INF_DEFAULT: f64 = 1e43; // inflációs Hubble-paraméter (1/s)

#[derive(Debug, Clone)]
pub struct BabyUniverse {
    pub scale_factor: f64,    // dimenzió nélküli tágulási faktor
    pub expansion_rate: f64,  // H_belső (1/s)
    pub internal_density: f64, // kg/m³
    pub total_energy: f64,    // J
    pub age: f64,             // s
    pub absorbed_energy: f64, // beeső anyagból
}

impl BabyUniverse {
    /// Kvantumvisszapattanás után azonnal létrejön
    pub fn new(initial_density: f64) -> Self {
        let h_inf = H_INF_DEFAULT;
        Self {
            scale_factor: L_P,
            expansion_rate: h_inf,
            internal_density: initial_density,
            total_energy: initial_density * L_P.powi(3) * C * C,
            age: 0.0,
            absorbed_energy: 0.0,
        }
    }

    /// Tágulási lépés — a(t) = a₀ · e^(H_inf · t)
    pub fn evolve(&mut self, dt: f64) {
        self.age += dt;
        self.scale_factor *= (self.expansion_rate * dt).exp();
        // Sűrűség csökken a tágulással: ρ ∝ a⁻³
        let volume_ratio = (self.expansion_rate * dt * 3.0).exp();
        self.internal_density /= volume_ratio;
        // Hubble-paraméter csökken (standard kozmológia)
        self.expansion_rate = H_INF_DEFAULT / (1.0 + self.age * H_INF_DEFAULT);
    }

    /// Beeső anyag energiájának integrálása a belső univerzumba
    pub fn absorb_energy(&mut self, energy: f64) {
        self.absorbed_energy += energy;
        self.total_energy += energy;
        // Az energia részlegesen sűrűségbe megy
        let v = self.scale_factor.powi(3);
        if v > 0.0 {
            self.internal_density += energy / (v * C * C);
        }
    }

    pub fn hubble_parameter(&self) -> f64 {
        self.expansion_rate
    }

    /// Szétszakadási ráta — a belső szélén szétszakadó anyag rátája
    pub fn edge_breakup_rate(&self) -> f64 {
        // Az a skálafaktor szélén v_tágulás = H * r
        // Szétszakadás ha v > c → e_tidal > e_bind
        // Egyszerűsített: ráta ∝ H² * a
        self.expansion_rate.powi(2) * self.scale_factor
    }

    /// Szétszakadás feltételének ellenőrzése egy belső objektumra
    pub fn check_breakup(
        &self,
        obj: &InternalObjectData,
        current_time: f64,
    ) -> Option<BreakupEvent> {
        let r = (obj.position[0].powi(2) + obj.position[1].powi(2) + obj.position[2].powi(2))
            .sqrt();

        // Tidal energia: E_tidal = 0.5 * m * H² * r²
        let e_tidal = 0.5 * obj.mass * self.expansion_rate.powi(2) * r.powi(2);

        // Kötési energia: E_bind = 3GM²/(5R)
        let e_bind = if obj.radius > 0.0 {
            3.0 * G * obj.mass.powi(2) / (5.0 * obj.radius)
        } else {
            f64::MAX
        };

        if e_tidal > e_bind {
            // A belső pozíciót az eseményhorizonton lévő pontra vetítjük
            let norm = if r > 0.0 { r } else { 1.0 };
            Some(BreakupEvent {
                released_energy: e_tidal - e_bind,
                position_on_horizon: [
                    obj.position[0] / norm,
                    obj.position[1] / norm,
                    obj.position[2] / norm,
                ],
                time: current_time,
            })
        } else {
            None
        }
    }

    /// A belső tágulás szélén szétszakadó anyag sugárzási spektruma
    pub fn edge_radiation_spectrum(&self) -> Vec<f64> {
        let mut spectrum = vec![0.0_f64; SPECTRUM_BINS];
        // Egyszerűsített: a szétszakadási rátával arányos emissziós spektrum
        let rate = self.edge_breakup_rate();
        if rate > 0.0 {
            for (i, val) in spectrum.iter_mut().enumerate() {
                let x = i as f64 / SPECTRUM_BINS as f64;
                // Módosított Planck-szerű spektrum a belső hőmérsékletre
                *val = rate * x * x / (x.exp() - 1.0 + 1e-100);
            }
        }
        spectrum
    }

    pub fn to_state(&self) -> BabyUniverseState {
        BabyUniverseState {
            scale_factor: self.scale_factor,
            expansion_rate: self.expansion_rate,
            internal_density: self.internal_density,
            edge_breakup_rate: self.edge_breakup_rate(),
            total_energy: self.total_energy,
            age: self.age,
        }
    }
}
