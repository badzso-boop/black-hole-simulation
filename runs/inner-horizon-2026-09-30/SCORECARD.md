# Belső horizont (S4, Level 1) — pontozólap (2026-09-30)

Előre rögzített kritériumok: `docs/inner-horizon-plan.md` §5 (2026-09-30); a számszerű részletek a `thesis/verdict.py` belső-horizont szakaszában.

| Kérdés | Eredmény | Várt (§5) | Indoklás |
|---|---|---|---|
| L1b validation gate | **passed** | — | A fizikai ítéletek csak akkor számítanak, ha a kód minden ellenőrzésen átment. |
| L1a star's own bounce vs inner horizon | **supports** | supports | A csillag saját anyaga a nem forgó (LMYZ) modell belső horizontját átlépve legfeljebb 0.69 e-redőnyi tömeg-infláció idején belül visszapattan (tömegfüggetlenül ≈ ln 2), és a külső r₋-tartomány csak a felszín áthaladása után létezik: a visszapattanás megelőzi az instabilitást. Maga az LMYZ belső horizont instabil (Ori-modell: a tömeg a héj előjelétől függően −∞-be fut vagy a beépített görbületi plafont éri el) — ez a visszapattant labda SZÉLÉT érinti; a szél zavara csillag-tömegnél a labda 10⁻⁹-éig hatol, de Planck-tömegű magnál (WP4b) az egészig. |
| L1c the spark crosses r_- | **open (mixed)** | open (depends on spin) | A szikra (a csillag tengely-menti magja) akkor jut át, ha legalább 10×-rel a belső horizont Planck-görbületűvé válása előtt lép át, és a torzulás D = M/r₋ ≤ 10. GW (GWTC-4, Beta fit): 22%, natal (theory): 0%. Gyors spinnél átjut, lassúnál (születési ~0.01) nem. |
| L1d quantum vs classical | **info** | info (classical first for stellar masses) | A kvantum-fluxus csak akkor érne előbb Planck-görbületet, ha a klasszikus perturbáció amplitúdója δ kisebb a táblázatbeli küszöbnél (~(m_P/M)-szerű, csillag-tömegnél ~10⁻³⁸ körül): minden valós tömegnél a klasszikus tömeg-infláció nyer. A kvantum-tag nem lassul hatványszerűen (Ori-modell: tiszta e^{κv}), így v → ∞-ben ő dominál — de addigra a tartomány már rég Planck-görbületű. |
| L1e the asteroid | **against** | against | Egy napnál később beeső test (aszteroida, bolygó) minden spinnél olyan belső horizontot talál, amely már Planck-görbületű (klasszikusan: a Cauchy-horizont tömeg-inflációs szingularitása). Az eredeti Norbi-„táplálás” ezen az úton nem működik; hogy a kvantumgravitáció ott visszapattanást csinál-e, azt ez a számolás nem dönti el. |

## Számok

