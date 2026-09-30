# Critical review of the project (2026-09-30)

**Scope.** Everything up to commit `cccdabe` (inner-horizon code, S4 Level 1): the Rust
simulator's headline results, the `thesis/` package (WP0–WP6, WP1b, WP4b, WP5b/5c), the new
inner-horizon code, `data/observations.json`, and the docs.

**Method.**
- I read the code and recomputed the key formulas independently. The computations were cheap,
  analytic ones (milliseconds). I ran the 9 new inner-horizon unit tests (all pass) but **not** the
  Ryzen resolution ladder or the full thesis run.
- I re-checked three literature numbers on the web (§5).
- The companion plan is [upgrade-plan.md](upgrade-plan.md).

**The short version.**
- The arithmetic and the numerics are in good shape. The validations are real, and the pipeline
  reproduces published numbers.
- The weak points are in the **modelling assumptions** and in **how results are labelled**:
  - several "supports" rows hold only under an assumption the thesis never states;
  - one mechanical verdict does not follow its own pre-registered rule;
  - two data entries are out of date or mislabelled;
  - the project's own new result (edge confinement) undermines WP4b.

---

## 1. Suggested scorecard, at a glance

| Row | Current label | Suggested label | Main reason (section) |
|---|---|---|---|
| Norbi claim 3 (information in Hawking radiation) | fails | **fails** (confirmed) | f(r_b) = 1 in LMYZ: the bounce is inside r₋ (§2) |
| Norbi claim 2 (infalling matter feeds the baby universe) | not scored | **no classical path** | L1e preview (§4.3) |
| WP1 inflation | mixed | **mixed, conditional**: no mechanism puts the inflaton on its plateau | §3.1 |
| WP1b | supports | supports (add-on, post hoc) | chosen after seeing ACT |
| WP2 anisotropy | neutral | neutral; **drop the Ω_σ = 0.2 figure** | §3.4 |
| WP3 curvature | neutral | neutral | — |
| WP3b edge beyond horizon | supports | **consistency check**, not support | §3.3, §3.5 |
| WP4 spin | neutral + model limit | **against, for the homogeneous model** | §3.6 |
| WP4b spin route | supports / open | **against, pending an amplitude estimate** | §4.1 |
| WP5/5b/5c CMB | neutral | neutral, not BH-specific | §3.7 |
| WP6 natural selection | against, 3.2σ | against, **3.7σ with 2025 masses, resting on one pulsar** | §3.8 |
| EHT consistency | key result | **units/GR sanity check** | §3.9 |
| L1a | supports (preview) | supports (narrow) | §4.4 |
| L1c | open, "GW 22%" | open; **decided by the D ≤ 10 heuristic** | §4.2 |
| L1e | against (preview) | **neutral, under its own §5 rule** | §4.3 |

---

## 2. What holds up

- **The central negative result is correct and easy to verify.**
  - The LMYZ exterior is f(r) = 1 − 2m/r + αm²/r⁴, and the bounce radius obeys r_b³ = αm/2.
  - So αm²/r_b⁴ = 2m/r_b, and **f(r_b) = 1 exactly**. The bounce happens in the static region
    inside the inner horizon, which is causally cut off from the exterior.
  - The "0 bits recovered" is therefore a consequence of the geometry, not a coding choice.
- **The key formulas reproduce independently:**
  - r_b(M);
  - the edge condition N_tot > ln(R_obs/r_b), which is 126.8 for the 5.1e11 kg parent;
  - sin²χ₀ = r_s/R₀ for a dust ball released from rest;
  - the Kantowski–Sachs shear σ² = 3m/r³;
  - the WP4 spin limits (9e-8 for the smallest parent);
  - the Kerr on-axis crossing integral in `spark_crossing_dv`;
  - the Planck-curvature mass m_Pl = r₋³(M/m_P)²/√48.
