use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, WIEN_FREQ};

/// Page-idő: amikor a fekete lyuk elvesztette kezdeti Bekenstein–Hawking-entrópiájának
/// felét, azaz M = M0/√2. Állandó α mellett ez t_evap·(1 − 2^(−3/2)) ≈ 0.646·t_evap
/// (Page 1993; Page 2013 foton+graviton esetben 0.538·t_evap-ot ad, mert ott a
/// sugárzási entrópia/BH-entrópia arány β ≠ 1 — ezt a toy modell nem követi).
pub fn page_mass(bh: &dyn BlackHoleTrait) -> f64 {
    bh.initial_mass() / 2f64.sqrt()
}

/// Wien-törvény: ν_max = WIEN_FREQ · T
pub fn wien_peak_frequency(temperature: f64) -> f64 {
    WIEN_FREQ * temperature
}

/// Energiamegmaradás ellenőrzése: (M_előtte − M_utána)c² = kisugárzott energia
pub fn check_energy_conservation(
    mass_before: f64,
    mass_after: f64,
    emitted_energy: f64,
    tolerance: f64,
) -> bool {
    let delta_e = (mass_before - mass_after) * C * C;
    (delta_e - emitted_energy).abs() / delta_e.max(1e-100) < tolerance
}
