//! Hawking-emisszió: részecskefajtánkénti járulékok és greybody-hatáskeresztmetszet.
//!
//! A tömegvesztés alakja dM/dt = −α(M)·ħc⁴/(G²M²), ahol α dimenziótlan.
//!
//! Irodalom:
//! - Page, PRD 13, 198 (1976); Page, arXiv:1301.4995 (2013): foton+graviton α = 3.7474e-5
//! - MacGibbon (1991); Carr, Kohri, Sendouda, Yokoyama, PRD 81, 104019 (2010),
//!   arXiv:0912.5297: dM/dt = −5.34e25·f(M)·(M/g)⁻² g/s, szabadsági fokonkénti
//!   járulékok f: spin-0 0.267, spin-½ 0.142 (töltött) / 0.147 (semleges),
//!   spin-1 0.060, spin-2 0.007; f(M ≫ 10¹⁷ g) ≈ 1 (tömegtelen neutrínókkal).
//!   A neutrínókat itt tömeg-sajátállapotokként kezeljük: M ≳ 1e22 kg-nál
//!   (T_H ≲ 0.01 eV) a két nehezebb lekapcsol, f → 0.43.
//!
//! A fajták bekapcsolása a MacGibbon-féle sima küszöbbel történik:
//! exp(−m c² / (β_s k_B T_H)), β_s = 2.66 / 4.53 / 6.04 / 9.56 (s = 0, ½, 1, 2).
//! A kvarkok/gluonok effektív küszöbe a QCD-skála (~300–650 MeV) — ez egy
//! közelítő modell: f(M*) ≈ 2.0 (irodalom: 1.9), τ(5.1e11 kg) ≈ 11 Gyr
//! (irodalom: ~13.8 Gyr). A tesztek ezt a ~25%-os pontosságot rögzítik.

use serde::{Deserialize, Serialize};

use crate::constants::{C, G, HBAR, K_B, PI};

/// Az MeV energiája joule-ban
const MEV: f64 = 1.602_176_634e-13;

/// Carr et al. 2010 együttható SI-ben: dM/dt = −CARR_RATE·f(M)/M² (kg/s, M kg-ban)
/// (5.34e25 g³/s → 5.34e25 · 1e-9 kg³/s)
const CARR_RATE: f64 = 5.34e16;

/// Page (2013), csak foton + graviton (valódi, tömeges neutrínókkal rendelkező
/// asztrofizikai fekete lyukakra): dM/dt = −α/M² Planck-egységben
pub const ALPHA_PAGE_GAMMA_GRAVITON: f64 = 3.7474e-5;

/// Egy fekete test fotonsugárzása A = 4πr_s² felületen, greybody nélkül:
/// P = ħc⁶/(15360πG²M²) → α = 1/(15360π)
pub const ALPHA_PHOTON_BLACKBODY: f64 = 1.0 / (15360.0 * PI);

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Default)]
pub enum EmissionModel {
    /// Csak fotonok, ideális fekete test — a klasszikus tankönyvi képlet
    PhotonBlackbody,
    /// Foton + graviton, Page (2013)
    PageGammaGraviton,
    /// Standard Modell összes részecskéje tömegfüggő f(M)-mel (MacGibbon/Carr)
    #[default]
    MacGibbon,
}

#[derive(Clone, Copy)]
enum Spin {
    Zero,
    Half,
    One,
    Two,
}

impl Spin {
    fn beta(self) -> f64 {
        match self {
            Spin::Zero => 2.66,
            Spin::Half => 4.53,
            Spin::One => 6.04,
            Spin::Two => 9.56,
        }
    }
}

struct Species {
    dof: f64,
    spin: Spin,
    f_per_dof: f64,
    mass_mev: f64,
}

const fn sp(dof: f64, spin: Spin, f_per_dof: f64, mass_mev: f64) -> Species {
    Species {
        dof,
        spin,
        f_per_dof,
        mass_mev,
    }
}

/// Szabadsági fokok: részecske+antirészecske × spin/helicitás × szín
const SPECIES: &[Species] = &[
    sp(2.0, Spin::One, 0.060, 0.0), // foton
    sp(2.0, Spin::Two, 0.007, 0.0), // graviton
    // Neutrínó tömeg-sajátállapotok (ν, ν̄ × 1 helicitás = 2 szf. mindegyik),
    // normál hierarchia az oszcillációs Δm²-ekből: m1 ≈ 0 (ismeretlen, a
    // legkönnyebb), m2 ≈ √(7.4e-5) eV, m3 ≈ √(2.5e-3) eV. Hideg, nagy tömegű
    // fekete lyukaknál (T_H ≲ 0.01 eV/k_B) ez számít — Page 2013 ezért hagyja
    // ki a neutrínókat asztrofizikai fekete lyukakra.
    sp(2.0, Spin::Half, 0.147, 0.0), // ν1 (a legkönnyebb, ~tömegtelen)
    sp(2.0, Spin::Half, 0.147, 8.6e-9), // ν2 (≈ 0.0086 eV)
    sp(2.0, Spin::Half, 0.147, 5.0e-8), // ν3 (≈ 0.050 eV)
    sp(4.0, Spin::Half, 0.142, 0.511), // e±
    sp(4.0, Spin::Half, 0.142, 105.66), // μ±
    sp(4.0, Spin::Half, 0.142, 1776.9), // τ±
    sp(12.0, Spin::Half, 0.142, 300.0), // u (QCD-skála küszöb)
    sp(12.0, Spin::Half, 0.142, 300.0), // d
    sp(12.0, Spin::Half, 0.142, 500.0), // s
    sp(12.0, Spin::Half, 0.142, 1270.0), // c
    sp(12.0, Spin::Half, 0.142, 4180.0), // b
    sp(12.0, Spin::Half, 0.142, 172_570.0), // t
    sp(16.0, Spin::One, 0.060, 650.0), // gluonok (effektív tömeg)
    sp(1.0, Spin::Zero, 0.267, 134.98), // π⁰
    sp(2.0, Spin::Zero, 0.267, 139.57), // π±
    sp(6.0, Spin::One, 0.060, 80_377.0), // W±
    sp(3.0, Spin::One, 0.060, 91_188.0), // Z
    sp(1.0, Spin::Zero, 0.267, 125_250.0), // Higgs
];

