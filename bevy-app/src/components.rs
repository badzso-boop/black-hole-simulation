use bevy::prelude::*;

// ---------------------------------------------------------------------------
// Külső univerzum komponensek
// ---------------------------------------------------------------------------

#[derive(Component, Debug, Clone)]
pub struct ExternalObject {
    pub mass: f64,
    pub radius: f64,
    pub obj_type: ObjectType,
}

#[derive(Component, Debug, Clone)]
pub struct BlackHoleMarker {
    pub schwarzschild_radius: f64,
    pub mass: f64,
}

#[derive(Component, Debug, Clone)]
pub struct HawkingEmissionPoint {
    pub energy: f64,
    pub lifetime: f32,
    pub max_lifetime: f32,
}

#[derive(Component, Debug, Clone)]
pub struct TrailRenderer {
    pub points: Vec<Vec3>,
    pub max_points: usize,
}

// ---------------------------------------------------------------------------
// Belső univerzum komponensek
// ---------------------------------------------------------------------------

#[derive(Component, Debug, Clone)]
pub struct InternalObject {
    pub mass: f64,
    pub fragmented: bool,
    pub entry_time: f64,
}

#[derive(Component, Debug, Clone)]
pub struct BabyUniverseMarker {
    pub scale_factor: f64,
    pub age: f64,
}

// ---------------------------------------------------------------------------
// Kamera markerek
// ---------------------------------------------------------------------------

#[derive(Component)]
pub struct ExternalCameraMarker;

#[derive(Component)]
pub struct InternalCameraMarker;

// ---------------------------------------------------------------------------
// Segédtípusok
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, PartialEq)]
pub enum ObjectType {
    Star,
    Planet,
    Asteroid,
    GasCloud,
}
