use bevy::prelude::*;
use crate::components::{BlackHoleMarker, HawkingEmissionPoint};

/// Hawking-sugárzás pont spawnoláss az eseményhorizonton
pub fn spawn_hawking_point(
    commands: &mut Commands,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<StandardMaterial>,
    position: Vec3,
    energy: f64,
) {
    let lifetime = 2.0_f32;
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(0.15))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::srgba(1.0, 0.6, 0.1, 0.9),
            emissive: LinearRgba::new(8.0, 3.0, 0.2, 1.0),
            unlit: true,
            ..default()
        })),
        Transform::from_translation(position),
        HawkingEmissionPoint {
            energy,
            lifetime,
            max_lifetime: lifetime,
        },
    ));
}

/// Periodikus Hawking-emissziók szimulálása (vizuális demo)
pub fn periodic_hawking_demo(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    time: Res<Time>,
    bh_q: Query<(&BlackHoleMarker, &Transform)>,
    mut timer: Local<f32>,
) {
    *timer += time.delta_secs();
    if *timer < 0.5 { return; }
    *timer = 0.0;

    for (bh, bh_transform) in bh_q.iter() {
        let r_s = bh.schwarzschild_radius as f32;
        let angle = time.elapsed_secs() * 2.3;
        let pos = bh_transform.translation + Vec3::new(
            angle.cos() * r_s * 1.1,
            (angle * 0.7).sin() * r_s * 0.3,
            angle.sin() * r_s * 1.1,
        );
        spawn_hawking_point(&mut commands, &mut meshes, &mut materials, pos, 1e20);
    }
}
