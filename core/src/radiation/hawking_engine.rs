use crate::black_hole::{BlackHoleTrait, RadiationEngine};
use crate::constants::{PI, SPECTRUM_BINS, WIEN_FREQ};
use crate::error::SimulationError;
use crate::radiation::emission::photon_cross_section;
use crate::radiation::spectrum::{planck_spectrum, spectral_nonthermality};
use crate::types::{BabyUniverseState, Spectrum};

/// HawkingEngine — a külső megfigyelő által látott Hawking-sugárzás.
///
/// A foton-spektrum dP/dν = 4π·σ(ν)·B_ν(T_H) (σ: spin-1 greybody hatáskeresztmetszet),
/// a teljes görbe pedig a fotonokra eső teljesítményre (α-modell) van normálva.
#[derive(Debug, Clone, Default)]
pub struct HawkingEngine;

impl HawkingEngine {
    pub fn new() -> Self {
        Self
    }

    /// A frekvenciarács: 0 … 15·ν_Wien(T) (a greybody a csúcsot felfelé tolja)
    fn frequency_grid(temp: f64) -> Vec<f64> {
        let freq_max = 15.0 * WIEN_FREQ * temp;
        let df = freq_max / SPECTRUM_BINS as f64;
        (0..SPECTRUM_BINS).map(|i| (i as f64 + 0.5) * df).collect()
    }

    /// Greybody-val módosított foton-spektrum, a `photon_power`-re normálva (W/Hz)
    fn photon_spectrum(mass: f64, temp: f64, photon_power: f64) -> (Vec<f64>, Vec<f64>) {
        let freqs = Self::frequency_grid(temp);
        let df = freqs.get(1).map(|f| f - freqs[0]).unwrap_or(1.0);
        let raw: Vec<f64> = freqs
            .iter()
            .map(|&f| {
                4.0 * PI * photon_cross_section(mass, f) * planck_spectrum(f, temp).unwrap_or(0.0)
            })
            .collect();
        let raw_power: f64 = raw.iter().sum::<f64>() * df;
        let scale = if raw_power > 0.0 {
            photon_power / raw_power
        } else {
            0.0
        };
        (freqs, raw.iter().map(|v| v * scale).collect())
    }

    /// A greybody-illesztés nyers (nem normált) foton-teljesítménye (W) — a
    /// tesztek ezzel ellenőrzik, hogy a σ(ν) közelítés összhangban van az
    /// irodalmi foton-α-val.
    pub fn unnormalized_photon_power(mass: f64) -> f64 {
        let temp = crate::radiation::emission::hawking_temperature(mass);
        let freqs = Self::frequency_grid(temp);
        let df = freqs[1] - freqs[0];
        freqs
            .iter()
            .map(|&f| {
                4.0 * PI * photon_cross_section(mass, f) * planck_spectrum(f, temp).unwrap_or(0.0)
            })
            .sum::<f64>()
            * df
    }

    /// Norbi-módú spektrum: Hawking alap + bébiuniverzum él-sugárzás keveréke.
    /// (Átmeneti, a 4–5. fázisban a kauzalitással kapuzott változat váltja fel.)
    pub fn compute_spectrum_norbi(
        &self,
        bh: &dyn BlackHoleTrait,
        baby_state: &BabyUniverseState,
    ) -> Result<Spectrum, SimulationError> {
        let base = self.compute_spectrum(bh)?;
        let temp_edge =
            crate::interior::baby_universe::gibbons_hawking_temperature(baby_state.expansion_rate);
        let edge_raw: Vec<f64> = base
            .frequencies
            .iter()
            .map(|&f| planck_spectrum(f, temp_edge).unwrap_or(0.0))
            .collect();
        let alpha = baby_state.breakup_fraction.clamp(0.0, 1.0);
        let sum_h: f64 = base.intensities.iter().sum();
        let sum_e: f64 = edge_raw.iter().sum();
        let blended: Vec<f64> = base
            .intensities
            .iter()
            .zip(&edge_raw)
            .map(|(&h, &e)| {
                let hn = if sum_h > 0.0 { h / sum_h } else { 0.0 };
                let en = if sum_e > 0.0 { e / sum_e } else { 0.0 };
                ((1.0 - alpha) * hn + alpha * en) * sum_h
            })
            .collect();
        let (kl, t_fit) = spectral_nonthermality(&base.frequencies, &blended, base.temperature);
        Ok(Spectrum {
            intensities: blended,
            hawking_fraction: 1.0 - alpha,
            edge_fraction: alpha,
            spectral_nonthermality: kl,
            fit_temperature: t_fit,
            ..base
        })
    }

    /// Planck-spektrum közvetlen számítása (teszteléshez)
    pub fn planck_spectrum(&self, freq: f64, temp: f64) -> Result<f64, SimulationError> {
        planck_spectrum(freq, temp)
    }
}

impl RadiationEngine for HawkingEngine {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError> {
        let temp = bh.hawking_temperature()?;
        let total_power = bh.hawking_power()?;
        let photon_power = total_power * bh.emission_model().photon_fraction(bh.mass());
        let (frequencies, intensities) = Self::photon_spectrum(bh.mass(), temp, photon_power);
        let (kl, t_fit) = spectral_nonthermality(&frequencies, &intensities, temp);
        Ok(Spectrum {
            frequencies,
            intensities,
            temperature: temp,
            total_power,
            photon_power,
            hawking_fraction: 1.0,
            edge_fraction: 0.0,
            spectral_nonthermality: kl,
            fit_temperature: t_fit,
        })
    }

    fn energy_loss_rate(&self, bh: &dyn BlackHoleTrait) -> Result<f64, SimulationError> {
        bh.hawking_power()
    }
}
