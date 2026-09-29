# Fekete Lyuk — Belső Univerzum Szimulátor

A „Norbi-hipotézis" numerikus vizsgálata: ha egy fekete lyuk belsejében a
gravitációs összeomlás kvantum-visszapattanásba fordul és egy táguló
„bébiuniverzum" jön létre, eljuthat-e ennek a sugárzása — és vele a beeső
anyag információja — a külső megfigyelőhöz Hawking-sugárzásként?

> **Rövid válasz (v3.2):** a jelenlegi, irodalmi alapokra épülő modellben
> **nem**. A visszapattanás a belső horizont *alatt* történik, és onnan egyetlen
> fénysugár sem ér ki a külső térbe. A külső spektrum ezért a közönséges
> Hawking-spektrum, a beeső üzenet pedig nem nyerhető vissza. A v2.0 pozitív
> eredményei (≈10 visszanyert bit, 138× nem-termalitás) numerikus műtermékek
> voltak — részletesen lásd [summary.md](summary.md), 9. fázis.
>
> **A nagyobb kérdés — egy fekete lyukban élünk-e?** — nyitott: a modell ezt
> nem zárja ki (a bébiuniverzum *kauzális leválasztása* épp ehhez kellene), de
> nem is bizonyítja. A tesztelhető következményeket egy hat számolásból álló
> tézis-terv rendezi — lásd [docs/are-we-in-a-black-hole.md](docs/are-we-in-a-black-hole.md)
> és [docs/thesis-plan.md](docs/thesis-plan.md).

A szimulátor mára valódi fekete lyukakat is kezel (Sgr A\*, M87\*, Cygnus X-1,
GW-maradványok) forgással, akkrécióval és a kozmikus háttérsugárzással, és az
EHT által mért gyűrűméreteket visszaadja.

## Dokumentáció

| Dokumentum | Tartalom |
|---|---|
| **README.md** (ez) | modell, képletek, telepítés, futtatás, kimenet |
| [summary.md](summary.md) | fejlesztési napló fázisonként (1–12), mi volt hibás és miért |
| [runs/2026-09-28/ANALYSIS.md](runs/2026-09-28/ANALYSIS.md) | 71 futásos kampány az i5-ön: eredmények és értelmezés ([RESULTS.md](runs/2026-09-28/RESULTS.md), naplók) |
| [docs/are-we-in-a-black-hole.md](docs/are-we-in-a-black-hole.md) | „Egy fekete lyukban élünk?" — mit mondhat a projekt, mi adat és mi modell |
| [docs/thesis-plan.md](docs/thesis-plan.md) | tézis-terv: 6 számolás (+ egy új), egyenletek, adatok, előre rögzített kimenetek |
| [docs/spin-plan.md](docs/spin-plan.md) | a forgó szülő-probléma (WP4b): adatok, két kiút, első becslés, előre rögzített kimenetek |
| [docs/thesis-progress.md](docs/thesis-progress.md) | a tézis-számolások kódja, futtatása és eredményei (pontozólap: `runs/thesis-2026-09-29/`) |
| [docs/norbi-documentation-summary.md](docs/norbi-documentation-summary.md) | az eredeti `norbi_teljes_dokumentacio.pdf` (v2.0) kivonata és pontonkénti állapota |
| [data/observations.json](data/observations.json) | megfigyelési adatok forrással (Planck, DESI, ACT, BICEP/Keck, neutroncsillagok, …) |
| [data/planck/](data/planck/README.md) | Planck 2018 CMB-spektrumok ellenőrzőösszeggel |

---

## A Norbi-hipotézis

1. Az összeomló anyag sűrűsége eléri a kvantumgravitációs kritikus sűrűséget.
2. Loop Quantum Cosmology (LQC) szerint itt nem szingularitás, hanem
   **visszapattanás** következik: H² = (8πG/3)·ρ·(1 − ρ/ρ_c).
3. A visszapattanás után a belső tartomány **tágul** (bébiuniverzum).
4. A tágulás szélén szétszakadó anyag **sugároz**, és ezt látjuk kívülről
   Hawking-sugárzásként.
5. A sugárzás így **nem teljesen termális**, és a beeső anyag információja
   visszanyerhető.

A szimuláció ezt a láncot lépésenként, az irodalomban publikált egyenletekkel
ellenőrzi. Az 1–3. lépés megvalósítható (ez maga az LQC-porösszeomlás); a 4.
lépés **a kauzalitáson bukik el**; így az 5. sem teljesül.

---

## Mit számol a program

