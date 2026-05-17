# Fekete Lyuk — Belső Univerzum Szimulátor

A „Norbi-hipotézis" numerikus vizsgálata: vajon egy fekete lyuk belsejében kvantumvisszapattanással bébiuniverzum keletkezik-e, és a Hawking-sugárzás forrása a belső tágulás szélén szétszakadó anyag?

---

## A Norbi-hipotézis

A standard modell szerint a fekete lyuk elpárlása során a Hawking-sugárzás az eseményhorizont közelében keletkező virtuális részecskepárokból ered, és az információ elvész (információs paradoxon).

A **Norbi-hipotézis** szerint:

1. A fekete lyuk belsejében a sűrűség eléri a Planck-sűrűséget (ρ_P ≈ 5.155×10⁹⁶ kg/m³)
2. A Loop Quantum Cosmology (LQC) módosított Friedmann-egyenlete szerint a gravitációs összeomlás **kvantumvisszapattanásba** fordul
3. A visszapattanás egy új, tágul **bébiuniverzumot** hoz létre a fekete lyuk belsejében
4. A bébiuniverzum tágulásának szélén az anyag **szétszakad** (tidal erő > kötési energia)
5. A szétszakadó anyag **sugároz** — ez az, amit kívülről Hawking-sugárzásként érzékelünk
6. Az információ nem vész el, hanem a bébiuniverzumba kerül

```
Fekete lyuk
    └─► Összeomlás → ρ → ρ_Planck
            └─► LQC: H² = (8πG/3)·ρ·(1 - ρ/ρ_P) = 0  → kvantumvisszapattanás
                    └─► BabyUniverse: a(t) = a₀·e^(H_inf·t)
                            └─► e_tidal > e_bind → szétszakadás + sugárzás
                                    └─► Hawking-spektrum (külső megfigyelőnek)
```

---

## Tech Stack

| Réteg | Technológia | Szerep |
|---|---|---|
| Fizikai mag | **Rust** (core/) | Minden számítás, OOP trait-ek |
| Python elemzés | **Python 3.12** + numpy/scipy/sklearn | PCA, FFT, hash rekonstrukció |
| 3D vizualizáció | **Bevy 0.15** (ECS) | Valós idejű 3D szimuláció |
| Asztali UI | **Tauri 2** + React + TypeScript | Vezérlőpult, grafikonok |
| Python↔Rust híd | **PyO3 0.21** + maturin | Natív Python modul |
| CI/CD | **GitHub Actions** | Automatikus tesztelés |

---

## Mappaszerkezet

