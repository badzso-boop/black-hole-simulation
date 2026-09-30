# Tézis-számolások — pontozólap (2026-09-30-local)

Előre rögzített kritériumok: `docs/thesis-plan.md` §0 (2026-09-28).
Küszöbök, amiket a táblázat nem adott meg számmal: `thesis/verdict.py` fejléce.

Az utolsó oszlop (A8, docs/upgrade-plan.md): megkülönbözteti-e a sor a fekete-lyuk-eredetet
egy közönséges LQC-visszapattanástól. A „nem” sorok konzisztencia-ellenőrzések, nem bizonyítékok.

| WP | Eredmény | Várt (§0) | Indoklás | BH-specifikus? |
|---|---|---|---|---|
| 1 Inflation | **mixed** | supports | A visszapattanás szinte mindig inflál (φ²: csak 5.6e-06 hányad kap < 68 e-redőt; Starobinsky: φ_B ≥ -1.46 ill. ≥ 3.62). Starobinsky n_s = 0.9653, r = 0.0034: Planck 95%-on belül, az ACT DR6-tól 2.9σ-ra. A feszültség a potenciálé (Starobinsky), nem a fekete-lyuk eredeté. FELTÉTELES: a számolás ρ_c 100%-át a skalármezőbe teszi, az összeomló csillag viszont por — a B1a szerint a por mellett a mezőnek ~99%-ot kellene vinnie; erre nincs mechanizmus (critical-review.md §3.1). Minden sor, amely a WP1 e-redőit örökli (WP2–WP5), ezt a feltételt is örökli. | no: a property of LQC + inflaton |
| 2 Anisotropy | **neutral** | neutral | A visszapattanáskori nyírás ismeretlen: 0 (a homogén Oppenheimer–Snyder-belső pontosan izotróp) és az LQC-plafon Ω_σ = 0.5625 között. A korábbi Ω_σ = 0.20 a klasszikus Kantowski–Sachs-nyírás r_b-re extrapolálva — de ott a LMYZ-metrikában f(r_b) = 1, a tartomány statikus, tehát ez nem fizikai érték (critical-review.md §3.4). Az ítélet a sáv egészén áll: a nyírás rövidíti az inflációt, de nem öli meg (a plafonon is elérhető, WP4b S3; Ω_σ = 0.20-nél a Starobinsky-küszöb -1.19), és ma (σ/H)₀ ≤ 10^-113 ≪ 4.7e-11 — nem mérhető. | partly: the initial shear is BH-specific, but inflation erases it |
| 3 Curvature | **neutral** | neutral | A zárt (kötött) szülőből jövő görbület a horizont-problémát épp megoldó inflációval is legfeljebb |Ω_K| = 2.4e-05 — ezerszer a mérhető alatt. | partly: closedness is BH-specific, but unmeasurably small |
| 3b Edge beyond horizon | **consistency check: passes** | supports | Minden szülőtömegre (5e11 kg … 5e22 M☉) a bébiuniverzum széle a horizontunkon túl van, ha N_tot > 126.8; ezt már a horizont-problémát megoldó infláció is biztosítja (legalább 4.2 e-redő ráhagyással). Ez szinte automatikus (r_b ≫ 1/H a visszapattanáskor), tehát konzisztencia-feltétel, nem bizonyíték. A régi szabály szerint „supports” — de annak „természetes 130–145” sávja a Linsefors–Barrau-féle inflációs e-redőt olvasta N_tot-nak. | no: automatic once inflation solves the horizon problem |
| 4 Parent spin | **neutral (model limit)** | neutral | A modell érvényességi tartományában (a* ≤ a*_max) (ω/H)₀ ≤ 10^-28 ≪ 7.6e-10: nincs mérhető tengely. DE: a homogén visszapattanás csak a* ≲ 9e-08 spinnel fér össze (a legkisebb, 5e11 kg-os szülőnél; nagyobbaknál még kisebb) — valódi fekete lyukak a* ~ 0.1–0.998. A forgó szülő tehát NEM írható le ezzel a modellel: ez nyitott modell-korlát, nem cáfolat és nem megerősítés. | yes: only a BH parent spins |
| 5 CMB imprint | **neutral** | neutral | A legjobb levágás k_c = 2.8e-04/Mpc (N_tot = 141.2) Δχ² = -1.2-et javít — nem szignifikáns (küszöb −9). S₁/₂ 34290 → 12318 μK⁴ (adat, teljes égbolt: 6777). A CMB szerint N_tot > 140.8 (95%), összhangban a WP3b-vel. Ez bármely LQC-visszapattanásra igaz, nem fekete-lyuk-specifikus. | no: any LQC bounce |
| 6 Natural selection | **against** | against | P(minden mért neutroncsillag < 2 M☉) = 9.3e-05 (3.7σ, a 2025-ös tömegekkel): Smolin kozmológiai természetes szelekciója a M_max < 2 M☉ olvasatban erős feszültségben van. DE az eredményt szinte egyedül a PSR_J0952-0607 viszi: nélküle 1.1σ (a tömege a fűtött kísérő fénygörbe-modelljéből jön). Smolin 2012 „~2.4 M☉ már ellentmondana” olvasatában nincs feszültség (-0.5σ). „Cáfolt” helyett: feszültség. A fekete-lyuk-eredetet ez NEM cáfolja — csak egy javasolt tesztjét. | yes: tests Smolin's extension |

