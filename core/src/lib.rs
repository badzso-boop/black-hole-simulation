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

/// Publikus API Tauri és más Rust crate-ek számára
pub fn run_simulation(mass: f64, config: SimulationConfig, _payload_json: &str) -> Result<SimulationResults, SimulationError> {
    use radiation::hawking_engine::HawkingEngine;

    let mut bh = SchwarzschildBlackHole::new(mass)?;
    let engine = HawkingEngine::new();
    let mut results = SimulationResults::new(config);
    let dt = 1e-10_f64;
    let steps = 100;

    for _ in 0..steps {
        let temp = bh.hawking_temperature()?;
        let entropy = bh.bekenstein_entropy();
        let spectrum = engine.compute_spectrum(&bh)?;
        let interior = InteriorState::default();

        results.timeline.push(TimeStep {
            time: bh.age(),
            mass: bh.mass(),
            temperature: temp,
            entropy,
            spectrum,
            interior,
        });

        if engine.evolve_step(&mut bh, dt).is_err() {
            results.evaporation_complete = true;
            break;
        }
    }

    Ok(results)
}

/// Egyszerűsített szimulációs futtatás — CLI és Python számára
#[allow(dead_code)]
fn run_simulation_json(mass: f64, norbi_mode: bool) -> Result<String, SimulationError> {
    use radiation::hawking_engine::HawkingEngine;

    let mut bh = SchwarzschildBlackHole::new(mass)?;
    let engine = HawkingEngine::new();
    let config = if norbi_mode {
        SimulationConfig::standard()
    } else {
        let mut c = SimulationConfig::standard();
        c.norbi_mode = false;
        c
    };

    let mut results = SimulationResults::new(config);
    let dt = 1e-10_f64;
    let steps = 100;

    for _ in 0..steps {
        let temp = bh.hawking_temperature()?;
        let entropy = bh.bekenstein_entropy();
        let spectrum = engine.compute_spectrum(&bh)?;
        let interior = InteriorState::default();

        results.timeline.push(TimeStep {
            time: bh.age(),
            mass: bh.mass(),
            temperature: temp,
            entropy,
            spectrum,
            interior,
        });

        if engine.evolve_step(&mut bh, dt).is_err() {
            results.evaporation_complete = true;
            break;
        }
    }

    Ok(serde_json::to_string(&results).unwrap_or_default())
}

#[cfg(feature = "python-ext")]
#[pymodule]
fn black_hole_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_simulation_py, m)?)?;
    Ok(())
}
