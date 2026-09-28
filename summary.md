# Fejlesztési Napló — Fekete Lyuk Szimulátor

**Készítők:** Norbi & Claude  
**Időszak:** 2025–2026  
**Verzió:** 3.0.0

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

**Norbi-hipotézis (lásd 7-8. fázis — fizikailag levezetett `alpha` és `H_inf`):**
- `edge_fraction` a `timeline`-on (külső, Hawking-elpárlási órán mintavételezve): ≈1.0 gyakorlatilag az első lépéstől
- `bounce_transient`-en (saját, Planck-idő nagyságrendű órán mintavételezve): fokozatos 0,496→0,999+ átmenet ~80 Planck-idő alatt
- `thermality_score`: 8.61 → 13.97 (erősen nem-termális)
- `thermality_ratio`: ~138×-os különbség a Standard-hoz képest
- `total_recovered_bits`: ~9.97 bit (Standard: ~0.95 bit)

### A becsületes összefoglalás

A szimuláció megmutatja, hogy a Norbi-hipotézis **belső konzisztencián** képes működni — a matematika nem omlik össze. Az LQC visszapattanás, a bébiuniverzum tágulása, és a nem-termális él-sugárzás együtt egy összefüggő fizikai képet adnak.

A modell mára minden korábban azonosított szabad/le nem vezetett paraméterét elvesztette a Norbi-ágban: a csatolási formula (`alpha = e_tidal/(e_tidal+e_bind)`) a tidal-fizikából, az él-spektrum hőmérséklete (Gibbons-Hawking) a bébiuniverzum tágulási rátájából, maga a tágulási ráta (`H_inf`) pedig az LQC-egyenlet analitikus maximumából adódik. Ami megmaradt "kényelmi" feltevés: a `particle.mass = BH tömegének 0,1%-a` — egy reprezentatív, tetszőlegesen választott beeső anyagmennyiség, ez nem ered semmilyen egyenletből.

---

## 7. fázis — az `alpha` és az él-spektrum levezetése (v3)

### Amit korrigáltunk

A 4. fázisban bevezetett `alpha = E_baby / E_total` csatolás — bár helyes nagyságrendet adott — **nem következett a modell saját fizikájából**: a `BabyUniverse`-ben már meglévő tidal-számítás (`e_tidal` vs. `e_bind`, LQC-Hubble-ráta) ki volt számolva, de a normalizálás miatt hatástalanul kiesett, és a `check_breakup()` esemény-detekció csak tesztben létezett, a fő szimulációs ciklusba sosem volt bekötve.

**A javítás:**
- `BabyUniverse::breakup_fraction()` — az `alpha` immár közvetlenül `e_tidal / (e_tidal + e_bind)`-ból adódik, a bébiuniverzum teljes tömegtartalmára (`E_total/c²`) és a jelenlegi belső sűrűségből becsült önkötési sugárra alkalmazva. Ez a *tényleges* tidal-fizikát viszi be a csatolásba, nem egy külön kitalált energiaarányt.
- Az él-spektrum (`edge_radiation_spectrum`) valódi Planck-spektrum lett a bébiuniverzum **Gibbons–Hawking-hőmérsékletén** (`T = ħH/2πk_B` — egy de Sitter-szerű táguló téridő eseményhorizontjának ismert sugárzási hőmérséklete, [GH77]), és ugyanazon a frekvenciatengelyen fut, mint a Hawking-spektrum — korábban a két spektrum dimenziótlanul, egymással össze nem vethető skálán volt kiszámolva, és csak bin-indexenként keveredett.

### Az új eredmény (Planck-tömegű fekete lyuk)

| Lépés | edge_fraction | thermality_score |
|---|---|---|
| 0  | 1.000 | 8.61  |
| 10 | 1.000 | 13.97 |
| 99 | 1.000 | 13.97 |

A Standard végig: `edge_fraction = 0.0`, `thermality_score = 0.10` (változatlan).

`thermality_ratio ≈ 138×`, `total_recovered_bits`: Standard ~0.95 bit, Norbi ~9.97 bit.

### A becsületes összefoglalás — most is

Az `alpha` most már fizikailag levezetett a modellen belül, de ez leleplezett egy másik szabad paramétert: a bébiuniverzum inflációs Hubble-rátáját (korábban `H_INF_DEFAULT = 10⁴³ s⁻¹` hardcode). Ezzel az értékkel a tidal szétszakadás gyakorlatilag azonnal, teljesen (`alpha ≈ 1.0`) bekövetkezik a `timeline` felbontásán nézve — a korábbi, szemléletesebb "52% → 81%" növekvő görbe egy le nem vezetett formula műterméke volt, nem valódi fizikai jelenség.

## 8. fázis — H_inf levezetése és a két időskála szétválasztása