```
                 ┌─────────────────────────── Rust mag (core/) ────────────────────────────┐
config (JSON) ──►│ 1. Külső: (M, a*) — Hawking (Kerr) + CMB + akkréció + beesések          │
payload (JSON) ─►│    dM/dt = −α(M)·ħc⁴/(G²M²), MacGibbon/Carr f(M), greybody foton-spektrum│
                 │ 2. Belső: Oppenheimer–Snyder porgömb, saját idő τ                       │
                 │    Standard: klasszikus, ρ_c-nél érvényét veszti                        │
                 │    Norbi:    LQC visszapattanás ρ_c-nél → táguló bébiuniverzum          │
                 │ 3. Kauzalitás: LMY külső metrika, horizontok, fénysugár-követés         │
                 └──────────────────────────────┬──────────────────────────────────────────┘
                                                │ SimulationResults (schema 3.2, JSON)
                 ┌──────────────────────────────▼──── Python (python/) ─────────────────────┐
                 │ 4. Kvantuminformáció: Page-görbe S(R), Hayden–Preskill I(Ref:R)          │
                 │    unitary / semiclassical / norbi (← causal_channel.exists)             │
                 └──────────────────────────────────────────────────────────────────────────┘
```

### Eredmények (v3.2, Norbi-mód, a* = 0, alapbeállítások: mai CMB, nincs akkréció)

| M (kg) | élettartam | T_H kezdetben | horizont → visszapattanás (sajátidő) | r_b | r_+ | kauzális csatorna |
|---|---|---|---|---|---|---|
| 4.35e-8 (2 m_P) | 3.1e-41 s | 2.8e30 K | 1.4e-43 s | 1.7e-35 m | 6.3e-35 m | nincs |
| 1 | 4.0e-19 s | 1.2e23 K | 3.3e-36 s | 4.8e-33 m | 1.5e-27 m | nincs |
| 5.1e11 (ma párolgó PBH) | **11.1 Gyr** | 2.4e11 K | 1.7e-24 s | 3.9e-29 m | 7.6e-16 m | nincs |
| 1e12 | 110 Gyr | 1.2e11 K | 3.3e-24 s | 4.8e-29 m | 1.5e-15 m | nincs |
| M_☉ | **nem párolog — nő** (CMB) | 6.2e-8 K | 6.6e-6 s | 6.1e-23 m | 2.95 km | nincs |

- **Külső spektrum:** Standard és Norbi módban bitre azonos (teszt).
- **Spektrális nem-termalitás:** minden tömegre 0.267 — ez a greybody-torzítás
  skálafüggetlen alakja, nem információ.
- **Információ** (toy modell, 12+1 qubit): unitary → I(Ref:R) = 2 bit (az üzenet
  visszajön), Page-görbe visszafordul; semiclassical és Norbi → I = 0, S(R)
  monoton nő.
- **A mai CMB-ben** M_eq ≈ 5.6e22 kg felett a fekete lyuk több háttérsugárzást
  nyel el, mint amennyit kisugároz: egy Nap-tömegű fekete lyuk 13.8 Gyr alatt
  ~1e4 kg-ot *nő* (a Hawking-kibocsátás ~1e-10 J). Párolgás csak a kis
  (primordiális) fekete lyukakra releváns.
- **Energiamérleg:** E0 + beesések + elnyelt + akkretált = E_vég + Hawking,
  ugyanabban az ODE-ben integrálva — a hiba ~1e-14; a belső porgömb energiája
  pontosan Mc² (semmi nem keletkezik a semmiből).

---

## Fizikai modell és képletek

### Állandók — `core/src/constants.rs`

CODATA 2022: c, h, k_B egzakt; G = 6.67430e-11. A Planck-egységek ezekből
származtatottak (teszt ellenőrzi). LQC: γ = 0.2375,
ρ_c = √3/(32π²γ³)·ρ_Pl ≈ **0.409 ρ_Pl** (nem ρ_Pl!), α = 16√3πγ³ℓ_P²,
M_min = 4√α c²/(3√3 G) ≈ **0.83 m_P**.

### Hawking-párolgás — `black_hole/evaporation.rs`, `radiation/emission.rs`

| Mennyiség | Képlet | Forrás |
|---|---|---|
| Hőmérséklet | T_H = ħc³/(8πGMk_B) | Hawking 1974 |
| Entrópia | S = A/(4ℓ_P²) | Bekenstein 1973 |
| Tömegvesztés | dM/dt = −5.34e25·f(M)·(M/g)⁻² g/s | MacGibbon 1991; Carr et al. 2010 |
| f(M) | Σ szabadsági fok × {0.267, 0.142/0.147, 0.060, 0.007} (spin 0, ½, 1, 2) × küszöb | Carr et al. 2010 |
| Foton+graviton | α = 3.7474e-5 (Planck-egység) | Page 2013 |
| Foton greybody | σ → (4A/3)(GMω/c³)² ill. 27π(GM/c²)²; ℓ=1 bekapcsolás x_c = 0.21 | Page 1976 |

A tömegfejlődést a végtömegtől *visszafelé*, ln M-ben integráljuk (Dopri5), így a
végfázis is teljes pontossággal felbontott; az idővonal a tömegben logaritmikus,
az eredmény független a lépésszámtól. Ellenőrzés: τ(5.1e11 kg) ≈ 11 Gyr
(irodalom: ~13.8 Gyr; az eltérés a közelítő fajta-küszöbökből jön).

