use crate::constants::{C, H_PLANCK, K_B, SPECTRUM_BINS, WIEN_FREQ};
use crate::error::{check_finite, SimulationError};
use crate::types::Spectrum;

/// Planck-féle spektrális radiancia egyetlen frekvencián (W·m⁻²·sr⁻¹·Hz⁻¹):
/// B_ν(T) = (2hν³/c²) · 1/(e^(hν/k_BT) − 1)
pub fn planck_spectrum(freq: f64, temp: f64) -> Result<f64, SimulationError> {
    if freq <= 0.0 || temp <= 0.0 {
        return Ok(0.0);
    }
    let x = H_PLANCK * freq / (K_B * temp);
    if x > 700.0 {
        return Ok(0.0); // exp túlcsordulás elkerülése — a Wien-farok itt gyakorlatilag 0
    }
    // exp_m1(x) = e^x − 1 pontosan: kis x-re (Rayleigh–Jeans) nincs kioltás
    let denominator = x.exp_m1();
    if denominator <= 0.0 || denominator.is_nan() {
        return Ok(0.0);
    }
    let prefactor = 2.0 * H_PLANCK * freq.powi(3) / (C * C);
    check_finite(
        prefactor / denominator,
        &format!("planck_spectrum(freq={freq:.3e}, temp={temp:.3e})"),
    )
}

/// Wien-törvény szerinti csúcsfrekvencia: ν_max = WIEN_FREQ · T
pub fn peak_frequency(temp: f64) -> f64 {
    WIEN_FREQ * temp
}

/// Teljes Hawking-sugárzási spektrum generálása (SPECTRUM_BINS bin)
pub fn build_spectrum(temp: f64, total_power: f64, greybody_fn: impl Fn(f64) -> f64) -> Spectrum {
    let freq_max = peak_frequency(temp) * 10.0;
    let df = freq_max / SPECTRUM_BINS as f64;

    let mut frequencies = Vec::with_capacity(SPECTRUM_BINS);
    let mut intensities = Vec::with_capacity(SPECTRUM_BINS);

    for i in 0..SPECTRUM_BINS {
        let freq = (i as f64 + 0.5) * df;
        let planck = planck_spectrum(freq, temp).unwrap_or(0.0);
        let gamma = greybody_fn(freq);
        frequencies.push(freq);
        intensities.push(planck * gamma);
    }

    Spectrum {
        frequencies,
        intensities,
        temperature: temp,
        total_power,
        ..Default::default()
    }
}

impl Spectrum {
    /// Spektrum csúcsfrekvenciájának megkeresése (Wien-törvény ellenőrzés)
    pub fn peak_frequency(&self) -> f64 {
        self.frequencies
            .iter()
            .zip(self.intensities.iter())
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .map(|(f, _)| *f)
            .unwrap_or(0.0)
    }

    pub fn normalize(&mut self) {
        let max = self.intensities.iter().cloned().fold(0.0_f64, f64::max);
        if max > 0.0 {
            self.intensities.iter_mut().for_each(|v| *v /= max);
        }
    }
}