```
black-hole-simulator/
│
├── Cargo.toml                      # Rust workspace (core + bevy-app + tauri)
├── pyproject.toml                  # Python projekt (maturin build backend)
│
├── core/                           # Rust fizikai mag
│   ├── src/
│   │   ├── constants.rs            # G, c, ħ, k_B, l_P, ρ_Planck, M_Planck, M_Sun
│   │   ├── error.rs                # SimulationError enum (thiserror)
│   │   ├── types.rs                # Adatsémák (Particle, Spectrum, TimeStep, ...)
│   │   ├── lib.rs                  # Publikus API + PyO3 binding
│   │   │
│   │   ├── black_hole/
│   │   │   ├── mod.rs              # Trait definíciók (BlackHoleTrait, InteriorModel, RadiationEngine)
│   │   │   ├── schwarzschild.rs    # Schwarzschild fekete lyuk implementáció
│   │   │   ├── thermodynamics.rs   # Page-idő, greybody faktor, Wien-törvény
│   │   │   └── kerr.rs             # Kerr stub (v3)
│   │   │
│   │   ├── interior/
│   │   │   ├── baby_universe.rs    # BabyUniverse: tágulás, szétszakadás detekció
│   │   │   ├── norbi.rs            # NorbiInterior: kvantumvisszapattanás + bébiuniverzum
│   │   │   ├── standard.rs         # StandardInterior: geodézia, Planck-határnál megáll
│   │   │   └── cauchy.rs           # Cauchy-horizont stub (v3)
│   │   │
│   │   ├── radiation/
│   │   │   ├── hawking_engine.rs   # HawkingEngine: 1000-bines Planck-spektrum, greybody
│   │   │   ├── spectrum.rs         # Planck-spektrum számítás, normálás, csúcs frekvencia
│   │   │   └── soft_hair.rs        # Hawking soft hair stub (v3)
│   │   │
│   │   ├── quantum/
│   │   │   ├── lqc.rs              # LQCEquation: H²=(8πG/3)·ρ·(1-ρ/ρ_P), bounce detekció
│   │   │   ├── island.rs           # IslandFormula: Page-görbe (generalizált entrópia)
│   │   │   └── complexity.rs       # Holografikus komplexitás stub (v3)
│   │   │
│   │   ├── time_evolution/
│   │   │   ├── integrator.rs       # RK45 adaptív integrátor
│   │   │   └── checkpoint.rs       # Atomikus checkpoint mentés (MessagePack)
│   │   │
│   │   └── tests/                  # 12 tesztfájl, 53 teszt
│   │       ├── test_schwarzschild.rs
│   │       ├── test_hawking.rs
│   │       ├── test_lqc.rs
│   │       ├── test_interior.rs
│   │       ├── test_spectrum.rs
│   │       ├── test_edge_cases.rs
│   │       ├── test_validation.rs   # 7 irodalmi validáció (val_01..val_07)
│   │       ├── test_model_comparison.rs
│   │       ├── test_baby_universe.rs
│   │       ├── test_checkpoint.rs
│   │       ├── test_integrator.rs
│   │       └── test_norbi_eta.rs
│   │
│   └── benches/
│       └── simulation_bench.rs     # Criterion benchmarkok
│
├── python/                         # Python elemző réteg
│   ├── config.py                   # SimulationConfig (lite/standard/research gyárak)
│   ├── information_packet.py       # SHA3-256 hash, qubit kódolás, Von Neumann entrópia
│   ├── reverse_engineer.py         # PCA, FFT, hash rekonstrukció kísérlet
│   ├── comparator.py               # Standard vs Norbi spektrum/evolúció összehasonlítás
│   ├── quantum_sim.py              # Qiskit kvantum áramkör szimuláció
│   ├── qec_model.py                # HKLL rekonstrukció stub (v3)
│   ├── logging_config.py           # JSON logging inicializálás
│   ├── __main__.py                 # CLI belépési pont (argparse)
│   └── tests/
│       ├── test_information.py     # 7 teszt: hash, qubit, entrópia
│       ├── test_reverse_eng.py     # 4 teszt: PCA, FFT, similarity
│       └── test_comparator.py      # 6 teszt: spektrum SNR, evolúció összehasonlítás
│
├── bevy-app/                       # Bevy 3D vizualizáció
│   └── src/
│       ├── main.rs                 # App belépési pont, Startup + Update rendszerek
│       ├── components.rs           # ECS komponensek
│       ├── cameras.rs              # Osztott képernyő (külső orbit + belső fly kamera)
│       ├── materials.rs            # PBR anyagok (fekete lyuk, Hawking pont, bolygó)
│       ├── bridge.rs               # SimulationState (Arc<Mutex<...>>)
│       └── systems/
│           ├── external.rs         # Gravitációs tér gizmos, pályavonalak, eltűnő sugárzás
│           ├── internal.rs         # N-test gravitáció, bébiuniverzum tágulás
│           ├── hawking.rs          # Hawking emissziós pontok spawnolása
│           ├── breakup.rs          # Szétszakadás animáció (GPU-részecske spray)
│           └── input.rs            # Egér+billentyű: objektum lerakás, reset
│
├── tauri-app/                      # Tauri asztali vezérlőpult
│   ├── src/
│   │   ├── main.tsx                # React belépési pont
│   │   ├── styles.css              # Sötét téma (space aesthetic)
│   │   ├── hooks/
│   │   │   └── useSimulation.ts    # Szimuláció állapotkezelés (invoke API)
│   │   └── components/
│   │       ├── Dashboard.tsx       # Főképernyő, teljes layout
│   │       ├── ConfigPanel.tsx     # Tömeg csúszka, Norbi kapcsoló, presetek
│   │       ├── SpectrumChart.tsx   # Hawking-sugárzás spektrum SVG
│   │       ├── EntropyPlot.tsx     # Bekenstein-Hawking entrópia + Page-görbe
│   │       ├── KruskalDiagram.tsx  # Interaktív Kruskal–Szekeres diagram SVG
│   │       ├── InteriorView.tsx    # Belső állapot animált vizualizáció
│   │       └── ResultsPanel.tsx    # Számszerű eredmények, Norbi-magyarázat
│   └── src-tauri/
│       ├── src/
│       │   ├── main.rs             # Tauri app belépési pont
│       │   ├── commands.rs         # #[tauri::command]: run_simulation, get_state, toggle_norbi
│       │   └── python_bridge.rs    # subprocess JSON kommunikáció Python elemzővel
│       ├── build.rs                # tauri_build::build()
│       └── tauri.conf.json         # App konfiguráció (1400×900, identifier)
│
├── scripts/
│   ├── setup_dev.sh                # Fejlesztői környezet egy lépésben
│   ├── validate_results.py         # CI validátor (monoton tömeg, entrópia, NaN/Inf)
│   ├── benchmark_compare.py        # Két szimuláció összehasonlítása
│   ├── checkpoint_inspect.py       # MessagePack checkpoint megtekintése
│   └── export_csv.py               # Timeline CSV export
│
└── .github/workflows/
    ├── rust-tests.yml              # fmt + clippy + cargo test + tarpaulin
    ├── python-tests.yml            # maturin develop + ruff + mypy + pytest (3.11, 3.12)
    └── integration.yml             # E2E Planck-tömeg szimuláció + validáció (nightly)
```

