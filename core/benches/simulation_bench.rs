use black_hole_core::{
    HawkingEngine, RadiationEngine, SchwarzschildBlackHole, BlackHoleTrait,
};
use black_hole_core::constants::{M_PLANCK, M_SUN, T_PLANCK};
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_hawking_temperature(c: &mut Criterion) {
    c.bench_function("hawking_temp_sun_mass", |b| {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        b.iter(|| bh.hawking_temperature().unwrap())
    });
}

fn bench_schwarzschild_radius(c: &mut Criterion) {
    c.bench_function("schwarzschild_radius_sun", |b| {
        let bh = SchwarzschildBlackHole::new(M_SUN).unwrap();
        b.iter(|| black_box(bh.schwarzschild_radius()))
    });
}

fn bench_spectrum_computation(c: &mut Criterion) {
    c.bench_function("spectrum_1000_bins", |b| {
        let bh = SchwarzschildBlackHole::new(1e15).unwrap();
        let engine = HawkingEngine::new();
        b.iter(|| engine.compute_spectrum(&bh).unwrap())
    });
}

fn bench_full_evaporation_planck(c: &mut Criterion) {
    c.bench_function("planck_mass_evaporation", |b| {
        let engine = HawkingEngine::new();
        b.iter(|| {
            let mut bh = SchwarzschildBlackHole::new(M_PLANCK).unwrap();
            while bh.mass() > M_PLANCK * 0.001 {
                if engine.evolve_step(&mut bh, T_PLANCK).is_err() {
                    break;
                }
            }
        })
    });
}

criterion_group!(
    benches,
    bench_hawking_temperature,
    bench_schwarzschild_radius,
    bench_spectrum_computation,
    bench_full_evaporation_planck
);
criterion_main!(benches);
