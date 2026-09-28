#[cfg(test)]
mod tests {
    use crate::run_simulation;
    use crate::time_evolution::checkpoint::Checkpoint;
    use crate::types::SimulationConfig;
    use std::fs;

    #[test]
    fn checkpoint_roundtrip_and_atomic_write() {
        let tmp =
            std::env::temp_dir().join(format!("bh_test_checkpoint_{}.bhs", std::process::id()));
        let cfg = SimulationConfig {
            mass: 1e12,
            norbi_mode: true,
            steps: 20,
            interior_steps: 20,
            ..Default::default()
        };
        let results = run_simulation(&cfg, serde_json::json!({"a": 1})).unwrap();
        Checkpoint::new(results.clone()).save(&tmp).unwrap();
        assert!(
            !tmp.with_extension("tmp").exists(),
            "Nem maradhat .tmp fájl"
        );
        let loaded = Checkpoint::load(&tmp).unwrap();
        assert_eq!(loaded.schema_version, "3.1");
        assert_eq!(loaded.results.timeline.len(), results.timeline.len());
        assert_eq!(
            loaded.results.baby_universe.len(),
            results.baby_universe.len()
        );
        let _ = fs::remove_file(&tmp);
    }
}