## Számok

### 1 Inflation
```json
{
 "phi2_fraction_fail": 5.559236409336363e-06,
 "starobinsky_threshold_plus_N60": -1.4601074218749999,
 "starobinsky_threshold_minus_N60": 3.6207336425781254,
 "n_s": 0.9653358289488297,
 "r": 0.0034287370663584507,
 "N_star": 55.58371011437709,
 "inside_planck_95": true,
 "inside_act_95": false,
 "act_sigma": -2.8880570170567443
}
```
### 2 Anisotropy
```json
{
 "omega_sigma_band": [
  0.0,
  0.5625
 ],
 "omega_sigma_classical_extrapolation": 0.19999999999999998,
 "starobinsky_threshold_plus_N60_at_extrapolation": -1.1915512084960938,
 "starobinsky_threshold_minus_N60_at_extrapolation": 3.352693176269531,
 "phi2_fraction_fail_at_extrapolation": 6.218497103035376e-06,
 "max_log10_shear_today_with_60_efolds": -113.22595498041223,
 "limit_log10": -10.33
}
```
### 3 Curvature
```json
{
 "max_abs_omega_k_minimal_inflation": 2.4086641989708335e-05,
 "desi": [
  0.0023,
  0.0011
 ]
}
```
### 3b Edge beyond horizon
```json
{
 "max_n_tot_min_edge": 126.7720955065631,
 "n_tot_references": {
  "zhu2017_lower_95": 141.0,
  "lb2013_n_infl_peak": 145.0,
  "lb2013_implied_n_tot": [
   214.93583051740143,
   228.61728169138536
  ]
 },
 "n_tot_minimal_inflation": 130.92519672354544,
 "min_margin_efolds": 4.153101216982336,
 "old_rule_outcome": "supports"
}
```
### 4 Parent spin
```json
{
 "max_log10_omega_over_h_today_valid": -27.538523352814785,
 "max_log10_omega_over_h_today_formal_a0.9_invalid": -6.7768765659113495,
 "largest_a_star_max": 9.034456122678962e-08,
 "limit_log10": -9.119186407719209,
 "model_valid_for_real_spins": false
}
```
### 5 CMB imprint
```json
{
 "best_k_c_mpc": 0.0002786040328192925,
 "best_n_tot": 141.24525126491068,
 "dchi2": -1.1948768362394873,
 "n_tot_lower_95": 140.76993605868932,
 "S_half_lcdm": 34290.16799109282,
 "S_half_best": 12318.16763553142,
 "S_half_data_fullsky": 6776.845128294178
}
```
### 6 Natural selection
```json
{
 "p_all_below_2Msun": 9.26044505258455e-05,
 "sigma": 3.7383813006645257,
 "leave_one_out_min_sigma": {
  "PSR_J0952-0607": 1.1428575745488128
 },
 "smolin_2_4_reading_sigma": -0.45454090861094704
}
```

