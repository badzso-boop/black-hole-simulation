use bevy::prelude::*;

/// Black hole: sötét gömb + emissive eseményhorizont gyűrű
pub fn black_hole_material(materials: &mut Assets<StandardMaterial>) -> Handle<StandardMaterial> {
    materials.add(StandardMaterial {
        base_color: Color::srgb(0.02, 0.02, 0.05),
        emissive: LinearRgba::new(0.8, 0.4, 0.0, 1.0),
        metallic: 0.9,
        perceptual_roughness: 0.1,
        ..default()
    })
}

/// Hawking-sugárzás pont: fényes narancs
pub fn hawking_point_material(materials: &mut Assets<StandardMaterial>) -> Handle<StandardMaterial> {
    materials.add(StandardMaterial {
        base_color: Color::srgba(1.0, 0.6, 0.1, 0.9),
        emissive: LinearRgba::new(5.0, 2.0, 0.1, 1.0),
        unlit: true,
        ..default()
    })
}

/// Belső objektum: kőzetszerű
pub fn internal_object_material(materials: &mut Assets<StandardMaterial>) -> Handle<StandardMaterial> {
    materials.add(StandardMaterial {
        base_color: Color::srgb(0.6, 0.5, 0.4),
        metallic: 0.1,
        perceptual_roughness: 0.8,
        ..default()
    })
}

/// Külső bolygó
pub fn planet_material(color: Color, materials: &mut Assets<StandardMaterial>) -> Handle<StandardMaterial> {
    materials.add(StandardMaterial {
        base_color: color,
        metallic: 0.0,
        perceptual_roughness: 0.6,
        ..default()
    })
}
