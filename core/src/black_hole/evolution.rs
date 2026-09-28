//! A fekete lyuk tömegfejlődése környezettel:
//!   dM/dt = f(M) = [P_abs(M) − P_H(M)]/c² + (1 − ε)·Ṁ_acc(M)
//! plusz diszkrét ugrások a beesési eseményeknél.
//!
//! Állandó környezetben f autonóm és (−1/M² párolgás + M² elnyelés/Bondi)
//! miatt legfeljebb egy gyöke van: alatta a fekete lyuk párolog, felette nő.
//! A beesések közötti szakaszokat ezért kétféleképpen integráljuk:
//!
//! - **Párolgó szakasz, ami a szakaszon belül véget ér** (f < 0 és a hátralévő
//!   idő ≤ a szakasz hossza): a hátralévő időt a végtömegtől *visszafelé*,
//!   ln M-ben integráljuk (mint a tiszta Hawking-esetben) — a végfázis is pontos.
//! - **Minden más** (növekedés, vagy lassú párolgás a szakasz végéig): időben
//!   integráljuk a tömeg *változását* δ = M − M_a, a várható változás
//!   nagyságrendjével normálva. Így a parányi változások is pontosak
//!   (egy Nap-tömegű fekete lyuk 13.8 Gyr alatt ~1e4 kg CMB-t nyel el: ez
//!   1e-26 relatív — M-ben f64-ben nem is ábrázolható, δ-ban igen).
//!
//! Az energiamérleg tételeit (kisugárzott, elnyelt, akkretált, akkréciós
//! luminozitás) ugyanabban az ODE-ben integráljuk, így a mérleg az integrálás
//! konzisztenciáját ellenőrzi.

use ode_solvers::{SVector, System};

use crate::black_hole::environment::{Environment, InfallEvent, Rates};
use crate::constants::C;
use crate::error::SimulationError;
use crate::radiation::emission::EmissionModel;
use crate::time_evolution::ode::integrate_on_grid;

/// Az Univerzum kora (s) — Planck 2018: 13.787 Gyr
pub const AGE_OF_UNIVERSE: f64 = 13.787e9 * 3.155_76e7;

#[derive(Debug, Clone)]
pub struct MassSample {
    pub time: f64,
    pub mass: f64,
    /// Hátralévő idő a párolgás végéig (s), ha a fekete lyuk a jelenlegi
    /// környezetben párolog; `None`, ha nő
    pub time_to_evaporation: Option<f64>,
    pub rates: Rates,
    pub net_mass_rate: f64,
    /// Ha ez a mintapont közvetlenül egy beesés után van: a beeső objektum címkéje
    pub after_infall: Option<String>,
}

#[derive(Debug, Clone, Default)]
pub struct EnergyTotals {
    /// ∫P_H dt (J)
    pub hawking_radiated: f64,
    /// ∫P_abs dt (J)
    pub background_absorbed: f64,
    /// ∫Ṁ c² dt — a beáramló nyugalmi tömeg-energia (J)
    pub accretion_inflow: f64,
    /// ∫εṀc² dt — az akkréciós korongból kisugárzott energia (J)
    pub accretion_luminosity: f64,
    /// Σ m_i c² a diszkrét beesésekből (J)
    pub infall_events: f64,
}

#[derive(Debug, Clone)]
pub struct AppliedInfall {
    pub event: InfallEvent,
    pub mass_before: f64,
    pub mass_after: f64,
}

#[derive(Debug, Clone)]
pub struct MassHistory {
    pub samples: Vec<MassSample>,
    /// A fekete lyuk elpárolgott (elérte a végtömeget)
    pub evaporated: bool,
    pub end_mass: f64,
    pub end_time: f64,
    pub energy: EnergyTotals,
    pub applied_infalls: Vec<AppliedInfall>,
    /// A párolgás vége vagy a szimulációs horizont utáni beesések
    pub skipped_infalls: Vec<InfallEvent>,
}

// ---------------------------------------------------------------------------
// ODE-rendszerek
// ---------------------------------------------------------------------------

/// Időben integrált szakasz, normált változókkal:
/// τ = (t − t_a)/T, y_i = X_i/s_i, ahol s_i = |ẋ_i(M_a)|·T a várható változás.
/// Állapot: [δ, E_H, E_abs, E_inflow, L_acc]
#[derive(Clone)]
struct TimeSegment {
    emission: EmissionModel,
    env: Environment,
    m_a: f64,
    span: f64,
    scales: [f64; 5],
    floor_mass: f64,
}

