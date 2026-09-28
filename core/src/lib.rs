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

use black_hole::evaporation::evaporation_history;
use constants::{C, M_MIN_LMY, SEMICLASSICAL_MIN_MASS};
use interior::baby_universe::baby_universe_states;
use interior::collapse::OSCollapse;

/// A teljes szimuláció — egyetlen csővezeték a CLI, a Python és a tesztek számára.
///
/// 1. Külső: Hawking-párolgás M0-tól a tömegrésig (M_min), a tömegben log-rácson
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

    // --- Külső: párolgás ---
    let history = evaporation_history(config.emission_model, mass, M_MIN_LMY, config.steps)?;
    let mut bh = SchwarzschildBlackHole::with_emission(mass, config.emission_model)?;
    let engine = HawkingEngine::new();
    let mut timeline = Vec::with_capacity(history.samples.len());
    for sample in &history.samples {
        bh.set_state(sample.mass, sample.time)?;
        timeline.push(TimeStep {
            time: sample.time,
            time_to_evaporation: sample.remaining,
            mass: sample.mass,
            temperature: bh.hawking_temperature()?,
            entropy: bh.bekenstein_entropy(),
            semiclassical_valid: sample.mass > SEMICLASSICAL_MIN_MASS,
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

    // --- Energiamérleg: ∫P dt a hátralévő idő (t_h) szerint ---
    // Állandó α-ra P ∝ t_h^(−2/3) (M_vég → 0 határesetben), így intervallumonként
    // P ≈ A·t_h^(−2/3), ∫P dt = 3A·(t_h0^(1/3) − t_h1^(1/3)); A a két végpont
    // P·t_h^(2/3) értékének mértani közepe. A log-rácson ez sokkal pontosabb a
    // trapéz-szabálynál (ami 100 lépésnél ~28% hibát adott).
    let radiated: f64 = timeline
        .windows(2)
        .map(|w| {
            let (p0, r0) = (w[0].spectrum.total_power, w[0].time_to_evaporation);
            let (p1, r1) = (w[1].spectrum.total_power, w[1].time_to_evaporation);
            if r1 > 0.0 {
                let a = (p0 * r0.powf(2.0 / 3.0) * p1 * r1.powf(2.0 / 3.0)).sqrt();
                3.0 * a * (r0.cbrt() - r1.cbrt())
            } else {
                // utolsó szakasz (t_h → 0): trapéz — itt P véges, Δt apró
                0.5 * (p0 + p1) * (r0 - r1)
            }
        })
        .sum();
    let e0 = mass * C * C;
    let e_end = history.end_mass * C * C;
    let energy = EnergyLedger {
        initial_energy: e0,
        final_exterior_energy: e_end,
        radiated_energy: radiated,
        relative_error: (e0 - e_end - radiated).abs() / e0,
        interior_energy: e0,
    };

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
        evaporation_complete: history.reached_end_mass,
        end_mass: history.end_mass,
        interior,
        baby_universe,
        causal_channel,
        energy,
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