## WP4b — a forgó szülő (docs/spin-plan.md §6)

| Kérdés | Eredmény | Várt (§6) | Indoklás | BH-specifikus? |
|---|---|---|---|---|
| S1+S2 observed spins | **supports** | supports | Reális (n = 3) magprofillal C = 1.23: minden megfigyelt populáció zöme belefér N_tot ≤ 145-be, a GW-populáció 100%-a már N_tot ≤ 142-nél. A tömegrés-korlát a* ≤ 1.19 — de a mag a* = 0.9-nél csak 1.9 m_P: Planck-méretű, ahol az effektív LQC a határán van. Legpesszimistább profillal (C = 0.45) a gyorsan forgó (röntgen, SMBH) populációk kiesnek. FIGYELEM: a 145-ös plafon téves bemenet (Linsefors–Barrau inflációs e-redője; N_tot-ként ≈ 215 lenne), és a szél-bezártság (S7) ezt a sort felülírja. | yes |
| S3 axial core inflates | **supports** | open | Klasszikusan bármely σ/H > 10⁻¹⁴…10⁻⁴⁸ kezdeti anizotrópia ρ_c-ig telíti az LQC nyírás-korlátot, ezért a legrosszabb esetet (σ² = 11.57, Ω_σ = 0.5625) számoltuk: az infláció így is elérhető (Starobinsky φ̇ > 0: φ_B ≥ -0.60; φ²: kudarc 8.4e-06). A merev-folyadék közelítés itt a határán van. | partly |
| S4 crossing r_- | **open** | open | Gyors spinnél (a* ≥ 0.9) a tengely-mag ~50–140-szer hamarabb lépi át r₋-t, mint ahogy a tömeg-infláció Planck-görbületet ér el, és a torzulás O(1) (1.3–1.8). Lassú spinnél (a* ~ 0.01) r₋ apró, a Planck-görbület előbb alakul ki (D ~ 2·10⁴); a GW-medián (0.26) határeset. Rendkívül durva becslés: a forgó összeomlás kvantumos számolása hiányzik az irodalomból. | yes |
| S5 rotation today | **neutral** | neutral | (ω/H)₀ ≤ 10^-28 ≪ 7.6e-10 — nincs mérhető forgás, tengely sem. | yes |
| CMB consistency | **supports** | supports | Ha az alacsony-ℓ hiány a visszapattanás (N_tot = 141.2), a szülő spinje a* ≲ 0.76 (fiduciális C) — ez a GW-populáció 98%-ára igaz. Gyorsabb szülőnél a nyom ℓ ≲ 2-n van, láthatatlan. | no |
| S6 torsion (info) | **info** | — | Popławski-torzió (ρ ≈ 237 ρ_Pl): ugyanahhoz a spinhez 3.2 e-redővel több kell, és a tömegrés-szerű korlát (1 m_P) a* ≤ 0.39: a torzió rosszabb, nem jobb. | n/a |
| S7 edge confinement (B3a) | **against (unless the disturbance amplitude is ≪ 1, B3b)** | against (estimated in critical-review §4.1) | A labda szélén keletkező zavar a visszapattanástól az infláció végéig η ≈ 9.6e+03 ℓ_P-ig hatol befelé. A mag csak akkor maradhat érintetlen, ha nagyobb ennél: M_s ≳ 3e+04 kg, ami a WP4b magtömeg-korlátjával a* ≲ 9.8e-05 spint enged (ε = 0.1-gyel 9.8e-06). Egyetlen megfigyelt populáció sem fér bele: a spin-út csak akkor él, ha a zavar amplitúdója ≪ 1 (B3b, még nincs számolva). | yes |

### WP4b számok

