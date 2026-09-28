//! Fizikai állandók — CODATA 2022 (SI).
//!
//! A c, h, k_B az SI 2019 óta egzakt definíciós értékek; G mért érték
//! (6.67430(15)e-11). A Planck-egységek ezekből származtatottak — a
//! `tests::test_constants` modul ellenőrzi, hogy a beégetett számok
//! valóban a képletekből adódnak (a `const` kontextusban nincs `sqrt`).

pub use std::f64::consts::PI;

/// Fénysebesség (m/s) — egzakt
pub const C: f64 = 299_792_458.0;

/// Planck-állandó (J·s) — egzakt
pub const H_PLANCK: f64 = 6.626_070_15e-34;

/// Redukált Planck-állandó ħ = h/2π (J·s)
pub const HBAR: f64 = 1.054_571_817_646_156_5e-34;

/// Boltzmann-állandó (J/K) — egzakt
pub const K_B: f64 = 1.380_649e-23;

/// Gravitációs állandó (m³ kg⁻¹ s⁻²) — CODATA 2022
pub const G: f64 = 6.674_30e-11;

/// Planck-hossz ℓ_P = √(ħG/c³) (m)
pub const L_P: f64 = 1.616_255_024_423_705_3e-35;

/// Planck-tömeg m_P = √(ħc/G) (kg)
pub const M_PLANCK: f64 = 2.176_434_342_717_898_4e-8;

/// Planck-idő t_P = ℓ_P/c (s)
pub const T_PLANCK: f64 = 5.391_246_448_313_604e-44;

/// Planck-hőmérséklet T_P = m_P c²/k_B (K)
pub const TEMP_PLANCK: f64 = 1.416_784_162_157_342_5e32;

/// Planck-sűrűség ρ_Pl = c⁵/(ħG²) (kg/m³)
pub const RHO_PLANCK: f64 = 5.154_848_503_244_934e96;

/// Nap tömege (kg) — IAU névleges GM_☉ / G
pub const M_SUN: f64 = 1.988_47e30;

/// Wien-féle frekvencia-eltolódási állandó ν_max/T = 2.8214·k_B/h (Hz/K)
pub const WIEN_FREQ: f64 = 5.878_925_757_646_825e10;

// ---------------------------------------------------------------------------
// Loop Quantum Gravity / LQC
// ---------------------------------------------------------------------------

/// Barbero–Immirzi-paraméter (fekete lyuk entrópia-számlálásból; Ashtekar & Singh 2011)
pub const GAMMA_BI: f64 = 0.2375;

/// LQC kritikus sűrűség ρ_c = √3/(32π²γ³)·ρ_Pl ≈ 0.409 ρ_Pl (kg/m³)
/// [Lewandowski–Ma–Yang–Zhang 2023, arXiv:2210.02253; Ashtekar & Singh 2011]
pub const RHO_CRIT_LQC: f64 = 2.110_260_005_140_884_4e96;

/// A kvantum Oppenheimer–Snyder külső metrika paramétere α = 16√3πγ³ℓ_P² (m²)
/// f(r) = 1 − 2GM/(c²r) + α(GM/c²)²/r⁴   [LMY 2023]
pub const ALPHA_LMY: f64 = 3.046_780_031_237_495_4e-70;

/// Tömegrés: M_min = 4√α c²/(3√3 G) ≈ 0.83 m_P — ez alatt nem alakul ki horizont (kg)
pub const M_MIN_LMY: f64 = 1.809_398_982_325_308_2e-8;

// ---------------------------------------------------------------------------
// Numerikus beállítások
// ---------------------------------------------------------------------------

/// Spektrum binszám
pub const SPECTRUM_BINS: usize = 256;

/// A szemiklasszikus (Hawking) leírás érvényességi határa: M > 10 m_P
pub const SEMICLASSICAL_MIN_MASS: f64 = 10.0 * M_PLANCK;