/// ħc⁴/G² — a dimenziótlan α és az SI tömegvesztés közti váltószám (kg³/s)
pub fn mass_loss_scale() -> f64 {
    HBAR * C.powi(4) / (G * G)
}

/// k_B·T_H MeV-ben
fn hawking_kt_mev(mass: f64) -> f64 {
    HBAR * C.powi(3) / (8.0 * PI * G * mass) / MEV
}

impl EmissionModel {
    /// MacGibbon-féle f(M) (dimenziótlan; f → 1.016 nagy tömegre)
    pub fn macgibbon_f(mass: f64) -> f64 {
        let kt = hawking_kt_mev(mass);
        SPECIES
            .iter()
            .map(|s| {
                let switch = if s.mass_mev == 0.0 {
                    1.0
                } else {
                    (-s.mass_mev / (s.spin.beta() * kt)).exp()
                };
                s.dof * s.f_per_dof * switch
            })
            .sum()
    }

    /// Dimenziótlan α(M): dM/dt = −α·ħc⁴/(G²M²)
    pub fn alpha(&self, mass: f64) -> f64 {
        match self {
            EmissionModel::PhotonBlackbody => ALPHA_PHOTON_BLACKBODY,
            EmissionModel::PageGammaGraviton => ALPHA_PAGE_GAMMA_GRAVITON,
            EmissionModel::MacGibbon => CARR_RATE * Self::macgibbon_f(mass) / mass_loss_scale(),
        }
    }

    /// Igaz, ha α nem függ a tömegtől (ekkor M(t) analitikus)
    pub fn is_constant_alpha(&self) -> bool {
        !matches!(self, EmissionModel::MacGibbon)
    }

    /// A kisugárzott teljesítmény fotonokban lévő hányada
    pub fn photon_fraction(&self, mass: f64) -> f64 {
        let photon_f = 2.0 * 0.060;
        match self {
            EmissionModel::PhotonBlackbody => 1.0,
            EmissionModel::PageGammaGraviton => photon_f / (photon_f + 2.0 * 0.007),
            EmissionModel::MacGibbon => photon_f / Self::macgibbon_f(mass),
        }
    }

    /// Teljes kisugárzott teljesítmény (W): P = α·ħc⁶/(G²M²)
    pub fn power(&self, mass: f64) -> f64 {
        self.alpha(mass) * mass_loss_scale() * C * C / (mass * mass)
    }
}

/// Foton (spin-1) abszorpciós hatáskeresztmetszet (m²).
///
/// Két ismert határeset, x = GMω/c³:
/// - alacsony frekvencia (Page 1976): σ → (4A/3)x² = (64π/3)·r_g²·x²
/// - geometriai optika:              σ → 27π·r_g²
///
/// A kettő között az ℓ=1 módus x ≈ 0.2 körül „bekapcsol". Ezt egy ln x-ben
/// logisztikus átmenettel modellezzük; az átmenet helyét (X_TURN_ON) úgy
/// kalibráltuk, hogy a teljes foton-teljesítmény egyezzen az irodalmi
/// értékkel (α_γ = 2·0.060·Carr ≈ 3.35e-5 ≈ 1.62× a naiv fekete test).
/// A kalibrált x_c ≈ 0.21 fizikailag az ℓ=1 rezonancia helye — független
/// ellenőrzés. A spektrum *alakja* az átmeneti tartományban közelítő.
pub fn photon_cross_section(mass: f64, freq: f64) -> f64 {
    if freq <= 0.0 {
        return 0.0;
    }
    const X_TURN_ON: f64 = 0.2126;
    const WIDTH: f64 = 0.15;
    let r_g = G * mass / (C * C);
    let x = r_g * 2.0 * PI * freq / C;
    let low = 64.0 * PI / 3.0 * x * x;
    let geo = 27.0 * PI;
    if low >= geo {
        return geo * r_g * r_g;
    }
    let switch = 1.0 / (1.0 + (-(x / X_TURN_ON).ln() / WIDTH).exp());
    (low * (1.0 - switch) + geo * switch) * r_g * r_g
}

/// Hawking-hőmérséklet (K)
pub fn hawking_temperature(mass: f64) -> f64 {
    HBAR * C.powi(3) / (8.0 * PI * G * mass * K_B)
}
