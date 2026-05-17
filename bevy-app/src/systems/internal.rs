use bevy::prelude::*;
use crate::components::{BabyUniverseMarker, InternalObject};

/// Belső objektumok gravitációs mozgása (N-test közelítés)
pub fn update_internal_gravity(
    time: Res<Time>,
    mut objects_q: Query<(&InternalObject, &mut Transform)>,
) {
    const G: f64 = 6.674e-11;
    const SOFTENING: f64 = 0.1;

    // Pozíciók összegyűjtése
    let positions: Vec<(Entity, Vec3, f64)> = objects_q
        .iter()
        .map(|(obj, t)| (Entity::PLACEHOLDER, t.translation, obj.mass))
        .collect();

    // Erők kiszámítása és alkalmazása
    for (_obj, mut transform) in objects_q.iter_mut() {
        let pos = transform.translation;
        let mut force = Vec3::ZERO;

        for (_, other_pos, other_mass) in &positions {
            let r = *other_pos - pos;
            let r_sq = r.length_squared() as f64 + SOFTENING * SOFTENING;
            let r_mag = r_sq.sqrt();
            let f_mag = G * other_mass / r_sq;
            force += r.normalize() * (f_mag / r_mag) as f32;
        }

        transform.translation += force * time.delta_secs();
    }
}

/// Belső tágulás vizualizálása — a háttér csillagok távolabb kerülnek
pub fn update_baby_universe_expansion(
    time: Res<Time>,
    mut bu_q: Query<(&mut BabyUniverseMarker, &mut Transform)>,
) {
    for (mut bu, mut transform) in bu_q.iter_mut() {
        bu.age += time.delta_secs() as f64;
        let expansion = (bu.age * 0.01).exp() as f32;
        transform.scale = Vec3::splat(expansion.min(100.0));
    }
}

/// Szétszakadt objektumok vizuális jelzése
pub fn highlight_fragmented(
    mut gizmos: Gizmos,
    objects_q: Query<(&InternalObject, &Transform)>,
) {
    for (obj, transform) in objects_q.iter() {
        if obj.fragmented {
            gizmos.sphere(
                Isometry3d::from_translation(transform.translation),
                0.5,
                Color::srgb(1.0, 0.1, 0.1),
            );
        }
    }
}
