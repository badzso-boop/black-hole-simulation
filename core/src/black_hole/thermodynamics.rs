use crate::black_hole::BlackHoleTrait;
use crate::constants::{C, HBAR, K_B, PI, WIEN_FREQ};
use crate::error::{check_finite, SimulationError};

/// Page-idő: az elpárlási idő fele
pub fn page_time(bh: &dyn BlackHoleTrait) -> f64 {
    bh.evaporation_time() / 2.0
}

/// Wien-törvény: ν_max = WIEN_FREQ · T
pub fn wien_peak_frequency(temperature: f64) -> f64 {
    WIEN_FREQ * temperature
}

/// Greybody faktor közelítés (geometriai optika közelítés)
/// Eredmény: [0, 1]
pub fn greybody_factor(freq: f64, bh: &dyn BlackHoleTrait) -> f64 {
    if freq <= 0.0 {
        return 0.0;
    }
    let r_s = bh.schwarzschild_radius();
    // Geometriai keresztmetszet: σ = 27π r_s²
    // Közelítő greybody: γ ≈ 1 - exp(-freq/freq_c), ahol freq_c = c/(2π·r_s)
    let freq_c = C / (2.0 * PI * r_s);
    let gamma = 1.0 - (-freq / freq_c).exp();
    gamma.clamp(0.0, 1.0)
}

/// Sugárzási hőmérséklet a Norbi-modellben (belső szétszakadásból)
pub fn norbi_effective_temperature(
    internal_density: f64,
    breakup_rate: f64,
    bh: &dyn BlackHoleTrait,
) -> Result<f64, SimulationError> {
    let standard_t = bh.hawking_temperature()?;
    // A belső szétszakadás extra járuléka a hőmérséklethez
    let norbi_correction = (internal_density * breakup_rate).sqrt() * HBAR / K_B;
    let t = standard_t + norbi_correction;
    check_finite(t, "norbi_effective_temperature")
}

/// Elpárlási teljesítmény ellenőrzés energiamegmaradásra
pub fn check_energy_conservation(
    mass_before: f64,
    mass_after: f64,
    emitted_energy: f64,
    tolerance: f64,
) -> bool {
    let delta_e = (mass_before - mass_after) * C * C;
    (delta_e - emitted_energy).abs() / delta_e.max(1e-100) < tolerance
}
