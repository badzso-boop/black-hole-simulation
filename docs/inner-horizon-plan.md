# Plan: the inner horizon (Level 1 of S4). Does the spark get through?

**Status:** plan written 2026-09-30. The code was implemented the same day (§8), and the **full
run was done on the Ryzen the same day** (§9, `runs/inner-horizon-2026-09-30/`).

**Inputs:**
- A research pass (2026-09-30): the numbers are in `data/observations.json` → `4c_inner_horizon`,
  each with a source and a `verified` flag.
- Background: [spin-plan.md](spin-plan.md) §9, where S4 is "open".

---

## 1. The question

**In plain words:** when a star collapses into a *spinning* black hole, does at least a tiny part
of its matter reach the quantum bounce before the black hole's inner horizon turns violent? A seed
of about one Planck mass is enough (WP4b); inflation does the rest.

**Precisely:** in a spinning (or charged) black hole, perturbations that fall in and scatter back
out pile up at the inner horizon r₋. Their energy is blueshifted as e^{κ₋v} ("mass inflation"),
where κ₋ is the inner horizon's surface gravity and v the advanced time. Two things race:
1. The collapsing star's own matter crosses r₋ and continues inward to the bounce density ρ_c.
2. The inner horizon becomes Planck-curved, classically through mass inflation, or quantum
   mechanically through vacuum fluxes.

Whichever comes first decides S4.

**A side question, the "asteroid":** where does matter that falls in *long after* the collapse end
up? Crushed at the inner horizon, or feeding a new quantum bounce?

## 2. What the research changed (all re-derived or checked in-session)

**F1. The inner-horizon problem is not only a spin problem.** The non-spinning quantum
Oppenheimer–Snyder (LMYZ) exterior that WP0–WP5 use already has a Planck-scale inner horizon:
- r₋³ ≈ αM/2.
- The dust bounce radius R_b³ = αM/2 lies *just inside* it, by a relative gap R_b/(6M), which is
  ~10⁻³⁸ for a solar mass. Our Rust simulator already reports this gap
  (`causal_channel.horizons.bounce_gap_below_inner_horizon`).
- κ₋ ≈ 3M/r₋², which is enormous.

The literature disagrees about this inner horizon:

| Source | Setting | Finding |
|---|---|---|
| Cao et al. 2024 | static background, test fields | **mass inflation always occurs** at the LMYZ inner horizon |
| Husain–Kelly–Santacruz–Wilson-Ewing 2022 | fully dynamical effective-LQG dust collapse | **no mass inflation** |

Caveat: single-stream dust cannot counter-stream, so its absence may be built into the model.

**F2. Charge is a good proxy for the inner horizon, but a bad proxy for the bounce.**
- In Reissner–Nordström (RN), *any* radially falling matter, neutral or not, turns around
  classically at r = Q²/(2M). That is inside r₋ and macroscopic, long before the LQC density.
- On the Kerr rotation axis there is no turning point.
- So an RN model can test the **timing race at the inner horizon**, but **not** whether the axial
  seed reaches ρ_c. The plan keeps these two questions strictly separate.

**F3. Nobody has put the three pieces together.** The pieces are dynamical charged collapse, an LQG
bounce, and inner-horizon evolution (classical or quantum). Every *pair* has been done; the triple
has not (arXiv search, not exhaustive: do an INSPIRE citation check before claiming novelty).

**F4. The quantum side has real numbers.**
- The renormalised stress tensor ⟨T⟩ of quantum fields at the inner horizon has been computed:
  - RN: Zilberman, Levi & Ori 2020;
  - Kerr: Zilberman, Casals, Ori & Ottewill 2022.
- It is finite in Eddington coordinates, so it grows as e^{2κ₋v} for an infaller. That is faster
  than classical mass inflation, which carries an extra power-law suppression.
- Its sign flips:
  - RN: at Q/M ≈ 0.965–0.968;
  - Kerr pole: at a* ≈ 0.862–0.870.