### Környezet: ami utána beleesik — `black_hole/environment.rs`, `black_hole/evolution.rs`

dM/dt = [P_abs(M) − P_H(M)]/c² + (1 − ε)·Ṁ_acc(M), plusz ugrások a beeséseknél.

| Csatorna | Képlet | Forrás / ellenőrzés |
|---|---|---|
| CMB-elnyelés | P_abs = ∫4πσ(ν)B_ν(T_CMB)dν, ugyanazzal a σ-val, mint az emisszió | részletes egyensúly (teszt); nagy M-re 27πr_g²·4σT⁴ |
| Egyensúly | f(M_eq) = 0; T_CMB = 2.7255 K-ben M_eq ≈ 5.6e22 kg | T_H(4.5e22 kg) = 2.7 K |
| Állandó akkréció | Ṁ = áll. | — |
| Bondi | Ṁ = 4πλ(GM)²ρ_∞/c_s³, λ = 1/4 | Bondi 1952 |
| Eddington-korlát | Ṁ_Edd = 4πGMm_p/(εσ_T c); növekedés e^(t/t_S), t_S = εσ_Tc/((1−ε)4πGm_p) ≈ 50 Myr | L_Edd = 1.26e31 W/M_☉ (teszt) |
| Beesés | M → M + m a t időpontban | — |

A környezet időben állandó (a CMB lehűlése és a gáz kifogyása nincs
modellezve). Így a folytonos egyenlet autonóm, egyetlen (instabil) egyensúlyi
tömeggel: alatta párolgás (visszafelé integrálva ln M-ben), felette növekedés
(időben, a tömeg *változását* normálva — a Napra ez 1e-26 relatív, M-ben
f64-ben nem is ábrázolható). A neutrínók tömeg-sajátállapotként szerepelnek
(0, 0.0086, 0.05 eV), ami a hideg, nagy fekete lyukaknál számít.

**Belső „táplálás"** (a Norbi-dokumentáció 2. fázisa, `interior_feeding`):
minden beesés sajátideje a horizontig, és az összes befelé átlépett energia
E_belső = E_0 + Σm_ic² + ∫(P_abs + (1−ε)Ṁc²)dt. Ez *könyvelés*: a később
beeső anyag az LMY-geometriában a belső (Cauchy-)horizont felé tart; hogy
ugyanabba a bébiuniverzumba jut-e, nincs modellezve, és a belső horizontok
ismerten instabilak a késői beáramlással szemben (tömeg-infláció, Poisson &
Israel 1990).

### Forgó (Kerr) fekete lyukak — `black_hole/kerr.rs`, `radiation/emission.rs`

| Mennyiség | Képlet / érték | Forrás |
|---|---|---|
| Horizontok | r± = m(1 ± √(1−a*²)), m = GM/c² | Kerr 1963 |
| Hőmérséklet | T = ħc³/(4πGMk_B)·√(1−a*²)/(1+√(1−a*²)) | Bardeen, Carter, Hawking 1973 |
| Terület, entrópia | A = 8πm²(1+√(1−a*²)), S = A/4ℓ_P² | |
| ISCO, E_isco, L_isco | Z1, Z2 képletek; a* = 0: 6m, 0.9428 | Bardeen, Press, Teukolsky 1972 |
| Korong-hatásfok | ε = 1 − E_isco: 5.7% → 32% (a* = 0.998) | Novikov–Thorne |
| Akkréciós felpörgetés | dJ/dM₀ = L_isco, a Thorne-határig (0.998) | Bardeen 1970; Thorne 1974 |
| Hawking-emisszió | f(a*), g(a*) fajtánként; ν ×13.35, γ ×107.5, graviton ×26 380 a*→1-re | Page 1976b (Dong et al. 2016 táblázata) |

A spin a tömeggel együtt fejlődik: a Hawking-párolgás a forgást gyorsabban
viszi el, mint a tömeget (h = d ln a*/d ln M ≈ 7 kis spinre), így egy gyorsan
forgó primordiális fekete lyuk a tömegének ~40–50%-a elvesztése után már
alig forog, és 2.6–2.8× rövidebb ideig él (Page: 2.0–2.7). A vékony korong
felpörget; a gömbszimmetrikus akkréció, a CMB és a radiális beesés nem visz
be impulzusmomentumot (a*·M² állandó). **Közelítések:** a tömeges fajták az
azonos spinű tömegtelen mező Kerr-arányát kapják; a CMB-elnyelés
hatáskeresztmetszete a nem forgó esetre vonatkozik; a belső összeomlás és
a kauzalitás-elemzés a* = 0-val készül (forgó LQC-összeomlásra nincs
publikált effektív modell — a klasszikus Kerr-megoldásnak is van belső
Cauchy-horizontja, így a következtetés minőségileg ugyanaz).

