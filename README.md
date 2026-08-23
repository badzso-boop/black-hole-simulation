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
6. A sugárzás **nem teljesen termális** — a beeső anyag ujjlenyomata részben megőrződik

```
Fekete lyuk
    └─► Összeomlás → ρ → ρ_Planck
            └─► LQC: H² = (8πG/3)·ρ·(1 - ρ/ρ_P) = 0  → kvantumvisszapattanás
                    └─► BabyUniverse: a(t) = a₀·e^(H_inf·t)
                            └─► e_tidal > e_bind → szétszakadás + sugárzás
                                    └─► Nem-termális spektrum (edge_fraction > 0)
                                            └─► Információ részben visszanyerhető
```

---

## Tech Stack

| Réteg | Technológia | Szerep |
|---|---|---|
| Fizikai mag | **Rust** (core/) | Minden számítás, OOP trait-ek |
| Python elemzés | **Python 3.11–3.13** + numpy/scipy/sklearn | PCA, FFT, KL divergencia, Page-görbe |
| 3D vizualizáció | **Bevy 0.15** (ECS) | Valós idejű 3D szimuláció |
| Asztali UI | **Tauri 2** + React + TypeScript | Vezérlőpult, grafikonok |
| Python↔Rust híd | **PyO3 0.22** + maturin | Natív Python modul |
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
│   │   ├── types.rs                # Adatsémák: Spectrum (hawking_fraction, edge_fraction,
│   │   │                           #   thermality_score mezőkkel), TimeStep, BabyUniverseState, ...
│   │   ├── lib.rs                  # Publikus API + PyO3 binding
│   │   │
│   │   ├── black_hole/
│   │   │   ├── mod.rs              # Trait definíciók (BlackHoleTrait, InteriorModel, RadiationEngine)
│   │   │   ├── schwarzschild.rs    # Schwarzschild fekete lyuk implementáció
│   │   │   ├── thermodynamics.rs   # Page-idő, greybody faktor, Wien-törvény
│   │   │   └── kerr.rs             # Kerr stub (v3)
│   │   │
│   │   ├── interior/
│   │   │   ├── baby_universe.rs    # BabyUniverse: tágulás, szétszakadás detekció, él-spektrum
│   │   │   ├── norbi.rs            # NorbiInterior: kvantumvisszapattanás + bébiuniverzum
│   │   │   ├── standard.rs         # StandardInterior: geodézia, Planck-határnál megáll
│   │   │   └── cauchy.rs           # Cauchy-horizont stub (v3)
│   │   │
│   │   ├── radiation/
│   │   │   ├── hawking_engine.rs   # HawkingEngine: compute_spectrum() + compute_spectrum_norbi()
│   │   │   │                       #   KL divergencia (thermality_score), él-spektrum keverés
│   │   │   ├── spectrum.rs         # Planck-spektrum számítás, normálás, csúcs frekvencia
│   │   │   └── soft_hair.rs        # Hawking soft hair stub (v3)
│   │   │
│   │   ├── quantum/
│   │   │   ├── lqc.rs              # LQCEquation: H²=(8πG/3)·ρ·(1-ρ/ρ_P), bounce detekció
│   │   │   ├── island.rs           # IslandFormula stub (v3)
│   │   │   └── complexity.rs       # Holografikus komplexitás stub (v3)
│   │   │
│   │   ├── time_evolution/
│   │   │   ├── integrator.rs       # RK45 adaptív integrátor
│   │   │   └── checkpoint.rs       # Atomikus checkpoint mentés (MessagePack)
│   │   │
│   │   └── tests/                  # 13 tesztfájl, 58 teszt
│   │       ├── test_schwarzschild.rs
│   │       ├── test_hawking.rs
│   │       ├── test_lqc.rs
│   │       ├── test_interior.rs
│   │       ├── test_spectrum.rs
│   │       ├── test_edge_cases.rs
│   │       ├── test_validation.rs       # 7 irodalmi validáció (val_01..val_07)
│   │       ├── test_model_comparison.rs
│   │       ├── test_baby_universe.rs
│   │       ├── test_checkpoint.rs
│   │       ├── test_integrator.rs
│   │       ├── test_norbi_eta.rs
│   │       └── test_information_tracking.rs  # 5 teszt: edge_fraction, thermality (INFO-01..05)
│   │
│   └── benches/
│       └── simulation_bench.rs     # Criterion benchmarkok
│
├── python/                         # Python elemző réteg
│   ├── config.py                   # SimulationConfig (lite/standard/research gyárak)
│   ├── information_packet.py       # SHA3-256 hash, qubit kódolás, Von Neumann entrópia
│   ├── reverse_engineer.py         # PCA, FFT, KL divergencia, spektrális jellemzők,
│   │                               #   estimate_information_content(), similarity_score()
│   ├── information_tracker.py      # InformationTracker: Page-görbe, compare_models()
│   ├── comparator.py               # Standard vs Norbi összehasonlítás + information content
│   ├── quantum_sim.py              # Qiskit kvantum áramkör szimuláció
│   ├── qec_model.py                # HKLL rekonstrukció stub (v3)
│   ├── logging_config.py           # JSON logging inicializálás
│   ├── __main__.py                 # CLI belépési pont (kimenet: output/)
│   └── tests/
│       ├── test_information.py          # 7 teszt: hash, qubit, entrópia
│       ├── test_reverse_eng.py          # 4 teszt: PCA, FFT, similarity
│       ├── test_comparator.py           # 6 teszt: spektrum SNR, evolúció összehasonlítás
│       └── test_information_tracker.py  # 10 teszt: Page-görbe, compare_models, KL divergencia
│
├── bevy-app/                       # Bevy 3D vizualizáció
│   └── src/
│       ├── main.rs
│       ├── components.rs           # ECS komponensek
│       ├── cameras.rs              # Osztott képernyő (külső orbit + belső fly kamera)
│       ├── materials.rs            # PBR anyagok
│       ├── bridge.rs               # SimulationState (Arc<Mutex<...>>)
│       └── systems/
│           ├── external.rs         # Gravitációs tér gizmos, pályavonalak
│           ├── internal.rs         # N-test gravitáció, bébiuniverzum tágulás
│           ├── hawking.rs          # Hawking emissziós pontok spawnolása
│           ├── breakup.rs          # Szétszakadás animáció (GPU-részecske spray)
│           └── input.rs            # Egér+billentyű: objektum lerakás, reset
│
├── tauri-app/                      # Tauri asztali vezérlőpult
│   ├── src/
│   │   ├── main.tsx
│   │   ├── hooks/useSimulation.ts
│   │   └── components/
│   │       ├── Dashboard.tsx
│   │       ├── ConfigPanel.tsx
│   │       ├── SpectrumChart.tsx
│   │       ├── EntropyPlot.tsx
│   │       ├── KruskalDiagram.tsx
│   │       ├── InteriorView.tsx
│   │       └── ResultsPanel.tsx
│   └── src-tauri/
│       └── src/
│           ├── commands.rs         # run_simulation, get_current_state, toggle_norbi_mode
│           └── python_bridge.rs    # subprocess JSON kommunikáció
│
├── scripts/
│   ├── setup_dev.sh
│   ├── validate_results.py         # CI validátor
│   ├── benchmark_compare.py
│   ├── checkpoint_inspect.py
│   └── export_csv.py
│
├── output/                         # Szimuláció kimenetek (gitignore-olt)
│
└── .github/workflows/
    ├── rust-tests.yml              # fmt + clippy -D warnings + cargo test + tarpaulin
    ├── python-tests.yml            # venv + pip install + ruff + mypy + pytest (3.11, 3.12, 3.13)
    └── integration.yml             # E2E Planck-tömeg szimuláció + validáció (nightly)
