//! Valódi fekete lyukak — mért paraméterekkel (2019–2026 irodalom).
//!
//! Minden értékhez hivatkozás tartozik; a nem mért (feltételezett) értékek
//! külön jelölve (`assumptions`). A spin a legtöbb objektumra gyengén
//! korlátozott — ezt a `spin_note` rögzíti.
//!
//! Megfigyelhető mennyiségek (`ObjectObservables`):
//! - θ_g = GM/(c²D) szögméret
//! - árnyék: 2√27·θ_g ≈ 10.39 θ_g (a* = 0; a spin/látószög ≤ ~4%-kal csökkenti)
//! - EHT-gyűrű: d = α·θ_g, α ≈ 11.0 (EHT M87 VI. cikk: képalkotással 10.67–11.01,
//!   GRMHD-kalibrált geometriai modellekkel ≈ 11.5)
//! - δ = d_mért/(α·θ_g) − 1 (az EHT Sgr A* VI. cikk mérőszáma, δ = −0.08 ± 0.09)

use serde::{Deserialize, Serialize};

use crate::black_hole::environment::{AccretionModel, Environment};
use crate::black_hole::kerr;
use crate::constants::{C, G, M_SUN, PI};
use crate::types::SimulationConfig;

pub const PARSEC: f64 = 3.085_677_581_491_367e16;
pub const YEAR: f64 = 3.155_76e7;
/// EHT gyűrű-kalibráció: d_gyűrű ≈ α·θ_g
pub const EHT_RING_ALPHA: f64 = 11.0;
const MICROARCSEC_PER_RAD: f64 = 180.0 / PI * 3600.0 * 1e6;

#[derive(Debug, Clone, Serialize)]
pub struct CatalogObject {
    pub key: &'static str,
    pub name: &'static str,
    /// Tömeg (M_☉) és 1σ bizonytalanság
    pub mass_msun: f64,
    pub mass_err_msun: f64,
    /// Távolság (pc), ha ismert
    pub distance_pc: Option<f64>,
    pub spin: f64,
    pub spin_note: &'static str,
    /// Mért/becsült akkréciós ráta (M_☉/év)
    pub accretion_msun_per_yr: f64,
    pub accretion_note: &'static str,
    pub radiative_efficiency: f64,
    pub disk_accretion: bool,
    /// Mért EHT-gyűrű átmérő (μas) és hibája
    pub observed_ring_uas: Option<(f64, f64)>,
    /// Alapértelmezett szimulációs horizont (év) — `None`: az Univerzum kora
    pub default_horizon_yr: Option<f64>,
    pub assumptions: &'static str,
    pub references: &'static [&'static str],
}

impl CatalogObject {
    pub fn mass_kg(&self) -> f64 {
        self.mass_msun * M_SUN
    }

    pub fn environment(&self) -> Environment {
        let rate = self.accretion_msun_per_yr * M_SUN / YEAR;
        Environment {
            accretion: if rate > 0.0 {
                AccretionModel::Constant { rate }
            } else {
                AccretionModel::None
            },
            radiative_efficiency: self.radiative_efficiency,
            disk_accretion: self.disk_accretion,
            ..Environment::default()
        }
    }

    /// Szimulációs konfiguráció a katalógus-értékekből
    pub fn config(&self) -> SimulationConfig {
        SimulationConfig {
            mass: self.mass_kg(),
            spin: self.spin,
            environment: self.environment(),
            object: Some(self.key.to_string()),
            max_time: self.default_horizon_yr.map(|y| y * YEAR),
            ..SimulationConfig::default()
        }
    }
}

