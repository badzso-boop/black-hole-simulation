use black_hole_core::{SimulationConfig, SimulationResults, SimMode};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CurrentState {
    pub running: bool,
    pub step: usize,
    pub mass: f64,
    pub temperature: f64,
    pub norbi_mode: bool,
}

pub type AppState = Arc<Mutex<AppData>>;

pub struct AppData {
    pub running: bool,
    pub step: usize,
    pub last_results: Option<SimulationResults>,
    pub norbi_mode: bool,
}

impl AppData {
    pub fn new() -> Self {
        Self {
            running: false,
            step: 0,
            last_results: None,
            norbi_mode: false,
        }
    }
}

#[tauri::command]
pub async fn run_simulation(
    mass: f64,
    norbi_mode: bool,
    payload_json: String,
    state: tauri::State<'_, AppState>,
) -> Result<String, String> {
    {
        let mut data = state.lock().unwrap();
        data.running = true;
        data.norbi_mode = norbi_mode;
    }

    let config = SimulationConfig {
        mode: SimMode::Standard,
        max_external_objects: 16,
        max_internal_objects: 8,
        internal_dt: 1e-44,
        external_dt: 1e-3,
        norbi_mode,
        gravitational_softening: 1e-10,
    };

    let result = std::panic::catch_unwind(|| {
        black_hole_core::run_simulation(mass, config, &payload_json)
    });

    match result {
        Ok(Ok(results)) => {
            let json = serde_json::to_string(&results).map_err(|e| e.to_string())?;
            {
                let mut data = state.lock().unwrap();
                data.running = false;
                data.last_results = Some(results);
                data.step += 1;
            }
            Ok(json)
        }
        Ok(Err(e)) => {
            let mut data = state.lock().unwrap();
            data.running = false;
            Err(e.to_string())
        }
        Err(_) => {
            let mut data = state.lock().unwrap();
            data.running = false;
            Err("Szimuláció pánik — belső hiba".to_string())
        }
    }
}

#[tauri::command]
pub fn get_current_state(state: tauri::State<'_, AppState>) -> CurrentState {
    let data = state.lock().unwrap();
    let (mass, temperature) = data
        .last_results
        .as_ref()
        .and_then(|r| r.timeline.last())
        .map(|t| (t.mass, t.temperature))
        .unwrap_or((0.0, 0.0));

    CurrentState {
        running: data.running,
        step: data.step,
        mass,
        temperature,
        norbi_mode: data.norbi_mode,
    }
}

#[tauri::command]
pub fn toggle_norbi_mode(enabled: bool, state: tauri::State<'_, AppState>) {
    let mut data = state.lock().unwrap();
    data.norbi_mode = enabled;
}
