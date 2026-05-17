pub use std::f64::consts::PI;

// Gravitációs állandó (m³ kg⁻¹ s⁻²)
pub const G: f64 = 6.674e-11;

// Fénysebesség (m/s)
pub const C: f64 = 2.998e8;

// Redukált Planck-állandó (J·s)
pub const HBAR: f64 = 1.055e-34;

// Boltzmann-állandó (J/K)
pub const K_B: f64 = 1.381e-23;

// Planck-hossz (m)
pub const L_P: f64 = 1.616e-35;

// Planck-sűrűség (kg/m³)
pub const RHO_PLANCK: f64 = 5.155e96;

// Planck-tömeg (kg)
pub const M_PLANCK: f64 = 2.176e-8;

// Planck-idő (s)
pub const T_PLANCK: f64 = 5.391e-44;

// Nap tömege (kg)
pub const M_SUN: f64 = 1.989e30;

// Wien-állandó (Hz/K)
pub const WIEN_FREQ: f64 = 5.879e10;

// Spektrum binszám (sugárzási számításokhoz)
pub const SPECTRUM_BINS: usize = 1000;

// Gravitációs softening (ütközés elkerülés belső N-test számításban)
pub const DEFAULT_SOFTENING: f64 = 0.01;
