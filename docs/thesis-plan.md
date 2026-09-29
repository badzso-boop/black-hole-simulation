# Thesis plan: "Was our Big Bang a quantum bounce inside a black hole?"

**Status:** plan written 2026-09-28; §0 criteria fixed on that date. **All WPs implemented and
run on 2026-09-29** — code in `thesis/`, results and scorecard in
[thesis-progress.md](thesis-progress.md) and `runs/thesis-2026-09-29/`.

**Inputs:**
- `data/observations.json`: every observational number, with its source.
- `data/planck/`: Planck 2018 CMB spectra with checksums.
- The research pass behind these (Sept 2026), summarised in the references at the end.

**Background:** [are-we-in-a-black-hole.md](are-we-in-a-black-hole.md).

---

## 0. The thesis in one paragraph

> *If* our universe began as the loop-quantum-cosmology (LQC) bounce of matter
> that collapsed inside a black hole in a parent universe, *then* six
> consequences follow. This thesis derives each one quantitatively, compares it
> with current data, and reports which parts of the hypothesis survive.

The thesis does **not** claim we live in a black hole. It claims to have tested
a clearly stated model against data. This framing is what makes it defensible:
a negative result on a well-posed question is still a result.

### Pre-registered outcomes

Fix the pass/fail criteria *before* running the numbers, so they cannot be
tuned afterwards. Record the date of this section in the thesis.

| WP | Supports the hypothesis if… | Counts against it if… | Neutral / untestable if… |
|---|---|---|---|
| 1 Inflation | ≥ 60 e-folds for most bounce initial data **and** (n_s, r) inside Planck/ACT 95% | enough inflation only in a fine-tuned corner **or** (n_s, r) excluded | — |
| 2 Anisotropy | shear from a black-hole interior decays to (σ/H)₀ < 4.7×10⁻¹¹ with the WP1 e-folds | shear kills inflation (Linsefors–Barrau) for black-hole initial shear | shear today unmeasurably small either way |
| 3 Curvature | predicted Ω_K consistent with DESI DR2 + CMB (0.0023 ± 0.0011) | predicted closed Ω_K < −0.003 excluded at > 3σ | predicted \|Ω_K\| ≪ 10⁻³ (below measurement) |
| 3b Edge beyond horizon (novel) | LQC's natural N_tot (130–145) exceeds N_min(M) for plausible parent masses | N_min(M) > N_tot for all plausible M | — |
| 4 Parent spin | a predicted axis at a detectable amplitude that matches data | predicted amplitude above (ω/H)₀ < 7.6×10⁻¹⁰ | predicted amplitude ≪ limits (expected) |
| 5 CMB imprint | LQC spectrum improves the low-ℓ fit (Δχ² < 0, S₁/₂ closer to 1209 μK⁴) with k_c consistent with WP3b's N_tot | best-fit k_c inconsistent with WP1/3b e-folds | improvement not significant (look-elsewhere) |
| 6 Natural selection | M_max(NS) < 2 M☉ | a neutron star > 2 M☉ at > 3σ **(already the case)** | — |

**Expected honest outcome from what is already known:**
- WP1 and WP3b are likely positive.
- WP2 and WP4 are likely neutral (inflation erases the memory).
- WP3 is likely neutral.
- WP5 is mildly positive but not significant.
- WP6 is already falsified.

That is a coherent, defensible thesis: *"a black-hole origin is not excluded; its
distinctive signatures are erased by the inflation that makes it work; one
proposed extension (natural selection) is falsified."*

---

## 1. Work packages at a glance

| WP | Question | Builds on | Novelty | Effort on the i5 | Compute |
|---|---|---|---|---|---|
| 0 | Infrastructure: Python package, units, validation against the Rust core | v3.2 | — | 3–4 days | trivial |
| 1 | Does the bounce inflate enough, with correct n_s and r? | 0 | reproduction | 1.5 weeks | minutes |
| 2 | Does black-hole-interior shear survive the bounce and inflation? | 1 | partial (black-hole initial shear) | 2 weeks | minutes |
| 3 | What spatial curvature is predicted today? | 1 | reproduction + application | 1 week | seconds |
| 3b | How many e-folds so the baby universe's edge is beyond our horizon, vs parent mass? | 1, 3, simulator | **new** | 1 week | seconds |
| 4 | Does the parent's spin leave an axis? | 1, 2, Kerr part of simulator | new estimate | 4–5 days | seconds |
| 5 | Does the bounce leave a mark on the CMB at low ℓ? | 1, 3b | reproduction + connection to 3b | 3 weeks | CAMB runs: seconds each; optional MCMC: days (i5), hours (Ryzen) |
| 6 | Is Smolin's natural selection consistent with neutron-star masses? | data only | literature analysis | 3–4 days | trivial |
| — | Writing, figures, defence | all | — | 3–4 weeks | — |

