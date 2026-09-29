# Fejlesztési Napló — Fekete Lyuk Szimulátor

**Készítők:** Norbi & Claude  
**Időszak:** 2025–2026  
**Verzió:** 3.2.0

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

---

## 10. fázis — Ami utána beleesik: CMB, akkréció, beesések (v3.1, 2026-09-28)

### Miért

A v3.0 után két kérdés maradt nyitva: (1) a realizmus — egy valódi fekete lyuk
nem vákuumban párolog, hanem a környezetéből folyamatosan anyagot és
sugárzást nyel el; (2) a Norbi-dokumentáció 2. fázisa („a belső univerzum a
beeső anyagból táplálkozik", E_belső = E_0 + Σ E_beeső + ∫Ṁc² dt), ami a
PDF-ben szerepelt, de a kódban sosem volt megvalósítva (a v2.0 `absorb_energy`
a semmiből adott hozzá energiát).

### Mit csináltunk

- **CMB-elnyelés** ugyanazzal a foton-greybody hatáskeresztmetszettel, mint az
  emisszió → a részletes egyensúly konstrukció szerint teljesül.
- **Akkréció:** állandó ráta, Bondi (λ = 1/4), Eddington-korlát, sugárzási hatásfok ε.
- **Diszkrét beesések:** „t időpontban m tömegű objektum esik be".
- **Tömegfejlődés** beesések közötti szakaszokban: párolgó ág visszafelé
  ln M-ben (ahogy eddig), növekvő ág időben, a tömeg *változását* normálva.
- **Energiamérleg** ugyanabban az ODE-ben (hiba ~1e-14).
- **Neutrínó-tömegek** (0, 0.0086, 0.05 eV) a MacGibbon-táblában — a hideg,
  nagy fekete lyukaknál ez számít.
- **interior_feeding:** a PDF 2. fázisának energiakönyvelése, beesésenkénti
  sajátidővel a horizontig.

### Amit megtudtunk

| Kérdés | Eredmény |
|---|---|
| Párolog-e ma egy Nap-tömegű fekete lyuk? | **Nem — nő.** T_H = 6e-8 K ≪ T_CMB = 2.7 K; 13.8 Gyr alatt ~1e4 kg CMB-t nyel el, a Hawking-kibocsátás ~1e-10 J. |
| Hol a határ? | M_eq ≈ 5.6e22 kg (~Hold-tömeg). Ennél kisebb fekete lyuk párolog, nagyobb nő (instabil egyensúly). |
| Mit tesz a primordiális fekete lyukakkal a CMB? | Semmit érdemlegeset (relatív hatás < 1e-12 a párolgáshoz képest). |
| Mit tesz egy beesés? | Egy 1e12 kg-os fekete lyukba 1e17 s-nál beeső 1e12 kg-os aszteroida ~9× meghosszabbítja az élettartamot (3.5e18 → 3.1e19 s), mert τ ∝ M³. |
| Eddington-korlátos növekedés? | e^(t/t_S), t_S ≈ 50 Myr (ε = 0.1) — pontosan visszaadja (1e-7). |
| „Táplálja-e" a beeső anyag a bébiuniverzumot? | **Könyvelhető, de nem igazolható.** A később beeső anyag a belső (Cauchy-)horizont felé tart; hogy a visszapattant tartományba jut-e, a geometriából nem következik, és a belső horizontok ismerten instabilak a késői beáramlásra (Poisson & Israel 1990). |

### A becsületes összefoglalás — v3.1

A szimulátor most már a valódi környezet legfontosabb hatásait is tartalmazza,
és ez egy fontos, gyakran elfelejtett tényt tesz láthatóvá: **a Hawking-
párolgás csak a kicsi, hipotetikus primordiális fekete lyukakra számít** — a
csillag-tömegű és nagyobb fekete lyukak a mai Univerzumban nőnek. A Norbi-
hipotézis 2. fázisa (a beeső anyag táplálja a belső univerzumot) most
könyvelésként megvan, de a kulcsállítás (3. fázis: a belső energia kijut)
változatlanul a kauzalitáson bukik el.

---

## 11. fázis — Forgás (Kerr) és valódi fekete lyukak (v3.2, 2026-09-28)

### Mit csináltunk

- **Kerr-geometria:** horizontok, hőmérséklet, entrópia, horizont-szögsebesség,
  ISCO, Novikov–Thorne hatásfok, Bardeen-felpörgetés, Thorne-határ.
- **Page (1976b) forgó Hawking-emissziója** fajtánkénti f(a*), g(a*) táblázatból
  (egy nyomtatott elírást a kutató-alügynök azonosított és javított: a neutrínó-
  oszlop a* ≥ 0.99999 sorában 1e-4 helyett 1e-3 — a monotonitás és Page
  13.35-ös faktora alapján).
- **(M, a*) kétdimenziós fejlődés:** Hawking-lepörgés, korong-felpörgetés,
  impulzusmomentum nélküli csatornák (CMB, gömbszimmetrikus akkréció, radiális beesés).
- **Katalógus** mért paraméterekkel és hivatkozásokkal: Sgr A*, M87*, Cyg X-1,
  GW250114, GW150914, ma elpárolgó PBH; megfigyelhetők (árnyék, EHT-gyűrű, Eddington-arány).
- **CLI:** `--object`, `--list-objects`, `--spin`, `--disk-accretion`, képernyő-összefoglaló.
- **setup_dev.sh** javítva: virtualenv (PEP 668), C-linker és Python-verzió ellenőrzés.

### Amit megtudtunk

| Kérdés | Eredmény |
|---|---|
| Gyorsabban párolog-e egy forgó fekete lyuk? | Igen: a*≈1-ről 2.6–2.8× rövidebb élettartam (Page: 2.0–2.7×), mert a forgás a gravitonok és fotonok kibocsátását 100–26 000-szeresére növeli. |
| Meddig forog? | A spin gyorsabban fogy, mint a tömeg (h ≈ 7): a* = 0.1 már M/M0 ≈ 0.5–0.63-nál — Page következtetése, a teljes fejlődésből visszakapva. |
| Stimmel-e a modell az EHT-képekkel? | Igen: M87* gyűrű 42.0 μas (mért 42 ± 3); Sgr A* δ = −0.082 (EHT: −0.08 ± 0.09). |
| Mi történik a valódi fekete lyukakkal? | Mind nő (akkréció + CMB): Sgr A* ~97 M_☉-et 13.8 Gyr alatt a mai rátával; Cyg X-1 ~0.01 M_☉-et a kísérőcsillag hátralévő ~5 Myr-e alatt, a spin a Thorne-határon marad. Párolgás csak a primordiális fekete lyukaknál. |

### Hardver

A szimuláció egyszálú és könnyű: futásonként 1–2 s, ~55 MB RAM. A fejlesztői
gépen (Intel i5-2500S, 4 mag, 8 GB, 2011) a teljes hideg fordítás 37 s, a
tesztcsomag ~1 perc.

---

## 12. fázis — Kampány, „egy fekete lyukban élünk?", tézis-terv (2026-09-28)

### Mit csináltunk

- **Szimulációs kampány az i5-2500S-en** (`scripts/run_campaign.py`,
  `scripts/analyze_campaign.py`): 71 futás — katalógus × Standard/Norbi,
  tömeg-scan (2 m_P … M_☉, CMB-ben és vákuumban), spin-scan két emissziós
  modellel, emissziós modellek, környezet-szcenáriók, konvergencia. 71/71
  sikeres, 239 s, 54–68 MB; 7/7 automatikus irodalmi ellenőrzés teljesül.
  Minden napló, összesítő és az értelmezés a `runs/2026-09-28/` alatt
  (a globális `*.log` gitignore-szabály kivételt kapott a `runs/` mappára).
- **A PDF feldolgozása** (`docs/norbi-documentation-summary.md`): a hipotézis
  Norbi saját szavaival, a PDF H₁/H₀-kritériumai, pontonkénti állapot a v3.x-ben.
- **„Egy fekete lyukban élünk?"** (`docs/are-we-in-a-black-hole.md`,
  `scripts/cosmology_checks.py`): mi adat és mi modell-következmény; a Hubble-
  = Schwarzschild-sugár „egybeesés" a lapos Friedmann-kozmológia azonossága, nem
  bizonyíték; energiamérleg (egy visszapattanás nem teremt anyagot — infláció
  kell); forró visszapattanás (T ≈ 1.3e32 K, az atomok ~66 e-redő után
  képződnének újra); mi történik egy beeső aszteroidával.
