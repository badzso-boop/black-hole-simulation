use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Részecske típusok
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ParticleType {
    Photon,
    Electron,
    Proton,
    Neutron,
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Particle {
    pub mass: f64,
    pub energy: f64,
    pub angular_momentum: f64,
    pub initial_radius: f64,
    pub particle_type: ParticleType,
}

impl Particle {
    pub fn test_particle() -> Self {
        Self {
            mass: 1.0,
            energy: 1e20,
            angular_momentum: 0.0,
            initial_radius: 1e6,
            particle_type: ParticleType::Proton,
        }
    }
}

// ---------------------------------------------------------------------------
// Sugárzási spektrum
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Spectrum {
    pub frequencies: Vec<f64>,
    pub intensities: Vec<f64>,
    pub temperature: f64,
    pub total_power: f64,
}


// ---------------------------------------------------------------------------
// Belső fizika állapotok
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BabyUniverseState {
    pub scale_factor: f64,
    pub expansion_rate: f64,
    pub internal_density: f64,
    pub edge_breakup_rate: f64,
    pub total_energy: f64,
    pub age: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhysicsBoundary {
    pub radius: f64,
    pub density: f64,
    pub time: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InteriorState {
    pub time: f64,
    pub proper_time: f64,
    pub radius: f64,
    pub density: f64,
    pub ricci_scalar: f64,
    pub at_planck_scale: bool,
    pub radiation: Spectrum,
    pub physics_boundary: Option<PhysicsBoundary>,
    pub bounce_occurred: bool,
    pub baby_universe: Option<BabyUniverseState>,
}

// ---------------------------------------------------------------------------
// Szimulációs konfiguráció
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SimMode {
    Lite,
    Standard,
    Research,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationConfig {
    pub mode: SimMode,
    pub max_external_objects: usize,
    pub max_internal_objects: usize,
    pub internal_dt: f64,
    pub external_dt: f64,
    pub norbi_mode: bool,
    pub gravitational_softening: f64,
}

impl SimulationConfig {
    pub fn lite() -> Self {
        Self {
            mode: SimMode::Lite,
            max_external_objects: 10,
            max_internal_objects: 20,
            internal_dt: 1e-10,
            external_dt: 1e6,
            norbi_mode: true,
            gravitational_softening: 0.01,
        }
    }

    pub fn standard() -> Self {
        Self {
            mode: SimMode::Standard,
            max_external_objects: 100,
            max_internal_objects: 200,
            internal_dt: 1e-11,
            external_dt: 1e5,
            norbi_mode: true,
            gravitational_softening: 0.001,
        }
    }

    pub fn research() -> Self {
        Self {
            mode: SimMode::Research,
            max_external_objects: 1000,
            max_internal_objects: 5000,
            internal_dt: 1e-12,
            external_dt: 1e4,
            norbi_mode: true,
            gravitational_softening: 0.0001,
        }
    }
}

// ---------------------------------------------------------------------------
// Szimulációs eredmények
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeStep {
    pub time: f64,
    pub mass: f64,
    pub temperature: f64,
    pub entropy: f64,
    pub spectrum: Spectrum,
    pub interior: InteriorState,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationResults {
    pub schema_version: String,
    pub config: SimulationConfig,
    pub timeline: Vec<TimeStep>,
    pub evaporation_complete: bool,
}

impl SimulationResults {
    pub fn new(config: SimulationConfig) -> Self {
        Self {
            schema_version: "2.0".to_string(),
            config,
            timeline: Vec::new(),
            evaporation_complete: false,
        }
    }
}

// ---------------------------------------------------------------------------
// Bevy-hez: belső objektum (vizualizációhoz)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ObjectType {
    Star,
    Planet,
    Asteroid,
    GasCloud,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternalObjectData {
    pub mass: f64,
    pub radius: f64,
    pub position: [f64; 3],
    pub velocity: [f64; 3],
    pub entry_time: f64,
    pub fragmented: bool,
    pub obj_type: ObjectType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BreakupEvent {
    pub released_energy: f64,
    pub position_on_horizon: [f64; 3],
    pub time: f64,
}