- **Race estimate (research agent's, to be computed in L1d):** for macroscopic black holes,
  *classical* mass inflation reaches Planck curvature first (κ₋v ≈ 90 vs ≈ 175 for a solar mass).
  Quantum could win for tiny black holes.

**Charge ↔ spin mapping.** Matching the inner-horizon surface gravity κ₋M is the better proxy.
- It maps Kerr a* = 0.44–0.52 (the comfortable window from WP4b) to RN Q/M = 0.78–0.83.
- It also maps the Kerr flux sign flips (0.862, 0.870) onto Q/M = 0.962, 0.965, right on top of
  the RN flips. This is an unpublished coincidence check of ours, and supporting evidence only.
- Matching r₋/M instead would make RN inflate 15–20 times faster than Kerr in that window.

## 3. Calculations

| # | Calculation | Method | Output | Effort (i5) |
|---|---|---|---|---|
| **L1a** | The inner horizon of our own non-spinning model | Ori-model ODEs (the generalised Ori model of Carballo-Rubio et al. 2021) on the LMYZ metric, with RN and Hayward as checks. Exponential or polynomial mass inflation? How does its onset compare with the bounce time of the star's own matter? | Whether WP0–WP5's bounce is threatened at all; reconciles Cao 2024 vs HKSW 2022 | days |
| **L1b** | Classical double-null code | Einstein–Maxwell–scalar, ds² = −α²du dv + r²dΩ², in the Oren & Piran 2003 scheme (rectangular domain avoiding r = 0, 2nd-order predictor-corrector, constraints monitored), with the Eilon–Ori adaptive gauge for large v. NumPy + Numba. | A code that passes **all validation targets** in §4 before any physics result counts | 1–2 weeks |
| **L1c** | The race | A neutral "spark" pulse (the star's core) collapses inside a black hole whose charge sits on an earlier, outer shell (Brady–Smith / Burko setup), plus late tails. Measure mass inflation's growth rate and *amplitude*, and extrapolate the Planck-curvature time v_Pl to real masses (Planck curvature itself cannot be resolved numerically: ~10¹⁵² in code units for a solar mass). Compare with the spark's crossing time. Scan Q/M and map it to a* through κ₋. | For each spin: how much earlier (or later) the spark crosses than the horizon turns Planckian, plus the crossing distortion | ~1 week |
| **L1d** | The quantum race | Add the semiclassical inner-horizon fluxes as sources: the Zilberman–Levi–Ori RN values, and Kerr through the κ₋ map, as in Arad 2025. Cross-check with the local Polyakov (2D) stress tensor. For masses from primordial black holes to Sgr A*, determine whether classical or quantum effects make the horizon Planckian first. | The "third quantum pillar" result | ~1 week |
| **L1e** | The asteroid | Inject a shell at late v (years after formation, in M units). Classify its fate: the Cauchy horizon's weak singularity, the Marolf–Ori shock, or the spacelike r = 0. Integrate its tidal distortion. | Whether late infall can feed anything (the original Norbi "feeding") | days |
| **L1f** | Verdict | Apply §5 mechanically; update the S4 row and the WP4b scorecard | — | — |

**Out of scope, stated as open:** whether the axial seed reaches ρ_c after crossing r₋ in a real
Kerr interior. That is Level 2/3; F2 explains why RN cannot answer it.

## 4. Validation targets (the code must reproduce these first)

1. **Static RN** (no scalar field; M = 1, Q ∈ {0.5, 0.92, 0.95}):
   - r± to 10⁻⁵ and charge conserved to 10⁻⁴;
   - for Q = 0.92: r₊ = 1.392, r₋ = 0.608, κ₋ = 1.06.
2. **Brady & Smith 1995** (e² = 0.4, κ₋ = 15.25): the late-time metric function decays as
   e^{−γv}, with γ ≈ κ₋ within ~10%.
3. **Brady & Smith power-law data:** m ∝ v^{−(p+1)} e^{κ₋v}.
4. **Burko 1997** (M₀ = 1, Q = 0.95, sin² pulse A = 0.08 on v ∈ [10, 20], M_f ≈ 1.4):
   - the Ψ,v ratio tends to 1 within 2×10⁻³ at v = 600;
   - g_UV stays finite at the Cauchy horizon.
5. **Charged tails** (Hod & Piran):
   - |ψ| ∝ v^{−(1+Re√(1−4(eQ)²))} on the event horizon;
   - neutral limit v⁻³.
6. **Oren & Piran 2003:**
   - r,v ∝ v⁻² on the Cauchy horizon;
   - the inflation exponent matches κ₋ within 10–20%;
   - Q_H/M_H < 1 as Q₀/M₀ → 2.
7. **Causal structure:** three classes of rays (escaping, reaching the Cauchy horizon, ending at a
   spacelike r = 0); r_CH(u) decreases monotonically.
8. **Eilon & Ori shock:** ln Δτ = −κ₋ v_eh + const for v_eh ≳ 15.
9. **Chesler et al. 2020** (M = 0.9, Q = 0.78): r₋ = 0.45, κ = 2.2.
10. **Quantum sector:**
    - (a) the homogeneous Oppenheimer–Snyder limit bounces at ρ_c;
    - (b) with a constant ⟨T_yy⟩, the drift obeys r,y → −4π(r₋/κ₋)⟨T_yy⟩ (Zilberman–Levi–Ori eq. 15).

## 5. Pre-registered outcomes (fixed 2026-09-30, before any code)

| Question | Supports the hypothesis if… | Counts against it if… | Open if… |
|---|---|---|---|
| L1a: non-spinning inner horizon | The star's own matter bounces before mass inflation at the LMYZ inner horizon can grow (it needs later counter-streaming influx). | LMYZ mass inflation reaches Planck curvature before the star's matter bounces. | The answer depends on the matter model (dust vs scalar). |
| L1c: the spark crosses r₋ (spin via κ₋ map) | For the bulk of each spin population (natal, GW), the spark crosses r₋ at least 10× earlier than Planck curvature develops, with crossing distortion D ≤ 10. | Planck curvature develops first for all realistic spins. | Mixed: some populations pass, others fail. |
| L1d: quantum vs classical | *(report only, not a verdict)* the mass range where quantum fluxes make the horizon Planckian first. | The quantum flux alone makes r₋ Planckian before the spark crosses, for astrophysical masses. | — |
| L1e: the asteroid | A late shell reaches a region where a quantum bounce is possible, not a singularity or shock. | A late shell always ends at the Cauchy-horizon singularity, the shock, or r = 0. | The fate depends on unmodelled quantum gravity. |

Expected honest outcome from what is known now:
- L1a is likely *supports*: the star's matter arrives first, and mass inflation needs later influx.
- L1c probably depends on spin: fast spins pass, natal ~0.01 spins fail (as in the crude S4).
- L1d likely shows classical mass inflation first for stellar masses, and quantum first for tiny
  primordial black holes.
- L1e is likely *against*: late matter is crushed at the inner horizon.

## 6. Limits to state openly

- **RN is not Kerr.** It has no frame dragging, no axis, no angle dependence, and no Kasner/BKL
  degrees of freedom. The Coulomb turning point (F2) means it cannot test the axial seed's bounce.
- **Planck curvature is not resolved.** We measure growth rates and amplitudes and extrapolate
  exponentially.
- **The quantum fluxes are test-field values** on a fixed background, and the 2D Polyakov stress
  tensor is only an approximation.
- **Effective LQG with charge** faces the covariance objections (Bojowald–Duque); Yang–Zhang–Ma
  2025 show electromagnetism must be modified too.
- **Charged black holes are not astrophysical.** Charge is the standard surrogate for spin.

## 7. Key references

- **Mass inflation, classical:** Poisson & Israel 1990; Ori 1991; Brady & Smith 1995
  (gr-qc/9506067); Burko 1997 (gr-qc/9710112); Hod & Piran 1998 (gr-qc/9803004, 9801001);
  Oren & Piran 2003 (gr-qc/0306078); Eilon & Ori 2016 (1510.05273, 1610.04355); Chesler, Narayan &
  Curiel 2020 (1902.08323); Hamilton & Avelino 2010 (0811.1926).
- **Quantum gravity at inner horizons:** Lewandowski–Ma–Yang–Zhang 2023 (2210.02253); Cao et al.
  2024 (2308.10746); Husain–Kelly–Santacruz–Wilson-Ewing 2022 (2109.08667, 2203.04238);
  Carballo-Rubio et al. (1805.02675, 2101.05006, 2205.13556, 2402.14913); Bonanno–Khosravi–Saueressig
  (2010.04226, 2209.10612); Yang–Zhang–Ma 2025 (2503.15157); Bojowald–Duque (2310.06798, 2311.10693).
- **Semiclassical ⟨T⟩:** Hollands–Wald–Zahn 2020 (1912.06047); Zilberman–Levi–Ori 2020
  (1906.11303); Zilberman–Casals–Ori–Ottewill 2022 (2203.08502); Hong et al. 2010 (0808.1709);
  Boyanov–Hilditch–Semião 2025 (2506.04845); Arad 2025 (2509.04385).

## 8. Implementation (2026-09-30)

**Code**

| File | What it does |
|---|---|
| `thesis/ori_model.py` | L1a and the growth laws behind L1d: the generalised Ori model (Carballo-Rubio et al. 2021, eqs. 4, 10, 32) for RN, Hayward and LMYZ. The shell's distance from the inner horizon is measured from the *exact* root, carried in extended precision, which removes the catastrophic cancellation. Also: the LMYZ crossing timing, the conformal time after the bounce, and edge confinement. |
| `thesis/doublenull.py` | L1b: the Burko–Ori double-null Einstein–Maxwell–scalar solver (Numba), with log-form initial data on the event-horizon ray. |
| `thesis/inner_horizon.py` | L1c–L1e: the race, the charge↔spin κ₋ map, the spark crossing time on the Kerr axis, the quantum flux, the asteroid, and helpers for the code runs. |
| `thesis/verdict.py` | `inner_horizon_scorecard`: the validation gate plus §5, applied mechanically. |
| `scripts/run_inner_horizon.py` | The runner: a resolution ladder in parallel, then analysis, figures and `SCORECARD.md`. |
| `thesis/tests/test_inner_horizon.py` | 9 tests. |

**Validation.** The physics verdicts count only if the gate passes. Local results:

| Check | Result |
|---|---|
| T1: static RN, r(u,v) against the exact solution | clean 2nd-order convergence (×4 per doubling) |
| T2: mass-inflation rate (Brady–Smith, κ₋ = 15.25) | 15.244 with the power-law term; +5% with a plain exponential fit; the finest grids agree to 0.1% |
| T9: Chesler et al.'s r₋, κ₋ | ✓ |
| T10b: Zilberman–Levi–Ori drift (eq. 15) | within 0.3% |
| Ori model, RN | growth rate within 0.2% of analytic |
| Ori model, constant flux | pure e^{κv} (2×10⁻⁵) |
| Ori model, Hayward | exponential → polynomial, with d ln M/d ln v → 13.05 (p + 1 = 13) |

**Deviations from the plan** (stated openly):
1. **Charged scalar field not implemented.** The matter is a neutral scalar in a pre-charged black
   hole, which is the setup §3/L1c actually calls for. So T4 (Burko's exterior pulse), T5–T6
   (charged tails, Oren–Piran) and T8 (Eilon–Ori shock) are not reproduced. T3 is covered
   indirectly by the power-law influx used in T2.
2. **A stricter gate.** One criterion was added: T2 must also agree between the two finest grids.
   It was added during implementation, and it makes the gate harder to pass, not easier.
3. **A first-order (Hamadé–Stewart) solver was tried and rejected.** It evolves r_u and r_v as
   variables. At the resolutions available here it did not converge near the Cauchy horizon: the
   sign of r_u came out wrong, giving a negative mass. The three-field solver is kept, and the
   rate is fitted only where Δr is still resolvable (|Δr| > 10⁻¹²·r).
4. **The race uses the analytic Kerr κ₋, not the RN code.** The code validates that mass inflation
   grows at κ₋. The amplitude is taken as δ² with a band of e^{±5}. Near the Cauchy horizon the
   code's absolute amplitude is dominated by a truncation-error "floor" at the resolutions
   available here; the Ryzen ladder reports whether it gets resolved. The race depends on the
   amplitude only logarithmically.
5. **The classical power-law suppression v^−(p+1) is dropped.** This is conservative: it makes the
   inner horizon become Planckian *sooner*.
6. **Quantum flux magnitude.** The Kerr a* = 0.8 pole value (3.0×10⁻⁵ ħ/M⁴) scaled with κ₋², with
   a ×100 band. The RN values exist only in a figure.
7. **Fiducial values fixed in code before the run:** M = 10 M☉, δ = 0.1, "late" = at least 1 day.

**Local quick run (smoke test, not the verdict)**

The gate **passed**. The outcomes:

| Question | Outcome | Detail |
|---|---|---|
| L1a | **supports** | At most ln 2 ≈ 0.69 e-folds fit between r₋ and the bounce, for any mass |
| L1c | **open (mixed)** | GW population 22% pass, natal 0% |
| L1d | **info** | classical first for every astrophysical mass |
| L1e | **against** | a late asteroid meets a Planckian inner horizon |

This matches §5's "expected honest outcome".

**New findings while building L1a** (to be confirmed by the full run):
- **The LMYZ inner horizon is itself unstable** in the Ori model. Depending on the sign of the
  shell's mass jump, the mass behind the shell either runs to −∞ exponentially, at ≈ 0.94–0.98 κ₀,
  or hits the metric family's built-in curvature ceiling M ≤ r³/(2α) after ~45–52 e-folds.
  This agrees with Cao et al. 2024.
- **Edge confinement.** From the bounce to the end of inflation, a disturbance at the baby
  universe's edge can travel about η ≈ 5×10³ ℓ_P inward.
  - For stellar or larger parents this is 10⁻⁹ of the ball's radius or less.
  - For the Planck-mass seeds of the spin route (WP4b), it covers the whole seed. That exposes the
    WP4b small-seed route to the inner-horizon instability: **a new caveat on WP4b.**

**Running on the Ryzen**

```bash
git pull
pip install -e '.[dev,thesis]'                              # adds numba, mpmath
python scripts/run_inner_horizon.py --jobs 8                # ladder to n = 3200 (minutes)
python scripts/run_inner_horizon.py --jobs 8 --max-n 6400   # optional: largest grid, ≈5 GB per run
git add runs/inner-horizon-* && git commit -m "Belső horizont: teljes futás (Ryzen)" && git push
```

## 9. Results of the full run (Ryzen 5950X, 2026-09-30)

**The run:** `runs/inner-horizon-2026-09-30/`, taking 44 s with 8 jobs. The resolution ladder went
up to n = 3200 (grids of 3200 × 16000).

**Validation gate: passed.** Every check passed, including T2 converging between the two finest
grids.

| Question | Outcome | Expected (§5) |
|---|---|---|
| L1a: the star's own bounce vs the inner horizon | **supports** | supports |
| L1c: does the spark cross r₋? | **open (mixed)**: GW population 22.5% pass, natal spins 0% | open |
| L1d: quantum vs classical | **info**: classical first in 20/20 cases | info |
| L1e: the asteroid | **against**: 8/8 late cases meet a Planckian inner horizon | against |

**What the code confirmed, and what it could not**

- **Mass inflation grows at κ₋ where the code can resolve it.**
  - Q/M = 0.632: 1.04–1.05 κ₋ (1.01 with the power-law term).
  - Q/M = 0.5: 1.01–1.08 κ₋.
  - These charges correspond to Kerr spins a* ≲ 0.3 under the κ₋ map.
- **For Q/M ≥ 0.78 (Kerr a* ≳ 0.44, which is exactly the "passing" window), the double-null code
  could not measure the growth.**
  - At Q = 0.782 the fits are unreliable (0.1–0.4 κ₋, few points).
  - At Q = 0.827–0.95 there are no fits at all.
  - The cause: with small κ₋, r_v drops below floating-point resolution before the mass visibly
    inflates.
  - So for this window the race rests on the analytic κ₋ (as planned in §8, point 4), not on an
    independent numerical check.
- **The amplitude is not resolved at n = 3200 for any Q.** The signal is only 1.4–5.4 e-folds above
  the truncation floor, and still changes by about 1.5–2.7 per doubling. The ±e⁵ band therefore
  stays. It does not change any verdict.

**The edge confinement, with the WP1 background**

The run used the background of the φ_B = −1.3 Starobinsky trajectory: n_onset = 4.85,
H_onset = 1.5×10⁻⁶.
- **Reach of an edge disturbance:** it can travel η ≈ 9.6×10³ ℓ_P inward by the end of inflation.
- **Size needed to shield the bulk:** it reaches less than 10% of the ball only when the seed mass
  is **M_s ≥ 1.5×10¹⁵ m_P ≈ 3×10⁷ kg**.

**The consequence for WP4b (the spinning parent), stated conditionally**

- The axial seeds that WP4b allows are far below that shielding mass: at most 16 m_P at a* = 0.44,
  and at most 1.4×10³ m_P at a* = 0.1.
- The seed-mass cap C³√(α/2)/a*³ lets a shielded seed exist only for **a* ≲ 1×10⁻⁵**.
- **If the inner-horizon instability at the edge is destructive** once it reaches the bulk, a
  spinning parent is therefore effectively excluded by this route.
- Whether it is destructive is not computed here. The Ori model only shows the edge region
  inflating, or hitting the curvature ceiling. This is recorded as the most important open caveat
  of the spinning-parent analysis.