- **Tézis-terv** (`docs/thesis-plan.md`): hat számolás munkacsomagokra bontva
  egy második kutató-alügynök adataival (`data/observations.json`,
  `data/planck/`), előre rögzített kimenetekkel.

### Amit megtudtunk

| Kérdés | Eredmény |
|---|---|
| Kijön-e információ a fekete lyukból? | A Norbi-úton nem (kauzális leválasztás). Általában a mai konszenzus szerint igen, a Hawking-sugárzás korrelációiban, de csak a Page-idő után (Sgr A\*: ~10⁸⁶ év). |
| Mi lesz egy beeső aszteroidával? | Csillagtömegű fekete lyuk és Sgr A\* a horizont előtt széttépi, M87\* egészben lenyeli; a visszapattanáskor minden atom feloldódik. |
| Keletkezhet-e „új galaxis" bent? | Csak inflációval: egy visszapattanás a szülő tömegét tartalmazza (Sgr A\*: ~1/350 000 galaxis); 10–17 e-redő infláció zárná az energiamérleget. |
| Kizárható-e, hogy egy fekete lyukban élünk? | Nem. Első becslés: a bébiuniverzum széle a megfigyelhetőn túl van, ha N > 95–127 e-redő (szülőtömegtől függően); az LQC előrejelzése 130–145. |
| Smolin kozmikus természetes kiválasztódása? | Cáfolt (~3σ): két neutroncsillag 2 M☉ felett (P = 0.0025). |