### Valódi fekete lyukak — `catalog.rs`

| Kulcs | Tömeg | Távolság | Spin | Ṁ | Forrás |
|---|---|---|---|---|---|
| `sgr-a` | 4.2996e6 M_☉ | 8.276 kpc | 0.9 (gyengén korlátozott) | 7e-9 M_☉/év | GRAVITY 2024; EHT 2022 |
| `m87` | 6.5e9 M_☉ | 16.8 Mpc | 0.9 (nem mért) | 1e-3 M_☉/év | EHT 2019, 2021 |
| `cyg-x1` | 21.2 M_☉ | 2.22 kpc | 0.998 (> 0.9985 mért) | 3e-9 M_☉/év, korong | Miller-Jones 2021; Zhao 2021 |
| `gw250114` | 62.7 M_☉ | ~440 Mpc | 0.68 | — | LVK 2025 |
| `gw150914` | 63.1 M_☉ | 440 Mpc | 0.69 | — | GWTC-1 |
| `pbh-today` | 5.1e11 kg | — | 0 | — | Carr et al. 2010 |

**Ellenőrzés az EHT-képekkel:** a tömegből és távolságból számolt gyűrű
(≈ 11·GM/(c²D)) M87*-ra 42.0 μas (mért: 42 ± 3), Sgr A*-ra 56.4 μas
(mért: 51.8 ± 2.3), azaz δ = −0.082 — pontosan az EHT által publikált
δ = −0.08 ± 0.09 eltérés. A mai akkréciós rátát a program állandónak veszi
a teljes horizonton (objektumonként jelölt feltevés); Cyg X-1-nél a horizont
a kísérőcsillag hátralévő élete (~5 Myr).

### Összeomlás és visszapattanás — `interior/collapse.rs`, `quantum/lqc.rs`

Marginálisan kötött homogén porgömb (Oppenheimer–Snyder), R0 = n·r_s-ről.
Sajátidő τ a visszapattanástól:

```
klasszikus:  ρ(τ) = 1/(6πGτ²)                        H = 2/(3τ)
LQC:         ρ(τ) = ρ_c/(1 + τ²/τ_b²),  τ_b = 1/√(6πGρ_c)
             H(τ) = (2/3)·τ/(τ_b² + τ²),  H_max = √(2πGρ_c/3) ≈ 0.926/t_P
             r_b  = (3M/(4πρ_c))^(1/3) = (αGM/(2c²))^(1/3)
```

[Kelly–Santacruz–Wilson-Ewing 2020; Lewandowski–Ma–Yang–Zhang 2023]. A
Raychaudhuri-egyenlet numerikus integrálása 1e-8 pontossággal egyezik az
analitikus megoldással (teszt). A horizont → klasszikus szingularitás sajátidő
4GM/(3c³) (teszt).

### Bébiuniverzum — `interior/baby_universe.rs`

A visszapattanás utáni szakasz ugyanaz az LQC-megoldás, log-változókban:
a = R/r_b = (1 + τ²/τ_b²)^(1/3), N = ln a. Nincs exp(H·dt), így nincs
túlcsordulás egyik tömegen sem. Az él Gibbons–Hawking-hőmérséklete
T = ħH/(2πk_B), belső luminozitása σT⁴·4π(c/H)².

### Kauzalitás — `geometry/mod.rs`

Külső metrika (LMY 2023): f(r) = 1 − 2m/r + αm²/r⁴, m = GM/c².

1. **f(r_b) = 1 pontosan**, és r_b < r_* (f minimuma) ⇒ r_b a belső horizont
   (r_−) *alatt* van.
2. Befutó Eddington–Finkelstein koordinátákban a kifelé tartó fénysugarakra
   dr/dv = f/2; r_− fixpont, így a sugár δ ∝ e^(−κ_−v) szerint csak
   aszimptotikusan közelíti — a külső horizontot (r_+) sosem éri el.

Nagy tömegre r_b és r_− f64-ben megkülönböztethetetlen (a Napra ~1e-26
relatív), ezért a δ_b = r_− − r_b távolságot kioltásmentesen számoljuk.

Ez összhangban van a bébiuniverzum-irodalommal (Frolov–Markov–Mukhanov 1990;
Chakrabarty et al. 2020; Masó-Ferrando et al. 2023): a belső univerzum
horizont mögött, kauzálisan leválasztva jön létre. **Nem modellezett:**
a Husain–Kelly–Santacruz–Wilson-Ewing (2022) LTB-modellben a visszapattanó
anyag lökéshullámként *a mi* univerzumunkba jön ki ~M² idő alatt — ez nem
bébiuniverzum és nem Hawking-szerű spektrum.

### Kvantuminformáció — `python/quantum_info.py`

