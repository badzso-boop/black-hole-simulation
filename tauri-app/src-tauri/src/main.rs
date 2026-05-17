// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;

use commands::AppData;
use std::sync::{Arc, Mutex};

fn main() {
    let app_state = Arc::new(Mutex::new(AppData::new()));

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            commands::run_simulation,
            commands::get_current_state,
            commands::toggle_norbi_mode,
        ])
        .run(tauri::generate_context!())
        .expect("Tauri alkalmazás indítása sikertelen");
}