- **The literature reproductions work:**
  - Ashtekar–Sloan's and Bonga–Gupt's thresholds;
  - CAMB against Planck (0.28%);
  - ΛCDM in the MCMC within 0.06σ of Planck 2018;
  - Brady–Smith κ₋ to 0.01%.
- **k_c → N_tot is purely geometric** (`thesis/cmb.py:136`), so the CMB bound N_tot > 140.7 does
  not depend on the reheating temperature.
- **The pre-registration discipline is real.** The one criterion added during implementation
  (the stricter T2 gate) makes the bar harder to pass, not easier.

---

## 3. Findings in WP0–WP6 and the simulator

### 3.1 No mechanism connects the star's matter to the inflaton (WP1). Severity: high

- `thesis/inflation.py` starts every run at the bounce with **100% of ρ_c in the scalar field**, and
  scans φ_B (with the Ashtekar–Sloan measure for φ²).
- But the Oppenheimer–Snyder ball that collapses is **dust**. In a parent universe like ours, the
  inflaton sits at its minimum, and compressing baryons does not lift it onto the plateau.
- With dust carrying ρ_c and the field at rest at its minimum, a bounce produces **no inflation at
  all**.
- So "inflation after the bounce is almost certain" is a statement about *cosmological* LQC with a
  scalar-dominated bounce. It is not a statement about a black-hole interior. The docs never state
  this gap.
- Secondary point: the "almost certain" number comes from φ², a potential that Planck excludes. For
  Starobinsky only thresholds exist, so there is no probability (the docs say this correctly).

**Consequence:** WP1 is conditional on an unexplained initial state. Every row that inherits WP1's
e-folds (WP2, WP3, WP3b, WP4, WP5) inherits that condition.

### 3.2 Matching an inflating ball to the exterior is not addressed. Severity: medium

- Oppenheimer–Snyder matching works because dust has P = 0. A scalar-field ball with P ≈ −ρ cannot
  be joined to the vacuum LMYZ exterior along a comoving boundary without a thin shell: the Israel
  junction conditions need the pressure to be continuous.
- This is the Farhi–Guth–Guven problem. `are-we-in-a-black-hole.md` cites it, but no WP uses it.
- One point may help the hypothesis: the effective LQC dynamics violates the null energy condition,
  which is the assumption behind Farhi–Guth's singularity argument. That has not been checked either.

### 3.3 The "LQC natural N_tot 130–145" band mixes two definitions. Severity: medium (confirmed)

- `data/observations.json` → `1_inflation.efolds_distribution_peak = 145` (Linsefors & Barrau 2013)
  is used in `thesis/curvature.py:100` and `thesis/spin.py` (`N_TOT_LQC_MAX`) as a **total**
  bounce-to-today N_tot.
- The paper's abstract says the probability "for a given number of **inflationary** e-folds is
  quite sharply peaked around 145". It also uses a different initial state: a pre-bounce oscillating
  φ² field.
- As N_tot, that would be about 145 + N_onset + N_post, roughly 200. The bounce imprint would then be
  far outside the CMB.
- Consequences:
  - The upper end of the "natural band" has no literature source as an N_tot value. Zhu et al.
    2017's 141 is an observational lower bound, not a prediction.
  - WP3b's pre-registered criterion ("natural N_tot exceeds N_min(M)") and WP4b's 145 ceiling both
    rest on this.

### 3.4 WP2's Ω_σ = 0.2 is evaluated where its metric does not apply. Severity: medium

- `thesis/anisotropy.py:44` evaluates the classical vacuum Kantowski–Sachs shear at r = r_b.
- In LMYZ, f(r_b) = 1 (§2): that region is static, not Kantowski–Sachs.
- So 0.2 is a classical extrapolation into a region where the quantum-corrected metric is completely
  different. It is not "the black hole's interior shear".
- The Oppenheimer–Snyder interior itself is exactly isotropic (Ω_σ = 0).
- **The WP2 verdict survives:** even the LQC cap Ω_σ = 0.5625 still inflates (WP4b S3). But the
  thesis should quote a band, 0 ≤ Ω_σ ≤ 0.5625, not a mass-independent 0.2.