impl TimeSegment {
    fn raw_rates(&self, m: f64) -> [f64; 5] {
        let r = self.env.rates(self.emission, m);
        [
            r.net_mass_rate(self.env.radiative_efficiency),
            r.hawking_power,
            r.absorbed_power,
            r.accretion_inflow * C * C,
            r.accretion_luminosity,
        ]
    }
}

impl System<f64, SVector<f64, 5>> for TimeSegment {
    fn system(&self, _tau: f64, y: &SVector<f64, 5>, dy: &mut SVector<f64, 5>) {
        let m = (self.m_a + y[0] * self.scales[0]).max(self.floor_mass);
        let rates = self.raw_rates(m);
        for i in 0..5 {
            dy[i] = rates[i] * self.span / self.scales[i];
        }
    }
}

/// Párolgó szakasz a végtömegtől visszafelé: v = ln(M/M_end),
/// állapot: [t_hátralévő, E_H, E_abs, E_inflow, L_acc] (mind a végtől felfelé)
#[derive(Clone)]
struct BackwardEvaporation {
    emission: EmissionModel,
    env: Environment,
    end_mass: f64,
}

impl System<f64, SVector<f64, 5>> for BackwardEvaporation {
    fn system(&self, v: f64, _y: &SVector<f64, 5>, dy: &mut SVector<f64, 5>) {
        let m = self.end_mass * v.exp();
        let r = self.env.rates(self.emission, m);
        let f = r.net_mass_rate(self.env.radiative_efficiency);
        // dt/dv = M/(−f) > 0 a párolgó ágon
        let dt_dv = m / (-f);
        dy[0] = dt_dv;
        dy[1] = r.hawking_power * dt_dv;
        dy[2] = r.absorbed_power * dt_dv;
        dy[3] = r.accretion_inflow * C * C * dt_dv;
        dy[4] = r.accretion_luminosity * dt_dv;
    }
}

// ---------------------------------------------------------------------------
// Szakaszok
// ---------------------------------------------------------------------------

struct SegmentResult {
    samples: Vec<MassSample>,
    evaporated: bool,
    end_mass: f64,
    energy: [f64; 4],
}

fn sample(
    emission: EmissionModel,
    env: &Environment,
    time: f64,
    mass: f64,
    remaining: Option<f64>,
) -> MassSample {
    let rates = env.rates(emission, mass);
    MassSample {
        time,
        mass,
        time_to_evaporation: remaining,
        rates,
        net_mass_rate: rates.net_mass_rate(env.radiative_efficiency),
        after_infall: None,
    }
}

/// A végtömegtől M_a-ig visszafelé integrált párolgás (n pont).
/// Visszaadja a hátralévő időt minden rácsponton és az energiákat M_a-nál.
fn backward_evaporation(
    emission: EmissionModel,
    env: &Environment,
    m_a: f64,
    end_mass: f64,
    n: usize,
) -> Result<(Vec<f64>, Vec<SVector<f64, 5>>), SimulationError> {
    let v_top = (m_a / end_mass).ln();
    let n = n.max(2);
    let grid: Vec<f64> = (0..n)
        .map(|j| (v_top * j as f64 / (n - 1) as f64).min(v_top))
        .collect();
    // A párolgó ágon f < 0 kell legyen végig (egyetlen gyök: M < M_eq)
    for &v in &grid {
        let m = end_mass * v.exp();
        if env.net_mass_rate(emission, m) >= 0.0 {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("A párolgó ágon dM/dt ≥ 0 lett M = {m:.3e} kg-nál"),
            });
        }
    }
    let e_end = end_mass * C * C;
    let t_end_scale = end_mass / (-env.net_mass_rate(emission, end_mass));
    let atol = 1e-13 * t_end_scale.min(e_end).max(f64::MIN_POSITIVE);
    let sys = BackwardEvaporation {
        emission,
        env: env.clone(),
        end_mass,
    };
    let ys = integrate_on_grid(&sys, &grid, SVector::<f64, 5>::zeros(), atol)?;
    Ok((grid, ys))
}