pub const CATALOG: &[CatalogObject] = &[
    CatalogObject {
        key: "sgr-a",
        name: "Sagittarius A* (a Tejútrendszer központi fekete lyuka)",
        mass_msun: 4.2996e6,
        mass_err_msun: 0.0118e6,
        distance_pc: Some(8275.9),
        spin: 0.9,
        spin_note: "gyengén korlátozott: az EHT 2022 kizárja a* = 0-t; a 2024-es \
                    polarimetriai legjobb modell a* = 0.94 (MAD) — itt 0.9",
        accretion_msun_per_yr: 7.0e-9,
        accretion_note: "EHT Sgr A* V. cikk (2022): (5.2–9.5)e-9 M_☉/év, GRMHD-illesztés; \
                         a Bondi-skálán befogott gáz ~1e-5 M_☉/év, ennek <1%-a éri el \
                         (Wang et al. 2013)",
        radiative_efficiency: 0.002,
        disk_accretion: false,
        observed_ring_uas: Some((51.8, 2.3)),
        default_horizon_yr: None,
        assumptions: "a mai Ṁ állandónak feltételezve a teljes horizonton; ε = 0.002 a mért L_bol ≈ 8e35 erg/s és Ṁ = 7e-9 M_☉/év hányadosa \
                      (sugárzásban szegény, forró áramlás — nem vékony korong)",
        references: &[
            "GRAVITY Collaboration 2024, A&A 692, A242 (arXiv:2409.12261) — tömeg, távolság",
            "EHT Collaboration 2022, ApJL 930, L12 (I. cikk) — gyűrű 51.8 ± 2.3 μas",
            "EHT Collaboration 2022, ApJL 930, L16 (V. cikk) — Ṁ, L_bol",
            "EHT Collaboration 2024, ApJL 964, L26 (VIII. cikk) — spin a* = 0.94 legjobb modell",
            "Baganoff et al. 2003, ApJ 591, 891; Wang et al. 2013, Science 341, 981 — Bondi-skála",
        ],
    },
    CatalogObject {
        key: "m87",
        name: "M87* (a Messier 87 galaxis központi fekete lyuka)",
        mass_msun: 6.5e9,
        mass_err_msun: 0.7e9,
        distance_pc: Some(16.8e6),
        spin: 0.9,
        spin_note: "nem mért; a MAD-modellek |a*| ≲ 0.2-t gyengén kizárják, jellemzően \
                    0.5–0.94 — itt 0.9",
        accretion_msun_per_yr: 1.0e-3,
        accretion_note: "EHT M87 VIII. cikk (2021): (3–20)e-4 M_☉/év, polarimetria + GRMHD; \
                         a Bondi-ráta 0.1–0.2 M_☉/év (Russell et al. 2015), a tényleges \
                         ennél ≥ 100×-osan kisebb",
        radiative_efficiency: 0.1,
        disk_accretion: false,
        observed_ring_uas: Some((42.0, 3.0)),
        default_horizon_yr: None,
        assumptions: "a mai Ṁ állandónak feltételezve a teljes horizonton; ε = 0.1 feltételezett (a tömegnövekedésre alig hat); a tömeg \
                      alternatívái: 5.37e9 (Liepold 2023), 3.45e9 M_☉ (gázdinamika)",
        references: &[
            "EHT Collaboration 2019, ApJL 875, L6 (VI. cikk) — M = 6.5 ± 0.7 × 10⁹ M_☉, D = 16.8 Mpc",
            "EHT Collaboration 2019, ApJL 875, L1 — gyűrű 42 ± 3 μas (2018: 43.3 μas)",
            "EHT Collaboration 2021, ApJL 910, L13 (VIII. cikk) — Ṁ",
            "Russell et al. 2015, MNRAS 451, 588 — Bondi-skála",
            "Liepold et al. 2023, ApJL (arXiv:2302.07884) — alternatív tömeg",
        ],
    },
    CatalogObject {
        key: "cyg-x1",
        name: "Cygnus X-1 (röntgen-kettős, csillagtömegű fekete lyuk)",
        mass_msun: 21.2,
        mass_err_msun: 2.2,
        distance_pc: Some(2220.0),
        spin: 0.998,
        spin_note: "a* > 0.9985 (3σ, kontinuum-illesztés, Zhao et al. 2021) — a Thorne-határon",
        accretion_msun_per_yr: 3.0e-9,
        accretion_note: "L ≈ 0.02 L_Edd és ε ≈ 0.32-ből: Ṁ ≈ 3e-9 M_☉/év (számolt); \
                         a kísérőcsillag szele táplálja",
        radiative_efficiency: 0.32,
        disk_accretion: true,
        observed_ring_uas: None,
        default_horizon_yr: Some(5.0e6),
        assumptions: "vékony korong: ε és a spin-felpörgetés az ISCO-ból; a szél-akkréció \
                      csak a ~40 M_☉-es O-szuperóriás kísérő hátralévő életéig tart — a \
                      horizont ezért 5 millió év (feltételezés, nem mért érték)",
        references: &[
            "Miller-Jones et al. 2021, Science 371, 1046 — M = 21.2 ± 2.2 M_☉, D = 2.22 kpc",
            "Zhao et al. 2021, ApJ 908, 117 — a* > 0.9985",
        ],
    },
    CatalogObject {
        key: "gw250114",
        name: "GW250114 összeolvadási maradvány (LIGO–Virgo–KAGRA)",
        mass_msun: 62.7,
        mass_err_msun: 1.1,
        distance_pc: Some(440.0e6),
        spin: 0.68,
        spin_note: "χ_f = 0.68 ± 0.01 (gravitációshullám-lecsengés)",
        accretion_msun_per_yr: 0.0,
        accretion_note: "nincs akkréció (izolált maradvány)",
        radiative_efficiency: 0.1,
        disk_accretion: false,
        observed_ring_uas: None,
        default_horizon_yr: None,
        assumptions: "a távolság (~440 Mpc) nem ellenőrzött",
        references: &["LVK 2025, PRL (arXiv:2509.08054) — M_f = 62.7 M_☉, χ_f = 0.68"],
    },
    CatalogObject {
        key: "gw150914",
        name: "GW150914 összeolvadási maradvány (az első észlelt gravitációs hullám)",
        mass_msun: 63.1,
        mass_err_msun: 3.4,
        distance_pc: Some(440.0e6),
        spin: 0.69,
        spin_note: "a_f = 0.69 (+0.05/−0.04)",
        accretion_msun_per_yr: 0.0,
        accretion_note: "nincs akkréció (izolált maradvány)",
        radiative_efficiency: 0.1,
        disk_accretion: false,
        observed_ring_uas: None,
        default_horizon_yr: None,
        assumptions: "",
        references: &["LVC GWTC-1, PRX 9, 031040 (2019) — M_f = 63.1 M_☉, a_f = 0.69, D_L = 440 Mpc"],
    },
    CatalogObject {
        key: "pbh-today",
        name: "Ma elpárolgó primordiális fekete lyuk (hipotetikus)",
        mass_msun: 5.1e11 / M_SUN,
        mass_err_msun: 0.0,
        distance_pc: None,
        spin: 0.0,
        spin_note: "a primordiális fekete lyukak kis spinnel keletkeznek (feltételezés)",
        accretion_msun_per_yr: 0.0,
        accretion_note: "elhanyagolható",
        radiative_efficiency: 0.1,
        disk_accretion: false,
        observed_ring_uas: None,
        default_horizon_yr: None,
        assumptions: "hipotetikus objektum; a tömeg a „ma elpárolgó\" M* (Carr et al. 2010)",
        references: &["Carr, Kohri, Sendouda, Yokoyama 2010, PRD 81, 104019 — M* ≈ 5.1e11 kg"],
    },
];

