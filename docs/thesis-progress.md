# Tézis-számolások — munkanapló és eredmények

**Mi ez:** a [thesis-plan.md](thesis-plan.md) hat számolásának (WP0–WP6) *kódolt* változata,
lefuttatva, és összevetve az ott **előre rögzített** kritériumokkal (§0). Ez nem a tézis
szövege — csak az, hogy mit csinálunk, hogyan, és mi jött ki.

**Állapot (2026-09-29):** minden WP le van kódolva, tesztelve és lefuttatva.
Eredmény: [`runs/thesis-2026-09-29/SCORECARD.md`](../runs/thesis-2026-09-29/SCORECARD.md).

## Futtatás

```bash
pip install -e '.[dev,thesis]'          # camb, getdist, matplotlib
python scripts/run_thesis.py            # → runs/thesis-<dátum>/  (~100 s az i5-ön)
python -m pytest thesis/tests -q        # 15 teszt, ~15 s
```

## Pontozólap

| WP | Kérdés | Eredmény | §0-ban várt |
|---|---|---|---|
| 1 | Elég inflációt ad-e a visszapattanás, jó-e az (n_s, r)? | **vegyes** | támogat |
| 2 | Túléli-e a fekete lyuk belsejének anizotrópiája? | **semleges** | semleges |
| 3 | Mekkora térgörbületet jósol a zárt szülő? | **semleges** | semleges |
| 3b | A bébiuniverzum széle túl van-e a horizontunkon? (új számolás) | **támogat** | támogat |
| 4 | Hagy-e tengelyt a szülő forgása? | **semleges + modell-korlát** | semleges |
| 5 | Látszik-e a visszapattanás a CMB alacsony ℓ-jein? | **semleges** | semleges |
| 6 | Smolin természetes szelekciója vs neutroncsillagok | **ellene (cáfolt)** | ellene |

Hat WP-ből öt pontosan az előre várt kimenetet adta. Két eltérés van:
- **WP1** ACT-feszültsége.
- **WP4** modell-korlátja.

Mindkettő lent részletezve.

## Mit számol a kód, WP-nként

A kód a `thesis/` csomagban van (Planck-egység, G = ħ = c = 1).
Minden integrálás `scipy` DOP853-mal fut, rtol 1e-10.

### WP0 — alapok (`units.py`, `lqc.py`, `history.py`)

**Effektív LQC:**
- H² = (8π/3)ρ(1 − ρ/ρ_c), ahol ρ_c = 0.4094.
- Por-visszapattanás, és r_b(M) a LMY 2023 szerint.

**Ellenőrzés a Rust mag ellen:** r_b és H_max 1e-15 pontossággal egyezik
(`test_matches_rust_core`).

**Az infláció utáni tágulás** (`history.py`):
- felmelegedés w = 0-val,
- utána entrópia-megmaradás,
- z_eq = 3402.

### WP1 — infláció a visszapattanás után (`inflation.py`, `wp1.py`)

**Egyenletek:** skalármező a visszapattanáson át:
- Ḣ = −4π(ρ+P)(1−2ρ/ρ_c),
- φ̈ + 3Hφ̇ + V′ = 0.

**Numerikus módszer:**
1. Az első szakasz kozmikus időben fut a szuperinfláció végéig (Ḣ = 0).
2. Utána az e-redő a független változó. H itt a Friedmann-kényszerből jön, nem a
   Raychaudhuri-egyenletből. Az utóbbi instabil (δH/H ∝ e^{6N}), és az első változatban
   hamis, 166 e-redős „plafon"-eredményeket adott. A kényszer hibája most ~1e-11.

**Reprodukált irodalom:**

| | mi | cikk |
|---|---|---|
| Starobinsky küszöb, φ̇_B > 0 (60 e-redő) | φ_B ≥ −1.460 | −1.45 (Bonga–Gupt 2016) |
| Starobinsky küszöb, φ̇_B < 0 | φ_B ≥ 3.621 | 3.63 |
| φ² kudarc-sáv (< 68 e-redő) | φ_B ∈ [−5.50, 1.03] | [−5.5, 0.94] (Ashtekar–Sloan 2011) |
| φ² kudarc-hányad | 4.4e-6 (egyenletes) / 5.6e-6 (Liouville) | „< 3e-6" |