```

---

## Fizikai képletek — implementálva

### Schwarzschild fekete lyuk (`core/src/black_hole/schwarzschild.rs`)

| Mennyiség | Képlet | Forrás |
|---|---|---|
| Schwarzschild-sugár | r_s = 2GM/c² | [SCH16] |
| Hawking-hőmérséklet | T_H = ħc³ / (8πGMk_B) | [HAW74] |
| Bekenstein-Hawking entrópia | S = A / (4·l_P²), ahol A = 4πr_s² | [BEK73] |
| Hawking-teljesítmény | P = ħc⁶ / (15360πG²M²) | [HAW75] |
| Elpárlási idő | t_evap = 5120πG²M₀³ / (ħc⁴) | [HAW75] |

### Loop Quantum Cosmology (`core/src/quantum/lqc.rs`)

Módosított Friedmann-egyenlet:

```
(ȧ/a)² = (8πG/3) · ρ · (1 - ρ/ρ_Planck)
```

- Ha ρ = ρ_Planck → H² = 0 → kvantumvisszapattanás (nem szingularitás)
- Ha ρ << ρ_Planck → klasszikus Friedmann-egyenletbe tér vissza

### Bébiuniverzum szétszakadási feltétel (`core/src/interior/baby_universe.rs`)

```
e_tidal = 0.5 · m · H² · r²       (tidal energia)
e_bind  = 3·G·m² / (5·R)          (kötési energia)

