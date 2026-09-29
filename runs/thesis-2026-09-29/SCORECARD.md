# Tézis-számolások — pontozólap (2026-09-29)

Előre rögzített kritériumok: `docs/thesis-plan.md` §0 (2026-09-28).
Küszöbök, amiket a táblázat nem adott meg számmal: `thesis/verdict.py` fejléce.

| WP | Eredmény | Várt (§0) | Indoklás |
|---|---|---|---|
| 1 Inflation | **mixed** | supports | A visszapattanás szinte mindig inflál (φ²: csak 5.6e-06 hányad kap < 68 e-redőt; Starobinsky: φ_B ≥ -1.46 ill. ≥ 3.62). Starobinsky n_s = 0.9653, r = 0.0034: Planck 95%-on belül, az ACT DR6-tól 2.9σ-ra. A feszültség a potenciálé (Starobinsky), nem a fekete-lyuk eredeté. |
| 2 Anisotropy | **neutral** | neutral | A fekete lyuk belsejéből örökölt nyírás (Ω_σ = 0.20) rövidíti az inflációt (Linsefors–Barrau), de nem öli meg: a Starobinsky-küszöb -1.19-re tolódik; φ²-nél a kudarc 6.2e-06. Ma (σ/H)₀ ≤ 10^-113 ≪ 4.7e-11: a nyírás nyomtalanul eltűnik — nem mérhető. |
| 3 Curvature | **neutral** | neutral | A zárt (kötött) szülőből jövő görbület a horizont-problémát épp megoldó inflációval is legfeljebb |Ω_K| = 2.4e-05 — ezerszer a mérhető alatt. |
| 3b Edge beyond horizon | **supports** | supports | Minden szülőtömegre (5e11 kg … 5e22 M☉) a bébiuniverzum széle a horizontunkon túl van, ha N_tot > 126.8; ezt már a horizont-problémát megoldó infláció is biztosítja (legalább 4.2 e-redő ráhagyással), és az LQC természetes 130–145-je is. |
| 4 Parent spin | **neutral (model limit)** | neutral | A modell érvényességi tartományában (a* ≤ a*_max) (ω/H)₀ ≤ 10^-28 ≪ 7.6e-10: nincs mérhető tengely. DE: a homogén visszapattanás csak a* ≲ 9e-08 spinnel fér össze (a legkisebb, 5e11 kg-os szülőnél; nagyobbaknál még kisebb) — valódi fekete lyukak a* ~ 0.1–0.998. A forgó szülő tehát NEM írható le ezzel a modellel: ez nyitott modell-korlát, nem cáfolat és nem megerősítés. |
| 5 CMB imprint | **neutral** | neutral | A legjobb levágás k_c = 2.8e-04/Mpc (N_tot = 141.2) Δχ² = -1.2-et javít — nem szignifikáns (küszöb −9). S₁/₂ 34290 → 12318 μK⁴ (adat, teljes égbolt: 6777). A CMB szerint N_tot > 140.8 (95%), összhangban a WP3b-vel. Ez bármely LQC-visszapattanásra igaz, nem fekete-lyuk-specifikus. |
| 6 Natural selection | **against** | against | P(minden mért neutroncsillag < 2 M☉) = 7.8e-04 (3.2σ): Smolin kozmológiai természetes szelekciója a publikált formájában cáfolt. A fekete-lyuk-eredetet ez NEM cáfolja — csak egy javasolt tesztjét. |

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
 "omega_sigma_bh": 0.19999999999999998,
 "starobinsky_threshold_plus_N60_bh_shear": -1.1915512084960938,
 "starobinsky_threshold_minus_N60_bh_shear": 3.352693176269531,
 "phi2_fraction_fail_bh_shear": 6.218497103035376e-06,
 "max_log10_shear_today_with_60_efolds": -113.22595498041224,
 "limit_log10": -10.33
}
```
### 3 Curvature
```json
{
 "max_abs_omega_k_minimal_inflation": 2.4086641989706966e-05,
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
 "lqc_natural_n_tot": [
  130.0,
  145.0
 ],
 "n_tot_minimal_inflation": 130.92519672354547,
 "min_margin_efolds": 4.15310121698235
}
```
### 4 Parent spin
```json
{
 "max_log10_omega_over_h_today_valid": -27.5385233528148,
 "max_log10_omega_over_h_today_formal_a0.9_invalid": -6.776876565911362,
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
 "dchi2": -1.1948768362393878,
 "n_tot_lower_95": 140.76993605868932,
 "S_half_lcdm": 34290.1679910909,
 "S_half_best": 12318.167635531165,
 "S_half_data_fullsky": 6776.845128294178
}
```
### 6 Natural selection
```json
{
 "p_all_below_2Msun": 0.000775888513722981,
 "sigma": 3.1648222796209273
}
```

## Validáció

- CAMB vs Planck minimum-theory (ℓ 2–2500): max eltérés 0.28%
- φ² kudarc-sáv (φ̇_B > 0): [[-5.5006144762037845, 1.0295583963396444]] (Ashtekar–Sloan: [−5.5, 0.94])
- Bonga–Gupt küszöbök (60 e-redő): -1.460 / 3.621 (cikk: −1.45 / 3.63)

Futási idők (s): {"wp1": 64.7, "wp2": 43.5, "wp5": 97.0, "wp6": 1.1, "wp3_wp4": 0.00044753000111086294, "total": 97.5}