- **unitary** (Page 1993, Hayden–Preskill 2007): n + k qubit egzakt Haar-unitérrel
  összekeverve, qubitenkénti kisugárzás. S(R) Page-görbe, I(Ref:R) → 2k bit.
- **semiclassical** (Hawking 1976): minden kisugárzott qubit Bell-pár fele,
  párja bent marad: ρ_{Ref,R} = ρ_Ref ⊗ (I/2)^j, I = 0.
- **norbi**: `causal_channel.exists` alapján; leválasztott bébiuniverzumnál
  = semiclassical.

A toy modell qubitszáma leskálázott (a valódi S_BH ~10⁴⁰+ bit); az időtengely
(a j. qubit kisugárzásának ideje: M_j = M0·√(1 − j/n)) a valódi párolgásból jön.

---

## Mappaszerkezet

```
core/src/
  constants.rs, units.rs     CODATA 2022, LQC-állandók, Planck-egység konverziók
  black_hole/                BlackHoleTrait, Schwarzschild, Kerr, párolgás, környezet, (M, a*)-fejlődés
  catalog.rs                 valódi fekete lyukak (Sgr A*, M87*, Cyg X-1, GW-maradványok)
  radiation/                 emissziós modellek, greybody, spektrum, HawkingEngine
  interior/                  collapse.rs (OS), standard.rs, norbi.rs, baby_universe.rs
  quantum/lqc.rs             effektív Friedmann/Raychaudhuri, porral analitikus megoldás
  geometry/                  LMY-metrika, horizontok, kauzális csatorna
  time_evolution/            ode.rs (Dopri5), checkpoint.rs (MessagePack)
  tests/                     105 teszt
python/
  __main__.py                CLI: python -m python ...
  quantum_info.py            Page-görbe, Hayden–Preskill
  comparator.py              Standard vs. Norbi összevetés
  information_packet.py      payload SHA3 → determinisztikus mag
  config.py, constants.py    a Rust típusok/állandók tükre
  tests/                     22 teszt (Page-formula, HP, hypothesis, végponttól végpontig)
scripts/
  setup_dev.sh               telepítés egy lépésben (venv, Rust mag, tesztek)
  run_campaign.py            71 futásos kampány naplózva → runs/<dátum>/
  analyze_campaign.py        összesítő, táblázatok, irodalmi ellenőrzések
  cosmology_checks.py        „egy fekete lyukban élünk?" becslések (képletenként)
  fetch_planck_data.sh       Planck-spektrumok letöltése ellenőrzőösszeggel
  validate_results.py, export_csv.py, checkpoint_inspect.py, benchmark_compare.py
runs/2026-09-28/             kampány: logs/, tests.log, system.txt, summary.csv, RESULTS.md, ANALYSIS.md
docs/                        elemzések és a tézis-terv (lásd Dokumentáció)
thesis/                      a tézis-számolások Python-csomagja (WP0–WP6, CAMB) — scripts/run_thesis.py
data/                        observations.json (forrásokkal), planck/ (CMB-spektrumok)
```

---

## Telepítés és futtatás

### Hardver

A szimuláció könnyű: egyszálú, futásonként **1–2 másodperc és ~55 MB RAM**
(minden katalógus-objektumra mérve). A fejlesztői gépen — egy 2011-es
**Intel i5-2500S, 4 mag, 8 GB RAM** — a teljes, gyorsítótár nélküli
release-fordítás **37 s**, a tesztcsomag (105 Rust + 22 Python) **~1 perc**.
Egy erősebb gép (pl. 16 magos Ryzen) csak a fordítást gyorsítja, illetve sok
paraméter-szkennelést tud párhuzamosan futtatni (egy futás egy magot használ).

### Első telepítés (Debian/Ubuntu)

```bash
# 1. Rendszercsomagok (C-linker, Python venv, git)
sudo apt update
sudo apt install -y git curl build-essential python3 python3-venv

# 2. Rust (ha még nincs) — rustup, felhasználói szinten
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 3. A repó és a környezet (virtualenv, a Rust mag lefordítása, tesztek)
git clone https://github.com/badzso-boop/black-hole-simulation.git
cd black-hole-simulation
bash scripts/setup_dev.sh
```

Python 3.11 vagy újabb kell. A `setup_dev.sh` létrehozza a `.venv`-et (a
rendszer-Pythonba a PEP 668 miatt nem telepít), `pip install -e '.[dev]'`-vel
lefordítja a Rust magot Python-modullá (maturin), majd lefuttatja a teszteket.
Conda-környezetben előtte: `unset CONDA_PREFIX`.

### Futtatás

```bash
source .venv/bin/activate

python -m python --list-objects                       # a valódi fekete lyukak katalógusa
python -m python --object sgr-a                       # Sagittarius A*, mért paraméterekkel
python -m python --object m87 --norbi-mode true       # M87*, Norbi-belsővel
python -m python --object cyg-x1 --output output/cyg.json
python -m python --mass 1e12 --spin 0.99              # forgó primordiális fekete lyuk
python -m python --object sgr-a --spin 0.5 --accretion none   # a kapcsolók felülírják a katalógust

python scripts/validate_results.py output/*.json      # ellenőrzés
python scripts/export_csv.py output/cyg.json output/cyg.csv
```