#### S1+S2 observed spins
```json
{
 "C_fiducial": 1.225554059774758,
 "C_range": [
  0.4468098289663603,
  3.3918529853756976
 ],
 "a_star_gap_fiducial": 1.1913373853445162,
 "a_star_semiclassical_10mP_fiducial": 0.5199533265837288,
 "seed_mass_max_a0.9_mP": 1.9282598343338169,
 "fraction_allowed_N145_fiducial": {
  "GW (GWTC-4, Beta fit)": 1.0,
  "X-ray binaries (continuum fitting)": 1.0,
  "X-ray binaries (reflection, 36)": 1.0,
  "SMBH (reflection)": 1.0
 },
 "fraction_allowed_N145_pessimistic_C": {
  "GW (GWTC-4, Beta fit)": 0.77,
  "X-ray binaries (continuum fitting)": 0.3333333333333333,
  "X-ray binaries (reflection, 36)": 0.0,
  "SMBH (reflection)": 0.0
 },
 "gw_fraction_allowed_N142": 1.0
}
```
#### S3 axial core inflates
```json
{
 "omega_sigma": 0.5624999994375001,
 "thresholds_N60": {
  "plus_N60": -0.599090576171875,
  "minus_N60": 2.761077880859375
 },
 "phi2_fraction_fail": 8.41649745809112e-06,
 "saturating_sigma_over_h": [
  8.358381534184881e-37,
  2.4368459283337854e-39,
  2.6664055680559162e-45,
  1.7639298373292983e-48,
  3.2589001822118845e-14
 ]
}
```
#### S4 crossing r_-
```json
{
 "PBH 5.1e11 kg": {
  "a": 0.01,
  "v_planck_over_m": [
   0.006410092892395335,
   0.010555056934678522
  ],
  "planck_first": true,
  "D": 19999.499987503958
 },
 "10 M_sun natal": {
  "a": 0.01,
  "v_planck_over_m": [
   0.015432734959980566,
   0.019577699002263752
  ],
  "planck_first": true,
  "D": 19999.499987503958
 },
 "10 M_sun GW median": {
  "a": 0.2561138904629572,
  "v_planck_over_m": [
   11.995348658043605,
   14.855509086658197
  ],
  "planck_first": false,
  "D": 29.98196287120077
 },
 "10 M_sun XRB": {
  "a": 0.97,
  "v_planck_over_m": [
   1140.7094926621555,
   1398.79292966774
  ],
  "planck_first": false,
  "D": 1.3211870715515617
 },
 "Sgr A*": {
  "a": 0.9,
  "v_planck_over_m": [
   539.0209992892715,
   646.2976655485979
  ],
  "planck_first": false,
  "D": 1.7727035732766259
 },
 "M87*": {
  "a": 0.9,
  "v_planck_over_m": [
   576.9188047938583,
   684.1954710531849
  ],
  "planck_first": false,
  "D": 1.7727035732766259
 }
}
```
#### S5 rotation today
```json
{
 "max_log10_omega_over_h_today": -27.538352480914305,
 "n_infl_used": 60.989169482598555
}
```
#### CMB consistency
```json
{
 "n_best": 141.24525126491068,
 "a_star_max_at_best_fiducial": 0.7556160497625405,
 "gw_fraction_allowed_at_best": 0.985
}
```
#### S6 torsion (info)
```json
{
 "rho_torsion_over_rho_pl": 237.42988002237814,
 "extra_efolds_vs_lqc": 3.1814994507566507,
 "a_star_gap_fiducial": 0.38790776736560606,
 "n_needed_a0.9_fiducial": 144.60161210250658,
 "n_needed_a0.9_lqc_fiducial": 141.42011265174992
}
```
#### S7 edge confinement (B3a)
```json
{
 "eta_lP": 9553.679255733066,
 "a_star_max_eps1": 9.796196336597848e-05,
 "a_star_max_eps0.1": 9.796196336597849e-06,
 "m_conf_kg_eps1": 32543.646311907803,
 "fraction_allowed_eps1": {
  "GW (GWTC-4, Beta fit)": 0.0,
  "X-ray binaries (continuum fitting)": 0.0,
  "X-ray binaries (reflection, 36)": 0.0,
  "SMBH (reflection)": 0.0
 }
}
```

## Kiegészítések: WP1b, WP5b, B1a

A WP1b és a WP5b nem előre rögzített; a WP1/WP5 ítéletét nem írják felül, a WP5b a WP5 szabályát (Δχ² < −9) alkalmazza. A B1a előre rögzítve: docs/upgrade-plan.md.