### 3.5 Most "supports" rows cannot tell a black-hole origin from an ordinary bounce. Severity: medium (presentation)

- **WP1, WP1b:** properties of LQC plus inflation.
- **WP3b:** close to automatic.
  - r_b is much larger than the Hubble length at the bounce: r_b ≈ 2e6 ℓ_P for the smallest parent,
    against 1/H_max ≈ 1 ℓ_P.
  - So any inflation that solves the horizon problem already pushes the edge beyond the horizon.
    The computed margin is ≥ 4.2 e-folds.
  - It is a real consistency check, but it is not evidence.
- **WP5/5b/5c:** the scorecard itself says they are not BH-specific.
- For none of these rows does the likelihood ratio between "BH origin" and "generic LQC bounce"
  differ from about 1. Counting them as "supports" gives a misleading tally.

**Suggestion:** add a column "discriminates BH origin? yes/no" to the scorecard.

### 3.6 WP4's label is too kind. Severity: low–medium

- A model valid only for a* ≲ 1e-7 describes essentially **no** real black hole: natal spins are
  about 0.01 and GW spins about 0.1–0.9.
- The pre-registered table did not foresee this outcome. "Neutral + model limit" is formally
  defensible, but the text should say plainly that the homogeneous-bounce model **excludes the
  black holes that actually exist**.
- Minor: the docstring in `thesis/rotation.py:10` gives a*_max as "~10⁻¹⁶…10⁻¹³". The code gives
  9e-8 for the 5.1e11 kg parent.

### 3.7 The CMB rows test a vacuum initial state, not a stellar one. Severity: low (open)

- WP5b uses the hybrid-LQC spectrum, which assumes the perturbations start in a quantum vacuum
  state.
- In a black-hole origin, the pre-bounce perturbations come from the star's structure: an O(1)
  density profile on the scale of the ball. This is where a *BH-specific* CMB signal would come from
  if one exists, and it has not been estimated.

### 3.8 WP6: the data are out of date, and the result rests on one star. Severity: medium (confirmed)

The current masses (checked 2026-09-30) against what `observations.json` has:

| Pulsar | In the repo | Current value | Source |
|---|---|---|---|
| J1614−2230 | 1.97 ± 0.04 | **1.937 ± 0.013** | NANOGrav 15-yr (arXiv:2306.16217) |
| J0348+0432 | 2.01 ± 0.04 | **1.806 ± 0.037** | Saffer et al. 2025, ApJL 983, L20 (arXiv:2412.02850) |
| J0740+6620 | 2.08 ± 0.07 | 2.08 ± 0.07 (unchanged) | Fonseca et al. 2021 |
| J0952−0607 | 2.35 ± 0.17 | **2.35 ± 0.11** | Romani et al. 2025, ApJ (arXiv:2512.05099) |

Recomputed with the same `cns.py` method:

| Data set | P(all < 2 M☉) | σ |
|---|---|---|
| Repo values | 7.8e-4 | 3.2 |
| **Current values** | **9.3e-5** | **3.7** |
| Current, without J0952 | 0.13 | 1.1 |
| Current, Smolin's "~2.4 M☉ would be inconsistent" threshold | 0.68 | none |

- The verdict stays **against** under the pre-registered 3σ rule, and becomes stronger.
- But it rests almost entirely on **one black-widow pulsar**, whose mass comes from light-curve
  modelling of the heated companion.
- It also depends on reading Smolin's prediction as M_max < 2.0 rather than ~2.4.
- The thesis should say "in ~3.7σ tension, dominated by PSR J0952−0607", not "falsified".
- *Correction to my chat review:* I predicted 2.8σ there, before checking J0952's 2025 update. That
  was wrong.

### 3.9 The "EHT consistency" figures are not predictions. Severity: low (presentation)