A képernyőn rövid összefoglaló jelenik meg (végtömeg, spin, ΔM, EHT-gyűrű,
figyelmeztetések); a teljes eredmény a `--output` JSON-fájlban van
(alapból `output/results.json`).

Fontosabb kapcsolók:

| Kapcsoló | Jelentés |
|---|---|
| `--object KULCS` | katalógus-objektum: `sgr-a`, `m87`, `cyg-x1`, `gw250114`, `gw150914`, `pbh-today` |
| `--mass KG`, `--spin A` | kezdőtömeg (kg) és spin 0 ≤ a* < 1 |
| `--norbi-mode true` | LQC-visszapattanás + bébiuniverzum a belsőben |
| `--emission-model` | `MacGibbon` (alap), `PageGammaGraviton`, `PhotonBlackbody` |
| `--max-time S` | szimulációs horizont (s); alapból a párolgás végéig / az Univerzum koráig |
| `--cmb-temperature K` | háttérsugárzás (alap 2.7255 K; 0 = vákuum) |
| `--accretion {none,constant,bondi}` | akkréció; `--accretion-rate`, `--gas-density`, `--sound-speed`, `--no-eddington-limit` |
| `--disk-accretion` | vékony korong: ε = 1 − E_isco(a*), Bardeen-felpörgetés a Thorne-határig |
| `--radiative-efficiency E` | ε (gömbszimmetrikus akkrécióra) |
| `--infall IDŐ:TÖMEG[:CÍMKE]` | beesés, ismételhető (pl. `1e17:5.97e24:Föld`) |
| `--steps`, `--interior-steps` | mintapontok száma (a pontosságot nem befolyásolja, csak a felbontást) |
| `--qubits`, `--message-qubits`, `--payload JSON`, `--no-info` | kvantuminformációs toy modell |

M < M_min ≈ 1.81e-8 kg esetén a program hibával áll le (tömegrés: nincs horizont).

Teljes szimulációs kampány (71 futás, naplókkal és elemzéssel; ~4 perc az i5-ön):

```bash
python scripts/run_campaign.py            # → runs/<dátum>/logs, system.txt, tests.log
python scripts/analyze_campaign.py runs/<dátum>   # → RESULTS.md, summary.csv
```

A legutóbbi kampány és értelmezése: [runs/2026-09-28/ANALYSIS.md](runs/2026-09-28/ANALYSIS.md).

Kozmológiai becslések és a tézis előkészítése:

```bash
python scripts/cosmology_checks.py        # Hubble- vs Schwarzschild-sugár, energiamérleg,
                                          # forró visszapattanás, aszteroida a fekete lyukba
pip install -e '.[dev,thesis]'            # a tézis-számolásokhoz: camb, getdist, matplotlib
bash scripts/fetch_planck_data.sh         # Planck-spektrumok újraletöltése, ellenőrzéssel
```

Tesztek és benchmark:

```bash
cargo test --manifest-path core/Cargo.toml
python -m pytest python/tests
cargo bench --manifest-path core/Cargo.toml
```

---

## Kimenet (schema 3.2)

```jsonc
{
  "schema_version": "3.2",
  "config": { "mass": 5.1e11, "norbi_mode": true, "emission_model": "MacGibbon", "steps": 100, ... },
  "timeline": [ { "time", "time_to_evaporation"?, "mass", "spin", "temperature", "entropy",
                  "semiclassical_valid", "net_mass_rate", "absorbed_power",
                  "accretion_inflow", "after_infall"?, "spectrum": { "frequencies", "intensities",
                  "temperature", "total_power", "photon_power",
                  "spectral_nonthermality", "fit_temperature" } } ],
  "evaporation_complete": true, "end_mass": 1.81e-8, "end_time", "equilibrium_mass"?,
  "interior": { "kind": "norbi", "samples": [ { "tau", "radius", "density", "hubble",
                "ricci_scalar", "phase": "infall|trapped|inner_region|post_bounce" } ],
                "tau_start", "tau_horizon_crossing", "proper_time_horizon_to_end",
                "bounce": { "radius", "density", "max_hubble_rate", "timescale" } },
  "baby_universe": [ { "tau", "scale_factor", "efolds", "hubble", "density", "radius",
                       "total_energy", "gh_temperature", "interior_luminosity" } ],
  "causal_channel": { "exists": false, "reason": "...", "horizons": { ... },
                      "edge_ray_final_gap", "edge_ray_efolds" },
  "energy": { "initial_energy", "final_exterior_energy", "hawking_radiated",
              "background_absorbed", "accretion_inflow", "accretion_luminosity",
              "infall_events", "relative_error" },
  "interior_feeding": { "initial_energy", "events": [ { "exterior_time", "label", "mass",
                        "mass_before", "mass_after", "proper_time_to_horizon" } ],
                        "continuous_inflow_energy", "total_infallen_energy", "note" },
  "kerr": { "initial_spin", "final_spin", "r_plus", "r_minus", "isco_radius",
            "disk_efficiency", "horizon_angular_velocity" },
  "object"?: { "key", "name", "theta_g_uas", "shadow_diameter_uas", "predicted_ring_uas",
               "observed_ring_uas", "ring_deviation", "eddington_ratio", "references", ... },
  "warnings": [ ... ],
  "payload": { ... },
  "information": { "curves": { "unitary": {...}, "semiclassical": {...}, "norbi": {...} },
                   "active_model", "message_recoverable", "emission_times", ... }
}
```