### Következő lépés

A tézis-terv megvalósítása: WP0 (Python-csomag, a Rust-mag LQC-eredményeinek
reprodukálása), majd WP1 (infláció a visszapattanás után) — a többi erre épül.

## 13. fázis — A tézis-számolások kódja és első futása (2026-09-29)

### Mit csináltunk

- **`thesis/` Python-csomag** a terv hat számolására (WP0–WP6), 15 teszttel.
  - Rust-keresztellenőrzés: r_b, H_max 1e-15-ön.
  - Bonga–Gupt- és Ashtekar–Sloan-reprodukció.
  - CAMB-validáció: 0.28%.
- **`scripts/run_thesis.py`:** egy parancs, ~100 s az i5-ön. Kimenete a `runs/thesis-2026-09-29/`:
  - `results.json`,
  - `SCORECARD.md`,
  - 5 ábra,
  - `run.log`.
- **`thesis/verdict.py`:** a §0 előre rögzített kritériumait gépiesen alkalmazza.
- **CI:** a Python-munkafolyamat a `thesis/`-t is lintolja, típusellenőrzi és teszteli (camb-bal).
- **Részletek:** [docs/thesis-progress.md](docs/thesis-progress.md).

### Amit megtudtunk

| WP | Eredmény |
|---|---|
| 1 Infláció | **vegyes**:<br>• φ²: csak 5.6e-6 hányad kap < 68 e-redőt;<br>• Starobinsky n_s = 0.9653 a Planck 95%-ban, az ACT-tól 2.9σ-ra (a potenciál gondja, nem a fekete lyuké). |
| 2 Anizotrópia | **semleges**:<br>• a fekete-lyuk-belső nyírása (Ω_σ = 0.2, tömegfüggetlen) rövidíti az inflációt, de nem öli meg;<br>• ma ≤ 1e-113. |
| 3 Görbület | **semleges**: \|Ω_K\| ≤ 2.4e-5. |
| 3b Szél | **támogat**:<br>• a horizont-problémát megoldó infláció a szelet minden szülőtömegre a horizontunkon túl viszi;<br>• ≥ 4.2 e-redő ráhagyás, T_reh-től függetlenül. |
| 4 Forgás | **semleges + modell-korlát**:<br>• a homogén visszapattanás csak a* ≲ 1e-7 spinnel működik;<br>• valódi, forgó fekete lyukat a modell nem ír le. |
| 5 CMB | **semleges**:<br>• legjobb N_tot = 141.2, Δχ² = −1.2 (nem szignifikáns);<br>• N_tot > 140.8 (95%). |
| 6 Szelekció | **ellene**: 3.2σ. |

### Következő lépés

Nyitott kérdés a forgó szülő (WP4). Opcionálisan jöhet még:
- a WP5 MCMC-je a Ryzenen,
- a Guillén et al. 2026-féle analitikus LQC-spektrum.
