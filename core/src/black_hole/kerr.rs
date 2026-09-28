//! Forgó (Kerr) fekete lyuk — a spin a* = Jc/(GM²) ∈ [0, 1) függvényében.
//!
//! m = GM/c² (m), minden képlet a* = 0-ban a Schwarzschild-esetre redukálódik
//! (tesztek ellenőrzik):
//! - horizontok:         r± = m(1 ± √(1 − a*²))
//! - Hawking-hőmérséklet: T = ħc³/(4πGMk_B) · √(1 − a*²)/(1 + √(1 − a*²))
//! - horizont-terület:   A = 8πm²(1 + √(1 − a*²)),  S = A/(4ℓ_P²)
//! - szögsebesség:       Ω_H = a*c/(2r+)
//! - ISCO (prográd, egyenlítői): Bardeen–Press–Teukolsky (1972), lásd `isco_radius_m`
//! - fajlagos energia/impulzusmomentum az ISCO-n: lásd `isco_energy_momentum`
//! - sugárzási hatásfok (Novikov–Thorne): ε = 1 − E_isco
//!   (a* = 0: 5.72%, a* = 0.998: ~32%)
//! - akkréciós spin-felpörgetés (Bardeen 1970): nyugalmi Ṁ₀ beáramlásra
//!   dM/dt = E_isco·Ṁ₀, dJ/dt = L_isco·(GM/c)·Ṁ₀, azaz
//!   da*/dt = (Ṁ₀/M)·(L_isco − 2a*·E_isco)
//!   Thorne (1974): a fotonbefogás miatt a* ≤ 0.998.

use crate::constants::{C, G, HBAR, K_B, L_P, PI};

/// Thorne-határ (1974): az akkréció ennél jobban nem pörgeti fel
pub const THORNE_SPIN_LIMIT: f64 = 0.998;

fn root(a: f64) -> f64 {
    (1.0 - a * a).max(0.0).sqrt()
}

pub fn gravitational_radius(mass: f64) -> f64 {
    G * mass / (C * C)
}

/// (r+, r−) méterben
pub fn horizons(mass: f64, spin: f64) -> (f64, f64) {
    let m = gravitational_radius(mass);
    let s = root(spin);
    (m * (1.0 + s), m * (1.0 - s))
}

/// Hawking-hőmérséklet (K)
pub fn hawking_temperature(mass: f64, spin: f64) -> f64 {
    let s = root(spin);
    HBAR * C.powi(3) / (4.0 * PI * G * mass * K_B) * s / (1.0 + s)
}

/// Horizont-terület (m²)
pub fn horizon_area(mass: f64, spin: f64) -> f64 {
    let m = gravitational_radius(mass);
    8.0 * PI * m * m * (1.0 + root(spin))
}

/// Bekenstein–Hawking entrópia k_B egységben
pub fn entropy(mass: f64, spin: f64) -> f64 {
    horizon_area(mass, spin) / (4.0 * L_P * L_P)
}

/// A horizont szögsebessége (rad/s)
pub fn horizon_angular_velocity(mass: f64, spin: f64) -> f64 {
    // Ω_H = c·a/(r+² + a²), a = a*·m, és r+² + a² = 2m·r+  ⇒  Ω_H = a*c/(2r+)
    let (r_plus, _) = horizons(mass, spin);
    spin * C / (2.0 * r_plus)
}

/// Prográd ISCO-sugár m = GM/c² egységben (BPT 1972):
/// `Z1 = 1 + (1 − a²)^(1/3)·[(1 + a)^(1/3) + (1 − a)^(1/3)]`,
/// `Z2 = √(3a² + Z1²)`, `r_isco = 3 + Z2 − √((3 − Z1)(3 + Z1 + 2Z2))`
pub fn isco_radius_m(spin: f64) -> f64 {
    let a = spin;
    let z1 = 1.0 + (1.0 - a * a).cbrt() * ((1.0 + a).cbrt() + (1.0 - a).cbrt());
    let z2 = (3.0 * a * a + z1 * z1).sqrt();
    3.0 + z2 - ((3.0 - z1) * (3.0 + z1 + 2.0 * z2)).sqrt()
}

/// Fajlagos energia és impulzusmomentum az ISCO-n (E dimenziótlan, L m·c egységben),
/// x = √r (m = 1): `E = (x³ − 2x + a)/(x^(3/2)·√(x³ − 3x + 2a))`,
/// `L = (x⁴ − 2ax + a²)/(x^(3/2)·√(x³ − 3x + 2a))`
pub fn isco_energy_momentum(spin: f64) -> (f64, f64) {
    let a = spin;
    let r = isco_radius_m(a);
    let x = r.sqrt();
    let denom = x.powf(1.5) * (x.powi(3) - 3.0 * x + 2.0 * a).sqrt();
    let e = (x.powi(3) - 2.0 * x + a) / denom;
    let l = (x.powi(4) - 2.0 * a * x + a * a) / denom;
    (e, l)
}

