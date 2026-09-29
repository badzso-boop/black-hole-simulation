# Thesis calculations: work log and results

**What this is:** the six calculations of [thesis-plan.md](thesis-plan.md) (WP0–WP6)
turned into code, run, and scored against the criteria **fixed in advance** in its §0.
This is not the thesis text. It records what we compute, how, and what came out.

**Status (2026-09-29):** every WP is coded, tested and run.
The scorecard is in [`runs/thesis-2026-09-29/SCORECARD.md`](../runs/thesis-2026-09-29/SCORECARD.md).

## How to run

```bash
pip install -e '.[dev,thesis]'          # camb, getdist, matplotlib
python scripts/run_thesis.py            # → runs/thesis-<date>/  (~100 s on the i5)
python -m pytest thesis/tests -q        # 15 tests, ~15 s
```

## Scorecard

| WP | Question | Result | Expected in §0 |
|---|---|---|---|
| 1 | Does the bounce give enough inflation, with the right (n_s, r)? | **mixed** | supports |
| 2 | Does the black-hole interior's anisotropy survive? | **neutral** | neutral |
| 3 | What spatial curvature does a closed parent predict? | **neutral** | neutral |
| 3b | Is the baby universe's edge beyond our horizon? (new calculation) | **supports** | supports |
| 4 | Does the parent's spin leave an axis? | **neutral + model limit** | neutral |
| 5 | Does the bounce show up at low ℓ in the CMB? | **neutral** | neutral |
| 6 | Smolin's natural selection vs neutron stars | **against (falsified)** | against |

Five of the six WPs gave exactly the outcome expected in advance. The two surprises are
WP1's ACT tension and WP4's model limit; both are explained below.

## What the code computes, by WP

All code is in the `thesis/` package, in Planck units (G = ħ = c = 1).
Integration uses scipy's DOP853 with rtol 1e-10.

### WP0: foundations (`units.py`, `lqc.py`, `history.py`)

- **Effective LQC:** H² = (8π/3)ρ(1 − ρ/ρ_c) with ρ_c = 0.4094. It includes the dust bounce and
  r_b(M) from LMY 2023.
- **Cross-check against the Rust core:** r_b and H_max agree to 1e-15 (`test_matches_rust_core`).
- **Expansion after inflation:** reheating with w = 0, then entropy conservation, and z_eq = 3402.

### WP1: inflation after the bounce (`inflation.py`, `wp1.py`)

**Model.** A scalar field through the bounce:
- Ḣ = −4π(ρ+P)(1−2ρ/ρ_c)
- φ̈ + 3Hφ̇ + V′ = 0

**Integration** has two stages.
1. Cosmic time is the variable until the end of super-inflation (Ḣ = 0).
2. After that, e-folds are the variable, and H comes from the Friedmann constraint rather
   than the Raychaudhuri equation.

The Raychaudhuri equation is unstable here (δH/H ∝ e^{6N}). In the first version it produced
spurious results that all sat at the 166-e-fold cap. The constraint error is now ~1e-11.

**Literature reproduced:**

| | ours | paper |
|---|---|---|
| Starobinsky threshold, φ̇_B > 0 (60 e-folds) | φ_B ≥ −1.460 | −1.45 (Bonga–Gupt 2016) |
| Starobinsky threshold, φ̇_B < 0 | φ_B ≥ 3.621 | 3.63 |
| φ² failing band (< 68 e-folds) | φ_B ∈ [−5.50, 1.03] | [−5.5, 0.94] (Ashtekar–Sloan 2011) |
| φ² failing fraction | 4.4e-6 (uniform) / 5.6e-6 (Liouville) | "< 3e-6" |

About the φ² fraction: Ashtekar–Sloan's own Eq. 4.26, applied to their [−5.5, 0.94] band, gives
≈ 5.5e-6, not the 2.74e-6 they quote. The factor of two is in the paper; our Liouville value
agrees with their formula.

**(n_s, r).** N* is computed self-consistently from the reheating temperature (k* = 0.05/Mpc):

| T_reh | N* | n_s | r |
|---|---|---|---|
| instant (2.7e15 GeV) | 55.6 | 0.9653 | 0.0034 |
| 1e9 GeV | 50.6 | 0.9620 | 0.0041 |
| 4 MeV (BBN limit) | 41.9 | 0.9544 | 0.0059 |

- The best case is inside Planck's 95% range (0.9649 ± 0.0042).
- It is **2.9σ from ACT DR6** (0.974 ± 0.003), hence "mixed".
- The tension belongs to the Starobinsky *potential*, not to the black-hole origin: every
  Starobinsky inflation has it, with or without a bounce.

**Energy budget.**
- The parent's mass is exactly ρ_c · (4π/3) r_b³ (checked).
- About 22 e-folds of inflation are enough to turn 1 M☉ into the mass of today's Hubble volume (9e52 kg).

### WP2: anisotropy (`anisotropy.py`)

**New ingredient: the black hole's own initial shear.**
- A Schwarzschild interior is a vacuum Kantowski–Sachs space with shear σ² = 3m/r³.
- If the bouncing ball inherits this shear, then ρ_σ = ρ_c/4, i.e. **Ω_σ = 0.2 for every mass**.
- This is an upper estimate: the homogeneous Oppenheimer–Snyder ball is exactly isotropic.
- The value sits inside the LQC bound (σ² ≤ 11.57, i.e. Ω_σ ≤ 0.56).

