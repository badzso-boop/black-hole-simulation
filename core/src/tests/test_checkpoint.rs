#[cfg(test)]
mod tests {
    use std::fs;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::black_hole::BlackHoleTrait;
    use crate::time_evolution::checkpoint::Checkpoint;
    use crate::types::{InteriorState, SimulationConfig};

    #[test]
    fn test_checkpoint_save_and_load() {
        let tmp = std::env::temp_dir().join("test_checkpoint.bhs");
        let config = SimulationConfig::lite();
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let interior = InteriorState::default();

        let cp = Checkpoint::new(config.clone(), bh.age(), bh.mass(), vec![], interior);
        cp.save(&tmp).expect("Checkpoint mentés sikertelen");

        let loaded = Checkpoint::load(&tmp).expect("Checkpoint betöltés sikertelen");
        assert_eq!(loaded.schema_version, "2.0");
        assert!((loaded.current_mass - bh.mass()).abs() < 1e-10);

        let _ = fs::remove_file(&tmp);
    }

    #[test]
    fn test_checkpoint_atomic_write() {
        let tmp = std::env::temp_dir().join("test_atomic.bhs");
        let config = SimulationConfig::standard();
        let bh = SchwarzschildBlackHole::new(1e10).unwrap();
        let interior = InteriorState::default();

        let cp = Checkpoint::new(config, bh.age(), bh.mass(), vec![], interior);
        cp.save(&tmp).unwrap();

        // Az atomikus írás után nem marad tmp fájl
        let tmp_path = tmp.with_extension("tmp");
        assert!(!tmp_path.exists(), "Nem szabad maradék .tmp fájlnak lennie");

        let _ = fs::remove_file(&tmp);
    }
}
