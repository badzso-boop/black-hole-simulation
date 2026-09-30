# WP5c — teljes Planck-MCMC a hibrid LQC-spektrummal (2026-09-30)

Likelihoodok: Planck 2018 alacsony-ℓ TT (Gibbs) és EE, plik-lite TT/TE/EE. Konfiguráció: `scripts/cobaya/*.yaml`.

- LQC-lánc: 53152 sor (burn-in 30%), R−1 = 0.00834
- **N_tot > 140.71 (95%)**, > 140.27 (99%); a felső határ priorfüggő
- Δχ²_min (LQC − ΛCDM, minimize) = -0.23 → nem szignifikáns (küszöb -9.0)

## Következmények

- WP3b: a szél minden szülőtömegre a horizonton túl? igen (kell: N_tot > 126.8)
- WP4b: a spin-ablak felső széle a 95%-os alsó N_tot-nál (fiduciális C): a* ≤ 0.44; a* = 0.9-hez N_tot ≥ 141.42 kell

## Paraméterek (LQC-lánc)

| paraméter | átlag | szórás |
|---|---|---|
| n_tot | 145 | 2.9 |
| logA | 3.0452 | 0.0164 |
| ns | 0.96508 | 0.00442 |
| tau | 0.054694 | 0.00804 |
| ombh2 | 0.022361 | 0.00015 |
| omch2 | 0.12016 | 0.00137 |
| H0 | 67.281 | 0.611 |

## Megjegyzés (utólag hozzáadva, 2026-09-30 — a fenti szöveg a szkript változatlan kimenete)

- **Az n_tot „átlaga" (145 ± 2.9) priorfüggő, nem mérés:** a poszterior ~142 fölött lapos a
  prior 150-es széléig (lásd `n_tot.png`). Csak az alsó korlát értelmes: N_tot > 140.71 (95%).
  A szkript ezt a jövőben jelzi.
- **A csővezeték validálása:** a ΛCDM-lánc a Planck 2018 VI Table 2 (TT,TE,EE+lowE) mind a hat
  paraméterét 0.06σ-n belül reprodukálja (Ω_b h², Ω_c h², H0, n_s, τ, ln 10¹⁰A_s).
- **Δχ²_min = −0.23 bizonytalansága:** a minimalizáló négy indításának szórása a ΛCDM-nél
  Δχ² ≈ 1.4, az LQC-nél ≈ 0.9 (`runs/mcmc/*_bestfit.log`, „Modest spread in minima"), tehát
  Δχ² = −0.2 ± ~1: a nullával összefér. Likelihoodonként: alacsony-ℓ TT −0.51, EE +0.05,
  plik-lite +0.24.
