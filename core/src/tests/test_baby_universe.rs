#[cfg(test)]
mod tests {
    use crate::constants::RHO_PLANCK;
    use crate::interior::baby_universe::BabyUniverse;
    use crate::types::InternalObjectData;
    use crate::types::ObjectType;

    #[test]
    fn test_baby_universe_starts_with_positive_energy() {
        let bu = BabyUniverse::new(RHO_PLANCK);
        assert!(bu.total_energy > 0.0);
        assert!(bu.scale_factor > 0.0);
        assert!(bu.expansion_rate > 0.0);
    }

    #[test]
    fn test_baby_universe_expands_over_time() {
        let mut bu = BabyUniverse::new(RHO_PLANCK);
        let a0 = bu.scale_factor;
        bu.evolve(1e-40);
        assert!(bu.scale_factor > a0, "Bébiuniverzumnak tágulnia kell");
    }

    #[test]
    fn test_absorb_energy_increases_total() {
        let mut bu = BabyUniverse::new(RHO_PLANCK);
        let e0 = bu.total_energy;
        bu.absorb_energy(1e20);
        assert!(bu.total_energy > e0, "Energiaabszorpció után a teljes energia nő");
    }

    #[test]
    fn test_edge_breakup_rate_positive() {
        let bu = BabyUniverse::new(RHO_PLANCK);
        assert!(bu.edge_breakup_rate() > 0.0);
    }

    #[test]
    fn test_breakup_detected_for_large_object() {
        let bu = BabyUniverse::new(RHO_PLANCK);
        let obj = InternalObjectData {
            mass: 1e30,
            radius: 1.0,
            position: [1e10, 0.0, 0.0], // messze a szélen
            velocity: [0.0; 3],
            entry_time: 0.0,
            fragmented: false,
            obj_type: ObjectType::Star,
        };
        let event = bu.check_breakup(&obj, 0.0);
        // Nagy tömeg + nagy távolság → szétszakadás
        assert!(
            event.is_some(),
            "Nagy objektumnak szétszakadnia kell a belső szélén"
        );
    }

    #[test]
    fn test_no_breakup_at_origin() {
        // A belső univerzum középpontján (r=0) nulla a tidal erő → nincs szétszakadás
        let bu = BabyUniverse::new(RHO_PLANCK);
        let obj = InternalObjectData {
            mass: 1e10,
            radius: 1e6,
            position: [0.0, 0.0, 0.0], // origón: r=0 → e_tidal=0
            velocity: [0.0; 3],
            entry_time: 0.0,
            fragmented: false,
            obj_type: ObjectType::Planet,
        };
        let event = bu.check_breakup(&obj, 0.0);
        assert!(
            event.is_none(),
            "Az origón lévő objektumnak nem szabad szétszakadni (e_tidal=0)"
        );
    }
}