**Total:** about 12–15 weeks at a steady pace. WP6 and WP0 can run in
parallel with anything else.

```
WP0 ─► WP1 ─┬─► WP2 ─► WP4
            ├─► WP3 ─► WP3b ─► WP5
            └────────────────► WP5
WP6 (independent)
```

---

## 2. WP0: infrastructure (shared by everything)

**Code layout.** Add a new Python package next to the simulator, so the Rust
core stays untouched and stays validated:

```
thesis/
  units.py          Planck units (G = ħ = c = 1), m_Pl, M_Pl, conversions to SI/GeV/Mpc
  lqc.py            effective LQC background: flat / closed / scalar field / Bianchi I
  inflation.py      WP1: bounce initial data, e-fold counting, slow-roll observables
  anisotropy.py     WP2
  curvature.py      WP3 + WP3b
  rotation.py       WP4
  cmb.py            WP5: primordial spectra → CAMB → C_ℓ, S_1/2, χ²
  cns.py            WP6
  data.py           loads data/observations.json and data/planck/
  tests/            one test per validation target listed below
  figures/          generated figures (scripts write here, nothing hand-edited)
scripts/thesis_*.py one script per WP that regenerates its tables and figures
```

**Dependencies.** Add an extra to `pyproject.toml`:
- `thesis = ["camb>=2.0", "getdist", "matplotlib"]`
- `cobaya` is optional, for WP5 MCMC only.

CAMB 2.0.4 ships a ready-made Linux wheel (2.4 MB), so it installs in seconds on the i5.

**Integrator.** `scipy.integrate.solve_ivp(method="DOP853")`, with tight tolerances
(rtol 1e-10). Integrate in cosmic time t, in Planck units, through the bounce,
and use e-folds N = ln a as the output variable.

**Validation against the Rust core** (the Rust tests already pin these):
1. ρ_c = 0.409 ρ_Pl.
2. H_max = 0.926/t_P.
3. Dust bounce: ρ(τ) = ρ_c/(1 + 6πGρ_cτ²) to 1e-8.
4. Bounce radius r_b = (αGM/2c²)^{1/3}.

If the Python LQC module reproduces all four, every later result inherits the
Rust validation.

---

## 3. WP1: inflation after the bounce

**Question.** Starting at the bounce of the parent's collapsed matter, does a
scalar field inflate the region by ≥ 60 e-folds, and are the predicted
(n_s, r) consistent with observations?

**Equations** (flat, effective LQC; Ashtekar & Sloan 2010/2011; Bonga & Gupt 2016):

```
H² = (8πG/3) ρ (1 − ρ/ρ_c),         ρ = φ̇²/2 + V(φ),  P = φ̇²/2 − V
Ḣ  = −4πG (ρ + P)(1 − 2ρ/ρ_c)
φ̈ + 3Hφ̇ + V′(φ) = 0
```

At the bounce H = 0 and ρ = ρ_c, so the initial data are (φ_B, sign φ̇_B), with
|φ̇_B| = √(2(ρ_c − V(φ_B))).

**Potentials.**

| Name | V(φ) | Normalisation | Status |
|---|---|---|---|
| Starobinsky R² (main) | (3M²/32πG)(1 − e^{−√(16πG/3)φ})² | M = 2.51×10⁻⁶ m_Pl | allowed by Planck; 2–3σ tension with ACT's n_s = 0.974 ± 0.003 |
| φ² (control, literature check) | m²φ²/2 | m = 1.21×10⁻⁶ m_Pl | excluded by r (predicts 0.145 vs < 0.036); use only to reproduce Ashtekar–Sloan |

