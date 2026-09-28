//! A fekete lyuk tömegének időfejlődése Hawking-párolgás alatt.
//!
//! dM/dt = −K·α(M)/M², K = ħc⁴/G². A korábbi fix lépésközű explicit Euler
//! a teljes t_evap alatt csak M/M0 = 0.28-ig jutott, és a végső, legérdekesebb
//! fázist egyetlen lépés fedte le.
//!
//! Itt az idő helyett a tömeg logaritmusa a független változó, és a végtömegtől
//! *visszafelé* integráljuk a hátralévő időt: v = ln(M/M_end),
//!   dr/dv = M³/(Kα(M)),  r(0) = 0.
//! Ez sima, nem merev, és a végfázist is teljes relatív pontossággal oldja fel
//! (előre integrálva a hátralévő ~1e-40 s elveszne a ~1e18 s teljes idő
//! f64-felbontásában). A kimeneti rács a tömegben logaritmikus, így a
//! hátralévő élettartamban (∝ M³) is.
//!
//! Állandó α esetén a megoldás analitikus: M(t) = (M0³ − 3Kαt)^(1/3).

use ode_solvers::{System, Vector1};

use crate::error::SimulationError;
use crate::radiation::emission::{mass_loss_scale, EmissionModel};
use crate::time_evolution::ode::integrate_on_grid;

/// Egy mintavételi pont
#[derive(Debug, Clone, Copy)]
pub struct EvaporationSample {
    /// Tömeg (kg)
    pub mass: f64,
    /// Idő a kezdettől (s)
    pub time: f64,
    /// Hátralévő idő a végtömegig (s). A végfázisban ez a pontos mennyiség:
    /// ott a hátralévő idő (~1e-40 s) kisebb, mint a teljes idő (~1e18 s)
    /// f64-felbontása, így `time` már nem változik, `remaining` viszont igen.
    pub remaining: f64,
}

#[derive(Debug, Clone)]
pub struct EvaporationHistory {
    pub samples: Vec<EvaporationSample>,
    /// A párolgás a végtömegig (tömegrés / maradvány) lefutott
    pub reached_end_mass: bool,
    pub end_mass: f64,
}

/// dr/dv = M³/(Kα(M)), M = M_end·e^v — a hátralévő idő a végtömegtől visszafelé
#[derive(Clone)]
struct RemainingRate {
    model: EmissionModel,
    end_mass: f64,
}

impl System<f64, Vector1<f64>> for RemainingRate {
    fn system(&self, v: f64, _r: &Vector1<f64>, dr: &mut Vector1<f64>) {
        let m = self.end_mass * v.exp();
        dr[0] = m.powi(3) / (mass_loss_scale() * self.model.alpha(m));
    }
}

/// Élettartam állandó α mellett: τ = M³/(3Kα)
pub fn lifetime_constant_alpha(alpha: f64, mass: f64) -> f64 {
    mass.powi(3) / (3.0 * mass_loss_scale() * alpha)
}

/// Analitikus M(t) állandó α mellett
pub fn mass_at_time_constant_alpha(alpha: f64, m0: f64, t: f64) -> f64 {
    let m3 = m0.powi(3) - 3.0 * mass_loss_scale() * alpha * t;
    if m3 <= 0.0 {
        0.0
    } else {
        m3.cbrt()
    }
}

/// A tömegfejlődés M0-tól `end_mass`-ig, `n_samples` pontban (logaritmikus a tömegben).
pub fn evaporation_history(
    model: EmissionModel,
    m0: f64,
    end_mass: f64,
    n_samples: usize,
) -> Result<EvaporationHistory, SimulationError> {
    if !(m0.is_finite() && m0 > 0.0) {
        return Err(SimulationError::InvalidPhysicalState {
            reason: format!("Érvénytelen kezdőtömeg: {m0}"),
        });
    }
    let n = n_samples.max(2);
    if end_mass >= m0 {
        return Ok(EvaporationHistory {
            samples: vec![EvaporationSample {
                mass: m0,
                time: 0.0,
                remaining: 0.0,
            }],
            reached_end_mass: true,
            end_mass,
        });
    }
    let alpha0 = model.alpha(m0);
    let tau0 = lifetime_constant_alpha(alpha0, m0);
    let u_end = (m0 / end_mass).ln();
    let du = u_end / (n - 1) as f64;

    let samples: Vec<EvaporationSample> = if model.is_constant_alpha() {
        (0..n)
            .map(|i| {
                let u = (i as f64 * du).min(u_end);
                let m = m0 * (-u).exp();
                EvaporationSample {
                    mass: m,
                    time: tau0 * (1.0 - (-3.0 * u).exp()),
                    remaining: tau0 * ((-3.0 * u).exp() - (m0 / end_mass).powi(-3)),
                }
            })
            .collect()
    } else {
        // Hátralévő idő: integrálás a végtömegtől felfelé, v = ln(M/M_end)
        let r_scale = lifetime_constant_alpha(model.alpha(end_mass), end_mass);
        let grid: Vec<f64> = (0..n).map(|j| (j as f64 * du).min(u_end)).collect();
        let rem = integrate_on_grid(
            &RemainingRate { model, end_mass },
            &grid,
            Vector1::new(0.0),
            1e-13 * r_scale,
        )?;
        let rem_at = |j: usize| rem[j][0];

        // time = élettartam − hátralévő: konstrukció szerint monoton.
        let total = rem_at(n - 1);
        (0..n)
            .map(|i| {
                let u = (i as f64 * du).min(u_end);
                let rem = rem_at(n - 1 - i);
                EvaporationSample {
                    mass: m0 * (-u).exp(),
                    time: total - rem,
                    remaining: rem,
                }
            })
            .collect()
    };

    Ok(EvaporationHistory {
        samples,
        reached_end_mass: true,
        end_mass,
    })
}

/// Teljes élettartam M0-tól M → 0-ig (s). Tömegfüggő α esetén numerikus;
/// a nagyon kis tömegek maradékát a ott már állandó α-val analitikusan adjuk hozzá.
pub fn lifetime(model: EmissionModel, m0: f64) -> Result<f64, SimulationError> {
    if model.is_constant_alpha() {
        return Ok(lifetime_constant_alpha(model.alpha(m0), m0));
    }
    // 1e-6 kg alatt (T_H ≫ 100 TeV) minden fajta aktív, f állandó
    let m_tail = 1e-6_f64.min(m0);
    let hist = evaporation_history(model, m0, m_tail, 400)?;
    let t_body = hist.samples.last().map(|s| s.time).unwrap_or(0.0);
    Ok(t_body + lifetime_constant_alpha(model.alpha(m_tail), m_tail))
}
