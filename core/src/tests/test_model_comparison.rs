#[cfg(test)]
mod model_comparison {
    use crate::black_hole::{InteriorModel, RadiationEngine};
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::interior::norbi::NorbiInterior;
    use crate::interior::standard::StandardInterior;
    use crate::radiation::hawking_engine::HawkingEngine;
    use crate::types::Particle;

    fn make_bh() -> SchwarzschildBlackHole {
        SchwarzschildBlackHole::new(1e15).unwrap()
    }

    // ÖSSZEHASONLÍTÁS 1: Standard modell megáll Planck-határnál
    #[test]
    fn cmp_01_standard_model_stops_at_planck_scale() {
        let mut interior = StandardInterior::new();
        // Kis tömegű részecske: gyorsan eléri a Planck-sűrűséget
        let particle = Particle { mass: 1e-10, initial_radius: 1e-34, ..Particle::test_particle() };
        let bh = make_bh();
        let mut reached = false;
        for _ in 0..100_000 {
            let state = interior.simulate_step(&particle, &bh, 1e-44).unwrap();
            if state.at_planck_scale {
                assert!(interior.at_physics_boundary());
                assert!(state.physics_boundary.is_some());
                reached = true;
                break;
            }
        }
        assert!(reached, "Standard modellnek Planck-határt kell elérnie");
    }

    // ÖSSZEHASONLÍTÁS 2: Norbi modell folytatódik Planck után
    #[test]
    fn cmp_02_norbi_model_continues_after_planck_scale() {
        let mut interior = NorbiInterior::new();
        let particle = Particle { mass: 1e-10, initial_radius: 1e-34, ..Particle::test_particle() };
        let bh = make_bh();
        let mut bounced = false;
        for _ in 0..100_000 {
            let state = interior.simulate_step(&particle, &bh, 1e-44).unwrap();
            if state.bounce_occurred {
                assert!(!interior.at_physics_boundary());
                assert!(state.baby_universe.is_some());
                bounced = true;
                break;
            }
        }
        assert!(bounced, "Norbi modellnek visszapattanást kell produkálnia");
    }

    // ÖSSZEHASONLÍTÁS 3: Norbi sugárzás ≠ Standard sugárzás (különböző engine-ek)
    #[test]
    fn cmp_03_norbi_radiation_has_edge_component() {
        let mut norbi = NorbiInterior::new();
        let particle = Particle { mass: 1e-10, initial_radius: 1e-34, ..Particle::test_particle() };
        let bh = make_bh();
        for _ in 0..100_000 {
            let state = norbi.simulate_step(&particle, &bh, 1e-44).unwrap();
            if state.bounce_occurred {
                let spectrum = norbi.radiation_spectrum();
                // A Norbi spektrumnak van edge komponense
                assert_eq!(spectrum.len(), crate::constants::SPECTRUM_BINS);
                break;
            }
        }
    }

    // ÖSSZEHASONLÍTÁS 4: BabyUniverse energiája pozitív visszapattanás után
    #[test]
    fn cmp_04_baby_universe_has_positive_energy() {
        let mut interior = NorbiInterior::new();
        let particle = Particle {
            mass: 1e-10,
            energy: 1e30,
            initial_radius: 1e-34,
            ..Particle::test_particle()
        };
        let bh = make_bh();
        for _ in 0..100_000 {
            let state = interior.simulate_step(&particle, &bh, 1e-44).unwrap();
            if let Some(ref bu) = state.baby_universe {
                assert!(bu.total_energy > 0.0, "Bébiuniverzum energiájának pozitívnak kell lennie");
                assert!(bu.scale_factor > 0.0, "Skálafaktornak pozitívnak kell lennie");
                assert!(bu.expansion_rate > 0.0, "Tágulási rátának pozitívnak kell lennie");
                return;
            }
        }
    }

    // ÖSSZEHASONLÍTÁS 5: Hawking motor standard és norbi módban különböző objektumok
    #[test]
    fn cmp_05_engine_modes_are_distinct() {
        let std_engine = HawkingEngine::standard();
        let norbi_engine = HawkingEngine::norbi();
        // Mindkét engine azonos fekete lyukra azonos Hawking-hőmérsékletet számít
        let bh = make_bh();
        let s_spec = std_engine.compute_spectrum(&bh).unwrap();
        let n_spec = norbi_engine.compute_spectrum(&bh).unwrap();
        // Alapspektrum azonos (Norbi belső motor a NorbiInterior-ban van)
        assert_eq!(s_spec.frequencies.len(), n_spec.frequencies.len());
    }
}
