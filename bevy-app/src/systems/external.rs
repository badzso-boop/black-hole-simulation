use bevy::prelude::*;
use crate::components::{BlackHoleMarker, ExternalObject, HawkingEmissionPoint, TrailRenderer};

/// A fekete lyuk megjelenítése — sötét gömb + emissive eseményhorizont
pub fn update_black_hole_visual(
    mut bh_q: Query<(&BlackHoleMarker, &mut Transform)>,
) {
    for (bh, mut transform) in bh_q.iter_mut() {
        let r_s = bh.schwarzschild_radius as f32;
        transform.scale = Vec3::splat(r_s.max(0.1));
    }
}

/// Gravitációs tér vonalak (Gizmos)
pub fn draw_gravity_field(
    mut gizmos: Gizmos,
    bh_q: Query<(&BlackHoleMarker, &Transform)>,
) {
    for (bh, bh_transform) in bh_q.iter() {
        let center = bh_transform.translation;
        let r_s = bh.schwarzschild_radius as f32;

        // Eseményhorizont kör
        gizmos.circle(
            Isometry3d::new(center, Quat::from_rotation_x(std::f32::consts::FRAC_PI_2)),
            r_s,
            Color::srgb(1.0, 0.5, 0.0),
        );

        // Gravitációs tér vonalak (8 irányban)
        for i in 0..8 {
            let angle = i as f32 * std::f32::consts::TAU / 8.0;
            let dir = Vec3::new(angle.cos(), 0.0, angle.sin());
            for j in 1..=5 {
                let r = r_s * (j as f32 * 2.0);
                let alpha = 1.0 / (j as f32);
                gizmos.line(
                    center + dir * r,
                    center + dir * (r - r_s * 1.5),
                    Color::srgba(0.3, 0.6, 1.0, alpha),
                );
            }
        }
    }
}

/// Hawking-sugárzás pontok élettartam alapú eltüntetése
pub fn fade_hawking_points(
    mut commands: Commands,
    time: Res<Time>,
    mut points_q: Query<(Entity, &mut HawkingEmissionPoint, &mut Transform)>,
) {
    for (entity, mut point, mut transform) in points_q.iter_mut() {
        point.lifetime -= time.delta_secs();
        if point.lifetime <= 0.0 {
            commands.entity(entity).despawn();
        } else {
            let scale = (point.lifetime / point.max_lifetime).sqrt();
            transform.scale = Vec3::splat(scale * 0.3);
        }
    }
}

/// Pályavonal frissítése
pub fn update_trail(
    mut trail_q: Query<(&mut TrailRenderer, &Transform), With<ExternalObject>>,
) {
    for (mut trail, transform) in trail_q.iter_mut() {
        trail.points.push(transform.translation);
        if trail.points.len() > trail.max_points {
            trail.points.remove(0);
        }
    }
}

/// Pályavonal rajzolása Gizmos-szal
pub fn draw_trails(
    mut gizmos: Gizmos,
    trail_q: Query<&TrailRenderer>,
) {
    for trail in trail_q.iter() {
        let n = trail.points.len();
        for i in 1..n {
            let alpha = i as f32 / n as f32;
            gizmos.line(
                trail.points[i - 1],
                trail.points[i],
                Color::srgba(0.8, 0.8, 0.2, alpha * 0.7),
            );
        }
    }
}