**Megjegyzés a φ²-hányadhoz:** Ashtekar–Sloan saját Eq. 4.26-ja a [−5.5, 0.94] sávra
≈ 5.5e-6-ot ad, nem a közölt 2.74e-6-ot. A kettes faktor a cikkben van; a mi Liouville-
értékünk az ő képletükkel egyezik.

**(n_s, r):** N* önkonzisztensen jön a felmelegedési hőmérsékletből (k* = 0.05/Mpc).

| T_reh | N* | n_s | r |
|---|---|---|---|
| azonnali (2.7e15 GeV) | 55.6 | 0.9653 | 0.0034 |
| 1e9 GeV | 50.6 | 0.9620 | 0.0041 |
| 4 MeV (BBN-határ) | 41.9 | 0.9544 | 0.0059 |

- **Planck (0.9649 ± 0.0042):** a legjobb eset benne van a 95%-ban.
- **ACT DR6 (0.974 ± 0.003):** 2.9σ-ra van tőle, ezért „vegyes".
- A feszültség a Starobinsky-*potenciálé*, nem a fekete-lyuk-eredeté. Minden
  Starobinsky-infláció ugyanígy jár, visszapattanással vagy anélkül.

**Energiamérleg:** a szülő tömege pontosan ρ_c · (4π/3)r_b³ (ellenőrizve). Inflációkor
~22 e-redő elég, hogy 1 M☉-ből a mai Hubble-térfogat tömege (9e52 kg) legyen.

### WP2 — anizotrópia (`anisotropy.py`)

**Új elem: a fekete-lyuk kezdeti nyírása.** A Schwarzschild-belső vákuum Kantowski–Sachs-tér:
- A nyírás itt σ² = 3m/r³.
- Ha a visszapattanó gömb ezt örökli, akkor ρ_σ = ρ_c/4, vagyis **Ω_σ = 0.2 minden tömegre**.
- Ez felső becslés: a homogén Oppenheimer–Snyder-gömb pontosan izotróp.
- A 0.2 belül van az LQC-korláton (σ² ≤ 11.57 → Ω_σ ≤ 0.56).

**Eredmény:**
- A nyírás rövidíti az inflációt (Linsefors–Barrau-hatás). Például φ_B = −1.30-nál
  117 e-redő helyett csak 38 lesz.
- A Starobinsky-küszöb −1.46-ról −1.19-re tolódik.
- φ²-nél a kudarc-hányad 5.6e-6-ról csak 6.2e-6-ra nő.
- Ha a 60 e-redő megvan, (σ/H)₀ ≤ 10⁻¹¹³, ≪ 4.7e-11: **nem mérhető**.

### WP3 + WP3b — görbület és a bébiuniverzum széle (`curvature.py`)

**Geometria:** a nyugalomból (R0-ról) induló porgömb zárt Friedmann-darab, sin²χ0 = r_s/R0.
- Görbületi sugár a visszapattanáskor: r_b√(R0/r_s).
- Ma: Ω_K = −(R_H / R_c,0)².

**WP3:** a horizont-problémát *épp* megoldó inflációval is legfeljebb |Ω_K| = 2.4e-5.
Ez a legrosszabb eset: 5e11 kg-os szülő, R0 = r_s. **Nem mérhető** (a határ 1e-3).

**WP3b, az új eredmény:**
- A bébiuniverzum széle a részecskehorizontunkon (14.26 Gpc) túl van, ha N_tot > N_min(M).
- N_min 95.1 (5e22 M☉) és 126.8 (5e11 kg) között van.
- A horizont-problémát épp megoldó infláció N_tot = 130.9-et ad, **minden** szülőtömegre
  legalább 4.2 e-redő ráhagyással.
- Ez a ráhagyás független a felmelegedési hőmérséklettől (N_post kiesik).
- **Vagyis: ha az infláció megoldja a horizont-problémát, a szél automatikusan láthatatlan.**

**Analitikus mellékeredmény:** a széle-minimumon Ω_K = −0.097 · r_s/R0.
- A görbület és a szél ugyanabból a geometriából jön.
- Egy nyugalomból induló, valódi csillagra (R0/r_s ~ 1e5) ez ~1e-6: a görbület mindig kicsi.