/// Novikov–Thorne sugárzási hatásfok ε = 1 − E_isco
pub fn radiative_efficiency(spin: f64) -> f64 {
    1.0 - isco_energy_momentum(spin).0
}

/// da*/dt az akkrécióból (Bardeen 1970), Ṁ₀ nyugalmi beáramlás mellett (1/s).
/// A Thorne-határon felül nem pörget tovább.
pub fn accretion_spin_rate(mass: f64, spin: f64, rest_mass_inflow: f64) -> f64 {
    if rest_mass_inflow <= 0.0 {
        return 0.0;
    }
    let (e, l) = isco_energy_momentum(spin);
    let rate = rest_mass_inflow / mass * (l - 2.0 * spin * e);
    if spin >= THORNE_SPIN_LIMIT && rate > 0.0 {
        0.0
    } else {
        rate
    }
}

/// A fekete lyuk árnyékának szögátmérője (rad) D távolságból, a* = 0-ra
/// θ = 2√27·GM/(c²D). A spin és a látószög ezt legfeljebb ~4%-kal módosítja
/// (Johannsen & Psaltis 2010) — itt nem vesszük figyelembe.
pub fn shadow_angular_diameter(mass: f64, distance: f64) -> f64 {
    2.0 * 27f64.sqrt() * gravitational_radius(mass) / distance
}

// ---------------------------------------------------------------------------
// KerrBlackHole — a BlackHoleTrait általános (forgó) megvalósítása
// ---------------------------------------------------------------------------

use crate::black_hole::BlackHoleTrait;
use crate::error::{check_finite, SimulationError};
use crate::radiation::emission::EmissionModel;

/// Forgó fekete lyuk; a* = 0-ban azonos a `SchwarzschildBlackHole`-lal (teszt).
#[derive(Debug, Clone)]
pub struct KerrBlackHole {
    mass: f64,
    spin: f64,
    initial_mass: f64,
    age: f64,
    emission: EmissionModel,
}

impl KerrBlackHole {
    pub fn new(mass: f64, spin: f64, emission: EmissionModel) -> Result<Self, SimulationError> {
        if !(mass.is_finite() && mass > 0.0) {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Érvénytelen tömeg: {mass}"),
            });
        }
        if !(0.0..1.0).contains(&spin) {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("A spinnek 0 ≤ a* < 1 kell legyen, kapott: {spin}"),
            });
        }
        Ok(Self {
            mass,
            spin,
            initial_mass: mass,
            age: 0.0,
            emission,
        })
    }

    pub fn spin(&self) -> f64 {
        self.spin
    }

    pub fn set_spin(&mut self, spin: f64) {
        self.spin = spin.clamp(0.0, 0.9999);
    }
}

impl BlackHoleTrait for KerrBlackHole {
    fn mass(&self) -> f64 {
        self.mass
    }
    fn initial_mass(&self) -> f64 {
        self.initial_mass
    }
    /// A külső eseményhorizont sugara r+ (a* = 0-ban r_s)
    fn schwarzschild_radius(&self) -> f64 {
        horizons(self.mass, self.spin).0
    }
    fn hawking_temperature(&self) -> Result<f64, SimulationError> {
        check_finite(
            hawking_temperature(self.mass, self.spin),
            "kerr_hawking_temperature",
        )
    }
    fn bekenstein_entropy(&self) -> f64 {
        entropy(self.mass, self.spin)
    }
    fn hawking_power(&self) -> Result<f64, SimulationError> {
        let p = self.emission.power(self.mass)
            * self.emission.kerr_factors(self.mass, self.spin).power_ratio;
        check_finite(p, "kerr_hawking_power")
    }
    /// A kezdeti tömeg vákuumbeli, nem forgó élettartama (közelítés; a pontos,
    /// spin- és környezetfüggő időt az `evolution::evolve_mass` adja)
    fn evaporation_time(&self) -> f64 {
        crate::black_hole::evaporation::lifetime(self.emission, self.initial_mass)
            .unwrap_or(f64::NAN)
    }
    fn age(&self) -> f64 {
        self.age
    }
    fn emission_model(&self) -> EmissionModel {
        self.emission
    }
    fn photon_fraction(&self) -> f64 {
        self.emission.photon_fraction(self.mass)
            * self
                .emission
                .kerr_factors(self.mass, self.spin)
                .photon_share_ratio
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