---

## CI (GitHub Actions)

- `rust-tests.yml` — fmt, clippy `-D warnings`, `cargo test`, tarpaulin
- `python-tests.yml` — ruff (explicit szabálykészlet), mypy `--strict`, pytest (3.11–3.13)
- `integration.yml` — tömeg-scan (2 m_P, 1 kg, 5.1e11 kg, M_☉) × Standard/Norbi,
  három környezet-szcenárió (beesés, Bondi/Eddington, állandó akkréció),
  minden katalógus-objektum és egy forgó primordiális fekete lyuk,
  validátor; a tömegrés alatti tömegnek hibát kell adnia

---

## Korlátok

- **Emisszió:** a fajta-küszöbök közelítőek (τ(M*) ≈ 11 vs. 13.8 Gyr); a
  foton greybody a köztes frekvenciákon interpoláció. Pontosabb érték a
  BlackHawk kódból (Arbey & Auffinger) nyerhető.
- **Szemiklasszikus határ:** M < 10 m_P alatt a Hawking-képletek érvényessége
  kérdéses (`semiclassical_valid = false`); a párolgást a tömegrésnél
  (M_min ≈ 0.83 m_P) állítjuk meg.
- **Belső modell:** homogén, marginálisan kötött por (OS); nincs nyomás,
  forgás, töltés, és nincs a párolgás visszahatása a belsőre. A később beeső
  anyag csak könyvelve van (`interior_feeding`), a belső dinamikát nem módosítja.
- **Kerr:** a tömeges fajták Kerr-szorzója a tömegtelen mezőé; a CMB-elnyelés
  és a belső modell a nem forgó esetre vonatkozik (lásd fent).
- **Katalógus:** a spin Sgr A*-ra és M87*-ra gyengén korlátozott / nem mért
  (0.9 feltételezve); a mai akkréciós ráta állandónak tekintve.
- **Környezet:** időben állandó (a CMB nem hűl a kozmikus tágulással, a gáz
  nem fogy el); a kozmikus neutrínóháttér elnyelése nincs benne; a beesések
  pillanatszerűek.
- **Két óra:** a belső sajátidő (τ) és a külső idő közti leképezés nincs
  modellezve — erre csak kauzális csatorna esetén lenne szükség.
- **Toy modell:** az információs görbék 12–20 qubites leskálázott modellből jönnek.
- `norbi_teljes_dokumentacio.pdf` a v2.0 állapotot írja le, és ebben a
  revízióban nem frissült.

---

## Konklúzió

A v3.0 minden ismert numerikus és fizikai hibát kijavított, a v3.1–3.2 pedig
hozzáadta a környezetet (CMB, akkréció, beesések), a forgást (Kerr) és a valódi
fekete lyukakat (lásd [summary.md](summary.md)). Minden bemenet egzakt állandó,
publikált irodalmi érték vagy objektumonként jelölt feltevés. Az eredmény:

- A **visszapattanás és a bébiuniverzum** konzisztensen modellezhető: az
  LQC-por összeomlása minden tömegen ρ_c-nél megfordul, és a belső tartomány
  tágul, energia-megmaradással.
- A hipotézis kulcslépése — hogy a bébiuniverzum szélének sugárzása
  **kívülről** Hawking-sugárzásként látszik — **nem teljesül**: a visszapattanás
  a belső horizont alatt történik, onnan fénysugár nem ér ki. A külső spektrum
  Standard és Norbi módban azonos.
- Ezért a Norbi-forgatókönyvben az **információ nem nyerhető vissza** (I = 0),
  ugyanúgy, mint Hawking eredeti, félklasszikus képében. Információ-visszanyeréshez
  unitér párolgás kell (Page-görbe, szigetek), amit a bébiuniverzum-mechanizmus nem ad.