### WP4 — a szülő forgása (`rotation.py`)

**Becslés:**
- ω_B = J/I = 2.5 a* m/r_b².
- Hígulás: a por perdületével ω ∝ a⁻². Felső becslésként a sugárzás is hordozhatja.

**Modell-korlát (nem várt eredmény):** a homogén visszapattanás csak **a* ≲ 1e-7…1e-21**
spinnel fér össze (5e11 kg … 5e22 M☉). Nagyobb spinnél a forgás már jóval r_b előtt
dominál, és megállítja az összeomlást. Két független feltétel ad ilyen értéket:
- ω_B < H_max,
- a centrifugális gát r_b alatt van.

Valódi fekete lyukak spinje a* ~ 0.1–0.998. **Egy forgó szülőt ez a modell tehát nem ír le.**
Ez nyitott probléma, nem cáfolat: a Kerr-belső LQC-visszapattanása kutatási téma.

**Az érvényességi tartományban:** (ω/H)₀ ≤ 10⁻²⁸ ≪ 7.6e-10, ezért semleges.

**Javított hiba:** az első futás pontozása tévesen a formális a* = 0.9 sort használta (10^−6.8),
ami a modellen kívüli extrapoláció. Javítva, és a formális szám a JSON-ban továbbra is közölve.

### WP5 — CMB (`cmb.py`)

**Validáció:** a CAMB a Planck 2018 best-fit elméleti spektrumát ℓ = 2–2500-on max. 0.28%-kal
reprodukálja (cél: < 1%).

**Módszer:**
- Exponenciális levágás a primordiális spektrumban, λ = 3.35.
- 61 pontos k_c-rács.
- Alacsony-ℓ Wishart-likelihood (ℓ = 2–29, f_sky = 0.86).
- Mellette S₁/₂ számítás.

**Eredmény:**
- A legjobb k_c = 2.8e-4/Mpc, ami **N_tot = 141.2**-nek felel meg (Zhu et al. 2017: 141).
- A javulás Δχ² = −1.2. Ez **nem szignifikáns**; a küszöböt −9-re rögzítettük a futás előtt.
- S₁/₂ 34 290 → 12 318 μK⁴ (a Planck teljes-égbolt spektrumából: 6 777).
- 95%-os alsó korlát: N_tot > 140.8. Ez összhangban van a WP3b-vel.
- A levágás bármely LQC-visszapattanásra igaz, **nem fekete-lyuk-specifikus**.

### WP6 — természetes szelekció (`cns.py`)

- P(mind a négy mért neutroncsillag < 2 M☉) = 7.8e-4, azaz **3.2σ**.
- A két legnehezebb (J0740, J0952): 0.0025.
- Smolin 1.5 és 1.6 M☉-es korábbi jóslata > 16σ-val kizárt.

A természetes szelekció a publikált formájában cáfolt. **A fekete-lyuk-eredetet ez nem cáfolja**:
az nem igényli a szelekciót.

## Amit a kód NEM csinál (ismert korlátok)

- **WP2:** Bianchi-I merev-folyadék közelítés, nem teljes Kantowski–Sachs LQC.
- **WP3b:** a szél átmeneti tartománya (LMY-külső ↔ Friedmann-belső) nincs modellezve.
  A homogén gömb csak Oppenheimer–Snyder-re pontos.
- **WP4:** forgó szülőre a modell nem érvényes (lásd fent).
- **WP5:**
  - Fenomenologikus levágás, nem a Guillén et al. 2026-féle analitikus LQC-spektrum.
  - A ΛCDM-paraméterek rögzítettek.
  - Nincs MCMC; az a Ryzenre való.
- **Mérték-probléma:** Starobinskynél a φ_B-tér nem kompakt, ezért valószínűség helyett küszöböt adunk.

## Napló

- **2026-09-29:**
  - A `thesis/` csomag, WP0–WP6 és a pontozólap elkészült.
  - Első teljes futás: `runs/thesis-2026-09-29/`.
  - Javítások közben:
    - H a kényszerből, instabilitás;
    - A_s képlet;
    - potenciál-dominált visszapattanás plafon-eseménye;
    - a WP4 pontozása.