#[allow(clippy::too_many_arguments)]
fn run_segment(
    emission: EmissionModel,
    env: &Environment,
    t_a: f64,
    t_b: f64,
    m_a: f64,
    end_mass: f64,
    n: usize,
) -> Result<SegmentResult, SimulationError> {
    let f_a = env.net_mass_rate(emission, m_a);
    let span = t_b - t_a;

    // 1. Párolog-e a szakaszon belül?
    let mut known_remaining: Option<f64> = None;
    if f_a < 0.0 {
        let (grid, ys) = backward_evaporation(emission, env, m_a, end_mass, n)?;
        let top = ys.last().copied().unwrap_or_else(SVector::zeros);
        let lifetime = top[0];
        if lifetime <= span {
            let samples = (0..grid.len())
                .rev()
                .map(|j| {
                    let rem = if j == 0 { 0.0 } else { ys[j][0] };
                    let m = if j == 0 {
                        end_mass
                    } else {
                        end_mass * grid[j].exp()
                    };
                    let m = if j == grid.len() - 1 { m_a } else { m };
                    sample(emission, env, t_a + lifetime - rem, m, Some(rem))
                })
                .collect();
            return Ok(SegmentResult {
                samples,
                evaporated: true,
                end_mass,
                energy: [top[1], top[2], top[3], top[4]],
            });
        }
        known_remaining = Some(lifetime);
    }

    // 2. Időbeli integrálás δ-ban (növekedés vagy lassú párolgás)
    let seg = {
        let mut probe = TimeSegment {
            emission,
            env: env.clone(),
            m_a,
            span,
            scales: [1.0; 5],
            floor_mass: end_mass,
        };
        let r0 = probe.raw_rates(m_a);
        for (scale, rate) in probe.scales.iter_mut().zip(r0) {
            let s = rate.abs() * span;
            *scale = if s > 0.0 && s.is_finite() { s } else { 1.0 };
        }
        probe
    };
    let n = n.max(3);
    let mut grid = vec![0.0];
    // geometriai rács a szakasz elején sűrűbb: τ ∈ [1e-6, 1]
    for k in 0..(n - 1) {
        let x = -6.0 + 6.0 * k as f64 / (n - 2) as f64;
        grid.push(10f64.powf(x));
    }
    let ys = integrate_on_grid(&seg, &grid, SVector::<f64, 5>::zeros(), 1e-12)?;
    let mut samples = Vec::with_capacity(grid.len());
    for (tau, y) in grid.iter().zip(&ys) {
        let dt = tau * span;
        let m = m_a + y[0] * seg.scales[0];
        if !(m.is_finite() && m > end_mass) {
            return Err(SimulationError::NumericalDivergence {
                field: "mass".into(),
                value: m,
                time: t_a + dt,
            });
        }
        let rem = known_remaining.map(|r| (r - dt).max(0.0));
        samples.push(sample(emission, env, t_a + dt, m, rem));
    }
    let last = ys.last().copied().unwrap_or_else(SVector::zeros);
    let end = samples.last().map(|s| s.mass).unwrap_or(m_a);
    Ok(SegmentResult {
        samples,
        evaporated: false,
        end_mass: end,
        energy: [
            last[1] * seg.scales[1],
            last[2] * seg.scales[2],
            last[3] * seg.scales[3],
            last[4] * seg.scales[4],
        ],
    })
}

/// Tiszta Bondi-akkréció (Eddington-korlát nélkül) véges idő alatt divergál:
/// dM/dt = kM² → t_div = 1/(kM). Ezt előre jelezzük, mert a numerikus
/// integrálás egyébként csak a szingularitásnál akadna el.
fn check_bondi_runaway(
    env: &Environment,
    emission: EmissionModel,
    m: f64,
    span: f64,
) -> Result<(), SimulationError> {
    if let crate::black_hole::environment::AccretionModel::Bondi {
        eddington_limited: false,
        ..
    } = env.accretion
    {
        let k = env.accretion_inflow(m) * (1.0 - env.radiative_efficiency) / (m * m);
        if k > 0.0 && env.net_mass_rate(emission, m) > 0.0 {
            let t_div = 1.0 / (k * m);
            if t_div < span {
                return Err(SimulationError::InvalidPhysicalState {
                    reason: format!(
                        "Korlátlan Bondi-akkrécióval a tömeg t ≈ {t_div:.3e} s alatt divergál \
                         (a szimulációs szakasz {span:.3e} s) — kapcsold be az Eddington-korlátot"
                    ),
                });
            }
        }
    }
    Ok(())
}

