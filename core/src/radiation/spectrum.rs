use crate::constants::{C, H_PLANCK, K_B, WIEN_FREQ};
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

/// Planck-alak (ν³/(e^x−1)) normálva a megadott frekvenciarácson
fn planck_shape(frequencies: &[f64], temp: f64) -> Vec<f64> {
    let raw: Vec<f64> = frequencies
        .iter()
        .map(|&f| planck_spectrum(f, temp).unwrap_or(0.0))
        .collect();
    let sum: f64 = raw.iter().sum();
    if sum > 0.0 {
        raw.iter().map(|v| v / sum).collect()
    } else {
        raw
    }
}

fn kl_divergence(p: &[f64], q: &[f64]) -> f64 {
    p.iter()
        .zip(q)
        .filter(|(&pi, _)| pi > 0.0)
        .map(|(&pi, &qi)| pi * (pi / qi.max(1e-300)).ln())
        .sum::<f64>()
        .max(0.0)
}

/// Spektrális nem-termalitás: min_T KL(p ‖ Planck(T)), aranymetszéses kereséssel
/// ln T-ben a [0.2, 5]·T_guess intervallumon. Visszaadja: (KL, T_fit).
pub fn spectral_nonthermality(
    frequencies: &[f64],
    intensities: &[f64],
    t_guess: f64,
) -> (f64, f64) {
    let sum: f64 = intensities.iter().sum();
    if sum <= 0.0 || t_guess <= 0.0 || frequencies.len() != intensities.len() {
        return (0.0, t_guess);
    }
    let p: Vec<f64> = intensities.iter().map(|v| v / sum).collect();
    let cost = |ln_t: f64| kl_divergence(&p, &planck_shape(frequencies, ln_t.exp()));
    let (mut a, mut b) = ((0.2 * t_guess).ln(), (5.0 * t_guess).ln());
    let phi = (5f64.sqrt() - 1.0) / 2.0;
    let mut c = b - phi * (b - a);
    let mut d = a + phi * (b - a);
    let (mut fc, mut fd) = (cost(c), cost(d));
    for _ in 0..80 {
        if fc < fd {
            b = d;
            d = c;
            fd = fc;
            c = b - phi * (b - a);
            fc = cost(c);
        } else {
            a = c;
            c = d;
            fc = fd;
            d = a + phi * (b - a);
            fd = cost(d);
        }
    }
    let ln_t = 0.5 * (a + b);
    (cost(ln_t), ln_t.exp())
}
