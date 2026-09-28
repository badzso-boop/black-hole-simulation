//! Oppenheimer–Snyder porgömb összeomlása — klasszikusan és LQC effektív dinamikával.
//!
//! A korábbi modell hibái: a „beeső részecske" sugara 0-ról indult, így a
//! visszapattanás mindig a 0. lépésben következett be; a `particle.initial_radius`
//! soha nem volt használva; a sűrűség egy tetszőleges tömegű (a BH 0.1%-a)
//! pontszerű részecskéből jött.
//!
//! Itt maga a fekete lyukat alkotó M tömegű, homogén porgömb omlik össze
//! (marginálisan kötött, nyugalomból a végtelenből), R0 = n·r_s sugárról indulva.
//! Sajátidő τ a visszapattanástól (LQC) / a klasszikus szingularitástól mérve:
//!   klasszikus:  ρ(τ) = 1/(6πGτ²)
//!   LQC:         ρ(τ) = ρ_c/(1 + τ²/τ_b²)       (|τ| ≫ τ_b-re a kettő egyezik)
//!   R(τ) = (3M/(4πρ))^(1/3),  a visszapattanási sugár = r_b = (αm/2)^(1/3) [LMY]

use crate::constants::{C, G, PI};
use crate::error::SimulationError;
use crate::geometry::{Horizons, LmyMetric};
use crate::quantum::lqc::LQCEquation;
use crate::types::{
    BounceInfo, CollapsePhase, InteriorKind, InteriorSample, InteriorTrajectory, PhysicsBoundary,
};

#[derive(Debug, Clone)]
pub struct OSCollapse {
    pub mass: f64,
    pub initial_radius: f64,
    lqc: LQCEquation,
    horizons: Horizons,
}

