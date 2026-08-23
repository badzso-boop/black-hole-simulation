#[cfg(test)]
mod tests {
    use crate::black_hole::RadiationEngine;
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::constants::RHO_PLANCK;
    use crate::interior::baby_universe::BabyUniverse;
    use crate::radiation::hawking_engine::HawkingEngine;

    fn active_baby_state() -> crate::types::BabyUniverseState {
        // Mérsékelt, Planck-energia nagyságrendű abszorpció: ha itt túl nagy
        // energiát adnánk hozzá, a törésponti (breakup_fraction) formulában az
        // önkötési energia (∝m²) sokkal gyorsabban nőne mint a tidal energia
        // (∝m), és a bébiuniverzum fizikailag *ellenállóbbá* válna a
        // szétszakadással szemben — ahogy egy valódi, kompakt, nagy tömegű
        // objektum is nehezebben szakad szét árapályerővel.
        let mut bu = BabyUniverse::new(RHO_PLANCK);
        bu.absorb_energy(1e9);
        bu.to_state()
    }

    // INFO-01: Standard spektrum hawking_fraction=1.0, edge_fraction=0.0
    #[test]
    fn test_standard_hawking_fraction_one() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::standard();
        let s = engine.compute_spectrum(&bh).unwrap();
        assert!((s.hawking_fraction - 1.0).abs() < 1e-10,
            "hawking_fraction={}", s.hawking_fraction);
        assert!(s.edge_fraction < 1e-10,
            "edge_fraction={}", s.edge_fraction);
    }

    // INFO-02: Standard thermality_score kis pozitív (csak greybody-eltérés)
    #[test]
    fn test_standard_thermality_score_small() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::standard();
        let s = engine.compute_spectrum(&bh).unwrap();
        assert!(s.thermality_score >= 0.0,
            "thermality_score negatív: {}", s.thermality_score);
        assert!(s.thermality_score < 0.5,
            "Standard thermality_score túl nagy: {}", s.thermality_score);
    }

    // INFO-03: Norbi aktív bébiuniverzummal: edge_fraction > 0.0
    #[test]
    fn test_norbi_edge_fraction_positive() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::norbi();
        let baby = active_baby_state();
        let s = engine.compute_spectrum_norbi(&bh, &baby).unwrap();
        assert!(s.edge_fraction > 0.0,
            "Norbi edge_fraction nulla, holott bébiuniverzum aktív");
    }

    // INFO-04: Norbi thermality_score > Standard thermality_score
    #[test]
    fn test_norbi_thermality_greater_than_standard() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::norbi();
        let std_s = engine.compute_spectrum(&bh).unwrap();
        let baby = active_baby_state();
        let norbi_s = engine.compute_spectrum_norbi(&bh, &baby).unwrap();
        assert!(norbi_s.thermality_score > std_s.thermality_score,
            "Norbi thermality={} nem nagyobb Standard thermality={}",
            norbi_s.thermality_score, std_s.thermality_score);
    }

    // INFO-05: KL divergencia nemnegatív mindkét módban
    #[test]
    fn test_thermality_score_non_negative() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        let std_s = engine.compute_spectrum(&bh).unwrap();
        assert!(std_s.thermality_score >= 0.0);
        let baby = active_baby_state();
        let norbi_s = engine.compute_spectrum_norbi(&bh, &baby).unwrap();
        assert!(norbi_s.thermality_score >= 0.0);
    }
}
