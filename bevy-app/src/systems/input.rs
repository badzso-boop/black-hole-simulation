use bevy::prelude::*;
use crate::components::{BlackHoleMarker, ExternalObject, TrailRenderer, ObjectType};

/// Egér klikk alapú objektum lerakás a külső térben
pub fn handle_object_placement(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mouse_buttons: Res<ButtonInput<MouseButton>>,
    keyboard: Res<ButtonInput<KeyCode>>,
    bh_q: Query<(&BlackHoleMarker, &Transform)>,
    camera_q: Query<(&Camera, &GlobalTransform)>,
    windows: Query<&Window>,
) {
    if !mouse_buttons.just_pressed(MouseButton::Left) {
        return;
    }

    // Shift+klikk = objektum lerakás
    if !keyboard.pressed(KeyCode::ShiftLeft) && !keyboard.pressed(KeyCode::ShiftRight) {
        return;
    }

    let Ok(window) = windows.get_single() else { return };
    let Some(cursor_pos) = window.cursor_position() else { return };

    // Vetítés a 3D térbe: y=0 sík metszéspontja
    for (camera, cam_transform) in camera_q.iter() {
        let Ok(ray) = camera.viewport_to_world(cam_transform, cursor_pos) else { continue };

        let t = if ray.direction.y.abs() > 1e-6 {
            -ray.origin.y / ray.direction.y
        } else {
            10.0
        };
        let world_pos = ray.origin + ray.direction * t;

        // Automatikus keringési sebesség v = √(GM/r)
        let orbital_velocity = if let Some((bh, bh_t)) = bh_q.iter().next() {
            const G: f32 = 6.674e-11;
            let r = (world_pos - bh_t.translation).length();
            if r > 0.1 {
                let v_mag = (G * bh.mass as f32 / r).sqrt();
                let to_bh = (bh_t.translation - world_pos).normalize();
                let up = Vec3::Y;
                let tangent = up.cross(to_bh).normalize();
                tangent * v_mag.min(5.0) // vizuális korlát
            } else {
                Vec3::ZERO
            }
        } else {
            Vec3::ZERO
        };

        let _ = orbital_velocity; // sebesség jövőbeli fizika rendszerhez

        let color = if keyboard.pressed(KeyCode::KeyB) {
            Color::srgb(0.2, 0.5, 1.0) // kék = nehéz objektum
        } else {
            Color::srgb(0.3, 0.9, 0.3) // zöld = könnyű
        };

        let mass = if keyboard.pressed(KeyCode::KeyB) { 1e28_f64 } else { 1e24_f64 };

        commands.spawn((
            Mesh3d(meshes.add(Sphere::new(0.3))),
            MeshMaterial3d(materials.add(StandardMaterial {
                base_color: color,
                metallic: 0.0,
                perceptual_roughness: 0.6,
                ..default()
            })),
            Transform::from_translation(world_pos),
            ExternalObject {
                mass,
                radius: 0.3,
                obj_type: ObjectType::Planet,
            },
            TrailRenderer {
                points: Vec::new(),
                max_points: 200,
            },
        ));
        break;
    }
}

/// Szimuláció visszaállítás R billentyűvel
pub fn handle_reset(
    mut commands: Commands,
    keyboard: Res<ButtonInput<KeyCode>>,
    external_q: Query<Entity, With<ExternalObject>>,
) {
    if keyboard.just_pressed(KeyCode::KeyR) {
        for entity in external_q.iter() {
            commands.entity(entity).despawn();
        }
    }
}

/// HUD szöveg frissítése a jelenlegi tippekkel
pub fn update_help_text(
    mut text_q: Query<&mut Text, With<HelpText>>,
    keyboard: Res<ButtonInput<KeyCode>>,
) {
    for mut text in text_q.iter_mut() {
        if keyboard.pressed(KeyCode::KeyH) {
            text.0 = "Shift+klikk: bolygó lerak | Shift+B+klikk: nehéz | R: törlés | WASD: kamera".to_string();
        } else {
            text.0 = "H = súgó".to_string();
        }
    }
}

#[derive(Component)]
pub struct HelpText;
