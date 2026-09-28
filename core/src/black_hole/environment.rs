//! A fekete lyuk környezete: ami a keletkezés *után* beleesik.
//!
//! Három csatorna (mindegyik a tömeget növeli, szemben a Hawking-párolgással):
//!
//! 1. **Kozmikus mikrohullámú háttér (CMB) elnyelése.** Egy T hőmérsékletű
//!    izotróp fekete-test sugárzásból elnyelt teljesítmény
//!    `P_abs = ∫ 4π·σ(ν)·B_ν(T) dν`,
//!    ugyanazzal a foton-greybody hatáskeresztmetszettel σ(ν), amivel a
//!    Hawking-emissziót számoljuk — így a részletes egyensúly (T = T_H esetén
//!    emisszió = abszorpció fotonokra) konstrukció szerint teljesül.
//!    Nagy tömegre σ → 27π r_g² (geometriai optika): P_abs = 27π r_g²·4σ_SB T⁴.
//!    A Hawking-hőmérséklet 2.7255 K-nél M ≈ 4.5e22 kg: ennél nagyobb fekete
//!    lyuk ma több CMB-t nyel el, mint amennyit kisugároz — nő, nem párolog.
//!    (A kozmikus neutrínóháttér elnyelése nincs modellezve.)
//!
//! 2. **Folytonos akkréció** a környező gázból:
//!    - `Constant`: rögzített Ṁ (kg/s)
//!    - `Bondi`: Ṁ = 4πλ·(GM)²·ρ_∞ / c_s³, λ = 1/4 (γ = 5/3 ideális gáz)
//!      [Bondi 1952]; opcionálisan az Eddington-határral:
//!      Ṁ_Edd = 4πGM·m_p / (ε·σ_T·c)  [Eddington-luminozitás / (εc²)]
//!
//!    A beáramló nyugalmi tömeg ε hányada sugárzásként távozik (akkréciós
//!    luminozitás), a fekete lyuk tömege (1 − ε)·Ṁ-mal nő.
//!
//! 3. **Diszkrét beesések** (`InfallEvent`): egy m tömegű objektum (csillag,
//!    bolygó, aszteroida) t időpontban beesik — a tömeg ugrásszerűen nő.
//!
//! A környezet időben állandó (a CMB lehűlése a kozmikus tágulással, a gáz
//! kifogyása nincs modellezve) — ezért a folytonos tömegegyenlet
//! dM/dt = f(M) autonóm, és a (−1/M² Hawking + M² elnyelés) szerkezet miatt
//! egyetlen egyensúlyi tömege van (instabil): alatta párolog, felette nő.

use serde::{Deserialize, Serialize};

use crate::constants::{C, G, HBAR, H_PLANCK, K_B, PI};
use crate::radiation::emission::{photon_cross_section, EmissionModel};

/// A CMB mai hőmérséklete (K) — Fixsen 2009
pub const T_CMB_TODAY: f64 = 2.7255;
/// Proton tömege (kg) — CODATA 2022
pub const PROTON_MASS: f64 = 1.672_621_925_95e-27;
/// Thomson-hatáskeresztmetszet (m²) — CODATA 2022
pub const THOMSON_CROSS_SECTION: f64 = 6.652_458_705_1e-29;
/// Bondi-együttható γ = 5/3 ideális gázra
pub const BONDI_LAMBDA_ADIABATIC: f64 = 0.25;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum AccretionModel {
    /// Nincs folytonos akkréció
    #[default]
    None,
    /// Rögzített beáramlási ráta (kg/s)
    Constant { rate: f64 },
    /// Bondi-akkréció a környező gázból
    Bondi {
        /// Gázsűrűség a végtelenben (kg/m³); csillagközi közeg ~1.7e-21
        density: f64,
        /// Hangsebesség (m/s); ~10 km/s a 10⁴ K-es ionizált gázban
        sound_speed: f64,
        /// Az Eddington-határnál levágva
        #[serde(default = "default_true")]
        eddington_limited: bool,
    },
}

fn default_true() -> bool {
    true
}

/// Egy diszkrét beesés
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct InfallEvent {
    /// A beesés ideje a szimuláció kezdetétől (s)
    pub time: f64,
    /// A beeső objektum tömege (kg)
    pub mass: f64,
    #[serde(default)]
    pub label: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(default)]