- **Valódi fekete lyukak ma nem párolognak, hanem nőnek:** a mai CMB-ben
  M_eq ≈ 5.6e22 kg (kb. Hold-tömeg) felett az elnyelés nagyobb a Hawking-
  kibocsátásnál; minden ismert fekete lyuk 9–17 nagyságrenddel nehezebb. A
  párolgás csak primordiális fekete lyukaknál számít, ott erősen függ a
  részecskefizikától (17–32×) és a forgástól (a*≈1: 2.6–2.8× rövidebb élet).
- **A modell a megfigyelésekkel konzisztens:** a tömegből és távolságból várt
  EHT-gyűrű M87\*-ra 42.0 μas (mért 42 ± 3), Sgr A\*-ra δ = −0.082 (EHT: −0.08 ± 0.09).

A „Hawking-sugárzás = a bébiuniverzum széle" állítás továbbvitele csak olyan
geometriával lehetséges, ahol a belső tartomány kauzálisan összeköttetésben
marad a külső térrel (pl. a HKSW 2022-féle lökéshullám-modell, vagy fekete lyuk
→ fehér lyuk átmenet) — ezek viszont nem bébiuniverzumot, hanem a mi
univerzumunkba visszatérő anyagot írnak le.

**Egy fekete lyukban élünk?** A fordított kérdés — hogy *a mi* Ősrobbanásunk
egy szülő-univerzumbeli fekete lyuk visszapattanása volt-e — nyitott, és a
kauzális leválasztás éppen *szükséges* hozzá. Egy első becslés szerint a
bébiuniverzum széle a megfigyelhető Univerzumon túl van, ha a visszapattanás óta
N > 95–127 e-redőnyi tágulás történt (a szülő tömegétől függően); az LQC
természetes előrejelzése 130–145 — így ez semmilyen szülőtömegre nem kizárt.
Smolin „kozmikus természetes kiválasztódása" viszont (egy javasolt teszt) a
2 M☉ feletti neutroncsillagok miatt ~3σ-val cáfolt. A részletes, előre rögzített
kimenetekkel tervezett hat számolás: [docs/thesis-plan.md](docs/thesis-plan.md)
(**még nincs megvalósítva**).

---

## Irodalom

1. Ashtekar & Singh, *Loop Quantum Cosmology: A Status Report*, CQG 28, 213001 (2011), arXiv:1108.0893
2. Lewandowski, Ma, Yang, Zhang, PRL 130, 101501 (2023), arXiv:2210.02253
3. Kelly, Santacruz, Wilson-Ewing, arXiv:2006.09325 (2020)
4. Husain, Kelly, Santacruz, Wilson-Ewing, PRL 128, 121301 (2022), arXiv:2109.08667
5. Ashtekar, Olmedo, Singh, arXiv:1806.02406 (2018)
6. Page, PRD 13, 198 (1976); Page, arXiv:1301.4995 (2013)
7. Carr, Kohri, Sendouda, Yokoyama, PRD 81, 104019 (2010), arXiv:0912.5297; Rep. Prog. Phys. 84, 116902 (2021), arXiv:2002.12778
8. Page, PRL 71, 1291 (1993), gr-qc/9305007; Hayden & Preskill, JHEP 0709:120 (2007), arXiv:0708.4025
9. Almheiri, Hartman, Maldacena, Shaghoulian, Tajdini, Rev. Mod. Phys. 93, 035002 (2021), arXiv:2006.06872
10. Frolov, Markov, Mukhanov, PRD 41, 383 (1990); Chakrabarty et al., EPJC 80, 373 (2020), arXiv:1909.07129; Masó-Ferrando et al., arXiv:2304.12018 (2023)
11. Gibbons & Hawking, PRD 15, 2738 (1977)
12. Arbey & Auffinger, BlackHawk, arXiv:1905.04268
13. Bondi, MNRAS 112, 195 (1952) — gömbszimmetrikus akkréció
14. Poisson & Israel, PRD 41, 1796 (1990) — belső horizontok instabilitása (tömeg-infláció)
15. Fixsen, ApJ 707, 916 (2009) — T_CMB = 2.7255 K
16. Page, PRD 14, 3260 (1976b) — forgó fekete lyuk emissziója; Dong, Kinney & Stojkovic, JCAP (2016), arXiv:1511.05642 — f(a*), g(a*) táblázat
17. Bardeen, Press & Teukolsky, ApJ 178, 347 (1972); Bardeen, Nature 226, 64 (1970); Thorne, ApJ 191, 507 (1974)
18. GRAVITY Collaboration, A&A 692, A242 (2024) — Sgr A* tömeg és távolság
19. EHT Collaboration, ApJL 875, L1–L6 (2019); ApJL 910, L13 (2021) — M87*; ApJL 930, L12–L17 (2022) — Sgr A*
20. Miller-Jones et al., Science 371, 1046 (2021); Zhao et al., ApJ 908, 117 (2021) — Cygnus X-1
21. LIGO–Virgo–KAGRA, PRL (2025), arXiv:2509.08054 — GW250114; GWTC-1, PRX 9, 031040 (2019)
