use black_hole_core::black_hole::evaporation::evaporation_history;
use black_hole_core::constants::{M_MIN_LMY, M_SUN};
use black_hole_core::radiation::emission::EmissionModel;
use black_hole_core::{BlackHoleTrait, HawkingEngine, RadiationEngine, SchwarzschildBlackHole};
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

fn bench_full_evaporation_history(c: &mut Criterion) {
    c.bench_function("evaporation_history_1e12kg_100_samples", |b| {
        b.iter(|| evaporation_history(EmissionModel::MacGibbon, 1e12, M_MIN_LMY, 100).unwrap())
    });
}

criterion_group!(
    benches,
    bench_hawking_temperature,
    bench_schwarzschild_radius,
    bench_spectrum_computation,
    bench_full_evaporation_history
);
criterion_main!(benches);