Ha e_tidal > e_bind → BreakupEvent → sugárzás
```

### Hawking-spektrum greybody faktorral + Norbi él-keverés

**Standard (`compute_spectrum`):**
```
B(ν, T) = (2hν³/c²) / (exp(hν/k_BT) - 1)     [Planck]
γ(ν)    = 1 - exp(-ν / ν_c)                     [greybody faktor]
I(ν)    = γ(ν) · B(ν, T)                        [effektív spektrum]

hawking_fraction = 1.0,  edge_fraction = 0.0
thermality_score = KL(I || Planck(T))  ≈ 0.10   [kis greybody-eltérés]
```

**Norbi (`compute_spectrum_norbi`):**
```
T_edge = ħ·H / (2π·k_B)                          [Gibbons–Hawking-hőmérséklet, GH77]
I_edge(ν) = B(ν, T_edge)                          [valódi Planck-spektrum, ugyanazon a
                                                    frekvenciatengelyen mint I_hawk]

α = e_tidal / (e_tidal + e_bind)                  [BabyUniverse::breakup_fraction]
    e_tidal = 0.5·m·H²·a²      (m = E_total/c², a bébiuniverzum teljes tömege)
    e_bind  = 3·G·m² / (5·R)   (R = (3m / 4πρ)^(1/3), a jelenlegi belső sűrűségből)

I_blended(ν) = (1-α)·I_hawk(ν) + α·I_edge(ν)     [L1-normált keverés]