---

## Fizikai képletek — implementálva

### Schwarzschild fekete lyuk (`core/src/black_hole/schwarzschild.rs`)

| Mennyiség | Képlet | Fájl |
|---|---|---|
| Schwarzschild-sugár | r_s = 2GM/c² | schwarzschild.rs:21 |
| Hawking-hőmérséklet | T_H = ħc³ / (8πGMk_B) | schwarzschild.rs:28 |
| Bekenstein-Hawking entrópia | S = A / (4·l_P²), ahol A = 4πr_s² | schwarzschild.rs:36 |
| Hawking-teljesítmény | P = ħc⁶ / (15360πG²M²) | schwarzschild.rs:44 |
| Elpárlási idő | t_evap = 5120πG²M₀³ / (ħc⁴) | schwarzschild.rs:51 |

### Loop Quantum Cosmology (`core/src/quantum/lqc.rs`)

Módosított Friedmann-egyenlet:

```
(ȧ/a)² = (8πG/3) · ρ · (1 - ρ/ρ_Planck)
```

- Ha ρ = ρ_Planck → H² = 0 → kvantumvisszapattanás (nem szingularitás)
- Ha ρ << ρ_Planck → klasszikus Friedmann egyenletbe tér vissza

### Bébiuniverzum szétszakadási feltétel (`core/src/interior/baby_universe.rs`)

```
e_tidal = 0.5 · m · H² · r²       (tidal energia)
e_bind  = 3·G·m² / (5·R)          (kötési energia)

Ha e_tidal > e_bind → BreakupEvent → sugárzás
```

### Planck-spektrum greybody faktorral (`core/src/radiation/hawking_engine.rs`)

```
B(ν, T) = (2hν³/c²) / (exp(hν/k_BT) - 1)   [Planck]
γ(ν)    = 1 - exp(-ν / ν_c)                   [greybody faktor]
I(ν)    = γ(ν) · B(ν, T)                      [effektív spektrum]
```

---

## OOP felépítés Rust-ban

A projekt a Rust trait rendszerét használja objektumorientált interfészként:

```rust
// Interfészek (black_hole/mod.rs)
pub trait BlackHoleTrait {
    fn mass(&self) -> f64;
    fn schwarzschild_radius(&self) -> f64;
    fn hawking_temperature(&self) -> Result<f64, SimulationError>;
    fn bekenstein_entropy(&self) -> f64;
    fn hawking_power(&self) -> Result<f64, SimulationError>;
    fn evaporation_time(&self) -> f64;
    fn update_mass(&mut self, delta_m: f64) -> Result<(), SimulationError>;
}

pub trait InteriorModel {
    fn simulate_step(...) -> Result<InteriorState, SimulationError>;
    fn at_physics_boundary(&self) -> bool;
    fn radiation_spectrum(&self) -> Vec<f64>;
}

pub trait RadiationEngine {
    fn compute_spectrum(&self, bh: &dyn BlackHoleTrait) -> Result<Spectrum, SimulationError>;
    fn evolve_step(&self, bh: &mut dyn BlackHoleTrait, dt: f64) -> Result<f64, SimulationError>;
}
```