| Kérdés | Eredmény | Indoklás | BH-specifikus? |
|---|---|---|---|
| 1b ACT-compatible potential | **supports** | Polinomiális α-attraktorral (k = 2, μ = 0.2 m_Pl) n_s = 0.9722, r = 0.0036: Planck-tól 1.7σ, ACT-tól 0.6σ — mindkettő 95%-án belül. A visszapattanás a φ_B ∈ [[-3.45, -1.64]] sávon kívül mindig ≥ 60 e-redőt ad. Az ACT-feszültség tehát a potenciálé volt. | no: a property of the potential |
| 5b CMB with hybrid LQC spectrum | **neutral** | A Guillén et al. 2026-féle hibrid LQC-spektrummal (saját Wishart (a Planck-likelihoodok nincsenek telepítve)) a legjobb N_tot = 141.00, Δχ² = -0.59 — nem szignifikáns (küszöb −9). a saját csővezeték ugyanitt -0.59-t ad, S₁/₂ = 19439 μK⁴. A magas ℓ nem változik (plik-lite Δχ² ≈ 0). | no: any LQC bounce (vacuum initial state) |
| B1a inflaton origin (dust + field) | **against** | Ha a mező a vákuum-minimumában indul (φ_B = 0) a csillag pora mellett, ≥ 60 e-redőhöz Starobinskynél a ρ_c legalább 98.95%-át a mezőnek kell vinnie (a por legfeljebb ~1%), φ²-nél még 100% sem elég. A mező energiája az összeomlásban a porhoz képest ρ_c/ρ_freeze ≈ 5.4e+11-szeresére nő, így ehhez a H = m pillanatban a por energiájának 1.7e-10-ét kellene koherens, homogén inflaton-sebességként hordoznia — a csillag anyagában ilyen mechanizmus nincs (B1b). A WP1 „szinte biztos infláció”-ja tehát a fekete-lyuk belsejére nem vihető át. | yes: asks whether a BH interior can supply the inflaton |
#### 1b ACT-compatible potential
```json
{
 "potential": "poly-attractor-k2",
 "mu": 0.2,
 "n_s": 0.9722466158260569,
 "r": 0.003567236690219819,
 "N_star": 55.481688889407316,
 "planck_sigma": 1.7491942442992596,
 "act_sigma": -0.5844613913143689,
 "fail_bands_N60": [
  [
   -3.450295138358906,
   -1.6356827497480402
  ]
 ]
}
```
#### 5b CMB with hybrid LQC spectrum
```json
{
 "likelihood": "saját Wishart (a Planck-likelihoodok nincsenek telepítve)",
 "best_n_tot": 141.0,
 "dchi2": -0.594404933323073,
 "n_tot_lower_95": null,
 "full_likelihood_check": null,
 "own_pipeline_best": {
  "n_tot": 141.0,
  "dchi2_wishart": -0.594404933323073,
  "S_half": 19438.97983040531,
  "D2": 779.1088871740421
 }
}
```
#### B1a inflaton origin (dust + field)
```json
{
 "f_field_min": {
  "Starobinsky": 0.9895178845873218,
  "phi2": null
 },
 "r_freeze_required": {
  "Starobinsky": 1.7341373297259812e-10,
  "phi2": null
 },
 "amplification": {
  "Starobinsky": 544366290236.7798,
  "phi2": 2342437036487.082
 },
 "validation_pure_dust_inflated": false
}
```

## Validáció

- CAMB vs Planck minimum-theory (ℓ 2–2500): max eltérés 0.28%
- φ² kudarc-sáv (φ̇_B > 0): [[-5.5006144762037845, 1.0295583963396444]] (Ashtekar–Sloan: [−5.5, 0.94])
- Bonga–Gupt küszöbök (60 e-redő): -1.460 / 3.621 (cikk: −1.45 / 3.63)

Futási idők (s): {"wp5b": 21.1, "wp1": 25.9, "wp5": 76.6, "wp2": 16.8, "wp4b_s3": 16.2, "wp1b": 17.0, "wp6": 0.3, "b1a": 1.3, "wp3_wp4": 0.0005475200000546465, "wp4b": 0.1, "total": 77.5}
