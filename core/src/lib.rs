#[cfg(test)]
mod tests;

pub mod black_hole;
pub mod constants;
pub mod error;
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
pub use quantum::island::{IslandFormula, RadiationState};
pub use quantum::lqc::LQCEquation;
pub use radiation::hawking_engine::HawkingEngine;
pub use types::*;

// ---------------------------------------------------------------------------
// PyO3 Python binding
// ---------------------------------------------------------------------------

#[cfg(feature = "python-ext")]
use pyo3::prelude::*;

#[cfg(feature = "python-ext")]
#[pyfunction]
fn run_simulation_py(mass: f64, norbi_mode: bool, _payload_json: &str) -> PyResult<String> {
    let result = std::panic::catch_unwind(|| run_simulation_json(mass, norbi_mode));
    match result {
        Ok(Ok(json)) => Ok(json),
        Ok(Err(e)) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
            "Szimulációs hiba: {e}"
        ))),
        Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
            "Váratlan belső hiba (Rust panic)",
        )),
    }
}

/// A külső (Hawking-párolgási) idővonal: tömeg és idő mintapontok.
/// Végtömeg: az LQC tömegrés (M_min ≈ 0.83 m_P), ez alatt nincs horizont.
fn exterior_history(
    mass: f64,
    config: &SimulationConfig,
) -> Result<black_hole::evaporation::EvaporationHistory, SimulationError> {
    black_hole::evaporation::evaporation_history(
        config.emission_model,
        mass,
        constants::M_MIN_LMY,
        config.steps,
    )
}

/// Publikus API más Rust crate-ek számára
pub fn run_simulation(
    mass: f64,
    config: SimulationConfig,
    _payload_json: &str,
) -> Result<SimulationResults, SimulationError> {
    let history = exterior_history(mass, &config)?;
    let mut bh = SchwarzschildBlackHole::with_emission(mass, config.emission_model)?;
    let engine = HawkingEngine::new();
    let mut results = SimulationResults::new(config);

    for sample in &history.samples {
        bh.set_state(sample.mass, sample.time)?;
        results.timeline.push(TimeStep {
            time: bh.age(),
            mass: bh.mass(),
            temperature: bh.hawking_temperature()?,
            entropy: bh.bekenstein_entropy(),
            spectrum: engine.compute_spectrum(&bh)?,
            interior: InteriorState::default(),
        });
    }
    results.evaporation_complete = history.reached_end_mass;
    Ok(results)
}

/// Egyszerűsített szimulációs futtatás — CLI és Python számára
#[allow(dead_code)]
fn run_simulation_json(mass: f64, norbi_mode: bool) -> Result<String, SimulationError> {
    use constants::T_PLANCK;
    use interior::baby_universe::BabyUniverse;
    use interior::norbi::NorbiInterior;
    use interior::standard::StandardInterior;

    const BOUNCE_TRANSIENT_STEPS: usize = 80;
    const BOUNCE_TRANSIENT_DT: f64 = T_PLANCK;

    let config = {
        let mut c = SimulationConfig::standard();
        c.norbi_mode = norbi_mode;
        c
    };
    let history = exterior_history(mass, &config)?;
    let mut bh = SchwarzschildBlackHole::with_emission(mass, config.emission_model)?;
    let engine = HawkingEngine::new();
    let mut results = SimulationResults::new(config);

    let mut norbi_interior = NorbiInterior::new();
    let mut std_interior = StandardInterior::new();

    // Reprezentatív részecske a belső szimulációhoz (a 3. fázisban a valódi
    // Oppenheimer–Snyder összeomlás váltja fel)
    let particle = types::Particle {
        mass: mass * 0.001,
        energy: mass * 0.001 * constants::C * constants::C,
        angular_momentum: 0.0,
        initial_radius: bh.schwarzschild_radius() * 10.0,
        particle_type: types::ParticleType::Proton,
    };

    let mut bounce_transient_recorded = false;
    let mut prev_time = 0.0;

    for sample in &history.samples {
        bh.set_state(sample.mass, sample.time)?;
        let dt = (sample.time - prev_time).max(0.0);
        prev_time = sample.time;
        let temp = bh.hawking_temperature()?;
        let entropy = bh.bekenstein_entropy();
        let spectrum = engine.compute_spectrum(&bh)?;

        let (spectrum, interior) = if norbi_mode {
            let interior = norbi_interior
                .simulate_step(&particle, &bh, dt)
                .unwrap_or_default();
            if interior.bounce_occurred && !bounce_transient_recorded {
                results.bounce_transient = BabyUniverse::post_bounce_transient(
                    interior.density,
                    BOUNCE_TRANSIENT_STEPS,
                    BOUNCE_TRANSIENT_DT,
                );
                bounce_transient_recorded = true;
            }
            let spectrum = match &interior.baby_universe {
                Some(bu_state) => engine
                    .compute_spectrum_norbi(&bh, bu_state)
                    .unwrap_or(spectrum),
                None => spectrum,
            };
            (spectrum, interior)
        } else {
            let interior = std_interior
                .simulate_step(&particle, &bh, dt)
                .unwrap_or_default();
            (spectrum, interior)
        };

        results.timeline.push(TimeStep {
            time: bh.age(),
            mass: bh.mass(),
            temperature: temp,
            entropy,
            spectrum,
            interior,
        });
    }
    results.evaporation_complete = history.reached_end_mass;

    Ok(serde_json::to_string(&results).unwrap_or_default())
}

#[cfg(feature = "python-ext")]
#[pymodule]
fn black_hole_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_simulation_py, m)?)?;
    Ok(())
}