**H_inf levezetése:** a `H_INF_DEFAULT` konstanst lecseréltük a saját LQC-egyenlet analitikus maximumára: `H²(ρ)=(8πG/3)ρ(1-ρ/ρ_P)` deriváltját nullázva `ρ=ρ_P/2`-nél, ahonnan `H_inf = √((8πG/3)·ρ_P/4) ≈ 2,68×10⁴³ 1/s` — ez immár nem szabad paraméter, hanem a bounce-dinamika saját csúcsértéke (`LQCEquation::max_bounce_hubble_rate`).

Eközben egy valódi lebegőpontos hibát is találtunk: a `planck_spectrum()` `exp(x)-1` kifejezése extrém kicsi `x`-re (mély Rayleigh-Jeans tartomány, ami az él-spektrumnál a Gibbons-Hawking-hőmérséklet miatt előfordul) katasztrofális kioltással pontosan 0-t adott. Javítás: `exp_m1(x)`.

**A két időskála szétválasztása:** kiderült, hogy az "azonnali telítődés" nem hibás paraméterválasztás jele, hanem abból fakad, hogy a `timeline` a *külső* Hawking-elpárlási órán (`dt = t_evap/100`) mintavételez, miközben a bébiuniverzum bounce-dinamikája a *saját*, Planck-idő nagyságrendű óráján fut — ez a szemiklasszikus (Hawking) és a kvantumgravitációs (LQC-bounce) leírás érvényességi tartományának általános relativitáselméleti/standard fizikai különbsége, nem a Norbi-hipotézis extra feltevése.

Bevezettük a `BabyUniverse::post_bounce_transient()`-et és a `SimulationResults.bounce_transient` mezőt: a visszapattanás pillanatában 80, Planck-idő (`T_PLANCK`) nagyságrendű finom lépésben újra lejátsszuk a bébiuniverzum korai fejlődését, függetlenül a külső `dt`-től. Az eredmény:

| finom lépés | kor (s, a visszapattanástól) | breakup_fraction |
|---|---|---|
| 0  | 0            | 0,496 |
| 1  | 5,4×10⁻⁴⁴    | 0,927 |
| 3  | 1,6×10⁻⁴³    | 0,979 |
| 8  | 4,3×10⁻⁴³    | 0,993 |
| 20 | 1,1×10⁻⁴²    | 0,997 |
| 79 | 4,3×10⁻⁴²    | 0,999 |

Ez most már **valódi, fokozatos átmenetet** mutat (50%→99,9%+), csak épp néhány Planck-idő (~10⁻⁴³ s) alatt zajlik le — utólag visszatekintve a "52%→81%" régi görbe emlékeztet erre, csak rossz okból (formula-hibából) adódott, most viszont ugyanez a kép a tényleges fizikából (H, tidal energia, önkötés, helyes időfelbontás) jön ki.

---

## Ami következik

1. **Megfigyelési jóslat** — mit kellene mérni (gravitációs hullám visszhangjainak módosulása, analóg fekete lyukak laboratóriumi spektruma)
2. **Peer review** — a fizikai egyenletek külső ellenőrzése

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

---

## 9. fázis — Teljes átvilágítás és javítás (v3.0, 2026-09-28)

### Ami elindította

Egy teljes kód-átvilágítás és a szimuláció tényleges lefuttatása több tömegen
kimutatta, hogy a v2.0 fő eredményei **numerikus műtermékek** voltak, nem a
beépített fizika következményei. A javítás előtt egy kutató-alügynök átnézte a
friss szakirodalmat (LQC, LQG-összeomlás, fehér lyukak, bébiuniverzumok,
Hawking-emisszió, Page-görbe); minden új képlet és állandó ebből származik.

### Ami műtermék volt