**Method.**
1. Scan φ_B on a fine grid, with both signs of φ̇_B:
   - φ²: |φ_B| ≤ φ_max, where mφ_max = 0.90 m_Pl².
   - Starobinsky: φ_B ∈ [−3.47, +8] m_Pl.
2. Integrate each case until inflation ends (ε_H = −Ḣ/H² = 1).
3. Record the number of e-folds of slow roll, N_infl, and the total from the
   bounce, N_tot.
4. Compute n_s and r at the pivot, N* ≈ 50–60 e-folds before the end. For
   Starobinsky, n_s − 1 ≈ −2/N* and r ≈ 12/N*²; also compute them numerically
   from the slow-roll parameters.

**Validation.**
- Reproduce Ashtekar–Sloan: P(≥ 68 e-folds) > 0.999997 for φ², with a uniform
  measure in φ_B.
- Reproduce Bonga–Gupt's slow-roll thresholds: φ_B ≥ −1.45 m_Pl (φ̇_B > 0) and
  φ_B ≥ 3.63 m_Pl (φ̇_B < 0).
- The kinetic-dominated bounce should give the universal pre-inflation phase of
  Zhu et al. 2017.

**Deliverables.**
- Figure N_infl(φ_B) for both potentials, with the 60/68 lines marked.
- Table: fraction of initial data with enough inflation.
- (n_s, r) point on the Planck + BK18 contour, with the ACT n_s band shown.

**Energy budget.** Show that 10–17 e-folds already turn the parent's mass into a
Hubble volume's worth of energy (`cosmology_checks.py` §2). The remaining e-folds
solve horizon and flatness. This answers "where does a galaxy's worth of matter
come from?"

**Risks.**
- Stiff oscillation phases before inflation: use DOP853 and an event on ε_H.
- For Starobinsky the φ_B space is non-compact, so there is no natural uniform
  measure. Report the threshold values rather than a probability, as Bonga–Gupt do.

---

## 4. WP2: anisotropy through the bounce

**Question.** A black-hole interior is anisotropic (Kantowski–Sachs: one
direction stretches, two shrink), while our universe is isotropic to 10⁻⁵. Does
the anisotropy survive the bounce and inflation? Does it spoil inflation?

**Equations.**
- Tractable proxy: Bianchi I, effective LQC (Corichi & Singh 2009;
  Gupt & Singh 2012).
- Classically: H² = (8πG/3)ρ + σ²/6, with σ² = Σ²/a⁶.
- LQC bounds: σ²_max = 10.125/(3γ²λ²) ≈ 11.57 ℓ_Pl⁻², and θ_max = 3/(2γλ).
- The full directional equations are in Corichi–Singh, Eqs. 30–32.
- Start with the scalar-field version; dust as a check.

**Initial shear from the parent.** Evaluate the Kantowski–Sachs anisotropy of
the Schwarzschild interior at the radius where the collapsing matter reaches
ρ_c. Use this as the initial Σ, rather than choosing Σ freely.

This is the part that ties the calculation to *your* black-hole scenario rather
than generic LQC. The full Kantowski–Sachs LQC (Ashtekar–Olmedo–Singh 2018;
Joe & Singh 2015) is the advanced version. Mention it and use it only if time
allows.

**Method.**
1. Evolve σ/H through the bounce and WP1's inflation.
2. Check that σ² never exceeds σ²_max.
3. Scan Σ to find how much shear shortens inflation (Linsefors–Barrau 2015).
4. Propagate to today:
   (σ/H)₀ ≈ (σ/H)_onset · e^{−3N_infl} · (a_end/a_eq) · (a_eq/a₀)^{3/2}

**Validation.**
- σ ∝ a⁻³ in the classical regime.
- The bounds hold.
- The isotropic limit Σ → 0 reproduces WP1 exactly.
- Kasner-transition behaviour matches Gupt & Singh 2012.

**Deliverables.**
- Figure σ/H versus N through the bounce.
- N_infl(Σ).
- Predicted (σ/H)₀ compared with 4.7×10⁻¹¹ (vector) and 1.0×10⁻⁶ (tensor)
  (Saadeh et al. 2016).
- Cite Wald's no-hair theorem (1983).

