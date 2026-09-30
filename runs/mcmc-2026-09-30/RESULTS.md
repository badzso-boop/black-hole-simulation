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
