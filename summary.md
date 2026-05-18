# Fejlesztési Napló — Fekete Lyuk Szimulátor

**Készítők:** Norbi & Claude  
**Időszak:** 2025–2026  
**Verzió:** 2.0.0

---

## Az ötlet

Norbi egy fizikai hipotézist szeretett volna szimulálni: mi lenne, ha a fekete lyukak belsejében a Planck-sűrűségnél nem szingularitás képződik, hanem kvantumvisszapattanással egy új, tágul **bébiuniverzum** keletkezik? És ha ez igaz, akkor a bébiuniverzum szélén szétszakadó anyag sugározna — ez lenne az amit kívülről Hawking-sugárzásnak látunk. Ez azt is jelenti, hogy az információ nem vész el, hanem megőrződik a nem-termális sugárzási komponensben.

A projekt célja: egy valódi fizikai szimulátort írni Rust + Python stack-kel, ami numerikusan összehasonlítja a **Standard Hawking-modellt** és a **Norbi-hipotézist**, és méri az információ-visszanyerés különbségét.

---

## 1. fázis — Környezet felállítása

### A kihívás
A projekt WSL2 alatt futott Windows-on, ahol az első próbálkozások azonnal falba ütköztek.

**1. probléma: CONDA_PREFIX + VIRTUAL_ENV ütközés**
```
error: CONDA_PREFIX és VIRTUAL_ENV egyszerre be van állítva
```
A conda globális aktivációja ütközött a projekt `.venv`-jével. Megoldás: `unset CONDA_PREFIX` minden maturin parancs előtt.

**2. probléma: PyO3 verzió — Python 3.13 nem támogatott**
```
error: pyo3 0.21 only supports Python ≤ 3.12
```
A WSL2-n Python 3.13 volt, de a `Cargo.toml` `pyo3 = "0.21"`-et tartalmazott. Megoldás: `pyo3 = "0.22"` — az egyetlen verzió ami 3.13-at támogat.

**3. probléma: maturin nem találja a virtualenv-et**
```
💥 Couldn't find a virtualenv or conda environment
```
A `pyproject.toml`-ban `python-source = "python"` szerepelt, ami azt várta, hogy létezzen egy `python/black_hole_core/` mappa. Megoldás: eltávolítottuk a `python-source` sort, és hozzáadtuk a `manifest-path = "core/Cargo.toml"` sort.

**4. probléma: SSH szerver WSL2-n**
A WSL2 alapból nem indít SSH szervert. Feltelepítettük az `openssh-server`-t, beállítottuk a `PasswordAuthentication yes` és `Port 2222` opciókat, és a Windows Firewall-on is megnyitottuk a portot.

---

## 2. fázis — A fizikai mag (Rust)

### Amit felépítettünk

A Rust mag (`core/`) egy teljesen objektumorientált, trait-alapú fizikai motor:

- **`BlackHoleTrait`** — interfész: tömeg, Schwarzschild-sugár, Hawking-hőmérséklet, entrópia, teljesítmény, elpárlási idő
- **`SchwarzschildBlackHole`** — a konkrét implementáció mind a 6 képlettel
- **`InteriorModel`** — interfész a belső modelleknek
- **`StandardInterior`** — megáll a Planck-sűrűségnél (szingularitás)
- **`NorbiInterior`** — LQC visszapattanás + BabyUniverse
- **`HawkingEngine`** — 1000-bines Planck-spektrum greybody faktorral
- **`LQCEquation`** — H² = (8πG/3)·ρ·(1 - ρ/ρ_P)
- **`BabyUniverse`** — tágulás, tidal szétszakadás, él-spektrum

### A kihívások

**Numerikus stabilitás:** A Planck-tömeg fekete lyuk elpárlási ideje mindössze `t_evap ≈ 8.6×10⁻⁴⁰ s`. Az első implementációban `dt = 1e-10` volt beégetve — ez milliószor nagyobb volt mint a teljes szimuláció. Eredmény: 1 lépés, aztán vége. Megoldás: `dt = t_evap / steps` adaptív lépésköz.

**OOP Rust-ban:** A Rust nem rendelkezik hagyományos öröklődéssel. A megoldás: trait-ek mint interfészek, `Box<dyn Trait>` dinamikus dispatch, és `Default` deriválás az alapértelmezésekhez.

