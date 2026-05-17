use std::process::Command;

/// Python elemző futtatása subprocess-ként JSON kommunikációval
pub fn run_python_analysis(simulation_json: &str, original_hash: &str) -> Result<String, String> {
    let python_bin = which_python();

    let input = serde_json::json!({
        "simulation": simulation_json,
        "original_hash": original_hash,
    })
    .to_string();

    let output = Command::new(&python_bin)
        .args(["-m", "python.main", "--analyze-only"])
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .and_then(|mut child| {
            use std::io::Write;
            if let Some(stdin) = child.stdin.as_mut() {
                let _ = stdin.write_all(input.as_bytes());
            }
            child.wait_with_output()
        })
        .map_err(|e| format!("Python indítás sikertelen: {e}"))?;

    if output.status.success() {
        String::from_utf8(output.stdout).map_err(|e| e.to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python hiba: {stderr}"))
    }
}

fn which_python() -> String {
    // Workspace-relatív .venv keresés
    let candidates = [".venv/bin/python3", ".venv/bin/python", "python3", "python"];
    for candidate in &candidates {
        if std::path::Path::new(candidate).exists()
            || Command::new(candidate).arg("--version").output().is_ok()
        {
            return candidate.to_string();
        }
    }
    "python3".to_string()
}
