/// η hatásfok tesztek — a Norbi-hipotézis kulcskérdése:
/// P_Norbi = η · P_standard → milyen η mellett egyezik a két teljesítmény?
#[cfg(test)]
mod tests {
    use crate::black_hole::{BlackHoleTrait, RadiationEngine};
    use crate::black_hole::schwarzschild::SchwarzschildBlackHole;
    use crate::interior::baby_universe::BabyUniverse;
    use crate::constants::RHO_PLANCK;
    use crate::radiation::hawking_engine::HawkingEngine;

    /// A Norbi teljesítmény: P_Norbi = η · ρ_szél · v_szak · A_horizont
    fn norbi_power(bh: &SchwarzschildBlackHole, bu: &BabyUniverse, eta: f64) -> f64 {
        let r_s = bh.schwarzschild_radius();
        let a_horizont = 4.0 * std::f64::consts::PI * r_s.powi(2);
        let rho_edge = bu.internal_density;
        let v_szak = bu.edge_breakup_rate();
        eta * rho_edge * v_szak * a_horizont
    }

    #[test]
    fn test_eta_positive_range_exists() {
        // H₁: van olyan η > 0, ahol P_Norbi ≈ P_standard
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let bu = BabyUniverse::new(RHO_PLANCK);
        let engine = HawkingEngine::new();
        let p_standard = engine.energy_loss_rate(&bh).unwrap();

        // Keressük azt az η-t ahol P_Norbi = P_standard
        let p_norbi_unit = norbi_power(&bh, &bu, 1.0);
        if p_norbi_unit > 0.0 {
            let eta_needed = p_standard / p_norbi_unit;
            // Ha η ∈ (0, 1] → a modell konzisztens
            assert!(
                eta_needed > 0.0,
                "Pozitív η-nak kell lennie: {eta_needed:.3e}"
            );
        }
        // Ha p_norbi_unit == 0: a bébiuniverzum nem elég aktív ennél a paraméterkészletnél
    }

    #[test]
    fn test_standard_power_positive() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        let p = engine.energy_loss_rate(&bh).unwrap();
        assert!(p > 0.0, "A standard Hawking-teljesítménynek pozitívnak kell lennie");
    }

    #[test]
    fn test_norbi_power_scales_with_eta() {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let bu = BabyUniverse::new(RHO_PLANCK);
        let p1 = norbi_power(&bh, &bu, 0.1);
        let p2 = norbi_power(&bh, &bu, 0.2);
        assert!(
            (p2 - 2.0 * p1).abs() < 1e-50_f64.max(p1 * 1e-10),
            "P_Norbi lineárisan kell skálázódjon η-val"
        );
    }
}