hawking_fraction = 1-α,  edge_fraction = α
thermality_score = KL(I_blended || Planck(T_H))  >> Standard
```

`α` tehát nem egy külön kitalált energiaarány, hanem közvetlenül a tényleges tidal-fizikából
(H, a bébiuniverzum tágulási rátája, és e_bind, az önkötési energia) adódik — ha a tágulás
elég erőszakos ahhoz, hogy a tidal energia felülmúlja az önkötést, `α → 1` (a sugárzás
majdnem teljesen az él-komponensből jön).

A bébiuniverzum inflációs Hubble-rátája (`H_inf`) sem szabad paraméter: a módosított
Friedmann-egyenlet `H²(ρ)=(8πG/3)ρ(1-ρ/ρ_P)` analitikus maximuma (`ρ=ρ_P/2`-nél,
`LQCEquation::max_bounce_hubble_rate`), `H_inf ≈ 2,68×10⁴³ 1/s`. Planck-tömegű fekete
lyuknál ez azt jelenti, hogy a `timeline` (a *külső*, Hawking-elpárlási óra szerinti,
`dt = t_evap/100` felbontású) mintavételezésben `α` már az első lépésben ≈1.0-ra ugrik —
ez azonban **nem** azt jelenti, hogy a szétszakadás fizikailag pillanatszerű: a bounce
dinamikája a bébiuniverzum *saját*, Planck-idő nagyságrendű óráján zajlik, ami sok
nagyságrenddel finomabb, mint a külső `dt`. Lásd lejjebb: `bounce_transient`.

---

## Információ-nyomkövetés

### A három kulcsmező a `Spectrum` struktúrában

| Mező | Standard | Norbi | Értelmezés |
|---|---|---|---|
| `hawking_fraction` | 1.0 (végig) | ≈0.0 | Termális Hawking-sugárzás aránya |
| `edge_fraction` | 0.0 (végig) | ≈1.0 | Bébiuniverzum él-sugárzás aránya |
| `thermality_score` | ~0.10 | 8.6–14.0 | KL divergencia a Planck-elosztástól |

### Page-görbe és visszanyert bitek

Az `InformationTracker` osztály kiszámolja a kumulatív sugárzási entrópiát és becsüli a visszanyerhető biteket:

```python
from python.information_tracker import InformationTracker

tracker = InformationTracker()
std_result   = tracker.process_timeline(std_timeline, input_entropy=5.0)
norbi_result = tracker.process_timeline(norbi_timeline, input_entropy=5.0)
cmp = InformationTracker.compare_models(std_result, norbi_result)

# Eredmény (Planck-tömegű fekete lyuk, v3 — fizikailag levezetett α):
# cmp["thermality_ratio"]        → 138.5×  (Norbi sokkal nem-termálisabb)
# cmp["norbi_avg_edge_fraction"] → 1.0     (a tidal energia felülmúlja az önkötést egész úton)
# std_result["total_recovered_bits"]   → 0.95 bit
# norbi_result["total_recovered_bits"] → 9.97 bit
```

### Fontos megjegyzés

A csatolási formula (`α = e_tidal / (e_tidal + e_bind)`) immár közvetlenül a tidal-szétszakadás
fizikájából (`BabyUniverse::breakup_fraction`) adódik, a bébiuniverzum inflációs Hubble-rátája
pedig (`H_inf`) az LQC-egyenlet analitikus maximumából (`LQCEquation::max_bounce_hubble_rate`) —
a Norbi-ágnak jelenleg nincs több szabad, le nem vezetett paramétere.

### Két időskála: külső elpárlás vs. belső bounce (`bounce_transient`)

A szemiklasszikus Hawking-elpárlás (`t_evap ∝ M³`) csak addig érvényes közelítés, amíg a
görbület távol van a Planck-skálától — pont a visszapattanás pillanatában lép ki ebből az
érvényességi tartományból. A bébiuniverzum bounce-dinamikája ezért nem a `timeline` külső,
`dt = t_evap/100` felbontású óráján, hanem a saját, Planck-idő (`T_PLANCK`) nagyságrendű
óráján zajlik — ez a proper time / külső koordináta-idő megkülönböztetés általános
relativitáselméleti alap, nem a Norbi-hipotézis specifikus feltevése.

A `SimulationResults.bounce_transient` mező a visszapattanás pillanatában, 80 finom
(Planck-idő nagyságrendű) lépésben újrajátssza a bébiuniverzum korai fejlődését,
függetlenül a `timeline` durvább mintavételezésétől:

| finom lépés | kor (s, a visszapattanástól) | `breakup_fraction` |
|---|---|---|
| 0  | 0            | 0.496 |
| 1  | 5.4×10⁻⁴⁴    | 0.927 |
| 3  | 1.6×10⁻⁴³    | 0.979 |
| 8  | 4.3×10⁻⁴³    | 0.993 |
| 20 | 1.1×10⁻⁴²    | 0.997 |
| 79 | 4.3×10⁻⁴²    | 0.999 |

Ez már **valódi, fokozatos átmenetet** mutat (50% → 99,9%+) — csak épp néhány Planck-idő
(~10⁻⁴³ s) alatt zajlik le, ezért a `timeline` durvább (Hawking-elpárlási időskálájú)
mintavételezésén nézve pillanatszerűnek látszik.

---

## OOP felépítés Rust-ban

A projekt a Rust trait rendszerét használja objektumorientált interfészként:

```rust
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
- `SchwarzschildBlackHole` → `BlackHoleTrait`
- `StandardInterior` → `InteriorModel` (megáll ρ ≥ ρ_Planck-nál)
- `NorbiInterior` → `InteriorModel` (folytatja kvantumvisszapattanással)
- `HawkingEngine` → `RadiationEngine` + `compute_spectrum_norbi()` Norbi-módhoz