pub struct Environment {
    /// A háttérsugárzás hőmérséklete (K); 0 = vákuum
    pub cmb_temperature: f64,
    pub accretion: AccretionModel,
    /// Az akkretált nyugalmi tömeg sugárzásként távozó hányada (0 ≤ ε < 1)
    pub radiative_efficiency: f64,
    pub infall_events: Vec<InfallEvent>,
}

impl Default for Environment {
    fn default() -> Self {
        Self {
            cmb_temperature: T_CMB_TODAY,
            accretion: AccretionModel::None,
            radiative_efficiency: 0.1,
            infall_events: Vec::new(),
        }
    }
}

/// A folytonos csatornák pillanatnyi értékei egy adott tömegnél
#[derive(Debug, Clone, Copy, Default)]
pub struct Rates {
    /// Hawking-teljesítmény (W), minden részecskefajta
    pub hawking_power: f64,
    /// Elnyelt háttérsugárzás (W)
    pub absorbed_power: f64,
    /// Beáramló nyugalmi tömeg (kg/s)
    pub accretion_inflow: f64,
    /// Akkréciós luminozitás ε·Ṁ·c² (W) — elhagyja a rendszert
    pub accretion_luminosity: f64,
}

impl Rates {
    /// dM/dt (kg/s)
    pub fn net_mass_rate(&self, radiative_efficiency: f64) -> f64 {
        (self.absorbed_power - self.hawking_power) / (C * C)
            + (1.0 - radiative_efficiency) * self.accretion_inflow
    }
}

impl Environment {
    /// Üres tér: nincs háttérsugárzás, nincs akkréció, nincs beesés
    pub fn vacuum() -> Self {
        Self {
            cmb_temperature: 0.0,
            accretion: AccretionModel::None,
            radiative_efficiency: 0.1,
            infall_events: Vec::new(),
        }
    }

    pub fn validate(&self) -> Result<(), String> {
        if !(self.cmb_temperature.is_finite() && self.cmb_temperature >= 0.0) {
            return Err(format!(
                "Érvénytelen háttér-hőmérséklet: {}",
                self.cmb_temperature
            ));
        }
        if !(0.0..1.0).contains(&self.radiative_efficiency) {
            return Err(format!(
                "A sugárzási hatásfoknak 0 ≤ ε < 1 kell legyen, kapott: {}",
                self.radiative_efficiency
            ));
        }
        match &self.accretion {
            AccretionModel::None => {}
            AccretionModel::Constant { rate } => {
                if !(rate.is_finite() && *rate >= 0.0) {
                    return Err(format!("Érvénytelen akkréciós ráta: {rate}"));
                }
            }
            AccretionModel::Bondi {
                density,
                sound_speed,
                eddington_limited,
            } => {
                if !(density.is_finite() && *density >= 0.0) {
                    return Err(format!("Érvénytelen gázsűrűség: {density}"));
                }
                if !(sound_speed.is_finite() && *sound_speed > 0.0) {
                    return Err(format!("Érvénytelen hangsebesség: {sound_speed}"));
                }
                if *eddington_limited && self.radiative_efficiency <= 0.0 {
                    return Err("Az Eddington-határhoz ε > 0 kell".into());
                }
            }
        }
        for e in &self.infall_events {
            if !(e.time.is_finite() && e.time >= 0.0 && e.mass.is_finite() && e.mass > 0.0) {
                return Err(format!(
                    "Érvénytelen beesés: t = {}, m = {}",
                    e.time, e.mass
                ));
            }
        }
        Ok(())
    }

    /// Beáramló nyugalmi tömeg Ṁ (kg/s)
    pub fn accretion_inflow(&self, mass: f64) -> f64 {
        match &self.accretion {
            AccretionModel::None => 0.0,
            AccretionModel::Constant { rate } => *rate,
            AccretionModel::Bondi {
                density,
                sound_speed,
                eddington_limited,
            } => {
                let bondi = bondi_rate(mass, *density, *sound_speed);
                if *eddington_limited {
                    bondi.min(eddington_rate(mass, self.radiative_efficiency))
                } else {
                    bondi
                }
            }
        }
    }