**Expected result.** A black-hole-interior shear is erased: the prediction is
neutral, with no detectable anisotropy. The interesting part is the threshold Σ
above which inflation fails.

---

## 5. WP3: spatial curvature

**Question.** A collapsed star that is gravitationally bound is closed (k = +1).
What Ω_K does that predict today?

**Link to the simulator.**
- The existing collapse is marginally bound (k = 0, falling in from rest at
  infinity).
- A star starting at rest at radius R₀ is closed. Its interior is a k = +1
  Friedmann patch whose curvature is set by R₀ (the `initial_radius_rs`
  parameter).
- Adding this bound Oppenheimer–Snyder variant to the Rust core, as one
  function, gives Ω_K at the bounce from the parent's collapse.

**Equations.** Closed LQC (Ashtekar–Pawlowski–Singh–Vandersloot 2007; Gordon, Li & Singh 2021):

```
H² = (8πG/3)(ρ − ρ_min)[1 − (ρ − ρ_min)/ρ_c]
ρ_min = ρ_c[(1+γ²)D² − sin²D],   D = λ(2π²/v)^{1/3},   v = 2π²a³
```

Take Ω_K at the onset of slow roll (at the bounce H = 0, so Ω_K is undefined
there). Then:

```
|Ω_K,0| = |Ω_K,i| · e^{−2(N_infl − N_hor)}
```

Here N_hor ≈ 50–60 comes from Liddle & Leach 2003, Eq. 6, with the reheating
temperature as a parameter (T_RH ≥ 4 MeV from BBN).

**Data** (68%, Ω_K > 0 is open):
- DESI DR2 + CMB: 0.0023 ± 0.0011
- ACT DR6: 0.0019 ± 0.0015
- Planck + lensing + BAO: 0.0007 ± 0.0019
- Planck TT,TE,EE + lowE alone: −0.044 (+0.018/−0.015). This is the old
  "closed universe" result. Explain why it no longer counts once lensing and
  BAO are added.

**Deliverables.**
- Ω_K,0 as a function of N_infl and T_RH, showing the region where |Ω_K| > 10⁻³
  would be detectable.
- Comparison with Gaztañaga's black-hole-universe prediction
  (−0.07 ± 0.02 ≤ Ω_K < 0, mildly disfavoured by DESI DR2).

**Expected result.** With WP1's e-folds, |Ω_K| ≪ 10⁻³: neutral. The model is
*falsifiable* only if inflation was just barely long enough.

---

## 6. WP3b: the edge of the baby universe (novel calculation)

**Question.** The bounced region is finite. It is the parent's collapsed matter,
of radius r_b(M) at the bounce. For our observations to look like an infinite
homogeneous universe, its edge must lie beyond everything we can see. How many
e-folds from bounce to today does that need, as a function of the parent's mass?

**Equation.** Physical size today = r_b(M) · e^{N_tot}, where N_tot = ln(a₀/a_B).
This is the same definition as Zhu et al. 2017.

Requirements:
- Beyond our particle horizon: N_tot > N_min(M) = ln(R_obs/r_b(M)), with
  R_obs ≈ 14.3 Gpc (comoving).
- Stronger condition, using ACT's curvature-radius bound for a closed universe:
  R > 105 Gpc.

**First estimate** (r_b from the Lewandowski–Ma–Yang–Zhang geometry already in the simulator):

| Parent | r_b | N_min (edge > horizon) | N_min (R > 105 Gpc) |
|---|---|---|---|
| Primordial, 5×10¹¹ kg | 3.9×10⁻²⁹ m | 126.8 | 128.8 |
| 1 M☉ | 6.1×10⁻²³ m | 112.5 | 114.5 |
| 10 M☉ | 1.3×10⁻²² m | 111.7 | 113.7 |
| Sgr A* | 9.9×10⁻²¹ m | 107.4 | 109.4 |
| M87* | 1.1×10⁻¹⁹ m | 105.0 | 107.0 |
| Gaztañaga's parent, 5×10²² M☉ | 2.2×10⁻¹⁵ m | 95.1 | 97.1 |

LQC's own predictions for N_tot are all above these values:
- N_tot > 141 at 95% (Zhu et al. 2017)
- a distribution peaking near 145 (Linsefors & Barrau 2013)
- 130–143 preferred by the CMB fit (Guillén et al. 2026)

