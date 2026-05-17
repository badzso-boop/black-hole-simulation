use bevy::prelude::*;
use crate::components::{InternalObject, BlackHoleMarker};

/// Szétszakadás vizuális effekt — sugaras részecske spray
pub fn spawn_breakup_effect(
    commands: &mut Commands,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<StandardMaterial>,
    position: Vec3,
    energy: f64,
) {
    let count = (energy.log10().max(1.0) as usize).clamp(4, 16);
    let intensity = (energy / 1e30).clamp(0.1, 10.0) as f32;

    for i in 0..count {
        let angle = i as f32 * std::f32::consts::TAU / count as f32;
        let speed = 0.5 + intensity * 0.5;
        let velocity = Vec3::new(angle.cos() * speed, (i as f32 * 0.3).sin() * 0.2, angle.sin() * speed);

        commands.spawn((
            Mesh3d(meshes.add(Sphere::new(0.05))),
            MeshMaterial3d(materials.add(StandardMaterial {
                base_color: Color::srgba(1.0, 0.3, 0.05, 0.95),
                emissive: LinearRgba::new(12.0, 3.0, 0.1, 1.0),
                unlit: true,
                ..default()
            })),
            Transform::from_translation(position),
            BreakupFragment {
                velocity,
                lifetime: 1.5,
                max_lifetime: 1.5,
            },
        ));
    }
}

#[derive(Component)]
pub struct BreakupFragment {
    pub velocity: Vec3,
    pub lifetime: f32,
    pub max_lifetime: f32,
}

/// Szétszakadás töredékek mozgása és eltűnése
pub fn update_breakup_fragments(
    mut commands: Commands,
    time: Res<Time>,
    mut fragments_q: Query<(Entity, &mut BreakupFragment, &mut Transform)>,
) {
    let dt = time.delta_secs();
    for (entity, mut frag, mut transform) in fragments_q.iter_mut() {
        frag.lifetime -= dt;
        if frag.lifetime <= 0.0 {
            commands.entity(entity).despawn();
            continue;
        }
        transform.translation += frag.velocity * dt;
        frag.velocity *= 0.95; // légköri fékező hatás szimulálás
        let scale = (frag.lifetime / frag.max_lifetime).powi(2);
        transform.scale = Vec3::splat(scale * 0.15);
    }
}

/// Tidal erő alapú automatikus szétszakadás detekció
pub fn detect_tidal_breakup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut objects_q: Query<(Entity, &mut InternalObject, &Transform)>,
    bh_q: Query<(&BlackHoleMarker, &Transform)>,
) {
    const G: f64 = 6.674e-11;
    const H_INF: f64 = 1e10; // csökkentett belső tágulási ráta a vizuális demóhoz

    for (entity, mut obj, obj_transform) in objects_q.iter_mut() {
        if obj.fragmented {
            continue;
        }
        for (bh, bh_transform) in bh_q.iter() {
            let r_vec = obj_transform.translation - bh_transform.translation;
            let r = r_vec.length() as f64;
            let r_s = bh.schwarzschild_radius;

            // Egyszerűsített tidal trigger: r < 1.5 * r_s
            if r < r_s * 1.5 && r > 0.01 {
                let m = obj.mass;
                let obj_r = 0.1_f64; // objektum sugara
                let e_tidal = 0.5 * m * H_INF * H_INF * obj_r * obj_r;
                let e_bind = 3.0 * G * m * m / (5.0 * obj_r);

                if e_tidal > e_bind {
                    obj.fragmented = true;
                    let pos = obj_transform.translation;
                    let energy = e_tidal;
                    spawn_breakup_effect(&mut commands, &mut meshes, &mut materials, pos, energy);
                    commands.entity(entity).despawn();
                }
            }
        }
    }
}
