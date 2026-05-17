mod components;
mod cameras;
mod materials;
mod bridge;
mod systems;

use bevy::prelude::*;
use components::*;
use systems::{
    external::{update_black_hole_visual, draw_gravity_field, fade_hawking_points, update_trail, draw_trails},
    internal::{update_internal_gravity, update_baby_universe_expansion, highlight_fragmented},
    hawking::periodic_hawking_demo,
    breakup::{update_breakup_fragments, detect_tidal_breakup},
    input::{handle_object_placement, handle_reset, update_help_text, HelpText},
};

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Fekete Lyuk — Belső Univerzum Szimulátor".to_string(),
                resolution: (1600.0, 900.0).into(),
                ..default()
            }),
            ..default()
        }))
        .add_systems(Startup, setup)
        .add_systems(Update, (
            update_black_hole_visual,
            draw_gravity_field,
            fade_hawking_points,
            update_trail,
            draw_trails,
            update_internal_gravity,
            update_baby_universe_expansion,
            highlight_fragmented,
            periodic_hawking_demo,
            update_breakup_fragments,
            detect_tidal_breakup,
            handle_object_placement,
            handle_reset,
            update_help_text,
            cameras::fly_camera_system,
        ))
        .run();
}

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials_res: ResMut<Assets<StandardMaterial>>,
) {
    // Fekete lyuk
    let bh_material = materials::black_hole_material(&mut materials_res);
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(1.0))),
        MeshMaterial3d(bh_material),
        Transform::from_translation(Vec3::ZERO),
        BlackHoleMarker {
            schwarzschild_radius: 3.0,
            mass: 1e30,
        },
    ));

    // Külső kamera (bal viewport)
    cameras::setup_external_camera(&mut commands);

    // Belső kamera (jobb viewport)
    cameras::setup_internal_camera(&mut commands);

    // Direktionális fény
    commands.spawn((
        DirectionalLight {
            illuminance: 3000.0,
            color: Color::srgb(0.8, 0.85, 1.0),
            shadows_enabled: false,
            ..default()
        },
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.8, 0.4, 0.0)),
    ));

    // Pont fény a fekete lyuknál (eseményhorizont izzás)
    commands.spawn((
        PointLight {
            intensity: 500_000.0,
            color: Color::srgb(1.0, 0.5, 0.1),
            radius: 5.0,
            range: 20.0,
            ..default()
        },
        Transform::from_translation(Vec3::new(0.0, 0.0, 0.0)),
    ));

    // Háttér csillagok (belső tér)
    spawn_background_stars(&mut commands, &mut meshes, &mut materials_res);

    // Belső objektumok
    spawn_internal_objects(&mut commands, &mut meshes, &mut materials_res);

    // HUD szöveg
    commands.spawn((
        Text::new("H = súgó"),
        TextFont {
            font_size: 18.0,
            ..default()
        },
        TextColor(Color::WHITE),
        Node {
            position_type: PositionType::Absolute,
            bottom: Val::Px(12.0),
            left: Val::Px(12.0),
            ..default()
        },
        HelpText,
    ));

    // Cím szöveg
    commands.spawn((
        Text::new("Fekete Lyuk — Belső Univerzum Szimulátor"),
        TextFont {
            font_size: 22.0,
            ..default()
        },
        TextColor(Color::srgb(1.0, 0.7, 0.2)),
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(12.0),
            left: Val::Px(12.0),
            ..default()
        },
    ));
}

fn spawn_background_stars(
    commands: &mut Commands,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<StandardMaterial>,
) {
    use std::f32::consts::TAU;
    let star_mat = materials.add(StandardMaterial {
        base_color: Color::WHITE,
        emissive: LinearRgba::new(2.0, 2.0, 2.0, 1.0),
        unlit: true,
        ..default()
    });

    for i in 0..80 {
        let phi = (i as f32 * 137.5_f32.to_radians()) % TAU;
        let theta = ((i as f32 / 80.0) * std::f32::consts::PI).acos();
        let r = 40.0 + (i as f32 * 0.7) % 20.0;
        let pos = Vec3::new(
            r * theta.sin() * phi.cos(),
            r * theta.cos(),
            r * theta.sin() * phi.sin(),
        );
        commands.spawn((
            Mesh3d(meshes.add(Sphere::new(0.08))),
            MeshMaterial3d(star_mat.clone()),
            Transform::from_translation(pos),
        ));
    }
}

fn spawn_internal_objects(
    commands: &mut Commands,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<StandardMaterial>,
) {
    let obj_mat = materials::internal_object_material(materials);

    for i in 0..5 {
        let angle = i as f32 * std::f32::consts::TAU / 5.0;
        let r = 8.0 + i as f32 * 1.5;
        let pos = Vec3::new(angle.cos() * r, (i as f32 * 0.4).sin() * 2.0, angle.sin() * r);
        commands.spawn((
            Mesh3d(meshes.add(Sphere::new(0.4))),
            MeshMaterial3d(obj_mat.clone()),
            Transform::from_translation(pos),
            InternalObject {
                mass: 1e20,
                fragmented: false,
                entry_time: 0.0,
            },
        ));
    }

    // BabyUniverse mag
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(1.5))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::srgba(0.1, 0.3, 0.8, 0.4),
            emissive: LinearRgba::new(0.2, 0.5, 2.0, 1.0),
            alpha_mode: AlphaMode::Blend,
            ..default()
        })),
        Transform::from_translation(Vec3::new(10.0, 0.0, 0.0)),
        BabyUniverseMarker { scale_factor: 1.0, age: 0.0 },
    ));
}