So on this estimate the black-hole origin is **not excluded for any parent
mass**. This is the one place where the thesis says something new about the
specific hypothesis.

**Method (turning the estimate into a result).**
1. Replace "size = r_b e^{N}" by the actual comoving evolution:
   - dust/field bounce (WP1) → inflation → reheating → radiation → matter → Λ
     (standard background after reheating);
   - reheating temperature as a parameter.
2. Include the transition region at the edge: outside the dust ball the
   geometry is the LMY exterior, not a Friedmann universe.
3. Give the result as a band, N_min(M, T_RH).
4. Compare it with the WP1 N_tot distribution.

**Deliverables.**
- Figure N_min versus parent mass, with the LQC N_tot band overlaid (the key
  figure of the thesis).
- A table like the one above, with uncertainties.

**Risks.** The assumption that the whole dust ball becomes one homogeneous
patch holds exactly only for Oppenheimer–Snyder. For a realistic,
non-homogeneous star, only the core region is homogeneous. State this as a
limitation.

---

## 7. WP4: imprint of the parent's spin

**Question.** A Kerr parent (a* ≠ 0) carries angular momentum
J = a*GM²/c. Does the baby universe inherit a rotation or a preferred axis?

**Status of the literature.** Popławski (arXiv:1910.10819) claims a preferred
axis but gives **no numbers**. The thesis supplies the missing estimate.

**Estimate to make.**
1. Initial vorticity: at the bounce, the collapsed matter's angular momentum
   gives (ω/H)_B ~ O(a*) times a geometric factor. Compute it from the simulator's
   Kerr parameters (spin at the moment of collapse; Cyg X-1 has a* = 0.998).
2. Dilution: for a comoving fluid ω ∝ a⁻². Therefore:
   - during inflation (ω/H) ∝ e^{−2N};
   - afterwards it scales as ∝ a⁻¹ (radiation era) and ∝ a^{−1/2} (matter era);
   - combine these to get (ω/H)₀.
3. Compare with Planck's bound (ω/H)₀ < 7.6×10⁻¹⁰.

**Expected result.** (ω/H)₀ ~ e^{−2×60} ≈ 10⁻⁵² times O(1). That is 40+ orders of
magnitude below the bound, so the parent's spin is erased. Report it as
"prediction: no detectable axis".

**Observations to discuss honestly.**
- Planck's large-scale dipolar asymmetry: A = 0.070 (+0.032/−0.015), not
  significant after look-elsewhere correction.
- Shamir's galaxy-spin asymmetry in JADES: 158 vs 105 galaxies, p = 0.0007.
  This is contested; independent Bayesian re-analyses find isotropy.
- Neither can be attributed to a parent spin if the estimate above holds.
- Mention that a bounce can generate a dipolar asymmetry by a different,
  non-rotational mechanism (Agullo, Kranas & Sreenath 2021). This links to WP5.

---

## 8. WP5: the bounce's imprint on the CMB

**Question.** Does the LQC bounce suppress CMB power on the largest scales, as
observed? Is the required scale consistent with WP3b's N_tot for a black-hole parent?

**Primordial spectrum.** Two routes; use both.
1. **Planck's phenomenological cutoff templates.**
   - Exponential: P(k) = A_s(k/k*)^{n_s−1}[1 − exp(−(k/k_c)^λ)].
   - Kinetic-domination (physically closest to a kinetic-dominated bounce):
     Υ_kin(y) = (π/16) y|C_c(y) − D_c(y)|², with y = k/k_c.
2. **Analytic LQC spectrum** (Guillén, Langer, Mena Marugán et al. 2026,
   arXiv:2605.14657).
   - Two parameters: a₀ and k₀ = a₀H₀ = √(8πρ_c/(3a₀⁴)).
   - Accurate to < 1% near the suppression scale.
   - k₀ is set by N_tot, which ties this spectrum directly to WP3b.

**Pipeline.**

```
P(k) table ─► camb: pars.set_initial_power_table(k, pk) ─► C_ℓ^TT (ℓ = 2…2500)
          ─► compare with data/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt
             (ℓ, D_ℓ, −ΔD_ℓ, +ΔD_ℓ: use the asymmetric errors at ℓ < 30)
          ─► S_1/2 = ∫_{−1}^{1/2} C(θ)² d cosθ from the C_ℓ (Legendre sum)
```