/// A teljes tömegfejlődés.
///
/// `max_time`: `Some(T)` — T-ig (vagy a párolgás végéig); `None` — a párolgás
/// végéig, ha a fekete lyuk párolog; ha nem, az Univerzum koráig (vagy az
/// utolsó beesésig, ha az később van).
pub fn evolve_mass(
    emission: EmissionModel,
    env: &Environment,
    m0: f64,
    end_mass: f64,
    max_time: Option<f64>,
    steps: usize,
) -> Result<MassHistory, SimulationError> {
    env.validate()
        .map_err(|reason| SimulationError::InvalidPhysicalState { reason })?;
    if !(m0.is_finite() && m0 > end_mass) {
        return Err(SimulationError::InvalidPhysicalState {
            reason: format!(
                "A kezdőtömegnek a végtömeg ({end_mass:.3e} kg) felett kell lennie: {m0}"
            ),
        });
    }
    if let Some(t) = max_time {
        if !(t.is_finite() && t > 0.0) {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("Érvénytelen max_time: {t}"),
            });
        }
    }

    let mut events = env.infall_events.clone();
    events.sort_by(|a, b| a.time.total_cmp(&b.time));
    let mut skipped: Vec<InfallEvent> = Vec::new();
    if let Some(t_max) = max_time {
        let (keep, late): (Vec<_>, Vec<_>) = events.into_iter().partition(|e| e.time <= t_max);
        events = keep;
        skipped.extend(late);
    }
    let n_segments = events.len() + 1;
    let n_per = (steps / n_segments).max(16);

    let mut samples = vec![sample(emission, env, 0.0, m0, None)];
    let mut energy = EnergyTotals::default();
    let mut applied = Vec::new();
    let (mut t, mut m) = (0.0, m0);
    let mut evaporated = false;

    for seg_idx in 0..n_segments {
        let is_last = seg_idx == n_segments - 1;
        let t_b = if !is_last {
            events[seg_idx].time
        } else if let Some(t_max) = max_time {
            t_max
        } else if env.net_mass_rate(emission, m) < 0.0 {
            f64::INFINITY
        } else {
            AGE_OF_UNIVERSE.max(t)
        };
        if t_b > t {
            if t_b.is_finite() {
                check_bondi_runaway(env, emission, m, t_b - t)?;
            }
            let seg = run_segment(emission, env, t, t_b, m, end_mass, n_per)?;
            energy.hawking_radiated += seg.energy[0];
            energy.background_absorbed += seg.energy[1];
            energy.accretion_inflow += seg.energy[2];
            energy.accretion_luminosity += seg.energy[3];
            // az első pont a szakasz kezdete — azt már rögzítettük, csak a
            // (csak most ismert) hátralévő időt pótoljuk rajta
            if let (Some(prev), Some(first)) = (samples.last_mut(), seg.samples.first()) {
                prev.time_to_evaporation = first.time_to_evaporation;
            }
            samples.extend(seg.samples.into_iter().skip(1));
            m = seg.end_mass;
            t = samples.last().map(|s| s.time).unwrap_or(t_b).max(t);
            if seg.evaporated {
                evaporated = true;
                skipped.extend(events.drain(seg_idx.min(events.len())..));
                break;
            }
            t = if t_b.is_finite() { t_b } else { t };
        }
        if !is_last {
            let ev = events[seg_idx].clone();
            let before = m;
            m += ev.mass;
            energy.infall_events += ev.mass * C * C;
            let mut s = sample(emission, env, ev.time, m, None);
            if s.net_mass_rate < 0.0 {
                // a hátralévő idő a következő szakaszban derül ki; itt nem becsüljük
                s.time_to_evaporation = None;
            }
            s.after_infall = Some(if ev.label.is_empty() {
                format!("beesés {:.3e} kg", ev.mass)
            } else {
                ev.label.clone()
            });
            samples.push(s);
            applied.push(AppliedInfall {
                event: ev,
                mass_before: before,
                mass_after: m,
            });
        }
    }

    let end_time = samples.last().map(|s| s.time).unwrap_or(0.0);
    let end = if evaporated { end_mass } else { m };
    Ok(MassHistory {
        samples,
        evaporated,
        end_mass: end,
        end_time,
        energy,
        applied_infalls: applied,
        skipped_infalls: skipped,
    })
}
