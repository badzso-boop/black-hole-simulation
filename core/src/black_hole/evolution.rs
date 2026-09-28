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
//!
//! **Spin (a*):** a tömeg mellett a dimenziótlan spin is fejlődik (Hawking-
//! lepörgés, akkréciós felpörgetés, izotróp elnyelés, radiális beesés — lásd
//! `Environment::rates`). Az időben integrált szakaszon a* egyszerűen egy
//! további állapotváltozó. A visszafelé integrált párolgó szakaszon a*(M)-et
//! előbb egy előre irányú menetben ln M szerint kiintegráljuk (a tömeg ott
//! monoton), és a visszafelé menet ebből interpolál.

use ode_solvers::{SVector, System};

use crate::black_hole::environment::{Environment, InfallEvent, Rates};
use crate::black_hole::kerr::THORNE_SPIN_LIMIT;
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
    /// Dimenziótlan spin a* = Jc/(GM²)
    pub spin: f64,
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
    pub spin_before: f64,
    pub spin_after: f64,
}

#[derive(Debug, Clone)]
pub struct MassHistory {
    pub samples: Vec<MassSample>,
    /// A fekete lyuk elpárolgott (elérte a végtömeget)
    pub evaporated: bool,
    pub end_mass: f64,
    pub end_spin: f64,
    pub end_time: f64,
    pub energy: EnergyTotals,
    pub applied_infalls: Vec<AppliedInfall>,
    /// A párolgás vége vagy a szimulációs horizont utáni beesések
    pub skipped_infalls: Vec<InfallEvent>,
}

// ---------------------------------------------------------------------------
// ODE-rendszerek
// ---------------------------------------------------------------------------

/// A spin legnagyobb megengedett értéke a numerikában (a* < 1 kell a horizonthoz)
const SPIN_CAP: f64 = 0.9999;

fn clamp_spin(a: f64) -> f64 {
    a.clamp(0.0, SPIN_CAP)
}

/// Időben integrált szakasz, normált változókkal:
/// τ = (t − t_a)/T, y_i = X_i/s_i, ahol s_i = |ẋ_i(M_a)|·T a várható változás.
/// Állapot: [δ, E_H, E_abs, E_inflow, L_acc, a*] — a* nyersen (nem normálva)
#[derive(Clone)]
struct TimeSegment {
    emission: EmissionModel,
    env: Environment,
    m_a: f64,
    span: f64,
    scales: [f64; 5],
    floor_mass: f64,
    /// Az akkréció ennél jobban nem pörgethet fel: max(Thorne-határ, kezdeti spin)
    spin_cap: f64,
}

impl TimeSegment {
    fn raw_rates(&self, m: f64, spin: f64) -> ([f64; 5], f64) {
        let r = self.env.rates(self.emission, m, spin);
        (
            [
                r.net_mass_rate(),
                r.hawking_power,
                r.absorbed_power,
                r.accretion_inflow * C * C,
                r.accretion_luminosity,
            ],
            r.spin_rate,
        )
    }
}

impl System<f64, SVector<f64, 6>> for TimeSegment {
    fn system(&self, _tau: f64, y: &SVector<f64, 6>, dy: &mut SVector<f64, 6>) {
        let m = (self.m_a + y[0] * self.scales[0]).max(self.floor_mass);
        let (rates, spin_rate) = self.raw_rates(m, clamp_spin(y[5].min(self.spin_cap)));
        for i in 0..5 {
            dy[i] = rates[i] * self.span / self.scales[i];
        }
        let at_cap = y[5] >= self.spin_cap && spin_rate > 0.0;
        dy[5] = if at_cap { 0.0 } else { spin_rate * self.span };
    }
}

/// a*(M) táblázat a párolgó ágon: v = ln(M/M_end) szerint növekvő rács
#[derive(Clone, Default)]
struct SpinTable {
    v: Vec<f64>,
    spin: Vec<f64>,
}

impl SpinTable {
    fn at(&self, v: f64) -> f64 {
        if self.v.is_empty() {
            return 0.0;
        }
        let i = self.v.partition_point(|&x| x < v);
        if i == 0 {
            return self.spin[0];
        }
        if i >= self.v.len() {
            return *self.spin.last().unwrap_or(&0.0);
        }
        let (v0, v1) = (self.v[i - 1], self.v[i]);
        let w = if v1 > v0 { (v - v0) / (v1 - v0) } else { 0.0 };
        self.spin[i - 1] + w * (self.spin[i] - self.spin[i - 1])
    }
}

/// Előre irányú menet a párolgó ágon: u = ln(M_a/M), da*/du = −(da*/dt)·M/f
#[derive(Clone)]
struct SpinAlongMass {
    emission: EmissionModel,
    env: Environment,
    m_a: f64,
}

