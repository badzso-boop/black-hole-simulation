use crate::black_hole::{BlackHoleTrait, RadiationEngine};
use crate::black_hole::thermodynamics::greybody_factor as compute_greybody;
use crate::constants::C;
use crate::error::{check_finite, SimulationError};
use crate::radiation::spectrum::{planck_spectrum, peak_frequency};
use crate::types::Spectrum;
use crate::constants::SPECTRUM_BINS;

#[derive(Debug, Clone, PartialEq)]
pub enum EngineMode {
    Standard,
    Norbi,
}

/// HawkingEngine — a Hawking-sugárzás kiszámítása.
/// Standard módban: vákuumfluktuáció az eseményhorizonton.
/// Norbi módban: a belső bébiuniverzum szétszakadásából.
#[derive(Debug, Clone)]
pub struct HawkingEngine {
    #[allow(dead_code)]
    mode: EngineMode,
}

impl HawkingEngine {
    pub fn new() -> Self {
        Self { mode: EngineMode::Standard }
    }

    pub fn standard() -> Self {
        Self { mode: EngineMode::Standard }
    }

    pub fn norbi() -> Self {
        Self { mode: EngineMode::Norbi }
    }
}

impl Default for HawkingEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl RadiationEngine for HawkingEngine {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError> {
        let temp = bh.hawking_temperature()?;
        let power = bh.hawking_power()?;
        let r_s = bh.schwarzschild_radius();

        let freq_max = peak_frequency(temp) * 10.0;
        let df = freq_max / SPECTRUM_BINS as f64;
        let mut frequencies = Vec::with_capacity(SPECTRUM_BINS);
        let mut intensities = Vec::with_capacity(SPECTRUM_BINS);

        for i in 0..SPECTRUM_BINS {
            let freq = (i as f64 + 0.5) * df;
            let planck = planck_spectrum(freq, temp).unwrap_or(0.0);
            // Greybody faktor (r_s-t helyben számítjuk, nem kell bh referencia)
            let freq_c = C / (2.0 * std::f64::consts::PI * r_s);
            let gamma = (1.0 - (-freq / freq_c).exp()).clamp(0.0, 1.0);
            frequencies.push(freq);
            intensities.push(planck * gamma);
        }

        Ok(Spectrum { frequencies, intensities, temperature: temp, total_power: power })
    }

    fn energy_loss_rate(&self, bh: &dyn BlackHoleTrait) -> Result<f64, SimulationError> {
        bh.hawking_power()
    }

    fn evolve_step(
        &self,
        bh: &mut dyn BlackHoleTrait,
        dt: f64,
    ) -> Result<f64, SimulationError> {
        let power = bh.hawking_power()?;
        let mass_before = bh.mass();

        // ΔM = -P/c² · dt (tömeg csökken)
        let delta_m = -(power / (C * C)) * dt;
        bh.update_mass(delta_m)?;
        bh.advance_time(dt);

        let emitted_energy = (mass_before - bh.mass()) * C * C;
        check_finite(emitted_energy, "evolve_step emitted_energy")
    }

    fn greybody_factor(&self, freq: f64, bh: &dyn BlackHoleTrait) -> f64 {
        compute_greybody(freq, bh)
    }
}

impl HawkingEngine {
    /// Planck-spektrum közvetlen számítása (teszteléshez)
    pub fn planck_spectrum(
        &self,
        freq: f64,
        temp: f64,
    ) -> Result<f64, SimulationError> {
        planck_spectrum(freq, temp)
    }
}
