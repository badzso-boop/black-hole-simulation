//! A visszapattanás utáni táguló tartomány („bébiuniverzum").
//!
//! A korábbi modell hibái: exp(H·dt) f64-túlcsordulás (a Planck-tömeg felett a
//! skálafaktor ∞, a sűrűség 0 lett, és az α csatolás emiatt 0-ra esett);
//! a skálafaktor méterben indult (L_P), mégis dimenziótlannak volt dokumentálva;
//! vegyes de Sitter + 1/t Hubble-törvény; a beeső energia a semmiből
//! keletkezett (a fekete lyukból sosem vonódott le); H ≈ 1/dt miatt az
//! eredmény a külső lépésszámtól függött.
//!
//! Itt a tágulás ugyanaz az LQC-pormegoldás, ami a visszapattanáshoz vezetett
//! (egyetlen, önkonzisztens H(ρ)), log-változókban:
//!   a(τ) = (1 + τ²/τ_b²)^(1/3),   N = ln a = ⅓·ln1p(τ²/τ_b²)
//! Nincs exp(H·dt) sehol, így nincs túlcsordulás. A porgömb tömeg-energiája
//! (ρ·V·c² = M c²) megmarad.

use crate::constants::{C, HBAR, K_B, PI};
use crate::interior::collapse::OSCollapse;
use crate::types::{BabyUniverseState, CollapsePhase, InteriorTrajectory};

/// Stefan–Boltzmann-állandó (W m⁻² K⁻⁴)
fn stefan_boltzmann() -> f64 {
    PI * PI * K_B.powi(4) / (60.0 * HBAR.powi(3) * C * C)
}

/// Gibbons–Hawking-hőmérséklet egy H Hubble-rátájú táguló tartomány horizontján:
/// T = ħH/(2πk_B)  [Gibbons & Hawking 1977]
pub fn gibbons_hawking_temperature(hubble_rate: f64) -> f64 {
    HBAR * hubble_rate / (2.0 * PI * K_B)
}

/// Az él (Hubble-horizont) belső luminozitása: σT_GH⁴·4π(c/H)²  (∝ H²)
pub fn gibbons_hawking_luminosity(hubble_rate: f64) -> f64 {
    if hubble_rate <= 0.0 {
        return 0.0;
    }
    let t = gibbons_hawking_temperature(hubble_rate);
    stefan_boltzmann() * t.powi(4) * 4.0 * PI * (C / hubble_rate).powi(2)
}

/// A bébiuniverzum állapotsora a Norbi-trajektória visszapattanás utáni szakaszából
pub fn baby_universe_states(
    collapse: &OSCollapse,
    trajectory: &InteriorTrajectory,
) -> Vec<BabyUniverseState> {
    let tb = collapse.lqc().bounce_timescale();
    let r_b = collapse.radius_at_density(collapse.lqc().critical_density());
    trajectory
        .samples
        .iter()
        .filter(|s| s.phase == CollapsePhase::PostBounce)
        .map(|s| {
            let efolds = (1.0 / 3.0) * ((s.tau / tb).powi(2)).ln_1p();
            let volume = 4.0 / 3.0 * PI * s.radius.powi(3);
            BabyUniverseState {
                tau: s.tau,
                scale_factor: efolds.exp(),
                efolds,
                hubble: s.hubble,
                density: s.density,
                radius: r_b * efolds.exp(),
                total_energy: s.density * volume * C * C,
                gh_temperature: gibbons_hawking_temperature(s.hubble),
                interior_luminosity: gibbons_hawking_luminosity(s.hubble),
            }
        })
        .collect()
}
