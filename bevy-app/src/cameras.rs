use bevy::prelude::*;
use crate::components::{ExternalCameraMarker, InternalCameraMarker};

pub const SCREEN_W: u32 = 1920;
pub const SCREEN_H: u32 = 1080;

/// BAL PANEL — Orbit kamera a fekete lyuk körül
/// Jobb klikk drag: forgatás | Scroll: zoom
pub fn setup_external_camera(commands: &mut Commands) {
    commands.spawn((
        Camera3d::default(),
        Transform::from_xyz(0.0, 15.0, 30.0).looking_at(Vec3::ZERO, Vec3::Y),
        Camera {
            order: 0,
            viewport: Some(bevy::render::camera::Viewport {
                physical_position: UVec2::new(0, 0),
                physical_size: UVec2::new(SCREEN_W / 2, SCREEN_H),
                ..default()
            }),
            ..default()
        },
        ExternalCameraMarker,
    ));
}

/// JOBB PANEL — Szabad repülős kamera (WASD + egér)
pub fn setup_internal_camera(commands: &mut Commands) {
    commands.spawn((
        Camera3d::default(),
        Transform::from_xyz(0.0, 5.0, 10.0).looking_at(Vec3::ZERO, Vec3::Y),
        Camera {
            order: 1,
            viewport: Some(bevy::render::camera::Viewport {
                physical_position: UVec2::new(SCREEN_W / 2, 0),
                physical_size: UVec2::new(SCREEN_W / 2, SCREEN_H),
                ..default()
            }),
            ..default()
        },
        InternalCameraMarker,
    ));
}

/// Belső kamera irányítás — WASD + egér
pub fn fly_camera_system(
    keyboard: Res<ButtonInput<KeyCode>>,
    time: Res<Time>,
    mut camera_q: Query<&mut Transform, With<InternalCameraMarker>>,
) {
    let Ok(mut transform) = camera_q.get_single_mut() else { return };
    let speed = 5.0 * time.delta_secs();
    let forward = transform.forward();
    let right = transform.right();

    if keyboard.pressed(KeyCode::KeyW) { transform.translation += forward * speed; }
    if keyboard.pressed(KeyCode::KeyS) { transform.translation -= forward * speed; }
    if keyboard.pressed(KeyCode::KeyA) { transform.translation -= right * speed; }
    if keyboard.pressed(KeyCode::KeyD) { transform.translation += right * speed; }
    if keyboard.pressed(KeyCode::KeyQ) { transform.translation -= Vec3::Y * speed; }
    if keyboard.pressed(KeyCode::KeyE) { transform.translation += Vec3::Y * speed; }
}