pub fn lookup(key: &str) -> Option<&'static CatalogObject> {
    let k = key.trim().to_lowercase().replace(['*', '_', ' '], "-");
    let k = k.trim_end_matches('-');
    CATALOG.iter().find(|o| o.key == k)
}

/// Egy katalógus-objektum megfigyelhető mennyiségei a (szimulált) tömegével
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObjectObservables {
    pub key: String,
    pub name: String,
    pub spin_note: String,
    pub accretion_note: String,
    pub assumptions: String,
    pub references: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub distance_m: Option<f64>,
    /// θ_g = GM/(c²D) (μas)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub theta_g_uas: Option<f64>,
    /// Árnyék-átmérő a* = 0-ra (μas); a spin ezt ≤ ~4%-kal csökkenti
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub shadow_diameter_uas: Option<f64>,
    /// Várt EHT-gyűrű α·θ_g (μas)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub predicted_ring_uas: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub observed_ring_uas: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub observed_ring_err_uas: Option<f64>,
    /// δ = d_mért/(α·θ_g) − 1
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ring_deviation: Option<f64>,
    /// Az Eddington-luminozitás hányada a katalógus akkréciós rátájával
    pub eddington_ratio: f64,
}

pub fn observables(obj: &CatalogObject, mass: f64, spin: f64) -> ObjectObservables {
    let distance_m = obj.distance_pc.map(|d| d * PARSEC);
    let theta_g = distance_m.map(|d| G * mass / (C * C * d) * MICROARCSEC_PER_RAD);
    let shadow = distance_m.map(|d| kerr::shadow_angular_diameter(mass, d) * MICROARCSEC_PER_RAD);
    let predicted_ring = theta_g.map(|t| EHT_RING_ALPHA * t);
    let (obs, err) = match obj.observed_ring_uas {
        Some((d, e)) => (Some(d), Some(e)),
        None => (None, None),
    };
    let deviation = match (obs, predicted_ring) {
        (Some(o), Some(p)) => Some(o / p - 1.0),
        _ => None,
    };
    let eps = if obj.disk_accretion {
        kerr::radiative_efficiency(spin)
    } else {
        obj.radiative_efficiency
    };
    let l_acc = eps * obj.accretion_msun_per_yr * M_SUN / YEAR * C * C;
    let l_edd = 4.0 * PI * G * mass * crate::black_hole::environment::PROTON_MASS * C
        / crate::black_hole::environment::THOMSON_CROSS_SECTION;
    ObjectObservables {
        key: obj.key.into(),
        name: obj.name.into(),
        spin_note: obj.spin_note.into(),
        accretion_note: obj.accretion_note.into(),
        assumptions: obj.assumptions.into(),
        references: obj.references.iter().map(|r| r.to_string()).collect(),
        distance_m,
        theta_g_uas: theta_g,
        shadow_diameter_uas: shadow,
        predicted_ring_uas: predicted_ring,
        observed_ring_uas: obs,
        observed_ring_err_uas: err,
        ring_deviation: deviation,
        eddington_ratio: l_acc / l_edd,
    }
}