    pub fn rates(&self, emission: EmissionModel, mass: f64) -> Rates {
        let inflow = self.accretion_inflow(mass);
        Rates {
            hawking_power: emission.power(mass),
            absorbed_power: background_absorption_power(mass, self.cmb_temperature),
            accretion_inflow: inflow,
            accretion_luminosity: self.radiative_efficiency * inflow * C * C,
        }
    }

    pub fn net_mass_rate(&self, emission: EmissionModel, mass: f64) -> f64 {
        self.rates(emission, mass)
            .net_mass_rate(self.radiative_efficiency)
    }

    /// Az egyensúlyi tömeg (dM/dt = 0), ha a vizsgált tartományban létezik.
    /// Biszekció ln M-ben a [lo, hi] intervallumon (a folytonos csatornákra).
    pub fn equilibrium_mass(&self, emission: EmissionModel, lo: f64, hi: f64) -> Option<f64> {
        let f = |m: f64| self.net_mass_rate(emission, m);
        let (mut a, mut b) = (lo.ln(), hi.ln());
        if f(lo) >= 0.0 || f(hi) <= 0.0 {
            return None;
        }
        for _ in 0..200 {
            let mid = 0.5 * (a + b);
            if f(mid.exp()) < 0.0 {
                a = mid;
            } else {
                b = mid;
            }
        }
        Some((0.5 * (a + b)).exp())
    }
}

/// Bondi-akkréció: Ṁ = 4πλ(GM)²ρ/c_s³
pub fn bondi_rate(mass: f64, density: f64, sound_speed: f64) -> f64 {
    4.0 * PI * BONDI_LAMBDA_ADIABATIC * (G * mass).powi(2) * density / sound_speed.powi(3)
}

/// Eddington-határhoz tartozó beáramlás: Ṁ_Edd = L_Edd/(εc²), L_Edd = 4πGMm_p c/σ_T
pub fn eddington_rate(mass: f64, radiative_efficiency: f64) -> f64 {
    4.0 * PI * G * mass * PROTON_MASS / (radiative_efficiency * THOMSON_CROSS_SECTION * C)
}

/// Salpeter-idő: Eddington-korlátos növekedés e-redő ideje (s)
/// t_S = ε σ_T c / ((1 − ε)·4πG m_p)
pub fn salpeter_time(radiative_efficiency: f64) -> f64 {
    radiative_efficiency * THOMSON_CROSS_SECTION * C
        / ((1.0 - radiative_efficiency) * 4.0 * PI * G * PROTON_MASS)
}

/// Egy T hőmérsékletű izotróp fekete-test háttérből elnyelt teljesítmény (W):
/// P = ∫4πσ(ν)B_ν(T)dν = 8π(k_BT)⁴/(h³c²) · ∫ σ(y)·y³/(eʸ−1) dy,  y = hν/k_BT
/// Simpson-szabállyal y ∈ (0, 60]-on (a Wien-farok ott < 1e-20 relatív).
pub fn background_absorption_power(mass: f64, temperature: f64) -> f64 {
    if temperature <= 0.0 {
        return 0.0;
    }
    const N: usize = 600; // páros
    const Y_MAX: f64 = 60.0;
    let kt = K_B * temperature;
    let h = Y_MAX / N as f64;
    let integrand = |y: f64| {
        if y <= 0.0 {
            return 0.0;
        }
        let nu = y * kt / H_PLANCK;
        photon_cross_section(mass, nu) * y.powi(3) / y.exp_m1()
    };
    let mut sum = integrand(0.0) + integrand(Y_MAX);
    for i in 1..N {
        let w = if i % 2 == 1 { 4.0 } else { 2.0 };
        sum += w * integrand(i as f64 * h);
    }
    let integral = sum * h / 3.0;
    8.0 * PI * kt.powi(4) / (H_PLANCK.powi(3) * C * C) * integral
}

/// Az a tömeg, amelynél T_H = T (K): M = ħc³/(8πG k_B T)
pub fn mass_with_hawking_temperature(temperature: f64) -> f64 {
    HBAR * C.powi(3) / (8.0 * PI * G * K_B * temperature)
}