**Implementációk:**
- `SchwarzschildBlackHole` → `BlackHoleTrait` (standard + Norbi módban)
- `StandardInterior` → `InteriorModel` (megáll ρ ≥ ρ_Planck-nál)
- `NorbiInterior` → `InteriorModel` (folytatja, kvantumvisszapattanással)
- `HawkingEngine` → `RadiationEngine` (Standard és Norbi variáns)

---

## Tesztek

### Rust tesztek (`cargo test --manifest-path core/Cargo.toml`)

**53 teszt, mind zöld.**

| Tesztfájl | Tesztek | Mit validál |
|---|---|---|
| test_schwarzschild.rs | 6 | r_s(M_Nap)≈2954 m, T_H, entrópia, elpárlási idő arányok |
| test_hawking.rs | 4 | Tömegcsökkenés, energiamegmaradás, Wien-törvény, greybody |
| test_lqc.rs | 4 | H²=0 ha ρ=ρ_P, LQC≈Friedmann kis ρ-nál, bounce trigger |
| test_interior.rs | 4 | Standard megáll, Norbi folytat, mindkettő egyezik Planck előtt |
| test_spectrum.rs | 3 | Bin szám, nem-negatív intenzitás, hőmérséklet tárolás |
| test_edge_cases.rs | 4 | Nulla/negatív/NaN tömeg → hiba, tömeg sosem negatív |
| test_validation.rs | 7 | Irodalmi referenciák (SCH16, HAW74, HAW75, PLA00, BEK73, PAG93, ASH06) |
| test_model_comparison.rs | 5 | Standard vs Norbi összehasonlítás |
| test_baby_universe.rs | 6 | Tágulás, szétszakadás logika, sugárzási spektrum |
| test_checkpoint.rs | 4 | Mentés/betöltés körforgás, MessagePack formátum |
| test_integrator.rs | 3 | RK45 konvergencia, gyorsulás iránya |
| test_norbi_eta.rs | 3 | η hatásfok számítás |

### Kulcs validációs számok (test_validation.rs)

```
r_s(M_Nap)  = 2954 m            ±5 m      [Schwarzschild 1916]
T_H(M_Nap)  = 6.17×10⁻⁸ K                [Hawking 1974]
t_evap arány: 2× tömeg → 8× idő           [Hawking 1975]
S arány: 2× tömeg → 4× entrópia           [Bekenstein 1973]
Wien-törvény: ν_max = 5.879×10¹⁰·T Hz     [Planck 1900]
Page-görbe: emelkedik, majd csökken        [Page 1993]
LQC: H²=0 ha ρ=ρ_P (tol: 1×10⁻¹⁰)       [Ashtekar 2006]
```

### Python tesztek (`.venv/bin/python -m pytest python/tests/`)

**17 teszt, mind zöld.**

| Tesztfájl | Tesztek | Mit validál |
|---|---|---|
| test_information.py | 7 | SHA3-256 hash, qubit normálás, Von Neumann entrópia |
| test_reverse_eng.py | 4 | PCA főkomponensek, FFT csúcs, similarity score |
| test_comparator.py | 6 | Spektrum SNR, detektálhatóság, evolúció divergencia |

---

## Futtatás

### Előfeltételek

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python virtuális környezet
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy scikit-learn pytest

# Ubuntu/WSL2 rendszerfüggőségek (Bevy + Tauri)
sudo apt install libudev-dev libasound2-dev libdbus-1-dev libgtk-3-dev libwebkit2gtk-4.1-dev
```

Vagy egyben:
```bash
bash scripts/setup_dev.sh
```

### Rust tesztek

```bash
cargo test --manifest-path core/Cargo.toml --verbose
```

### Validációs tesztek (irodalmi értékek ellenőrzése)

```bash
cargo test --manifest-path core/Cargo.toml validation -- --nocapture
```

### Python tesztek

```bash
.venv/bin/python -m pytest python/tests/ -v
```

### CLI headless szimuláció

```bash
# Standard Hawking-modell
python -m python.main --mass 2.176e-8 --norbi-mode false --no-ui --output standard.json