impl OSCollapse {
    /// `initial_radius_rs`: kezdősugár a Schwarzschild-sugár egységében (> 1)
    pub fn new(mass: f64, initial_radius_rs: f64) -> Result<Self, SimulationError> {
        let horizons = LmyMetric::new(mass)
            .horizons()
            .ok_or(SimulationError::MassGap {
                mass,
                m_min: crate::constants::M_MIN_LMY,
            })?;
        let r_s = 2.0 * G * mass / (C * C);
        let initial_radius = initial_radius_rs * r_s;
        if initial_radius.is_nan() || initial_radius <= horizons.r_plus {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!(
                    "A kezdősugárnak a külső horizonton (r_+ = {:.3e} m) kívül kell lennie, \
                     kapott: {initial_radius:.3e} m",
                    horizons.r_plus
                ),
            });
        }
        Ok(Self {
            mass,
            initial_radius,
            lqc: LQCEquation::new(),
            horizons,
        })
    }

    pub fn horizons(&self) -> &Horizons {
        &self.horizons
    }

    pub fn lqc(&self) -> &LQCEquation {
        &self.lqc
    }

    pub fn density_at_radius(&self, r: f64) -> f64 {
        3.0 * self.mass / (4.0 * PI * r.powi(3))
    }

    pub fn radius_at_density(&self, rho: f64) -> f64 {
        (3.0 * self.mass / (4.0 * PI * rho)).cbrt()
    }

    fn classical_tau_at_density(rho: f64) -> f64 {
        -1.0 / (6.0 * PI * G * rho).sqrt()
    }

    fn tau_at_radius(&self, r: f64, kind: InteriorKind) -> f64 {
        let rho = self.density_at_radius(r);
        match kind {
            InteriorKind::Standard => Self::classical_tau_at_density(rho),
            InteriorKind::Norbi => self.lqc.dust_tau_at_density(rho),
        }
    }

    /// Fázis-besorolás. A belső horizont és r_b nagy tömegre f64-ben
    /// megkülönböztethetetlen (a Napra ~1e-26 relatív), ezért a „belső
    /// tartomány" feltételt kioltásmentesen, R − r_b < δ_b alakban vizsgáljuk.
    fn phase_of(&self, radius: f64, excess_over_bounce: f64, tau: f64) -> CollapsePhase {
        if tau > 0.0 {
            CollapsePhase::PostBounce
        } else if radius > self.horizons.r_plus {
            CollapsePhase::Infall
        } else if excess_over_bounce > self.horizons.bounce_gap_below_inner_horizon {
            CollapsePhase::Trapped
        } else {
            CollapsePhase::InnerRegion
        }
    }

    fn sample(&self, tau: f64, kind: InteriorKind) -> InteriorSample {
        let tb = self.lqc.bounce_timescale();
        let r_b = self.horizons.r_bounce;
        // R/r_b = (ρ_c/ρ)^(1/3); a többlet R − r_b kioltás nélkül:
        let (density, hubble, excess) = match kind {
            InteriorKind::Standard => (
                1.0 / (6.0 * PI * G * tau * tau),
                2.0 / (3.0 * tau),
                r_b * ((2.0 / 3.0) * (tau.abs() / tb).ln()).exp_m1(),
            ),
            InteriorKind::Norbi => (
                self.lqc.dust_density(tau),
                self.lqc.dust_hubble(tau),
                r_b * ((1.0 / 3.0) * (tau / tb).powi(2).ln_1p()).exp_m1(),
            ),
        };
        let radius = self.radius_at_density(density);
        InteriorSample {
            tau,
            radius,
            density,
            hubble,
            ricci_scalar: 8.0 * PI * G * density / (C * C),
            phase: self.phase_of(radius, excess, tau),
        }
    }

    /// A trajektória R0-tól:
    /// - Standard: a klasszikus megoldás addig, amíg ρ el nem éri ρ_c-t (τ = −τ_b):
    ///   ott a klasszikus leírás érvényét veszti (fizikai határ)
    /// - Norbi: LQC-megoldás a visszapattanáson át, τ = +|τ_start|-ig (tágulás R0-ig)
    ///
    /// A rács s = asinh(τ/τ_b)-ben egyenletes: sűrű a visszapattanásnál, logaritmikus
    /// a távoli szakaszokon (τ_b ~ 1e-43 s, τ_start akár ~1e-4 s).
    pub fn trajectory(&self, kind: InteriorKind, n: usize) -> InteriorTrajectory {
        let tb = self.lqc.bounce_timescale();
        // Norbi: páratlan n, hogy a középső pont pontosan a visszapattanás (τ = 0) legyen
        let n = match kind {
            InteriorKind::Norbi => n.max(3) | 1,
            InteriorKind::Standard => n.max(3),
        };
        let tau_start = self.tau_at_radius(self.initial_radius, kind);
        let tau_end = match kind {
            InteriorKind::Standard => -tb,
            InteriorKind::Norbi => -tau_start,
        };
        let (s0, s1) = ((tau_start / tb).asinh(), (tau_end / tb).asinh());
        let samples: Vec<InteriorSample> = (0..n)
            .map(|i| {
                let s = if kind == InteriorKind::Norbi && 2 * i == n - 1 {
                    0.0
                } else {
                    s0 + (s1 - s0) * i as f64 / (n - 1) as f64
                };
                self.sample(tb * s.sinh(), kind)
            })
            .collect();

        let tau_horizon_crossing = self.tau_at_radius(self.horizons.r_plus, kind);
        let (bounce, physics_boundary, tau_final) = match kind {
            InteriorKind::Standard => {
                let rho = self.lqc.critical_density();
                (
                    None,
                    Some(PhysicsBoundary {
                        radius: self.radius_at_density(rho),
                        density: rho,
                        tau: -tb,
                        reason: "A sűrűség elérte az LQC kritikus sűrűséget (ρ_c ≈ 0.41 ρ_Pl): \
                                 a klasszikus általános relativitás itt érvényét veszti, \
                                 τ → 0-ban szingularitás következne"
                            .into(),
                    }),
                    -tb,
                )
            }
            InteriorKind::Norbi => (
                Some(BounceInfo {
                    radius: self.horizons.r_bounce,
                    density: self.lqc.critical_density(),
                    max_hubble_rate: self.lqc.max_bounce_hubble_rate(),
                    timescale: tb,
                }),
                None,
                0.0,
            ),
        };

        InteriorTrajectory {
            kind,
            samples,
            tau_start,
            tau_horizon_crossing,
            proper_time_horizon_to_end: tau_final - tau_horizon_crossing,
            bounce,
            physics_boundary,
        }
    }
}