### L1b validation gate
```json
{
 "T1 static RN Q=0.5 (2nd order)": true,
 "T1 static RN Q=0.92 (2nd order)": true,
 "T1 static RN Q=0.95 (2nd order)": true,
 "T2 mass-inflation rate κ₋ (Brady–Smith e²=0.4)": true,
 "T2 rate converged (two finest grids within 5%)": true,
 "T10b semiclassical drift (ZLO eq. 15)": true,
 "Ori RN slope vs analytic": true,
 "Ori Hayward late polynomial (p+1)": true,
 "T9 Chesler r₋, κ₋ (analytic)": true
}
```
### L1a star's own bounce vs inner horizon
```json
{
 "max_efolds_between_r_minus_and_bounce": 0.6931050662616242,
 "lmyz_ori": [
  {
   "m0": 10.0,
   "shell_jump_sign": 1,
   "outcome": "M₊ → −∞ (unbounded, exponential)",
   "efolds_to_ceiling": null,
   "median_growth_over_kappa": 0.9401808857207253
  },
  {
   "m0": 10.0,
   "shell_jump_sign": -1,
   "outcome": "reaches the curvature ceiling R³/(2α)",
   "efolds_to_ceiling": 44.8601588683341,
   "median_growth_over_kappa": -3.2635939438415987e-07
  },
  {
   "m0": 1000.0,
   "shell_jump_sign": 1,
   "outcome": "M₊ → −∞ (unbounded, exponential)",
   "efolds_to_ceiling": null,
   "median_growth_over_kappa": 0.9851816956731251
  },
  {
   "m0": 1000.0,
   "shell_jump_sign": -1,
   "outcome": "reaches the curvature ceiling R³/(2α)",
   "efolds_to_ceiling": 51.73332881775257,
   "median_growth_over_kappa": -5.25933793243925e-09
  }
 ],
 "edge_confinement": {
  "eta": {
   "eta_kinetic": 4418.0665782605265,
   "eta_inflation": 5135.612677472533,
   "eta_total": 9553.67925573306
  },
  "rows": [
   {
    "label": "seed 1 m_P",
    "m_planck": 1.0,
    "r_b": 0.8354691979612149,
    "eta_over_rb": 11435.106499493679
   },
   {
    "label": "seed 100 m_P",
    "m_planck": 100.0,
    "r_b": 3.8779045000841985,
    "eta_over_rb": 2463.6190126718247
   },
   {
    "label": "PBH 5.1e11 kg",
    "m_planck": 2.3432822667332096e+19,
    "r_b": 2390774.6648727767,
    "eta_over_rb": 0.003996060103908392
   },
   {
    "label": "1 M_sun",
    "m_planck": 9.13636566457056e+37,
    "r_b": 3762890674138.955,
    "eta_over_rb": 2.538920229968994e-09
   },
   {
    "label": "Sgr A*",
    "m_planck": 3.92863723576534e+44,
    "r_b": 611896194868205.0,
    "eta_over_rb": 1.5613235277252877e-11
   }
  ],
  "m_min_for_10pct_planck": 1495273515637862.5,
  "m_min_for_10pct_kg": 32543646.311907724
 }
}
```
### L1c the spark crosses r_-
```json
{
 "fraction_pass": {
  "GW (GWTC-4, Beta fit)": 0.225,
  "natal (theory)": 0.0
 },
 "band": {
  "GW (GWTC-4, Beta fit)": [
   0.225,
   0.225
  ],
  "natal (theory)": [
   0.0,
   0.0
  ]
 },
 "window": [
  0.4398468580357399
 ],
 "fiducial": {
  "mass_kg": 1.98847e+31,
  "delta": 0.1
 }
}
```
### L1d quantum vs classical
```json
{
 "quantum_first_cases": 0,
 "cases": 20,
 "delta_thresholds": {
  "PBH 1e12 kg a=0.1": 2.819762449983908e-23,
  "PBH 1e12 kg a=0.44": 1.2084154349230328e-22,
  "PBH 1e12 kg a=0.8": 1.9560476387729706e-22,
  "PBH 1e12 kg a=0.95": 1.8502920884250407e-22,
  "PBH 5.1e11 kg a=0.1": 5.528945980360614e-23,
  "PBH 5.1e11 kg a=0.44": 2.369442029260853e-22,
  "PBH 5.1e11 kg a=0.8": 3.8353875270058315e-22,
  "PBH 5.1e11 kg a=0.95": 3.628023702794178e-22,
  "10 M_sun a=0.1": 1.4180563196748846e-42,
  "10 M_sun a=0.44": 6.077111723702286e-42,
  "10 M_sun a=0.8": 9.836948200239196e-42,
  "10 M_sun a=0.95": 9.305104368811433e-42,
  "Sgr A* a=0.1": 3.2978053945927656e-48,
  "Sgr A* a=0.44": 1.4132817962098385e-47,
  "Sgr A* a=0.8": 2.2876623721486575e-47,
  "Sgr A* a=0.95": 2.1639777601886814e-47,
  "M87* a=0.1": 2.1816251071921315e-51,
  "M87* a=0.44": 9.349402651849676e-51,
  "M87* a=0.8": 1.5133766461906464e-50,
  "M87* a=0.95": 1.4315545182786624e-50
 }
}
```
### L1e the asteroid
```json
{
 "late_cases_meeting_planckian_IH": 8.0,
 "late_cases": 8,
 "code_late_pulse": {
  "q": 0.782,
  "n": 1600,
  "v_late": 11.384891205768158,
  "ray_max_log10_m": 21.559800898403026,
  "ray_reaches_singularity": false,
  "ray_r_min": 0.3112687109656012,
  "n_rays_singular_before_v_max": 0,
  "n_rays": 1600
 }
}
```

## Az amplitúdó feloldása (felbontás-létra)

