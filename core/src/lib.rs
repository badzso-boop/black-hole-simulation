#[cfg(test)]
mod tests;

pub mod black_hole;
pub mod constants;
pub mod error;
pub mod geometry;
pub mod interior;
pub mod quantum;
pub mod radiation;
pub mod time_evolution;
pub mod types;
pub mod units;

// Kényelmes re-export
pub use black_hole::schwarzschild::SchwarzschildBlackHole;
pub use black_hole::{BlackHoleTrait, InteriorModel, RadiationEngine};
pub use error::SimulationError;
pub use interior::norbi::NorbiInterior;
pub use interior::standard::StandardInterior;
pub use quantum::lqc::LQCEquation;
pub use radiation::hawking_engine::HawkingEngine;
pub use types::*;

use black_hole::evolution::evolve_mass;
use constants::{C, M_MIN_LMY, SEMICLASSICAL_MIN_MASS};
use interior::baby_universe::baby_universe_states;
use interior::collapse::OSCollapse;

/// A teljes szimuláció — egyetlen csővezeték a CLI, a Python és a tesztek számára.
///
/// 1. Külső: tömegfejlődés — Hawking-párolgás, háttérsugárzás-elnyelés, akkréció és
///    diszkrét beesések (a párolgás végét az LQC tömegrés, M_min jelzi)
/// 2. Belső: Oppenheimer–Snyder összeomlás saját időben (Standard: klasszikus, a
///    kritikus sűrűségnél megáll; Norbi: LQC visszapattanás + tágulás)
/// 3. Kauzalitás: eljuthat-e a belső tartomány sugárzása a külső megfigyelőhöz
///    (LMY-metrika). Ha nem, a külső spektrum a tiszta Hawking-spektrum.
pub fn run_simulation(
    config: &SimulationConfig,
    payload: serde_json::Value,
) -> Result<SimulationResults, SimulationError> {
    let mass = config.mass;
    if !(mass.is_finite() && mass > 0.0) {
        return Err(SimulationError::InvalidPhysicalState {
            reason: format!("Érvénytelen tömeg: {mass}"),
        });
    }
    if mass <= M_MIN_LMY {
        return Err(SimulationError::MassGap {
            mass,
            m_min: M_MIN_LMY,
        });
    }
    let mut warnings = Vec::new();

    // --- Külső: tömegfejlődés (Hawking + háttér-elnyelés + akkréció + beesések) ---
    let env = &config.environment;
    let history = evolve_mass(
        config.emission_model,
        env,
        mass,
        M_MIN_LMY,
        config.max_time,
        config.steps,
    )?;
    let mut bh = SchwarzschildBlackHole::with_emission(mass, config.emission_model)?;
    let engine = HawkingEngine::new();
    let mut timeline = Vec::with_capacity(history.samples.len());
    for sample in &history.samples {
        bh.set_state(sample.mass, sample.time)?;
        timeline.push(TimeStep {
            time: sample.time,
            time_to_evaporation: sample.time_to_evaporation,
            mass: sample.mass,
            temperature: bh.hawking_temperature()?,
            entropy: bh.bekenstein_entropy(),
            semiclassical_valid: sample.mass > SEMICLASSICAL_MIN_MASS,
            net_mass_rate: sample.net_mass_rate,
            absorbed_power: sample.rates.absorbed_power,
            accretion_inflow: sample.rates.accretion_inflow,
            after_infall: sample.after_infall.clone(),
            spectrum: engine.compute_spectrum(&bh)?,
        });
    }
    if timeline.iter().any(|t| !t.semiclassical_valid) {
        warnings.push(format!(
            "A párolgás utolsó szakaszában M < 10 m_P ({:.3e} kg): itt a szemiklasszikus \
             Hawking-képlet érvényessége kérdéses (semiclassical_valid = false)",
            SEMICLASSICAL_MIN_MASS
        ));
    }
    let equilibrium_mass = env.equilibrium_mass(config.emission_model, M_MIN_LMY * 1.0001, 1e45);
    if !history.evaporated {
        let last = timeline.last().map(|t| t.net_mass_rate).unwrap_or(0.0);
        warnings.push(format!(
            "A fekete lyuk a szimulációs horizontig ({:.3e} s) nem párolgott el \
             (végtömeg {:.6e} kg, dM/dt = {:+.3e} kg/s){}",
            history.end_time,
            history.end_mass,
            last,
            match equilibrium_mass {
                Some(m_eq) if history.end_mass > m_eq => format!(
                    "; M > M_eq = {m_eq:.3e} kg: a környezetéből több energiát nyel el, \
                     mint amennyit Hawking-sugárzásként kibocsát — nő"
                ),
                _ => String::new(),
            }
        ));
    }
    for ev in &history.skipped_infalls {
        warnings.push(format!(
            "A t = {:.3e} s-os beesés ({:.3e} kg) kimaradt: a fekete lyuk addigra elpárolgott \
             vagy az esemény a szimulációs horizont után van",
            ev.time, ev.mass
        ));
    }

    // --- Energiamérleg ---
    let e = &history.energy;
    let e0 = mass * C * C;
    let e_end = history.end_mass * C * C;
    let income =
        e.infall_events + e.background_absorbed + e.accretion_inflow - e.accretion_luminosity;
    let energy = EnergyLedger {
        initial_energy: e0,
        final_exterior_energy: e_end,
        hawking_radiated: e.hawking_radiated,
        background_absorbed: e.background_absorbed,
        accretion_inflow: e.accretion_inflow,
        accretion_luminosity: e.accretion_luminosity,
        infall_events: e.infall_events,
        relative_error: ((e0 + income) - (e_end + e.hawking_radiated)).abs()
            / (e0 + income.max(0.0)),
    };

    // --- A belső tartomány „táplálása" (Norbi-dokumentáció 2. fázis) ---
    let feeding_events: Vec<FeedingEvent> = history
        .applied_infalls
        .iter()
        .map(|a| {
            let m = a.mass_before;
            let r_s = 2.0 * constants::G * m / (C * C);
            let r0 = config.initial_radius_rs * r_s;
            let r_plus = geometry::LmyMetric::new(m)
                .horizons()
                .map(|h| h.r_plus)
                .unwrap_or(r_s);
            FeedingEvent {
                exterior_time: a.event.time,
                label: a.event.label.clone(),
                mass: a.event.mass,
                mass_before: a.mass_before,
                mass_after: a.mass_after,
                proper_time_to_horizon: (2.0 / 3.0) * (r0.powf(1.5) - r_plus.powf(1.5))
                    / (2.0 * constants::G * m).sqrt(),
            }
        })
        .collect();
    let continuous = e.background_absorbed + e.accretion_inflow - e.accretion_luminosity;
    let interior_feeding = InteriorFeeding {
        initial_energy: e0,
        events: feeding_events,
        continuous_inflow_energy: continuous,
        total_infallen_energy: e.infall_events + continuous,
        note: "Könyvelés: ennyi energia lépett át befelé a külső horizonton. A kezdeti \
               porgömb (és Norbi módban a belőle lett bébiuniverzum) M0·c² energiát hordoz; \
               a később beeső anyag az LMY-geometriában a belső (Cauchy-)horizont felé \
               tart, amely a visszapattant tartomány múltjában/oldalán van — hogy ez az \
               anyag ugyanabba a bébiuniverzumba jut-e, nincs modellezve, és a belső \
               horizontok ismerten instabilak a késői beáramlással szemben \
               (tömeg-infláció, Poisson & Israel 1990). A Hawking-párolgás negatív \
               energiájú beáramlásának belső elszámolása szintén nyitott kérdés."
            .into(),
    };
    if !history.applied_infalls.is_empty() {
        warnings.push(
            "Beesések: a beeső tömeg a külső horizontot növeli (Δr_s = 2GΔM/c²); a belső \
             sorsáról lásd interior_feeding.note."
                .into(),
        );
    }

    // --- Belső: összeomlás ---
    let collapse = OSCollapse::new(mass, config.initial_radius_rs)?;
    let interior_model: Box<dyn InteriorModel> = if config.norbi_mode {
        Box::new(NorbiInterior::new())
    } else {
        Box::new(StandardInterior::new())
    };
    let interior = interior_model.trajectory(&collapse, config.interior_steps);
    let baby_universe = if interior_model.continues_through_bounce() {
        baby_universe_states(&collapse, &interior)
    } else {
        Vec::new()
    };

    // --- Kauzalitás ---
    let causal_channel = geometry::causal_channel(mass)?;
    if config.norbi_mode && !causal_channel.exists {
        warnings.push(
            "Norbi-mód: a bébiuniverzum széle kauzálisan le van választva a külső \
             megfigyelőről (lásd causal_channel.reason) — az él-sugárzás a külső \
             spektrumhoz nem járul hozzá; a külső spektrum a Hawking-spektrum."
                .into(),
        );
    }
    if config.norbi_mode && causal_channel.exists {
        // Az LMY-geometriában M > M_min-re ez nem fordulhat elő; ha mégis, azt
        // nem kezeljük csendben (a két óra közti leképezés nincs modellezve).
        return Err(SimulationError::InvalidPhysicalState {
            reason: "Váratlan kauzális csatorna: a belső→külső leképezés nincs implementálva"
                .into(),
        });
    }

    Ok(SimulationResults {
        schema_version: SCHEMA_VERSION.to_string(),
        config: config.clone(),
        timeline,
        evaporation_complete: history.evaporated,
        end_mass: history.end_mass,
        end_time: history.end_time,
        equilibrium_mass,
        interior,
        baby_universe,
        causal_channel,
        energy,
        interior_feeding,
        warnings,
        payload,
    })
}

// ---------------------------------------------------------------------------
// PyO3 Python binding
// ---------------------------------------------------------------------------

#[cfg(feature = "python-ext")]
use pyo3::prelude::*;

/// Python belépési pont: konfiguráció és payload JSON-ben, eredmény JSON-ben.
#[cfg(feature = "python-ext")]
#[pyfunction]
fn run_simulation_py(config_json: &str, payload_json: &str) -> PyResult<String> {
    let config: SimulationConfig = serde_json::from_str(config_json)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hibás konfiguráció: {e}")))?;
    let payload: serde_json::Value = serde_json::from_str(payload_json)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hibás payload: {e}")))?;
    let result = std::panic::catch_unwind(|| run_simulation(&config, payload));
    match result {
        Ok(Ok(results)) => serde_json::to_string(&results)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
        Ok(Err(e)) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
            "Szimulációs hiba: {e}"
        ))),
        Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
            "Váratlan belső hiba (Rust panic)",
        )),
    }
}

#[cfg(feature = "python-ext")]
#[pymodule]
fn black_hole_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_simulation_py, m)?)?;
    m.add("SCHEMA_VERSION", SCHEMA_VERSION)?;
    Ok(())
}
