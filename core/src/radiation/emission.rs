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

// ---------------------------------------------------------------------------
// Kerr (forgó) fekete lyukak emissziója — Page (1976b)
// ---------------------------------------------------------------------------
//
// f(a*) = −M² dM/dt, g(a*) = −(M/a*) dJ/dt (Planck-egység), fajtánként.
// Forrás: Page, PRD 14, 3260 (1976b); a táblázat Dong, Kinney & Stojkovic
// (2016, arXiv:1511.05642) B.1 táblázatából (a Page-féle értékek, a skalárra
// Taylor, Chambers & Hiscock 1998). A neutrínó-oszlop a* = 0.99999 és 1
// sorában a nyomtatott 1.074e-4 / 1.093e-4 elírás: 1.074e-3 / 1.093e-3 a
// helyes (monotonitás; 1.093e-3/8.185e-5 = 13.35 = Page neutrínó-faktora).
// Ellenőrzés: f(1)/f(0) = 13.35 (ν), 107.5 (γ), ~26 380 (graviton) — Page absztraktja.
//
// Az a* = 0 sor a 0.01-es sor (a táblázat ott kezdődik; az eltérés < 1e-3).
// A tömeges fajtákra ugyanazt az f(a*)/f(0), g(a*)/f(0) arányt alkalmazzuk,
// mint az azonos spinű tömegtelen mezőre — ez közelítés (a tömeg az alacsony
// frekvenciás, szuperradiáns módusokat elnyomja).

const KERR_SPINS: [f64; 15] = [
    0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.96, 0.99, 0.999, 0.99999, 1.0,
];
/// f_s(a*) oszlopok: [skalár, 1 neutrínó íz (ν+ν̄), foton, graviton]
const KERR_F: [[f64; 4]; 15] = [
    [7.429e-5, 8.185e-5, 3.366e-5, 3.845e-6],
    [7.442e-5, 8.343e-5, 3.580e-5, 4.684e-6],
    [7.319e-5, 8.830e-5, 4.265e-5, 7.732e-6],
    [7.265e-5, 9.669e-5, 5.525e-5, 1.494e-5],
    [7.097e-5, 1.089e-4, 7.570e-5, 3.116e-5],
    [6.996e-5, 1.258e-4, 1.080e-4, 6.822e-5],
    [7.008e-5, 1.487e-4, 1.594e-4, 1.574e-4],
    [7.119e-5, 1.804e-4, 2.450e-4, 3.909e-4],
    [7.969e-5, 2.284e-4, 4.014e-4, 1.104e-3],
    [1.024e-4, 3.195e-4, 7.520e-4, 4.107e-3],
    [1.551e-4, 4.567e-4, 1.313e-3, 1.305e-2],
    [2.283e-4, 6.708e-4, 2.151e-3, 3.578e-2],
    [2.625e-4, 9.253e-4, 3.057e-3, 7.251e-2],
    [2.667e-4, 1.074e-3, 3.555e-3, 9.785e-2],
    [2.667e-4, 1.093e-3, 3.616e-3, 1.012e-1],
];
/// g_s(a*) oszlopok, ugyanabban a sorrendben
const KERR_G: [[f64; 4]; 15] = [
    [8.867e-5, 6.161e-4, 4.795e-4, 1.064e-4],
    [9.085e-5, 6.174e-4, 4.895e-4, 1.167e-4],
    [9.391e-5, 6.218e-4, 5.207e-4, 1.514e-4],
    [1.024e-4, 6.299e-4, 5.759e-4, 2.233e-4],
    [1.125e-4, 6.430e-4, 6.599e-4, 3.603e-4],
    [1.281e-4, 6.631e-4, 7.845e-4, 6.236e-4],
    [1.507e-4, 6.946e-4, 9.668e-4, 1.155e-3],
    [1.803e-4, 7.457e-4, 1.245e-3, 2.322e-3],
    [2.306e-4, 8.366e-4, 1.706e-3, 5.286e-3],
    [3.166e-4, 1.034e-3, 2.632e-3, 1.544e-2],
    [4.515e-4, 1.343e-3, 3.976e-3, 4.057e-2],
    [6.160e-4, 1.810e-3, 5.829e-3, 9.555e-2],
    [6.905e-4, 2.340e-3, 7.723e-3, 1.753e-1],
    [6.997e-4, 2.641e-3, 8.730e-3, 2.271e-1],
    [7.006e-4, 2.678e-3, 8.851e-3, 2.338e-1],
];

fn spin_column(spin: Spin) -> usize {
    match spin {
        Spin::Zero => 0,
        Spin::Half => 1,
        Spin::One => 2,
        Spin::Two => 3,
    }
}