impl System<f64, SVector<f64, 1>> for SpinAlongMass {
    fn system(&self, u: f64, y: &SVector<f64, 1>, dy: &mut SVector<f64, 1>) {
        let m = self.m_a * (-u).exp();
        let r = self.env.rates(self.emission, m, clamp_spin(y[0]));
        let f = r.net_mass_rate();
        dy[0] = if f < 0.0 { -r.spin_rate * m / f } else { 0.0 };
    }
}

/// Párolgó szakasz a végtömegtől visszafelé: v = ln(M/M_end),
/// állapot: [t_hátralévő, E_H, E_abs, E_inflow, L_acc] (mind a végtől felfelé)
#[derive(Clone)]
struct BackwardEvaporation {
    emission: EmissionModel,
    env: Environment,
    end_mass: f64,
    spin: SpinTable,
}

impl System<f64, SVector<f64, 5>> for BackwardEvaporation {
    fn system(&self, v: f64, _y: &SVector<f64, 5>, dy: &mut SVector<f64, 5>) {
        let m = self.end_mass * v.exp();
        let r = self.env.rates(self.emission, m, self.spin.at(v));
        let f = r.net_mass_rate();
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
    end_spin: f64,
    energy: [f64; 4],
}

fn sample(
    emission: EmissionModel,
    env: &Environment,
    time: f64,
    mass: f64,
    spin: f64,
    remaining: Option<f64>,
) -> MassSample {
    let rates = env.rates(emission, mass, spin);
    MassSample {
        time,
        mass,
        spin,
        time_to_evaporation: remaining,
        rates,
        net_mass_rate: rates.net_mass_rate(),
        after_infall: None,
    }
}

/// a*(M) a párolgó ágon M_a-tól a végtömegig (előre irányú menet ln M-ben).
/// Ha a spin 0 és semmi nem pörgeti fel, nincs mit integrálni.
fn spin_table(
    emission: EmissionModel,
    env: &Environment,
    m_a: f64,
    spin_a: f64,
    end_mass: f64,
    n: usize,
) -> Result<SpinTable, SimulationError> {
    let v_top = (m_a / end_mass).ln();
    if spin_a <= 0.0 && !env.disk_accretion {
        return Ok(SpinTable {
            v: vec![0.0, v_top],
            spin: vec![0.0, 0.0],
        });
    }
    let n_fine = (8 * n).max(2000);
    let u_grid: Vec<f64> = (0..n_fine)
        .map(|j| (v_top * j as f64 / (n_fine - 1) as f64).min(v_top))
        .collect();
    let sys = SpinAlongMass {
        emission,
        env: env.clone(),
        m_a,
    };
    let ys = integrate_on_grid(&sys, &u_grid, SVector::<f64, 1>::new(spin_a), 1e-12)?;
    // v = v_top − u, növekvő sorrendbe fordítva
    let v: Vec<f64> = u_grid.iter().rev().map(|u| v_top - u).collect();
    let spin: Vec<f64> = ys.iter().rev().map(|y| clamp_spin(y[0])).collect();
    Ok(SpinTable { v, spin })
}

/// (rács, állapotok a rácson, spin-tábla)
type BackwardSolution = (Vec<f64>, Vec<SVector<f64, 5>>, SpinTable);

/// A végtömegtől M_a-ig visszafelé integrált párolgás (n pont).
/// Visszaadja a rácsot, a hátralévő időt/energiákat minden rácsponton és a spin-táblát.
fn backward_evaporation(
    emission: EmissionModel,
    env: &Environment,
    m_a: f64,
    spin_a: f64,
    end_mass: f64,
    n: usize,
) -> Result<BackwardSolution, SimulationError> {
    let v_top = (m_a / end_mass).ln();
    let n = n.max(2);
    let grid: Vec<f64> = (0..n)
        .map(|j| (v_top * j as f64 / (n - 1) as f64).min(v_top))
        .collect();
    let table = spin_table(emission, env, m_a, spin_a, end_mass, n)?;
    // A párolgó ágon f < 0 kell legyen végig (egyetlen gyök: M < M_eq)
    for &v in &grid {
        let m = end_mass * v.exp();
        if env.net_mass_rate_spin(emission, m, table.at(v)) >= 0.0 {
            return Err(SimulationError::InvalidPhysicalState {
                reason: format!("A párolgó ágon dM/dt ≥ 0 lett M = {m:.3e} kg-nál"),
            });
        }
    }
    let e_end = end_mass * C * C;
    let t_end_scale = end_mass / (-env.net_mass_rate_spin(emission, end_mass, table.at(0.0)));
    let atol = 1e-13 * t_end_scale.min(e_end).max(f64::MIN_POSITIVE);
    let sys = BackwardEvaporation {
        emission,
        env: env.clone(),
        end_mass,
        spin: table.clone(),
    };
    let ys = integrate_on_grid(&sys, &grid, SVector::<f64, 5>::zeros(), atol)?;
    Ok((grid, ys, table))
}

#[allow(clippy::too_many_arguments)]
fn run_segment(
    emission: EmissionModel,
    env: &Environment,
    t_a: f64,
    t_b: f64,
    m_a: f64,
    spin_a: f64,
    end_mass: f64,
    n: usize,
) -> Result<SegmentResult, SimulationError> {
    let f_a = env.net_mass_rate_spin(emission, m_a, spin_a);
    let span = t_b - t_a;

    // 1. Párolog-e a szakaszon belül?
    let mut known_remaining: Option<f64> = None;
    if f_a < 0.0 {
        let (grid, ys, table) = backward_evaporation(emission, env, m_a, spin_a, end_mass, n)?;
        let top = ys.last().copied().unwrap_or_else(SVector::zeros);
        let lifetime = top[0];
        if lifetime <= span {
            let samples = (0..grid.len())
                .rev()
                .map(|j| {
                    let rem = if j == 0 { 0.0 } else { ys[j][0] };
                    let (m, a) = if j == grid.len() - 1 {
                        (m_a, spin_a)
                    } else if j == 0 {
                        (end_mass, table.at(0.0))
                    } else {
                        (end_mass * grid[j].exp(), table.at(grid[j]))
                    };
                    sample(emission, env, t_a + lifetime - rem, m, a, Some(rem))
                })
                .collect();
            return Ok(SegmentResult {
                samples,
                evaporated: true,
                end_mass,
                end_spin: table.at(0.0),
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
            spin_cap: THORNE_SPIN_LIMIT.max(spin_a),
        };
        let (r0, _) = probe.raw_rates(m_a, spin_a);
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
    let mut y0 = SVector::<f64, 6>::zeros();
    y0[5] = spin_a;
    let ys = integrate_on_grid(&seg, &grid, y0, 1e-12)?;
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
        samples.push(sample(
            emission,
            env,
            t_a + dt,
            m,
            clamp_spin(y[5].min(seg.spin_cap)),
            rem,
        ));
    }
    let last = ys.last().copied().unwrap_or_else(SVector::zeros);
    let end = samples.last().map(|s| s.mass).unwrap_or(m_a);
    Ok(SegmentResult {
        samples,
        evaporated: false,
        end_mass: end,
        end_spin: clamp_spin(last[5].min(seg.spin_cap)),
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
    spin: f64,
    span: f64,
) -> Result<(), SimulationError> {
    if let crate::black_hole::environment::AccretionModel::Bondi {
        eddington_limited: false,
        ..
    } = env.accretion
    {
        let k = env.accretion_inflow_spin(m, spin) * (1.0 - env.efficiency(spin)) / (m * m);
        if k > 0.0 && env.net_mass_rate_spin(emission, m, spin) > 0.0 {
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
    spin0: f64,
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
    if !(0.0..1.0).contains(&spin0) {
        return Err(SimulationError::InvalidPhysicalState {
            reason: format!("A spinnek 0 ≤ a* < 1 kell legyen, kapott: {spin0}"),
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

    let spin0 = clamp_spin(spin0);
    let mut samples = vec![sample(emission, env, 0.0, m0, spin0, None)];
    let mut energy = EnergyTotals::default();
    let mut applied = Vec::new();
    let (mut t, mut m, mut a) = (0.0, m0, spin0);
    let mut evaporated = false;

    for seg_idx in 0..n_segments {
        let is_last = seg_idx == n_segments - 1;
        let t_b = if !is_last {
            events[seg_idx].time
        } else if let Some(t_max) = max_time {
            t_max
        } else if env.net_mass_rate_spin(emission, m, a) < 0.0 {
            f64::INFINITY
        } else {
            AGE_OF_UNIVERSE.max(t)
        };
        if t_b > t {
            if t_b.is_finite() {
                check_bondi_runaway(env, emission, m, a, t_b - t)?;
            }
            let seg = run_segment(emission, env, t, t_b, m, a, end_mass, n_per)?;
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
            a = seg.end_spin;
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
            let (before, spin_before) = (m, a);
            m += ev.mass;
            // radiális beesés: J nem változik → a* ∝ 1/M²
            a = clamp_spin(a * (before / m).powi(2));
            energy.infall_events += ev.mass * C * C;
            let mut s = sample(emission, env, ev.time, m, a, None);
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
                spin_before,
                spin_after: a,
            });
        }
    }

    let end_time = samples.last().map(|s| s.time).unwrap_or(0.0);
    let end = if evaporated { end_mass } else { m };
    Ok(MassHistory {
        samples,
        evaporated,
        end_mass: end,
        end_spin: a,
        end_time,
        energy,
        applied_infalls: applied,
        skipped_infalls: skipped,
    })
}