# Norbi-hipotézis
python -m python.main --mass 2.176e-8 --norbi-mode true --no-ui --output norbi.json

# Eredmény validáció
python scripts/validate_results.py standard.json norbi.json
```

### Bevy 3D vizualizáció

```bash
cargo run --manifest-path bevy-app/Cargo.toml
```

**Vezérlők:**
- `WASD + QE` — belső kamera (jobb panel)
- `Shift + klikk` — bolygó lerakása a külső térben
- `Shift + B + klikk` — nehéz objektum lerakása
- `R` — összes külső objektum törlése
- `H` — súgó megjelenítése

### Tauri asztali UI

```bash
cd tauri-app
npm install
cargo tauri dev
```

### Benchmarkok

```bash
cargo bench --manifest-path core/Cargo.toml
```

Elvárt teljesítmény:
- `hawking_temperature()` → < 100 ns
- Planck-tömeg teljes elpárlás → < 50 ms
- 1000-bines spektrum → < 1 ms

---

## Bevy 3D megjelenítés részletei

Az alkalmazás **osztott képernyőt** alkalmaz (1600×900):

- **Bal panel** — Külső nézet: orbit kamera a fekete lyuk körül
  - Eseményhorizont (emissive narancssárga gyűrű)
  - Gravitációs tér vonalak (8 irányban, távolságfüggő átlátszóság)
  - Hawking-sugárzás pontok (narancssárga gömbök, lifetime alapú eltűnés)
  - Pályavonalak (trail renderer, 200 pont)
  - Szétszakadás animáció (részecske spray, energiaarányos darabszám)

- **Jobb panel** — Belső nézet: szabad repülős kamera
  - 5 belső objektum N-test gravitációval
  - BabyUniverse mag (kék, félig átlátszó gömb)
  - 80 háttércsillag (fibonacci spirál elrendezés)
  - Szétszakadt objektumok piros Gizmos jelzéssel
  - Tidal erő alapú automatikus szétszakadás detekció

---

## Tauri UI komponensek

| Komponens | Funkció |
|---|---|
| `Dashboard.tsx` | Főlayout, állapotkezelés összefogója |
| `ConfigPanel.tsx` | Tömeg logaritmikus csúszka (10⁻¹⁰ – 10⁴⁰ kg), 3 preset, Norbi kapcsoló |
| `SpectrumChart.tsx` | Hawking-spektrum SVG polyline, valós idejű hőmérséklet felirat |
| `EntropyPlot.tsx` | Bekenstein-Hawking entrópia görbéje + Page-idő jelzővonal |
| `KruskalDiagram.tsx` | Kruskal–Szekeres téridő diagram, Norbi-módban bébiuniverzum jelzéssel |
| `InteriorView.tsx` | Animált belső állapot: horizont, sugárzási részecskék, bU mag |
| `ResultsPanel.tsx` | Számszerű eredmények táblázata, Norbi-magyarázat szöveg |

**Tauri parancsok:**
```typescript
invoke("run_simulation", { mass, norbi_mode, payload_json })
invoke("get_current_state")
invoke("toggle_norbi_mode", { enabled })
```

---

## CI/CD (GitHub Actions)

### `rust-tests.yml` — Minden push a `core/**`-ra

1. `cargo fmt -- --check` (formátum)
2. `cargo clippy -- -D warnings` (lint, warning = hiba)
3. `cargo test --verbose` (53 unit teszt)
4. `cargo tarpaulin` (kódlefedettség → Codecov)

### `python-tests.yml` — Minden push a `python/**`-ra

Matrix: Python 3.11 + 3.12

1. `maturin develop` (Rust mag fordítása Python modulnak)
2. `ruff check` (lint)
3. `mypy` (típusellenőrzés)
4. `pytest --cov` (17 teszt + lefedettség)

### `integration.yml` — Push main-re + nightly 02:00

1. Teljes build (maturin + pip)
2. Planck-tömeg szimuláció Standard módban → `ci_standard.json`
3. Planck-tömeg szimuláció Norbi módban → `ci_norbi.json`
4. `python scripts/validate_results.py` — monoton tömeg, nem-negatív entrópia, nincs NaN/Inf, schema v2.0
5. Artifact mentés (30 nap)

---

## Konstansok (`core/src/constants.rs`)

```rust
pub const G:          f64 = 6.674e-11;    // gravitációs állandó [m³·kg⁻¹·s⁻²]
pub const C:          f64 = 2.998e8;      // fénysebesség [m/s]
pub const HBAR:       f64 = 1.055e-34;    // redukált Planck-állandó [J·s]
pub const K_B:        f64 = 1.381e-23;    // Boltzmann-állandó [J/K]
pub const L_P:        f64 = 1.616e-35;    // Planck-hossz [m]
pub const RHO_PLANCK: f64 = 5.155e96;    // Planck-sűrűség [kg/m³]
pub const M_PLANCK:   f64 = 2.176e-8;    // Planck-tömeg [kg]
pub const T_PLANCK:   f64 = 5.391e-44;   // Planck-idő [s]
pub const M_SUN:      f64 = 1.989e30;    // Nap tömege [kg]
pub const WIEN_FREQ:  f64 = 5.879e10;    // Wien-állandó [Hz/K]
pub const SPECTRUM_BINS: usize = 1000;   // spektrum felbontás
```

---

## Checkpoint rendszer

A szimulációs állapotok **MessagePack** formátumban kerülnek mentésre (rmp-serde), atomikus fájlírással (temp fájl → rename), schema verzió: `"2.0"`.

```bash
# Checkpoint megtekintése
python scripts/checkpoint_inspect.py checkpoint.rmp

# CSV export
python scripts/export_csv.py simulation.json output.csv
```

---

## Python elemzési pipeline

```
SHA3-256 hash(payload)
    └─► InformationPacket
            ├─► qubit kódolás: θ = 2π·byte/255, α=cos(θ/2), β=sin(θ/2)
            ├─► Von Neumann entrópia: S = -Tr(ρ·log(ρ))
            └─► ReverseEngineer(spektrum, original_hash)
                    ├─► run_pca() → sklearn PCA (n_components=3)
                    ├─► run_fft() → numpy FFT, csúcs frekvencia
                    ├─► reconstruct_hash() → bit-szintű egyezés
                    └─► similarity_score() → [0, 1] skálán

Comparator.compare_spectra(standard, norbi)
    └─► SNR = RMS(delta) / noise_floor
        detectable = SNR > 3.0
```

---

## Irodalmi hivatkozások

| Azonosító | Hivatkozás |
|---|---|
| [SCH16] | Schwarzschild, K. (1916). Über das Gravitationsfeld eines Massenpunktes. |
| [HAW74] | Hawking, S.W. (1974). Black hole explosions? Nature, 248, 30-31. |
| [HAW75] | Hawking, S.W. (1975). Particle creation by black holes. Commun. Math. Phys. 43, 199-220. |
| [BEK73] | Bekenstein, J.D. (1973). Black holes and entropy. Phys. Rev. D, 7, 2333. |
| [PLA00] | Planck, M. (1900). Zur Theorie des Gesetzes der Energieverteilung im Normalspektrum. |
| [PAG93] | Page, D.N. (1993). Information in black hole radiation. Phys. Rev. Lett. 71, 3743. |
| [ASH06] | Ashtekar, A. & Pawlowski, T. (2006). Quantum nature of the Big Bang. Phys. Rev. Lett. 96, 141301. |

---

## Fejlesztői megjegyzések

- Az összes fizikai számítás `f64` pontossággal történik
- A `SimulationError` enum `thiserror`-al a hibakezelés biztonságos és exhaustive
- A Rust pánik-kezelés (`std::panic::catch_unwind`) megvédi a Python és Tauri réteget
- A Bevy ECS rendszer lehetővé teszi, hogy az entitások és komponensek lazán kapcsolódnak
- A Python venv a projekt gyökerében (`.venv/`) kerül létrehozásra — nem globális telepítés
- A Tauri `generate_context!()` makró a `build.rs`-ben lévő `tauri_build::build()` függvényt igényli