- `core/src/catalog.rs:260` computes δ = d_obs/(11·θ_g) − 1. That is plain GR with a fixed
  calibration: no spin, no LMYZ correction, no Norbi.
- For **M87\***, the mass (6.5e9 M☉) was itself derived by the EHT from the ring with a similar
  calibration, so δ = 0.000 is circular.
- For **Sgr A\***, −0.082 simply reproduces the EHT's own calculation with the GRAVITY mass and
  distance.
- This is a useful units check, but it should not be listed among the key results.

### 3.10 The Hawking lifetime is 20% short. Severity: low (documented)

- The hole that evaporates today has a lifetime of 11.1 Gyr in the model, against 13.8 Gyr in the
  literature (Carr et al. 2010, M* = 5.1e11 kg).
- The explanation (species thresholds) is plausible, but 20% is large for a row labelled
  "validated". A MacGibbon-style f(M) with greybody-weighted thresholds should get within ~5%.

---

## 4. Findings in the new inner-horizon code (`cccdabe`, preview only)

The code itself is careful:
- it finds r₋ in extended precision;
- it validates against independent literature values;
- it records a rejected solver openly.

The issues are in how the verdicts are built.

### 4.1 Edge confinement rules out WP4b's small-seed route. Severity: high

The commit finds that a disturbance from the ball's edge can travel only a limited comoving
distance η inward before inflation ends. The commit text quotes "≈ 5×10³ ℓ_P". The code's full
η (kinetic phase plus inflation, `ori_model.conformal_time_to_end_of_inflation`) is
**9.55×10³ ℓ_P**. Combined with WP4b's own seed bound, M_s ≤ C³√(α/2)/a*³ m_P with C = 1.23:

| Requirement | Minimum seed mass | Maximum spin |
|---|---|---|
| Seed larger than the region the disturbance reaches (η/r_b ≤ 1) | 1.5e12 m_P ≈ 33 t | a* ≲ **9.8e-5** |
| Disturbance reaches at most 10% of the seed | 1.5e15 m_P ≈ 33 000 t | a* ≲ **9.8e-6** |

These values come from the code, as the S7 row in `thesis/verdict.py` computes them. An earlier
draft of this table used η = 5×10³, which gave 1.9e-4 and 1.9e-5.

- Natal spins (~0.01) and every observed population are above both limits. The "comfortable window
  a* ≈ 0.44–0.52" disappears.
- **Caveats:**
  - η is a speed-of-light bound. Nobody has yet shown that the disturbance is large enough to spoil
    the seed's bounce.
  - The seed's surroundings are the rest of a rotating star, not vacuum.
- Until an amplitude estimate exists, WP4b should read **against, pending an amplitude estimate**,
  not "supports".
- **A related point, corrected from my chat review.** I argued that a Grishchuk–Zel'dovich
  (edge-quadrupole) bound adds about 4.6 e-folds to every edge condition. That is **wrong for an
  exact top-hat (Oppenheimer–Snyder) ball**: its interior is exactly Friedmann wherever the observer
  sits, so the edge produces no tidal or quadrupole signal until light from the edge arrives.
  - The bound does apply when the ball has an O(1) density gradient on its own scale. That is the
    case for a realistic star, and certainly for WP4b's axial seed inside an n = 3 polytrope.
  - So for WP4b it is a real, additional risk. For the Oppenheimer–Snyder WP3b it is not.

### 4.2 L1c is decided by the distortion cutoff, not by the timing race. Severity: medium

Values from `race()` at the 10 M☉ fiducial mass:

| a* | margin v_Pl/Δv (needs ≥ 10) | D = M/r₋ (needs ≤ 10) | passes |
|---|---|---|---|
| 0.26 | 20 | 29 | no |
| 0.44 | 62 | 9.8 | yes |
| 0.9 | 1128 | 1.8 | yes |

- For every spin above ~0.1, the timing margin is 20 to 4700. That is close to built in: the core
  falls first, and mass inflation needs material falling in later.