**Numbers to compare with.**
- Suppression expected for k ≲ 3.6×10⁻³ Mpc⁻¹ (ℓ ≲ 30), with k° ≈ 3.6×10⁻⁴ Mpc⁻¹
  (Ashtekar et al. 2020).
- S₁/₂ observed: 1142–1209 μK⁴ (masked), against ~42 000 in the standard
  full-sky model and ~14 300 in the LQC full-sky model (their Table).
- τ shifts from 0.054 to 0.060 in the LQC fit.
- The lensing anomaly A_L = 1.18 ± 0.065 has **largely disappeared**
  (Planck PR4: 1.039 ± 0.052; ACT finds no excess). Do not rely on it as
  motivation.

**Method.**
1. Grid over k_c (or a₀), keeping the other ΛCDM parameters at Planck best fit.
2. Compute Δχ²(ℓ < 30) and S₁/₂, and translate the best-fit k_c into N_tot.
3. Check that N_tot overlaps the WP3b band N_tot > N_min(M).
4. Optional, and where the Ryzen helps: a full cobaya MCMC with the Planck
   likelihoods. That is days on the i5 and hours on 32 threads.

**Validation.**
- With the cutoff removed, CAMB must reproduce the Planck best-fit theory file
  (`…minimum-theory_R3.01.txt`, D₂^TT = 1016.7 μK²) to < 1%.

**Deliverables.**
- Figure C_ℓ^TT at ℓ < 50, with data, ΛCDM and LQC curves.
- Table of Δχ² and S₁/₂.
- The k_c → N_tot mapping overlaid on the WP3b figure.

**Honest framing.** The low-ℓ anomaly has p ≈ 1% after look-elsewhere
correction. An LQC fit that improves it is *consistent with* a bounce, not proof.
And it is not specific to a black-hole parent: any LQC bounce gives it.

---

## 9. WP6: Smolin's cosmological natural selection

**Question.** If universes reproduce through black holes, the constants of
nature should maximise black-hole production. Smolin's sharpest test is a
maximum neutron-star mass.

**The prediction and the data.**

| Year | Smolin's criterion | Source |
|---|---|---|
| 2004 | M_max ≈ 1.5 M☉ ("anything higher would be troubling") | hep-th/0407213 |
| 2006 | M_max ≈ 1.6 M☉ | hep-th/0612185 |
| 2012 | M_max < 2 M☉; "~2.4 M☉ would be inconsistent" | arXiv:1202.3373 |

| Neutron star | Mass (M☉) |
|---|---|
| PSR J1614−2230 | 1.97 ± 0.04 |
| PSR J0348+0432 | 2.01 ± 0.04 |
| PSR J0740+6620 | 2.08 ± 0.07 |
| PSR J0952−0607 | 2.35 ± 0.17 (implies M_max > 2.09 M☉ at 3σ) |

**Calculation.** The joint probability that PSR J0952 and J0740 are both below
2 M☉ is 0.0025 (Gaussian errors), i.e. about 3σ. Refine this with the
equation-of-state-marginalised bound of Romani et al.

**Conclusion to write.** Natural selection is falsified in its published form.
**Important:** black-hole cosmology does *not* require natural selection.
Falsifying it does not falsify the baby-universe origin; it removes one
proposed way to test it.

Critiques to cite:
- Vilenkin 2006: raising Λ would raise black-hole production.
- Rothman & Ellis 1993.
- Silk 1997.

---

## 10. Thesis outline (chapters)

1. **Introduction:** the question, the Norbi hypothesis, what "testing" means here.
2. **Background:**
   - general relativity, black holes and Hawking radiation;
   - loop quantum cosmology and the bounce;
   - inflation;
   - the CMB;
   - black-hole cosmology literature (Pathria, Frolov–Markov–Mukhanov, Smolin, Popławski, Gaztañaga).
