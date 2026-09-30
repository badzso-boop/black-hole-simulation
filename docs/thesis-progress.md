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
python -m pytest thesis/tests -q        # 30 tests, ~45 s
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
| 4b | Can a *spinning* parent still work? ([spin-plan.md](spin-plan.md)) | **partly: see WP4b below** | — |
| 1b | Does bounce + inflation work with a potential that fits ACT too? (add-on) | **supports** | — |
| 5b | CMB with the real LQC spectrum and the official Planck likelihoods (add-on) | **neutral** | — |
| S4 L1 | Does the spark cross a spinning black hole's inner horizon? ([inner-horizon-plan.md](inner-horizon-plan.md)) | **code ready, awaiting Ryzen run** (preview: open / mixed) | — |
| 5c | Full Planck MCMC: all cosmological parameters free, plus N_tot (add-on) | **neutral** | — |

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

### WP4b: the spinning parent (`spin.py`, plan: [spin-plan.md](spin-plan.md))

**Why.** WP4 showed that the homogeneous bounce needs a* ≲ 10⁻⁷…10⁻²¹. Real black holes have
a* ~ 0.01–0.998 (`observations.json` → `4b_spin`).

**Tested way out: the axial core.** Matter near the rotation axis has almost no angular momentum.

**Model.** The low-j mass fraction is F(j) = C·j/j̄. From this:
- The seed bounces under its own mass only if M_s ≤ C³√(α/2)/a*³ m_P. This is independent of
  both the parent mass and N_tot.
- It must be at least the LMY mass gap (0.83 m_P).
- Its edge must lie beyond our horizon, which requires N_tot ≥ ln(a* R_obs/(C√(α/2) ℓ_P)).

**S1: profile coefficient** (polytropes, rotation Ω ∝ r^−β):
- C = 0.6 for a uniform sphere (checked analytically);
- 0.7604 for n = 1 (checked analytically);
- **1.23 for an n = 3 iron core** (the fiducial value);
- 0.45–3.4 across the scanned profiles.

**Results:**

| Question | Result | Key numbers |
|---|---|---|
| S1+S2 observed spins | **supports** | With C = 1.23, the bulk of every observed population fits at N_tot ≤ 145, and all of the GW population at ≤ 142. With the pessimistic C = 0.45, the X-ray binaries and SMBHs fail. |
| S3 axial core inflates | **supports** | Classically the core's shear saturates the LQC bound. Even at that maximum (Ω_σ = 0.5625), 60 e-folds are reachable (Starobinsky φ̇ > 0: φ_B ≥ −0.60). |
| S4 crossing the inner horizon | **open** | Fast spin: the seed crosses 50–140× before Planck curvature, with distortion 1.3–1.8. Slow spin (0.01): Planck curvature comes first. |
| S5 rotation today | **neutral** | ≤ 10⁻²⁸ |
| CMB consistency | **supports** | At N_tot = 141.2, a* ≲ 0.76 is allowed (98% of the GW population). |
| S6 torsion | info | Worse than LQC: 3.2 more e-folds needed. |

**The honest catch (found during implementation, not anticipated in the plan).**
- **Fast spin makes the seed a Planck-mass nugget:** 1.9 m_P at a* = 0.9. Staying above 10 m_P
  needs a* ≤ 0.52.
- **Slow spin makes the inner horizon so small** that mass inflation wins, by the rough S4 estimate.
  Keeping distortion O(1) needs a* ≥ 0.44.
- **Only a* ≈ 0.44–0.52 satisfies everything comfortably.** That is 8.5% of the GW population and
  none of the predicted natal spins, and the natal spin is the one that counts, because the bounce
  happens at formation. With the hard mass gap alone, the window is 0.44–1.19.
- **S4 is the weakest link:** a real rotating-collapse calculation in effective LQG does not exist
  yet.

### WP1b: an ACT-compatible potential (`inflation.PolyAttractor`, `wp1.run_act`)

**Why.** WP1 is "mixed" only because Starobinsky inflation sits 2.9σ from ACT DR6's n_s = 0.974.
The plan's risk table named the fix: another plateau potential. This is an **add-on**, reported as
its own row; the pre-registered WP1 verdict stays as it is.

**Potential.** The polynomial α-attractor with k = 2 (Kallosh & Linde 2022, arXiv:2202.06492):
- V = V₀ φ²/(φ² + μ²), with μ = 0.2 m_Pl (about one reduced Planck mass);
- V₀ is fixed by A_s = 2.1×10⁻⁹;
- the paper's attractor prediction is n_s = 1 − 3/(2N). Our numerical n_s matches it to 2×10⁻⁴
  (test).

**Result:**
- n_s = 0.9722 and r = 0.0036 (instant reheating, N* = 55.5). That is 1.7σ from Planck and
  0.6σ from ACT, inside both 95% ranges.