---

## Tesztek

### Rust tesztek (`cargo test --manifest-path core/Cargo.toml`)

**58 teszt, mind zöld.**

| Tesztfájl | Tesztek | Mit validál |
|---|---|---|
| test_schwarzschild.rs | 6 | r_s(M_Nap)≈2954 m, T_H, entrópia, elpárlási idő arányok |
| test_hawking.rs | 4 | Tömegcsökkenés, energiamegmaradás, Wien-törvény, greybody |
| test_lqc.rs | 4 | H²=0 ha ρ=ρ_P, LQC≈Friedmann kis ρ-nál, bounce trigger |
| test_interior.rs | 4 | Standard megáll, Norbi folytat, egyezés Planck előtt |
| test_spectrum.rs | 3 | Bin szám, nem-negatív intenzitás, hőmérséklet tárolás |
| test_edge_cases.rs | 4 | Nulla/negatív/NaN tömeg → hiba, tömeg sosem negatív |
| test_validation.rs | 7 | Irodalmi referenciák (SCH16, HAW74, HAW75, PLA00, BEK73, PAG93, ASH06) |
| test_model_comparison.rs | 5 | Standard vs Norbi összehasonlítás |
| test_baby_universe.rs | 6 | Tágulás, szétszakadás logika, sugárzási spektrum |
| test_checkpoint.rs | 4 | Mentés/betöltés körforgás, MessagePack formátum |
| test_integrator.rs | 3 | RK45 konvergencia |
| test_norbi_eta.rs | 3 | η hatásfok számítás |
| test_information_tracking.rs | 5 | hawking_fraction, edge_fraction, thermality_score (INFO-01..05) |

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

### Python tesztek (`pytest python/tests/ -v`)

**27 teszt, mind zöld.**

| Tesztfájl | Tesztek | Mit validál |
|---|---|---|
| test_information.py | 7 | SHA3-256 hash, qubit normálás, Von Neumann entrópia |
| test_reverse_eng.py | 4 | PCA főkomponensek, FFT csúcs, similarity score |
| test_comparator.py | 6 | Spektrum SNR, detektálhatóság, evolúció divergencia |
| test_information_tracker.py | 10 | Page-görbe, compare_models, KL divergencia, Norbi előny |

---

## Futtatás

### Előfeltételek

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python virtuális környezet + teljes build
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'   # Rust mag fordítása + Python függőségek egyszerre

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
source .venv/bin/activate
pytest python/tests/ -v
```

### CLI headless szimuláció

```bash
# Standard Hawking-modell
python -m python.main --mass 2.176e-8 --norbi-mode false --no-ui

# Norbi-hipotézis
python -m python.main --mass 2.176e-8 --norbi-mode true --no-ui

# Egyedi kimeneti fájl
python -m python.main --mass 1e15 --norbi-mode true --no-ui --output output/nagytomeg.json