3. **The simulator:** the v3.2 code, validation against literature (the
   `runs/2026-09-28` campaign), and the causality result (why "Hawking radiation
   is the baby universe's edge" fails).
4. **Inflation after the bounce (WP1)**, including the energy budget.
5. **Anisotropy (WP2).**
6. **Curvature and the edge of the baby universe (WP3, WP3b)**: the novel chapter.
7. **The parent's spin (WP4).**
8. **CMB imprint (WP5).**
9. **Cosmological natural selection (WP6).**
10. **Conclusions:** the scorecard against the pre-registered table in §0,
    limitations, and what future data would change the verdict:
    - CMB-S4 / LiteBIRD on r and low-ℓ polarisation;
    - DESI final Ω_K;
    - more massive pulsars.

Appendices: units and constants; numerical methods and convergence; data
provenance (`data/observations.json`); code availability.

---

## 11. Hardware

| Task | i5-2500S (4 cores, 8 GB) | Ryzen 9 5950X (32 threads, 48 GB) |
|---|---|---|
| WP0–WP4, WP6 (ODE scans) | minutes | seconds |
| WP5: one CAMB run | a few seconds | ~1 s |
| WP5: grid of ~1000 CAMB runs | ~1–2 hours | ~5 minutes (32 in parallel) |
| WP5: full cobaya MCMC with Planck likelihood | days | hours |

**Recommendation:** develop everything on the i5, and move only the optional
WP5 MCMC to the Ryzen.

---

## 12. Risks and how to handle them

| Risk | Mitigation |
|---|---|
| A reviewer says "this is just LQC, not black-hole cosmology" | WP2's initial shear and WP3b's N_min(M) come from the black-hole parent; that is the specific content. |
| ACT's n_s = 0.974 disfavours Starobinsky at 2–3σ | Report both Planck and ACT; mention α-attractor potentials as an alternative (one extra WP1 run). |
| The measure problem (no unique probability over bounce initial data) | Report thresholds and fractions under an explicitly stated measure, as the literature does. |
| Full Kantowski–Sachs LQC is hard | Bianchi I proxy with black-hole initial shear; discuss the Ashtekar–Olmedo–Singh results qualitatively. |
| Unverified numbers | The `verified: false` entries in `data/observations.json`: read the primary paper before citing any of them. |
| Over-claiming | The pre-registered table in §0; say "consistent with", never "evidence for", unless Δχ² is significant after look-elsewhere. |

---

## 13. References (core set)

1. Ashtekar & Sloan, PLB 694, 108 (2010); GRG 43, 3619 (2011), arXiv:1103.2475
2. Bonga & Gupt, GRG 48, 71 (2016), arXiv:1510.00680; PRD 93, 063513 (2016)
3. Zhu, Wang, Cleaver, Kirsten & Sheng, PRD 96, 083520 (2017), arXiv:1705.07544
4. Linsefors & Barrau, PRD 87, 123509 (2013); CQG 32, 035010 (2015)
5. Corichi & Singh, arXiv:0905.4949; Gupt & Singh, PRD 85, 044011 and 86, 024034 (2012)
6. Ashtekar, Pawlowski, Singh & Vandersloot, PRD 75, 024035 (2007); Gordon, Li & Singh, PRD 103, 046016 (2021)
7. Liddle & Leach, PRD 68, 103503 (2003)
8. Planck 2018 VI, VII, X: A&A 641, A6/A7/A10 (2020)
9. BICEP/Keck, PRL 127, 151301 (2021)
10. DESI DR2, PRD 112, 083515 (2025); ACT DR6, arXiv:2503.14452, 2503.14454
11. Saadeh et al., PRL 117, 131302 (2016); Planck 2015 XVIII, A&A 594, A18
12. Ashtekar, Gupt, Jeong & Sreenath, PRL 125, 051302 (2020); Agullo, Ashtekar & Nelson, PRL 109, 251301 (2012)
13. Guillén, Langer, Mena Marugán et al., arXiv:2605.14657 (2026)
14. Lewandowski, Ma, Yang & Zhang, PRL 130, 101501 (2023)
15. Smolin, hep-th/0612185, arXiv:1202.3373; Romani et al., ApJL 934, L17 (2022); Fonseca et al., ApJL 915, L12 (2021)
16. Popławski, PLB 694, 181 (2010), arXiv:1910.10819; Gaztañaga et al., PRD 111, 103537 (2025)
17. Wald, PRD 28, 2118 (1983)