- So "GW 22% pass" means "22% of GW spins exceed 0.44". That line is set by D ≤ 10, which was
  pre-registered but is a heuristic, not a computed tidal strain.
- `spark_crossing_dv` also treats the core as a test particle on the vacuum Kerr axis. In reality
  the core is inside the star's matter when the horizons form, where vacuum Kerr does not apply
  (the same kind of mismatch as §3.4).

### 4.3 L1e's mechanical verdict contradicts its own pre-registered rule. Severity: medium (bug)

- The plan's §5 says **against** only if a late shell "always ends at the Cauchy-horizon
  singularity, the shock, or r = 0". It says **neutral** if "the fate depends on unmodelled quantum
  gravity".
- `thesis/verdict.py:457` returns "against" as soon as the shell meets *Planck curvature*, and its
  own explanation says the calculation cannot decide whether quantum gravity produces a bounce
  there.
- In a thesis that uses LQG to resolve the central singularity, Planck curvature is precisely the
  "unmodelled quantum gravity" case. Under its own rule, **L1e is neutral**.
- The physics still matters and belongs in the key results: anything falling in more than about a
  millisecond after formation (10 M☉) meets a Planckian inner horizon. **Norbi's "feeding" (claim
  2) has no classical path.**

### 4.4 L1a is solid but narrow

- For a non-spinning parent, at most ln 2 e-folds fit between crossing r₋ and the bounce, so the
  star's own bounce is not threatened.
- The new finding that the LMYZ inner horizon is itself unstable (in agreement with Cao et al. 2024)
  is one more strike against anything that falls in later.

### 4.5 The heavy numerics barely affect the verdicts

- The double-null code confirms the growth rate κ₋. The amplitude is dominated by a
  truncation-error floor at the available resolutions (the commit says so).
- The race uses an analytic Kerr κ₋ with an assumed δ = 0.1, and the quantum flux is one Kerr
  a* = 0.8 value scaled by κ₋².
- The Ryzen ladder will refine L1b, but L1c and L1e depend on the amplitude only logarithmically.
- The thesis should present the code as a *validation of the growth law*, not as the source of the
  verdicts.

---

## 5. Literature checks made for this review

| Claim | Status | Source |
|---|---|---|
| Linsefors–Barrau's 145 counts **inflationary** e-folds | confirmed | PRD 87, 123509 (arXiv:1301.1264), abstract |
| J0348+0432 = 1.806(37) M☉ | confirmed | Saffer et al. 2025, ApJL 983, L20 (arXiv:2412.02850) |
| J1614−2230 = 1.937 (+0.012/−0.013) M☉ | confirmed | NANOGrav 15-yr (arXiv:2306.16217) |
| J0952−0607 = 2.35 ± 0.11 M☉ | confirmed | Romani et al. 2025 (arXiv:2512.05099) |

---

## 6. Overall picture after this review

1. **Norbi's claim 3** (information returns in Hawking radiation) **fails**: the bounce is causally
   disconnected (§2). This result is robust.
2. **Norbi's claim 2** (infalling matter feeds the baby universe) **has no classical path**: late
   matter meets a Planckian inner horizon (L1e). Whether quantum gravity changes that is open.
3. **"Our Big Bang was an LQC bounce in a black hole"** survives only in a narrow form:
   - it is **non-spinning** (a* ≲ 1e-7 homogeneous; the spin route is now in trouble, §4.1);
   - it is **homogeneous** (Oppenheimer–Snyder);
   - it rests on an **unexplained inflaton initial state** (§3.1).
   Within that form, nothing observed rules it out. Nothing observed prefers it over an ordinary
   LQC bounce either (§3.5).
4. **Smolin's natural selection** is in ~3.7σ tension, carried by one pulsar (§3.8).

This is still a coherent and honest thesis: "a precisely stated black-hole-origin model; which parts
survive the data; which parts fail on internal consistency". Its strength will come from stating
§3.1, §3.5 and §4.1 openly rather than from the count of "supports".