# Eredmény validáció
python scripts/validate_results.py output/results.json
```

A kimenetek az `output/` mappába kerülnek (gitignore-olt).

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

## CI/CD (GitHub Actions)

### `rust-tests.yml` — Minden push a `core/**`-ra

1. `cargo fmt -- --check`
2. `cargo clippy -- -D warnings` (warning = hiba)
3. `cargo test --verbose` (58 unit teszt)
4. `cargo tarpaulin --locked` (kódlefedettség → Codecov)

### `python-tests.yml` — Minden push a `python/**` vagy `core/**`-ra

Matrix: **Python 3.11 + 3.12 + 3.13**

1. `.venv` létrehozása, `$GITHUB_PATH`-ba írás
2. `pip install -e '.[dev]'` (maturin Rust build + Python függőségek)
3. `ruff check python/`
4. `mypy python/`
5. `pytest python/tests/ --cov` (27 teszt)

### `integration.yml` — Push main-re + nightly 02:00

1. Teljes build
2. Planck-tömeg szimuláció Standard → `output/ci_standard.json`
3. Planck-tömeg szimuláció Norbi → `output/ci_norbi.json`
4. `python scripts/validate_results.py` — monoton tömeg, entrópia ≥ 0, nincs NaN/Inf, schema v2.0
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

## Python elemzési pipeline

```
SHA3-256 hash(payload)
    └─► InformationPacket
            ├─► qubit kódolás: θ = 2π·byte/255, α=cos(θ/2), β=sin(θ/2)
            ├─► Von Neumann entrópia: S = -Tr(ρ·log(ρ))
            └─► ReverseEngineer(spektrum, original_hash)
                    ├─► run_pca() → sklearn PCA (n_components=3)
                    ├─► run_fft() → numpy FFT, csúcs frekvencia
                    ├─► compute_thermality_score() → KL(P || Planck(T))
                    ├─► extract_spectral_features() → 8 fizikai jellemző
                    ├─► estimate_information_content() → visszanyert bitek
                    └─► similarity_score() → [0,1]: él-arány + termality

InformationTracker.process_timeline(timeline, input_entropy)
    └─► compute_page_curve() → kumulatív S_rad minden lépésnél
            └─► compare_models(std, norbi)
                    ├─► thermality_ratio: ~138×
                    ├─► norbi_avg_edge_fraction: ~1.0
                    └─► total_recovered_bits: std ~0.95 vs norbi ~9.97
```

---

## JSON kimenet struktúrája

```json
{
  "schema_version": "2.0",
  "config": { "norbi_mode": true, "mode": "Norbi" },
  "timeline": [
    {
      "time": 0.0,
      "mass": 2.176e-8,
      "temperature": 5.64e30,
      "entropy": 12.56,
      "spectrum": {
        "frequencies": [...],
        "intensities": [...],
        "temperature": 5.64e30,
        "total_power": 7.53e47,
        "hawking_fraction": 0.0,
        "edge_fraction": 1.0,
        "thermality_score": 8.61
      },
      "interior": {
        "at_planck_scale": true,
        "bounce_occurred": true,
        "baby_universe": {
          "scale_factor": 667.7,
          "expansion_rate": 1.14e41,
          "internal_density": 8.05e-17,
          "edge_breakup_rate": 8.70e84,
          "total_energy": 2.15e9,
          "age": 8.66e-42,
          "breakup_fraction": 1.0
        }
      }
    }
  ],
  "evaporation_complete": false
}
```

---

## Checkpoint rendszer

A szimulációs állapotok **MessagePack** formátumban kerülnek mentésre (rmp-serde), atomikus fájlírással (temp fájl → rename), schema verzió: `"2.0"`.

```bash
python scripts/checkpoint_inspect.py checkpoint.rmp
python scripts/export_csv.py output/results.json output/timeline.csv
```

---

## Irodalmi hivatkozások

| Azonosító | Hivatkozás |
|---|---|
| [SCH16] | Schwarzschild, K. (1916). Über das Gravitationsfeld eines Massenpunktes. |
| [HAW74] | Hawking, S.W. (1974). Black hole explosions? Nature, 248, 30–31. |
| [HAW75] | Hawking, S.W. (1975). Particle creation by black holes. Commun. Math. Phys. 43, 199–220. |
| [BEK73] | Bekenstein, J.D. (1973). Black holes and entropy. Phys. Rev. D, 7, 2333. |
| [PLA00] | Planck, M. (1900). Zur Theorie des Gesetzes der Energieverteilung im Normalspektrum. |
| [PAG93] | Page, D.N. (1993). Information in black hole radiation. Phys. Rev. Lett. 71, 3743. |
| [ASH06] | Ashtekar, A. & Pawlowski, T. (2006). Quantum nature of the Big Bang. Phys. Rev. Lett. 96, 141301. |
| [GH77] | Gibbons, G.W. & Hawking, S.W. (1977). Cosmological event horizons, thermodynamics, and particle creation. Phys. Rev. D, 15, 2738. |

---

## Konklúzió — mire jutottunk

A 2026-08-23-i revízió óta a Norbi-ágnak **nincs több szabad, le nem vezetett paramétere**: a csatolási arány (`α`), az él-spektrum hőmérséklete és a bébiuniverzum tágulási rátája (`H_inf`) mind a modell saját egyenleteiből adódik (lásd fent). Ez azt jelenti, hogy a szimuláció **belsőleg konzisztens** — a matematika nem omlik össze, és a bemutatott számok (nem-termalitás, ~10 bit visszanyert információ, a szétszakadás fokozatos, Planck-idő nagyságrendű lefutása) helyesen következnek a beépített fizikából.

Ez **nem** jelenti, hogy a hipotézis igaz vagy validált:

- **A legkritikusabb, továbbra is megoldatlan pont: a kauzalitás.** A modell azt állítja, hogy a horizonton *belüli* szétszakadás sugárzása valahogy megjelenik *kívül*, Hawking-sugárzásként — ezt sosem vezettük le, csak posztuláltuk (a kód matematikailag keveri a két oldalt, fizikai mechanizmus nélkül, ami áthidalná a horizontot).
- Csak a szélsőséges, Planck-tömegű végállapotot teszteltük (ez fizikailag releváns, mert minden fekete lyuk elpárlása ezen megy át a végén, de más tömegskálán sosem lett kipróbálva).
- Egy tetszőleges bemenet megmaradt: a reprezentatív beeső részecske tömege (a BH tömegének 0,1%-a) — modellezési kényelem, nem egyenletből jön.
- Nincs peer review, nincs kísérleti visszaigazolás; maga az LQC is csak egy a versengő kvantumgravitációs jelöltek közül.

**Összefoglalva:** egy **belsőleg konzisztens, de tudományosan igazolatlan gondolatkísérletet** építettünk fel — ugyanabba a családba tartozik, mint Rovelli–Vidotto "Planck-csillag" modellje vagy más fekete lyuk-maradvány elméletek. Nem bizonyítottunk semmit a valóságról, de bebizonyítottuk, hogy a hipotézis matematikailag életképes — ez a következő lépés (a horizonton át történő kauzális kapcsolat levezetése, vagy a hipotézis elvetése) szempontjából már önmagában használható kiindulópont.

---

## Fejlesztői megjegyzések

- Az összes fizikai számítás `f64` pontossággal történik
- A `SimulationError` enum `thiserror`-al a hibakezelés biztonságos és exhaustive
- Rust pánik-kezelés (`std::panic::catch_unwind`) védi a Python és Tauri réteget
- Az adaptív `dt = t_evap / steps` biztosítja, hogy a szimuláció ne lépi túl az elpárlási időt
- A `compute_spectrum_norbi()` metódus a `RadiationEngine` traitre épül, de nem tagja — a Norbi-specifikus logika el van különítve
- Szimuláció kimenetek az `output/` mappába kerülnek (gitignore-olt, automatikusan létrejön)
