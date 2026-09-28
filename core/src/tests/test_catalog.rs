#[cfg(test)]
mod tests {
    use crate::black_hole::kerr::THORNE_SPIN_LIMIT;
    use crate::catalog::{lookup, observables, CATALOG, YEAR};
    use crate::constants::M_SUN;
    use crate::run_simulation;
    use approx::assert_relative_eq;

    #[test]
    fn lookup_accepts_common_spellings() {
        for k in [
            "sgr-a",
            "Sgr-A*",
            "sgr_a*",
            "M87",
            "m87*",
            "cyg-x1",
            "GW250114",
            "pbh-today",
        ] {
            assert!(lookup(k).is_some(), "{k}");
        }
        assert!(lookup("andromeda").is_none());
    }

    #[test]
    fn eht_rings_match_mass_and_distance() {
        // δ = d_mért/(11·θ_g) − 1; EHT Sgr A* VI. cikk: δ = −0.08 ± 0.09
        let sgr = lookup("sgr-a").unwrap();
        let o = observables(sgr, sgr.mass_kg(), sgr.spin);
        assert_relative_eq!(o.theta_g_uas.unwrap(), 5.13, max_relative = 5e-3);
        let d = o.ring_deviation.unwrap();
        assert!((d - (-0.08)).abs() < 0.09, "Sgr A* δ = {d}");
        // M87*: 6.5e9 M_☉, 16.8 Mpc → θ_g = 3.82 μas, gyűrű ≈ 42 μas
        let m87 = lookup("m87").unwrap();
        let o = observables(m87, m87.mass_kg(), m87.spin);
        assert_relative_eq!(o.theta_g_uas.unwrap(), 3.82, max_relative = 5e-3);
        assert!(
            o.ring_deviation.unwrap().abs() < 0.1,
            "M87* δ = {}",
            o.ring_deviation.unwrap()
        );
        assert_relative_eq!(o.shadow_diameter_uas.unwrap(), 39.7, max_relative = 5e-3);
        // mindkettő erősen sub-Eddington (sugárzásban szegény áramlás)
        assert!(observables(sgr, sgr.mass_kg(), sgr.spin).eddington_ratio < 1e-6);
        assert!(o.eddington_ratio < 1e-3);
    }

    #[test]
    fn every_catalog_object_simulates_cleanly() {
        for obj in CATALOG {
            let mut cfg = obj.config();
            cfg.steps = 40;
            cfg.interior_steps = 41;
            let r = run_simulation(&cfg, serde_json::json!({})).unwrap();
            let txt = serde_json::to_string(&r).unwrap();
            assert!(!txt.contains("null") && !txt.contains("NaN"), "{}", obj.key);
            assert!(
                r.energy.relative_error < 1e-6,
                "{}: {}",
                obj.key,
                r.energy.relative_error
            );
            assert_eq!(r.object.as_ref().unwrap().key, obj.key);
        }
    }

    #[test]
    fn physical_behaviour_of_real_objects() {
        let run = |key: &str| {
            let mut cfg = lookup(key).unwrap().config();
            cfg.steps = 40;
            cfg.interior_steps = 41;
            run_simulation(&cfg, serde_json::json!({})).unwrap()
        };
        // Sgr A*: 13.8 Gyr alatt Ṁ·t ≈ 7e-9 M_☉/év · 13.8 Gyr ≈ 97 M_☉ akkréció
        let r = run("sgr-a");
        assert!(!r.evaporation_complete);
        let gained = (r.end_mass - r.config.mass) / M_SUN;
        let expected = 7.0e-9 * (1.0 - 0.002) * r.end_time / YEAR;
        assert_relative_eq!(gained, expected, max_relative = 1e-3);
        // gömbszimmetrikus akkréció: a*·M² állandó → a spin alig változik
        assert_relative_eq!(
            r.kerr.final_spin * r.end_mass.powi(2),
            0.9 * r.config.mass.powi(2),
            max_relative = 1e-6
        );
        // Cyg X-1: vékony korong a Thorne-határon — a spin ott marad; a horizont
        // a kísérőcsillag élettartama (5 Myr), nem az Univerzum kora
        let r = run("cyg-x1");
        assert_relative_eq!(r.end_time / YEAR, 5.0e6, max_relative = 1e-9);
        assert_relative_eq!(r.kerr.final_spin, THORNE_SPIN_LIMIT, max_relative = 1e-9);
        assert!(r.kerr.disk_efficiency > 0.30);
        // a ma elpárolgó PBH valóban ~az Univerzum kora alatt párolog el
        let r = run("pbh-today");
        assert!(r.evaporation_complete);
        let gyr = r.end_time / YEAR / 1e9;
        assert!((9.5..18.0).contains(&gyr), "{gyr} Gyr");
        // az összeolvadási maradványok a mai CMB-ben nőnek (M ≫ M_eq)
        let r = run("gw250114");
        assert!(!r.evaporation_complete && r.timeline.iter().all(|t| t.net_mass_rate > 0.0));
    }
}