/// Page-féle (f, g) egy spin-osztályra, lineáris interpolációval a*-ban
pub fn page_kerr_fg(spin_class: usize, a: f64) -> (f64, f64) {
    let a = a.clamp(0.0, 1.0);
    let i = KERR_SPINS
        .partition_point(|&x| x < a)
        .clamp(1, KERR_SPINS.len() - 1);
    let (a0, a1) = (KERR_SPINS[i - 1], KERR_SPINS[i]);
    let w = if a1 > a0 { (a - a0) / (a1 - a0) } else { 0.0 };
    let lerp =
        |t: &[[f64; 4]; 15]| t[i - 1][spin_class] + w * (t[i][spin_class] - t[i - 1][spin_class]);
    (lerp(&KERR_F), lerp(&KERR_G))
}

/// Kerr-korrekció a Hawking-emisszióhoz (M, a*) függvényében
#[derive(Debug, Clone, Copy)]
pub struct KerrEmissionFactors {
    /// f(M, a*)/f(M, 0): a teljes teljesítmény növekedése a spinnel
    pub power_ratio: f64,
    /// h = d ln a*/d ln M = g/f − 2 a Hawking-párolgás alatt
    /// (> 0: gyorsabban veszít impulzusmomentumot, mint tömeget)
    pub h: f64,
    /// A fotonokra eső teljesítmény-hányad szorzója a nem forgó esethez képest
    pub photon_share_ratio: f64,
}

impl EmissionModel {
    /// A modell fajtái: (spin-osztály, α-járulék a* = 0-ban) — a MacGibbon
    /// szabadsági-fok-járulékok Page-normálásban egyeznek (foton 3.35e-5 vs
    /// Page 3.366e-5; 1 ν-íz 8.21e-5 vs 8.185e-5; graviton 3.9e-6 vs 3.845e-6).
    fn species_alphas(&self, mass: f64) -> Vec<(Spin, f64)> {
        let scale = CARR_RATE / mass_loss_scale();
        match self {
            EmissionModel::PhotonBlackbody => vec![(Spin::One, ALPHA_PHOTON_BLACKBODY)],
            EmissionModel::PageGammaGraviton => {
                // a Page (2013) α arányosan szétosztva a foton- és graviton-részre
                let (fg, gg) = (2.0 * 0.060, 2.0 * 0.007);
                vec![
                    (Spin::One, ALPHA_PAGE_GAMMA_GRAVITON * fg / (fg + gg)),
                    (Spin::Two, ALPHA_PAGE_GAMMA_GRAVITON * gg / (fg + gg)),
                ]
            }
            EmissionModel::MacGibbon => {
                let kt = hawking_kt_mev(mass);
                SPECIES
                    .iter()
                    .map(|s| {
                        let switch = if s.mass_mev == 0.0 {
                            1.0
                        } else {
                            (-s.mass_mev / (s.spin.beta() * kt)).exp()
                        };
                        (s.spin, scale * s.dof * s.f_per_dof * switch)
                    })
                    .collect()
            }
        }
    }

    /// Kerr-tényezők egy (M, a*) állapotban
    pub fn kerr_factors(&self, mass: f64, spin: f64) -> KerrEmissionFactors {
        if spin <= 0.0 {
            return KerrEmissionFactors {
                power_ratio: 1.0,
                h: 0.0,
                photon_share_ratio: 1.0,
            };
        }
        let (mut f0, mut f_a, mut g_a, mut ph0, mut ph_a) = (0.0, 0.0, 0.0, 0.0, 0.0);
        for (sp, alpha0) in self.species_alphas(mass) {
            let col = spin_column(sp);
            let (f_ref, _) = page_kerr_fg(col, 0.0);
            let (f, g) = page_kerr_fg(col, spin);
            f0 += alpha0;
            f_a += alpha0 * f / f_ref;
            g_a += alpha0 * g / f_ref;
            if matches!(sp, Spin::One) {
                // a spin-1 járulékból csak a foton (2 szf.) a „foton" — a
                // gluonok/W/Z ugyanazt az arányt kapják, így az arány változatlan
                ph0 += alpha0;
                ph_a += alpha0 * f / f_ref;
            }
        }
        let photon_share_ratio = if ph0 > 0.0 && f_a > 0.0 {
            (ph_a / f_a) / (ph0 / f0)
        } else {
            1.0
        };
        KerrEmissionFactors {
            power_ratio: f_a / f0,
            h: g_a / f_a - 2.0,
            photon_share_ratio,
        }
    }
}