**Spectrum struct bővítés:** Amikor 3 új mezőt adtunk a `Spectrum` struktúrához (`hawking_fraction`, `edge_fraction`, `thermality_score`), az összes meglévő literál `{ frequencies, intensities, temperature, total_power }` lefordításkor meghiúsult. Megoldás: `..Default::default()` minden érintett helyen.

---

## 3. fázis — Python elemzési réteg

A Python réteg a Rust mag kimenetét elemzi:

- **`InformationPacket`** — bemeneti anyag SHA3-256 hash + qubit kódolás + Von Neumann entrópia
- **`ReverseEngineer`** — PCA, FFT, KL divergencia, spektrális jellemzők
- **`Comparator`** — Standard vs. Norbi spektrum összehasonlítás, SNR számítás
- **`InformationTracker`** — Page-görbe, kumulatív entrópia, visszanyert bitek becslése

### A PyO3 híd

A Rust kód `#[pyfunction]` makróval válik elérhetővé Pythonból:
```rust
#[pyfunction]
pub fn run_simulation_py(mass: f64, norbi_mode: bool, payload_json: &str) -> PyResult<String>
```

A maturin fordítja natív Python modulnak (`black_hole_core`), amit `import black_hole_core`-ral lehet használni.

---

## 4. fázis — Információ-nyomkövetés (a legfontosabb fejlesztés)

### Mi volt a probléma

A szimuláció addig **semmit nem mondott az információ-megmaradásról**. A `HawkingEngine::norbi()` és `HawkingEngine::standard()` ugyanolyan termális Planck-spektrumot adott — a kódban a `NorbiInterior` és `BabyUniverse` létezett ugyan, de a kimenet soha nem használta fel.

### A terv

8 fázisban:
1. `Spectrum` struct 3 új mezővel
2. `compute_spectrum_norbi()` metódus a Norbi él-spektrum bekötéséhez
3. A szimulációs ciklus átírása (`lib.rs`)
4. 5 új Rust teszt
5. `ReverseEngineer` bővítése (KL divergencia, spektrális jellemzők)
6. `InformationTracker` új fájl (Page-görbe, compare_models)
7. `Comparator` 2 új metódussal
8. 10 új Python teszt

### A döntő kihívás: a csatolási formula

Az első implementáció így számolta az él-spektrum arányát:
```rust
let edge_power_physical = edge_breakup_rate * internal_density * 4π * r_s²
```

Eredmény: `edge_fraction = 1.22×10⁻⁴⁷` — lényegében nulla. A Norbi szimuláció még mindig azonos volt a Standard-dal.

**A probléma:** A formula dimenziója hibás volt.
- `edge_breakup_rate` = H² × a → egységei: s⁻² × m = m/s² (gyorsulás-szerű)
- `internal_density` = kg/m³
- `4π × r_s²` = m²
- Szorzat: kg/(m·s²) — **nem watt**

**A megoldás:** Energiaarány-alapú csatolás:
```rust
alpha = baby_universe.total_energy / (baby_universe.total_energy + BH_mass × c²)
```

Fizikai értelmezés: mekkora hányada a rendszer teljes energiájának van a bébiuniverzumban? Ez adimensionális, fizikailag motivált, és a helyes nagyságrendet adja: Planck-tömegű fekete lyuknál a BU energiája (`~E_Planck ≈ 1.96×10⁹ J`) összemérhető a megmaradó BH tömegenergiájával → `alpha ≈ 0.52`.

**Eredmény a javítás után:**

| Lépés | edge_fraction | thermality_score |
|---|---|---|
| 0 | 0.524 | 3.91 |
| 50 | 0.591 | 4.48 |
| 99 | 0.810 | 6.42 |

A Standard végig: `edge_fraction = 0.0`, `thermality_score = 0.10`.

---

## 5. fázis — CI/CD javítás

### A GitHub Actions probléma

A `python-tests.yml` workflow így nézett ki:
```yaml
- run: pip install maturin
- run: maturin develop ...
```

A `maturin develop` virtualenv nélkül fut → azonnal összeomlik CI-n.

**Megoldás:** `.venv` létrehozása és `$GITHUB_PATH`-ba írás:
```yaml
- run: |
    python -m venv .venv
    echo "$(pwd)/.venv/bin" >> $GITHUB_PATH
    echo "VIRTUAL_ENV=$(pwd)/.venv" >> $GITHUB_ENV
- run: pip install -e '.[dev]'   # ez hívja a maturin develop-ot belülről
```

