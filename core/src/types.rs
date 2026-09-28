use serde::{Deserialize, Serialize};

use crate::geometry::CausalChannel;
use crate::radiation::emission::EmissionModel;

pub const SCHEMA_VERSION: &str = "3.0";

// ---------------------------------------------------------------------------
// Sugárzási spektrum (külső megfigyelő)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Spectrum {
    /// Frekvenciák (Hz)
    pub frequencies: Vec<f64>,
    /// A külső megfigyelő által látott foton-spektrum dP/dν (W/Hz)
    pub intensities: Vec<f64>,
    /// Hawking-hőmérséklet (K)
    pub temperature: f64,
    /// Teljes kisugárzott teljesítmény, minden részecskefajta (W)
    pub total_power: f64,
    /// Fotonokban kisugárzott teljesítmény (W) — ennek az alakja az `intensities`
    pub photon_power: f64,
    /// KL(spektrum ‖ legjobban illeszkedő Planck-görbe). Spektrális diagnosztika —
    /// NEM információmérték: a greybody-torzítás miatt a standard Hawking-spektrumra
    /// is > 0, és egy termális keverék is adhat nagy értéket információ nélkül.
    pub spectral_nonthermality: f64,
    /// A KL-t minimalizáló Planck-hőmérséklet (K)
    pub fit_temperature: f64,
}

// ---------------------------------------------------------------------------
// Belső fizika: Oppenheimer–Snyder összeomlás (saját idő τ)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum CollapsePhase {
    /// A porfelület a külső horizonton kívül (R > r_+)
    Infall,
    /// Csapdázott tartomány (r_− < R < r_+)
    Trapped,
    /// A belső horizonton belül, visszapattanás előtt (R < r_−, τ < 0)
    InnerRegion,
    /// Visszapattanás után, táguló szakasz (τ > 0) — a Norbi-féle „bébiuniverzum"
    PostBounce,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InteriorSample {
    /// Sajátidő a (kvantum) visszapattanástól / klasszikus szingularitástól (s)
    pub tau: f64,
    /// A porgömb területi sugara (m)
    pub radius: f64,
    /// Sűrűség (kg/m³)
    pub density: f64,
    /// Ṙ/R (1/s); negatív: összehúzódás
    pub hubble: f64,
    /// Klasszikus nyom-görbület por esetén: R = 8πGρ/c² (1/m²)
    pub ricci_scalar: f64,
    pub phase: CollapsePhase,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BounceInfo {
    pub radius: f64,
    pub density: f64,
    pub max_hubble_rate: f64,
    /// τ_b = 1/√(6πGρ_c)
    pub timescale: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhysicsBoundary {
    pub radius: f64,
    pub density: f64,
    pub tau: f64,
    pub reason: String,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum InteriorKind {
    /// Klasszikus általános relativitás: a leírás ρ = ρ_c-nél érvényét veszti
    Standard,
    /// LQC effektív dinamika: visszapattanás ρ_c-nél, utána tágulás
    Norbi,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InteriorTrajectory {
    pub kind: InteriorKind,
    pub samples: Vec<InteriorSample>,
    /// A kezdőpont sajátideje (R = R0) (s)
    pub tau_start: f64,
    /// Sajátidő a külső horizont átlépésekor (s)
    pub tau_horizon_crossing: f64,
    /// Sajátidő a horizont átlépésétől a visszapattanásig / fizikai határig (s);
    /// klasszikus határesetben 4GM/(3c³)
    pub proper_time_horizon_to_end: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bounce: Option<BounceInfo>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub physics_boundary: Option<PhysicsBoundary>,
}

/// A visszapattanás utáni táguló tartomány állapota (csak Norbi módban)
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BabyUniverseState {
    /// Sajátidő a visszapattanástól (s)
    pub tau: f64,
    /// Dimenziótlan skálafaktor a = R/r_b (a visszapattanáskor 1)
    pub scale_factor: f64,
    /// e-redők: N = ln a
    pub efolds: f64,
    /// H = ȧ/a (1/s)
    pub hubble: f64,
    pub density: f64,
    /// Fizikai sugár R = a·r_b (m)
    pub radius: f64,
    /// ρ·V·c² — a porgömb teljes tömeg-energiája, megmarad (= M c²)
    pub total_energy: f64,
    /// Gibbons–Hawking-hőmérséklet T = ħH/(2πk_B) (K)
    pub gh_temperature: f64,
    /// Belső él-luminozitás σT⁴·4π(c/H)² (W) — csak a belső tartományban;
    /// a külső megfigyelőhöz csak kauzális csatorna esetén juthatna el
    pub interior_luminosity: f64,
}

// ---------------------------------------------------------------------------
// Szimulációs konfiguráció
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct SimulationConfig {
    /// Kezdeti fekete lyuk tömeg (kg)
    pub mass: f64,
    /// Norbi-mód: LQC visszapattanás + bébiuniverzum a belsőben
    pub norbi_mode: bool,
    /// Hawking-emissziós modell (részecskefajták)
    pub emission_model: EmissionModel,
    /// A külső idővonal mintapontjainak száma (a tömegben logaritmikus rács)
    pub steps: usize,
    /// A belső trajektória mintapontjai (τ-ban asinh-rács: sűrű a visszapattanásnál)
    pub interior_steps: usize,
    /// Az összeomló porgömb kezdősugara a Schwarzschild-sugár egységében (> 1)
    pub initial_radius_rs: f64,
}

impl Default for SimulationConfig {
    fn default() -> Self {
        Self {
            mass: 1e12,
            norbi_mode: false,
            emission_model: EmissionModel::MacGibbon,
            steps: 100,
            interior_steps: 200,
            initial_radius_rs: 10.0,
        }
    }
}

// ---------------------------------------------------------------------------
// Szimulációs eredmények
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeStep {
    /// Idő a kezdettől (s) — a végfázisban f64-felbontás alatt változik
    pub time: f64,
    /// Hátralévő idő a párolgás végéig (s) — a végfázisban is pontos
    pub time_to_evaporation: f64,
    pub mass: f64,
    pub temperature: f64,
    /// Bekenstein–Hawking entrópia (k_B egységben)
    pub entropy: f64,
    /// M > 10 m_P: a szemiklasszikus Hawking-leírás érvényes
    pub semiclassical_valid: bool,
    pub spectrum: Spectrum,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EnergyLedger {
    /// M0·c² (J)
    pub initial_energy: f64,
    /// M_vég·c² (J)
    pub final_exterior_energy: f64,
    /// ∫P dt az idővonalon (J) — intervallumonként P ∝ t_hátralévő^(−2/3)
    /// feltevéssel (állandó α-ra egzakt), a hátralévő idő szerint
    pub radiated_energy: f64,
    /// |E0 − E_vég − E_rad| / E0 — a mintavételezés numerikus konzisztenciája
    pub relative_error: f64,
    /// A belső porgömb tömeg-energiája (J) — állandó, nem keletkezik a semmiből
    pub interior_energy: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationResults {
    pub schema_version: String,
    pub config: SimulationConfig,
    pub timeline: Vec<TimeStep>,
    pub evaporation_complete: bool,
    /// A párolgás végtömege (kg) — az LQC tömegrés M_min
    pub end_mass: f64,
    pub interior: InteriorTrajectory,
    /// Csak Norbi módban: a visszapattanás utáni tágulás
    pub baby_universe: Vec<BabyUniverseState>,
    pub causal_channel: CausalChannel,
    pub energy: EnergyLedger,
    pub warnings: Vec<String>,
    /// A bemeneti payload változatlanul (nyomon követhetőség)
    pub payload: serde_json::Value,
}