- Through the bounce, fewer than 60 e-folds occur only for φ_B ∈ [−3.45, −1.64] (φ̇ > 0; the
  potential is even). Everything else inflates.
- **So the ACT tension belonged to the Starobinsky potential, not to the black-hole origin.**

### WP5b: the real LQC spectrum (`lqc_spectrum.py`, `cobaya_lqc.py`)

**Why.** WP5 used a phenomenological cutoff template. WP5b uses the hybrid-LQC primordial spectrum
of Guillén, Langer, Mena Marugán et al. 2026 (arXiv:2605.14657), and the **official Planck 2018
likelihoods** in their native Python versions via cobaya:
- low-ℓ TT (Gibbs);
- low-ℓ EE;
- plik-lite TT/TE/EE.

**How the spectrum is computed.** The paper's closed form (hypergeometric and Hankel functions) was
not transcribed. Instead the same physics is computed numerically:
1. Kinetic bounce a(t) = (1 + 24πρ_c t²)^{1/6}, with the end of the bounce period at t₀ = 0.4.
2. Pöschl–Teller mass U₀/cosh²(αη).
3. NO-AHD vacuum, which for this mass is the plane wave in the far past.
4. Mode integration to η₀, then matching to the exact kinetic Hankel solutions.
5. P_R = (|A_k| − |B_k|)² P_ΛCDM (the paper's Eq. 3.5).

**Checks against independent values:**

| Check | Ours | Reference |
|---|---|---|
| η₀ | 0.351 | paper: ≈ 0.35 |
| suppression scale k₀ | 1.02 | paper: ~1 |
| Pöschl–Teller scattering | agrees to 10⁻¹⁰ | exact analytic formula |
| Wronskian \|A\|² − \|B\|² | 1 (to 10⁻⁸) | exact identity |
| factor at high k | → 1 | — |
| plug-in at N_tot = 150 | reproduces ΛCDM | — |

The dressed-metric variant is not implemented.

**Result:**

| | best N_tot | Δχ² vs ΛCDM | 95% lower bound |
|---|---|---|---|
| Official Planck low-ℓ TT+EE | **141.0** | **−0.53** (TT −0.72, EE +0.19) | **N_tot > 140.25** |
| Full set incl. plik-lite, at 141.0 | — | −0.55 (high ℓ: +0.001) | — |
| Own Wishart pipeline, same spectrum | 141.0 | −0.59 | — |
| WP5 cutoff template (for comparison) | 141.2 | −1.2 | 140.8 |

- S₁/₂ drops from 34 290 to 19 440 μK⁴ at the best fit.
- **Not significant** (threshold −9), so the WP5 rule gives **neutral**.
- The N_tot constraint agrees with WP3b (edge > horizon needs > 126.8) and with WP4b (at 140.25
  the spin window reaches a* ≲ 0.35 with the fiducial core).

### WP5c: the full MCMC (run on the Ryzen 5950X, 2026-09-30)

**Results** (`runs/mcmc-2026-09-30/`, logs in `runs/mcmc/`):

**The run.**
- 8 chains × 4 threads per model.
- ΛCDM: converged in 80 min (R−1 = 0.0085, 52 608 accepted samples).
- LQC: R−1 = 0.0083, 75 930 samples.
- Both minimizers ran 4 starts each.

**Validation.** The ΛCDM chain reproduces all six parameters of Planck 2018 VI Table 2
(TT,TE,EE+lowE) to within **0.06σ**:
- H0 = 67.26 ± 0.62;
- n_s = 0.9648 ± 0.0044;
- τ = 0.0540 ± 0.0079;
- and the others.

This is an independent check of the whole pipeline.

**N_tot posterior.**
- It has a sharp lower edge, a small bump at ~141.3, then is flat up to the prior edge (150).
- The data give **only a lower bound: N_tot > 140.71 (95%), > 140.27 (99%)**.
- The quoted mean (145 ± 2.9) is prior-dominated and must not be cited.

**Best fit.**
- LQC N_tot = 141.05.
- **Δχ²_min (LQC − ΛCDM) = −0.23.** By likelihood: low-ℓ TT −0.51, EE +0.05, plik-lite +0.24.
- The four minimizer starts scatter by Δχ² ≈ 0.9–1.4, so this is −0.2 ± ~1: **consistent with
  zero, far from the −9 threshold → neutral.**

**Other parameters.** Adding N_tot changes none of them; the ΛCDM and LQC contours overlap in
`triangle.png`.

**Consequences:**
- WP3b holds: 140.71 > 126.8.
- The WP4b spin window at the 95% lower bound reaches a* ≤ 0.44 (0.62 at the best fit), with the
  fiducial core.

**All four CMB estimates agree:**

| | best N_tot | Δχ² | lower bound (95%) |
|---|---|---|---|
| WP5 cutoff template, own Wishart | 141.2 | −1.2 | 140.8 |
| WP5b hybrid LQC, official low-ℓ likelihoods, fixed cosmology | 141.0 | −0.53 | 140.25 |
| WP5b hybrid LQC, own Wishart | 141.0 | −0.59 | — |
| **WP5c full MCMC, all parameters free** | **141.05** | **−0.23** | **140.71** |

**Plain language.**
- The CMB is compatible with a bounce about 141 e-folds ago, but it doesn't need one.
- What it firmly says is that the bounce, if there was one, happened at least ~140.7 e-folds
  before today. Otherwise we would see the large-scale power missing from the sky.

**Files:**
- `scripts/cobaya/lqc_mcmc.yaml`: 6 ΛCDM parameters + N_tot (prior 138–150), same likelihoods.
- `lcdm_mcmc.yaml`: the ΛCDM reference.
- `*_bestfit.yaml`: minimizers for the true best-fit Δχ².
- `scripts/run_mcmc.sh`: MPI, 8 chains × 4 threads by default.
- `scripts/analyze_mcmc.py`: N_tot posterior, Δχ²_min, and the consequences for WP3b/WP4b, written
  to `runs/mcmc-<date>/`.

**Tested here:** both configs pass `cobaya-run --test`, and a 30-sample chain of each model ran
through the analysis script (on the i5, 2026-09-29).

**On the Ryzen:**

```bash
git pull
sudo apt install openmpi-bin libopenmpi-dev
pip install -e '.[dev,thesis]' mpi4py
cobaya-install planck_2018_lowl.TT planck_2018_lowl.EE planck_2018_highl_plik.TTTEEE_lite_native -p ~/cobaya_packages
bash scripts/run_mcmc.sh          # ΛCDM, then LQC, then both minimizers (hours)
# as root (e.g. WSL): OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 bash scripts/run_mcmc.sh
# if MPI hangs (the script tests it for 60 s first): NO_MPI=1 bash scripts/run_mcmc.sh
python scripts/analyze_mcmc.py    # → runs/mcmc-<date>/RESULTS.md; then commit runs/mcmc-*
```

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
- **WP4:** the homogeneous model is not valid for a spinning parent (see above).
- **WP4b:**
  - Newtonian centrifugal estimates with polytropic profiles, not tabulated stellar models.
  - S4 is an order-of-magnitude mass-inflation argument (Ori-type m(v) ≈ εm e^{κ₋v}, with
    v_seed = 10 m).
  - The seed's post-bounce evolution uses the same homogeneous stiff-shear model as WP2.
- **WP5:**
  - It uses a phenomenological cutoff, not the analytic LQC spectrum of Guillén et al. 2026.
  - The ΛCDM parameters are held fixed.
  - There is no MCMC (that job is for the Ryzen).
- **WP5b:**
  - Only the hybrid approach is implemented, not the dressed-metric one.
  - The asymptotic kinetic → inflation matching (k ≫ k_i) is used; this is valid for N_tot ≳ 135.
  - In the grid, the other ΛCDM parameters are held at the Planck best fit. The MCMC (WP5c)
    frees them.
- **Measure problem:** for Starobinsky the φ_B space is non-compact, so we give thresholds, not probabilities.

## Log

- **2026-09-29.** Built the `thesis/` package (WP0–WP6) and the scorecard. First full run:
  `runs/thesis-2026-09-29/`. Fixes along the way:
  - H from the constraint (instability);
  - the A_s formula;
  - a cap event for potential-dominated bounces;
  - the WP4 scoring.
  - This document was translated to English, per the repo's language rule for `docs/`.
  - WP4b (spinning parent): research pass, plan (`spin-plan.md`), then `thesis/spin.py` with
    S1–S6, 9 tests, and scorecard rows. The implementation added the seed-mass/mass-gap condition,
    which the plan had missed.
  - WP1b (polynomial α-attractor) and WP5b (hybrid LQC spectrum with official Planck
    likelihoods via cobaya) are implemented, 6 more tests.
  - WP5c (full MCMC) is prepared and smoke-tested; it runs on the Ryzen.
- **2026-09-30.** The WP5c MCMC ran on the Ryzen 5950X (WSL, 8 MPI chains).
  - Result: neutral (Δχ²_min = −0.23; N_tot > 140.71 at 95%). ΛCDM reproduces Planck 2018 within 0.06σ.
  - `run_mcmc.sh` got an MPI pre-check, unbuffered output and `--bind-to none`.
  - `analyze_mcmc.py` now finds best-fit files by pattern and flags the prior-dominated N_tot mean.
