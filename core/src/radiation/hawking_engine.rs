use crate::black_hole::{BlackHoleTrait, RadiationEngine};
use crate::black_hole::thermodynamics::greybody_factor as compute_greybody;
use crate::constants::{C, HBAR, K_B, PI, SPECTRUM_BINS};
use crate::error::{check_finite, SimulationError};
use crate::radiation::spectrum::{planck_spectrum, peak_frequency};
use crate::types::{BabyUniverseState, Spectrum};

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

    /// KL divergencia a tényleges spektrum és a legjobb Planck-illesztés között.
    /// 0 = tökéletesen termális, > 0 = nem-termális komponens van.
    fn kl_from_planck(intensities: &[f64], frequencies: &[f64], temp: f64) -> f64 {
        let sum_actual: f64 = intensities.iter().sum();
        if sum_actual <= 0.0 || temp <= 0.0 {
            return 0.0;
        }
        let p: Vec<f64> = intensities.iter().map(|v| v / sum_actual).collect();

        // Planck-spektrum ugyanazon a frekvencia-tengelyen
        let q_raw: Vec<f64> = frequencies.iter().map(|&f| {
            if f <= 0.0 { return 1e-300; }
            let x = HBAR * 2.0 * PI * f / (K_B * temp);
            let x_clamped = x.min(700.0);
            f.powi(3) / (x_clamped.exp() - 1.0 + 1e-300)
        }).collect();
        let sum_q: f64 = q_raw.iter().sum();
        if sum_q <= 0.0 { return 0.0; }
        let q: Vec<f64> = q_raw.iter().map(|v| v / sum_q).collect();

        // KL(P||Q) = sum p_i * ln(p_i / q_i)
        p.iter().zip(q.iter())
            .filter(|(&pi, _)| pi > 1e-300)
            .map(|(&pi, &qi)| pi * (pi / qi.max(1e-300)).ln())
            .sum::<f64>()
            .max(0.0)
    }

    /// Norbi-módú spektrum: Hawking alap + bébiuniverzum él-sugárzás keveréke.
    pub fn compute_spectrum_norbi(
        &self,
        bh: &dyn BlackHoleTrait,
        baby_state: &BabyUniverseState,
    ) -> Result<Spectrum, SimulationError> {
        let temp    = bh.hawking_temperature()?;
        let h_power = bh.hawking_power()?;
        let r_s     = bh.schwarzschild_radius();

        // --- Hawking alap-spektrum (Planck × greybody) ---
        let freq_max = peak_frequency(temp) * 10.0;
        let df = freq_max / SPECTRUM_BINS as f64;
        let mut hawk_freq = Vec::with_capacity(SPECTRUM_BINS);
        let mut hawk_int  = Vec::with_capacity(SPECTRUM_BINS);
        for i in 0..SPECTRUM_BINS {
            let freq = (i as f64 + 0.5) * df;
            let planck = planck_spectrum(freq, temp).unwrap_or(0.0);
            let freq_c = C / (2.0 * PI * r_s);
            let gamma  = (1.0 - (-freq / freq_c).exp()).clamp(0.0, 1.0);
            hawk_freq.push(freq);
            hawk_int.push(planck * gamma);
        }

        // --- Él-spektrum a bébiuniverzum állapotából ---
        let rate = baby_state.edge_breakup_rate;
        let mut edge_int: Vec<f64> = (0..SPECTRUM_BINS).map(|i| {
            let x = (i as f64 + 0.5) / SPECTRUM_BINS as f64;
            rate * x * x / (x.exp() - 1.0 + 1e-100)
        }).collect();

        // Keverési arány: bébiuniverzum tárolt energiája vs. BH tömeg-energia
        // Fizikai értelmezés: alpha = mekkora hányad jön az él-szétszakadásból
        // alpha→0: nincs bébiuniverzum (Standard), alpha→1: BU domináns (Planck-skála)
        let bh_energy = bh.mass() * C * C;
        let baby_energy = baby_state.total_energy.max(0.0);
        let alpha = if bh_energy + baby_energy > 0.0 {
            (baby_energy / (baby_energy + bh_energy)).clamp(0.0, 1.0)
        } else {
            0.0
        };

        // L1-normalizálás mindkét spektrumra
        let sum_hawk: f64 = hawk_int.iter().sum();
        let sum_edge: f64 = edge_int.iter().sum();
        if sum_hawk > 0.0 { hawk_int.iter_mut().for_each(|v| *v /= sum_hawk); }
        if sum_edge > 0.0 { edge_int.iter_mut().for_each(|v| *v /= sum_edge); }

        // Kevert spektrum, visszaskálázva a Hawking-teljesítményre
        let total_power = h_power;
        let blended: Vec<f64> = hawk_int.iter().zip(edge_int.iter())
            .map(|(&h, &e)| ((1.0 - alpha) * h + alpha * e) * total_power)
            .collect();

        // Thermality score (KL divergencia a Planck-tól)
        let thermality = Self::kl_from_planck(&blended, &hawk_freq, temp);

        Ok(Spectrum {
            frequencies: hawk_freq,
            intensities: blended,
            temperature: temp,
            total_power,
            hawking_fraction: 1.0 - alpha,
            edge_fraction: alpha,
            thermality_score: thermality,
        })
    }

    /// Planck-spektrum közvetlen számítása (teszteléshez)
    pub fn planck_spectrum(
        &self,
        freq: f64,
        temp: f64,
    ) -> Result<f64, SimulationError> {
        planck_spectrum(freq, temp)
    }
}

impl Default for HawkingEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl RadiationEngine for HawkingEngine {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError> {
        let temp  = bh.hawking_temperature()?;
        let power = bh.hawking_power()?;
        let r_s   = bh.schwarzschild_radius();

        let freq_max = peak_frequency(temp) * 10.0;
        let df = freq_max / SPECTRUM_BINS as f64;
        let mut frequencies = Vec::with_capacity(SPECTRUM_BINS);
        let mut intensities = Vec::with_capacity(SPECTRUM_BINS);

        for i in 0..SPECTRUM_BINS {
            let freq = (i as f64 + 0.5) * df;
            let planck = planck_spectrum(freq, temp).unwrap_or(0.0);
            let freq_c = C / (2.0 * PI * r_s);
            let gamma  = (1.0 - (-freq / freq_c).exp()).clamp(0.0, 1.0);
            frequencies.push(freq);
            intensities.push(planck * gamma);
        }

        // Standard módban: KL divergencia a greybody-korrekció miatt (kis pozitív érték)
        let thermality = Self::kl_from_planck(&intensities, &frequencies, temp);

        Ok(Spectrum {
            frequencies,
            intensities,
            temperature: temp,
            total_power: power,
            hawking_fraction: 1.0,
            edge_fraction: 0.0,
            thermality_score: thermality,
        })
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