**Result.**
- Shear shortens inflation (the Linsefors–Barrau effect). At φ_B = −1.30, for example, it drops
  from 117 to 38 e-folds.
- The Starobinsky threshold moves from −1.46 to −1.19.
- For φ², the failing fraction only rises from 5.6e-6 to 6.2e-6.
- Once there are 60 e-folds, (σ/H)₀ ≤ 10⁻¹¹³, far below the 4.7e-11 bound: **unmeasurable**.

### WP3 + WP3b: curvature and the edge of the baby universe (`curvature.py`)

**Geometry.** A dust ball that starts at rest at radius R0 is a closed Friedmann patch, with
sin²χ0 = r_s/R0. Its curvature radius at the bounce is r_b√(R0/r_s), and today
Ω_K = −(R_H / R_c,0)².

**WP3.** Even with just enough inflation to solve the horizon problem, |Ω_K| ≤ 2.4e-5.
The worst case is a 5e11 kg parent with R0 = r_s.
That is **unmeasurable**: the detection limit is 1e-3.

**WP3b, the new result.**
- The baby universe's edge lies beyond our particle horizon (14.26 Gpc) if N_tot > N_min(M).
- N_min ranges from 95.1 (for 5e22 M☉) to 126.8 (for 5e11 kg).
- Inflation that just solves the horizon problem gives N_tot = 130.9. That exceeds N_min for
  **every** parent mass, by at least 4.2 e-folds.
- The margin does not depend on the reheating temperature, because N_post cancels.
- **So: if inflation solves the horizon problem, the edge is automatically out of sight.**

**Analytic by-product.**
- At the edge minimum, Ω_K = −0.097 · r_s/R0; curvature and edge come from the same geometry.
- For a real star falling from rest (R0/r_s ~ 1e5), this is ~1e-6, so the curvature is always small.

### WP4: the parent's spin (`rotation.py`)

**Estimate.**
- At the bounce: ω_B = J/I = 2.5 a* m/r_b².
- Dilution: with the dust's angular momentum, ω ∝ a⁻². As an upper estimate we also let
  radiation carry the rotation.

**Model limit (an unexpected finding).**
- A homogeneous bounce is compatible only with **a* ≲ 1e-7…1e-21** (from 5e11 kg up to 5e22 M☉).
- Two independent conditions give this limit:
  - ω_B < H_max;
  - the centrifugal barrier lies below r_b.
- At larger spin, rotation dominates well before r_b and halts the collapse.
- Real black holes spin at a* ~ 0.1–0.998, **so this model does not describe a spinning parent.**
- This is an open problem, not a refutation; the LQC bounce of a Kerr interior is an active research topic.

**Inside the valid range:** (ω/H)₀ ≤ 10⁻²⁸, far below 7.6e-10, so the result is neutral.

**Bug fixed.** The first run's scoring wrongly used the formal a* = 0.9 row (10^−6.8), which
extrapolates outside the model. This is corrected; the formal number is still reported in the JSON.

### WP5: the CMB (`cmb.py`)

**Validation.** CAMB reproduces Planck 2018's best-fit theory spectrum over ℓ = 2–2500 to within
0.28% at most (target: < 1%).

**Method.**
- An exponential cutoff in the primordial spectrum, with λ = 3.35.
- A 61-point grid in k_c.
- A low-ℓ Wishart likelihood (ℓ = 2–29, f_sky = 0.86), plus S₁/₂.

**Result.**
- Best k_c = 2.8e-4/Mpc, which corresponds to **N_tot = 141.2** (Zhu et al. 2017: 141).
- The fit improves by Δχ² = −1.2. That is **not significant**: the threshold of −9 was fixed before the run.
- S₁/₂ drops from 34 290 to 12 318 μK⁴; the full-sky Planck spectrum gives 6 777.
- The 95% lower bound is N_tot > 140.8, consistent with WP3b.
- Any LQC bounce produces this; it is **not specific to black holes**.

### WP6: natural selection (`cns.py`)

- The probability that all four measured neutron stars are below 2 M☉ is 7.8e-4 (**3.2σ**).
- For the two heaviest (J0740 and J0952) alone, it is 0.0025.
- Smolin's earlier predictions of 1.5 and 1.6 M☉ are excluded by more than 16σ.

Natural selection is falsified in its published form. **That does not falsify the black-hole
origin**, which does not need it.

## What the code does NOT do (known limits)

- **WP2:** uses the Bianchi-I stiff-fluid approximation, not full Kantowski–Sachs LQC.
- **WP3b:** does not model the transition region at the edge (LMY exterior ↔ Friedmann interior).
  A homogeneous ball is exact only for Oppenheimer–Snyder collapse.
- **WP4:** the model is not valid for a spinning parent (see above).
- **WP5:**
  - It uses a phenomenological cutoff, not the analytic LQC spectrum of Guillén et al. 2026.
  - The ΛCDM parameters are held fixed.
  - There is no MCMC (that job is for the Ryzen).
- **Measure problem:** for Starobinsky the φ_B space is non-compact, so we give thresholds, not probabilities.

## Log

- **2026-09-29.** Built the `thesis/` package (WP0–WP6) and the scorecard. First full run:
  `runs/thesis-2026-09-29/`. Fixes along the way:
  - H from the constraint (instability);
  - the A_s formula;
  - a cap event for potential-dominated bounces;
  - the WP4 scoring.
  - This document was translated to English, per the repo's language rule for `docs/`.