| Q | δ | n_max | jel − padló | változás az utolsó duplázáskor | feloldva | κ_fit/κ₋ |
|---|---|---|---|---|---|---|
| 0.500 | 0.05 | 3200 | 1.35 | 2.68 | False | 1.0287 |
| 0.500 | 0.1 | 3200 | 5.44 | 2.52 | False | 1.0812 |
| 0.632 | 0.05 | 3200 | 2.76 | 1.63 | False | 1.0441 |
| 0.632 | 0.1 | 3200 | 4.96 | 1.47 | False | 1.0499 |
| 0.782 | 0.05 | 3200 | inf | 1.17 | False | 0.1092 |
| 0.782 | 0.1 | 3200 | inf | 0.53 | False | 0.4098 |

Futási idők (s): {"growth/0.5/3200/0.0": 15.3, "growth/0.5/3200/0.05": 15.4, "growth/0.5/3200/0.1": 15.3, "growth/0.632455532/3200/0.0": 15.3, "growth/0.632455532/3200/0.05": 15.5, "growth/0.632455532/3200/0.1": 15.3, "growth/0.782/3200/0.0": 15.3, "growth/0.782/3200/0.05": 15.4, "growth/0.782/3200/0.1": 6.9, "growth/0.827/3200/0.0": 6.9, "growth/0.827/3200/0.05": 7.0, "growth/0.827/3200/0.1": 7.0, "growth/0.907/3200/0.0": 7.0, "growth/0.907/3200/0.05": 7.0, "growth/0.907/3200/0.1": 7.1, "growth/0.95/3200/0.0": 7.0, "growth/0.95/3200/0.05": 6.6, "growth/0.95/3200/0.1": 6.6, "growth/0.5/1600/0.0": 2.4, "growth/0.5/1600/0.05": 2.4, "growth/0.5/1600/0.1": 2.5, "growth/0.632455532/1600/0.0": 2.5, "growth/0.632455532/1600/0.05": 2.4, "growth/0.632455532/1600/0.1": 2.3, "growth/0.782/1600/0.0": 2.4, "growth/0.782/1600/0.05": 2.4, "growth/0.782/1600/0.1": 2.4, "growth/0.827/1600/0.0": 2.4, "growth/0.827/1600/0.05": 2.4, "growth/0.827/1600/0.1": 2.5, "growth/0.907/1600/0.0": 2.4, "growth/0.907/1600/0.05": 2.4, "growth/0.907/1600/0.1": 2.4, "growth/0.95/1600/0.0": 2.4, "growth/0.95/1600/0.05": 2.3, "growth/0.95/1600/0.1": 2.4, "late/0.782/1600": 2.4, "growth/0.5/800/0.0": 1.0, "growth/0.5/800/0.05": 0.9, "growth/0.5/800/0.1": 0.9, "growth/0.632455532/800/0.0": 0.9, "growth/0.632455532/800/0.05": 1.0, "growth/0.632455532/800/0.1": 0.9, "growth/0.782/800/0.0": 1.0, "growth/0.782/800/0.05": 1.0, "growth/0.782/800/0.1": 1.1, "growth/0.827/800/0.0": 1.2, "growth/0.827/800/0.05": 1.2, "growth/0.827/800/0.1": 1.2, "growth/0.907/800/0.0": 1.2, "growth/0.907/800/0.05": 1.2, "growth/0.907/800/0.1": 1.2, "growth/0.95/800/0.0": 1.2, "growth/0.95/800/0.05": 1.2, "growth/0.95/800/0.1": 1.3, "static/0.5/1600": 0.9, "static/0.92/1600": 1.0, "static/0.95/1600": 0.9, "growth/0.5/400/0.0": 0.6, "growth/0.5/400/0.05": 0.6, "growth/0.5/400/0.1": 0.5, "growth/0.632455532/400/0.0": 0.6, "growth/0.632455532/400/0.05": 0.5, "growth/0.632455532/400/0.1": 0.6, "growth/0.782/400/0.0": 0.5, "growth/0.782/400/0.05": 0.6, "growth/0.782/400/0.1": 0.5, "growth/0.827/400/0.0": 0.5, "growth/0.827/400/0.05": 0.5, "growth/0.827/400/0.1": 0.5, "growth/0.907/400/0.0": 0.5, "growth/0.907/400/0.05": 0.5, "growth/0.907/400/0.1": 0.5, "growth/0.95/400/0.0": 0.6, "growth/0.95/400/0.05": 0.6, "growth/0.95/400/0.1": 0.6, "static/0.5/800": 0.3, "static/0.92/800": 0.4, "static/0.95/800": 0.3, "static/0.5/400": 0.1, "static/0.92/400": 0.2, "static/0.95/400": 0.2, "static/0.5/200": 0.1, "static/0.92/200": 0.1, "static/0.95/200": 0.1, "l1a": 3.5}
