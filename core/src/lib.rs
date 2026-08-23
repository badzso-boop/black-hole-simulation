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
    let steps = 100_usize;
    // dt = t_evap / steps — így minden futtatás lefedi a teljes elpárlást
    let dt = (bh.evaporation_time() / steps as f64).max(1e-100);

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
    use constants::T_PLANCK;
    use interior::baby_universe::BabyUniverse;
    use interior::norbi::NorbiInterior;
    use interior::standard::StandardInterior;
    use radiation::hawking_engine::HawkingEngine;

    const BOUNCE_TRANSIENT_STEPS: usize = 80;
    const BOUNCE_TRANSIENT_DT: f64 = T_PLANCK; // a bébiuniverzum saját, Planck-idő
                                                // nagyságrendű órája — lásd
                                                // BabyUniverse::post_bounce_transient

    let mut bh = SchwarzschildBlackHole::new(mass)?;
    let engine = if norbi_mode { HawkingEngine::norbi() } else { HawkingEngine::standard() };
    let config = {
        let mut c = SimulationConfig::standard();
        c.norbi_mode = norbi_mode;
        c
    };

    let mut results = SimulationResults::new(config);
    let steps = 100_usize;
    let dt = (bh.evaporation_time() / steps as f64).max(1e-100);

    // Belső modell: Norbi vagy Standard
    let mut norbi_interior = NorbiInterior::new();
    let mut std_interior   = StandardInterior::new();

    // Reprezentatív részecske a belső szimulációhoz
    let particle = types::Particle {
        mass: mass * 0.001,          // beeső részecske tömege (BH tömegének 0.1%-a)
        energy: mass * 0.001 * 9e16, // E = mc²
        angular_momentum: 0.0,
        initial_radius: bh.schwarzschild_radius() * 10.0,
        particle_type: types::ParticleType::Proton,
    };

    let mut bounce_transient_recorded = false;

    for _ in 0..steps {
        let temp    = bh.hawking_temperature()?;
        let entropy = bh.bekenstein_entropy();
        let spectrum = engine.compute_spectrum(&bh)?;

        // Belső fizika lépés + Norbi spektrum bekötése
        let (spectrum, interior) = if norbi_mode {
            let interior = norbi_interior.simulate_step(&particle, &bh, dt).unwrap_or_default();

            // A visszapattanás pillanatában rögzítjük a bébiuniverzum saját,
            // Planck-idő nagyságrendű órája szerinti finom tranzienst —
            // a külső `dt` (a teljes elpárlási idő százada) sok nagyságrenddel
            // durvább annál, mint amin a bounce dinamikája ténylegesen lezajlik.
            if interior.bounce_occurred && !bounce_transient_recorded {
                results.bounce_transient = BabyUniverse::post_bounce_transient(
                    interior.density,
                    BOUNCE_TRANSIENT_STEPS,
                    BOUNCE_TRANSIENT_DT,
                );
                bounce_transient_recorded = true;
            }

            let spectrum = match &interior.baby_universe {
                Some(bu_state) => engine.compute_spectrum_norbi(&bh, bu_state)
                    .unwrap_or(spectrum),
                None => spectrum,
            };
            (spectrum, interior)
        } else {
            let interior = std_interior.simulate_step(&particle, &bh, dt).unwrap_or_default();
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