| Állítás (v2.0) | Valójában | Oka |
|---|---|---|
| Norbi `edge_fraction = 1.0` | csak pontosan M = m_P-nél; 2.3 m_P-től minden tömegen 0 | `exp(H_inf·dt)` f64-túlcsordulás → skálafaktor ∞ (JSON `null`), sűrűség 0, `breakup_fraction()` → 0 |
| „9.97 visszanyert bit" (Standard: 0.95) | `edge_fraction · log2(1000)` | a spektrum bin-számának logaritmusa; a payload el sem jutott a szimulációig |
| thermality_ratio ≈ 138× | két Planck-görbe keverékének KL-je egy rögzített T_H-hoz | termális keverék nem hordoz információt; a KL ráadásul nem a legjobb illesztéshez mért |
| „Page-görbe" | 1000 bines hisztogram Shannon-entrópiája | felső korlátja ln 1000 ≈ 6.9, a BH entrópiája 12.6 |
| visszapattanás a beesés végén | mindig a 0. lépésben | `NorbiInterior` sugara 0-ról indult; `initial_radius` sosem volt használva |
| „nincs több szabad paraméter" | az él-hőmérséklet a `steps = 100`-tól függött | H ≈ 1/dt, dt = t_evap/100 |
| teljes párolgás | M/M0 = 0.28 a teljes t_evap után | fix lépésközű explicit Euler |
| energia | lépésenként +0.1% M c² a semmiből | `absorb_energy` sosem vont le a BH-ból |
| ρ_bounce = ρ_Planck | ρ_c ≈ 0.409 ρ_Pl | γ_BI = 0.2375 (Ashtekar–Singh 2011, LMY 2023) |
| RK45 integrátor | egyetlen RK4 lépés, be sem volt kötve | — |
| 58/58 zöld teszt | több tautológia (pl. a Page-„validáció" egy beégetett háromszög-függvényt tesztelt) | — |
| CI | mindhárom workflow hónapok óta piros | fmt, ruff, 55 mypy-hiba, nem létező `python.main` |

### Mit csináltunk (commitonként)

1. **Takarítás** — Bevy és Tauri törölve (a Tauri a Norbi-módot figyelmen kívül
   hagyta, a Bevy saját fizikát futtatott), stubok és placeholderek törölve,
   CLI javítva.
2. **Állandók** — CODATA 2022 teljes pontossággal; LQC-állandók; a Planck-spektrum
   prefaktora 4π²-szer túl nagy volt (Stefan–Boltzmann-teszt).
3. **Párolgás** — MacGibbon/Carr fajtánkénti f(M), Page 2013 foton+graviton α,
   greybody foton-spektrum; a hátralévő idő visszafelé integrálva ln M-ben
   (a végfázis is pontos, az eredmény független a lépésszámtól). Útközben
   kiderült: az `ode_solvers` crate dense kimenete ~1e-4 hibával interpolál —
   sparse kimenetre váltottunk.
4. **Belső fizika** — Oppenheimer–Snyder porgömb R0-ról; LQC-visszapattanás
   ρ_c-nél analitikusan (a numerikus Raychaudhuri-integrálás 1e-8-ra egyezik);
   bébiuniverzum log-változókban (nincs túlcsordulás); LMY külső metrika,
   tömegrés (0.83 m_P); **kauzális csatorna**: f(r_b) = 1 és r_b < r_−, a
   fénysugarak r_−-t csak aszimptotikusan közelítik → nincs kapcsolat kifelé.
5. **Információ** — egzakt Haar-unitér Page-görbe és Hayden–Preskill kölcsönös
   információ; félklasszikus Hawking (I = 0); Norbi a kauzalitásból.
6. **CI** — tömeg-scan mindkét módban, schema 3.0 validátor, explicit ruff-szabályok.

### Az új eredmény

| Mennyiség | v2.0 (csak M = m_P) | v3.0 (minden tömeg) |
|---|---|---|
| Norbi külső spektrum | „nem-termális" | azonos a Standard-dal (a belső le van választva) |
| Norbi visszanyert információ | „9.97 bit" | I(Ref:R) = 0 bit |
| Unitér referencia (Page/HP) | — | I(Ref:R) = 2k bit, Page-görbe visszafordul |
| Párolgás | nem fut le | lefut a tömegrésig; τ(5.1e11 kg) ≈ 11 Gyr |
| Visszapattanás | 0. lépés, ρ_Pl | a dinamikából, ρ_c ≈ 0.41 ρ_Pl, r_b = (αm/2)^(1/3) |
| Bébiuniverzum | túlcsordul m_P felett | minden tömegen véges, E = Mc² megmarad |
| Tesztek | 58 + 27 (több tautológia) | 68 Rust + 14 Python, irodalmi/analitikus ellenőrzésekkel |

### A becsületes összefoglalás — v3.0

A bébiuniverzum *létrejötte* konzisztensen modellezhető. A hipotézis döntő
lépése — hogy a sugárzása kívülről látszik — a jelenlegi legjobb geometriában
(LMY 2023) **nem teljesül**, és ezt a bébiuniverzum-irodalom is így látja: a
belső univerzum horizont mögött, kauzálisan leválasztva jön létre. Ezzel a
Norbi-forgatókönyv információ-szempontból Hawking eredeti, információvesztő
képével esik egybe.

A továbblépés iránya, ha a hipotézist életben akarjuk tartani: olyan geometria,
ahol a visszapattanó anyag kauzálisan összeköttetésben marad a külső térrel
(HKSW 2022 lökéshullám, fekete → fehér lyuk átmenet). Ezek azonban már nem
bébiuniverzumot írnak le, hanem a mi univerzumunkba visszatérő anyagot — és
ekkor a jóslat nem „nem-termális Hawking-spektrum", hanem egy késleltetett,
~M² idő utáni kitörés, amit a gravitációshullám-visszhang keresések és a
gamma-háttér (Carr et al. 2021) korlátoznak.

**A legfontosabb tanulság (változatlanul):** egy szimulációt megírni, ami *fut*,
sokkal könnyebb, mint egyet, ami *alátámaszt valamit*. A v2.0-ban a számok egy
része a numerikából jött, nem a természetből — a v3.0 minden számához teszt
tartozik, ami egy független (analitikus vagy irodalmi) értékhez méri.