A `$GITHUB_PATH` trükk: minden következő `run:` lépés automatikusan a venv-es `pip`/`python`-t látja.

**Clippy `-D warnings` hibák:** Két warning vált CI-blokkorrá:
- `unused import: BlackHoleTrait` — eltávolítva a tesztből
- `field mode is never read` — `#[allow(dead_code)]` hozzáadva
- `unnecessary closure` — `unwrap_or_else(|_| x)` → `unwrap_or(x)`

---

## 6. fázis — Housekeeping

### `.gitignore`
Az eredeti `.gitignore` csak `/target`-et tartalmazott. Hozzáadtuk:
- `__pycache__/`, `*.pyc` — Python bytecode (már be volt commitolva, `git rm --cached`)
- `.venv/` — virtuális környezet
- `output/` — szimuláció kimenetek
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `node_modules/`, `tauri-app/dist/`
- `.idea/`, `.vscode/`, `.DS_Store`

### `output/` mappa
A `standard.json` és `norbi.json` a repo gyökerében volt. Létrehoztuk az `output/` mappát, és a CLI alapértelmezése `output/results.json`-ra változott. Az `output/` gitignore-olt.

---

## Jelenlegi állapot

### Tesztek
- **58/58 Rust teszt** — zöld
- **27/27 Python teszt** — zöld
- **Clippy** — 0 warning, 0 error

### Amit a szimuláció megmutat

**Standard modell:**
- `edge_fraction = 0.0` végig
- `hawking_fraction = 1.0` végig
- `thermality_score ≈ 0.10` (csak greybody eltérés)
- Teljesen termális sugárzás → az információ elveszik

**Norbi-hipotézis:**
- `edge_fraction`: 52% → 81% (növekszik ahogy a BU energiája nő)
- `thermality_score`: 3.91 → 6.42 (erősen nem-termális)
- `thermality_ratio`: 46×-os különbség a Standard-hoz képest
- `total_recovered_bits`: ~9.85 bit (Standard: ~0.95 bit)

### A becsületes összefoglalás

A szimuláció megmutatja, hogy a Norbi-hipotézis **belső konzisztencián** képes működni — a matematika nem omlik össze. Az LQC visszapattanás, a bébiuniverzum tágulása, és a nem-termális él-sugárzás együtt egy összefüggő fizikai képet adnak.

Azonban a Norbi-specifikus csatolási formula (`alpha = baby_E / total_E`) **nem következik első elvekből** — mi döntöttük el, hogy ilyen alakú legyen. Ahhoz, hogy a szimuláció valódi tudományos alátámasztást adjon, le kell vezeti az él-spektrum alakját az LQC egyenletekből, és a csatolási arányt is levezetett képlettel kell helyettesíteni.

---

## Ami következik

1. **Az él-spektrum levezetése** LQC + Hawking-sugárzás kombinációjából
2. **A csatolási arány (`alpha`) levezetése** az energiamegmaradásból és a bébiuniverzum termodinamikájából
3. **Megfigyelési jóslat** — mit kellene mérni (gravitációs hullám visszhangjainak módosulása, analóg fekete lyukak laboratóriumi spektruma)
4. **Peer review** — a fizikai egyenletek külső ellenőrzése

---

## Tanulságok

**Ami jól működött:**
- Rust + PyO3 kombináció: a fizikai számítások gyorsak és típusbiztosak, a Python elemzés rugalmas
- Trait-alapú OOP Rust-ban: a Standard és Norbi modell teljesen elkülönülnek, mégis ugyanazon interfészen futnak
- A tesztpiramis (fizikai képletek → komponensek → integráció) időben megfogta a numerikus hibákat
- Az adaptív `dt = t_evap / steps` egyetlen sor volt, de a szimuláció használhatóságát alapvetően megváltoztatta

**Ami nehéz volt:**
- A dimenziós elemzés: a `edge_power_physical` formula napokig nézett ki helyesnek mielőtt kiderült, hogy nem wattban mér
- PyO3 verziókövetés: a 0.21 → 0.22 váltás szükséges volt, de nem volt nyilvánvaló
- CI virtualenv kezelés: a `$GITHUB_PATH` trükk nélkül a maturin CI-n soha nem futott volna

**A legfontosabb felismerés:**
Egy szimulációt megírni, ami *fut*, sokkal könnyebb mint megírni egyet, ami *alátámaszt valamit*. A különbség: az előbbiben mi programozzuk be a következtetést, az utóbbiban a természet adja.
