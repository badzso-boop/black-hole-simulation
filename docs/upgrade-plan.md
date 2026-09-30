# Upgrade plan: code and thesis (after the 2026-09-30 critical review)

**Status:** plan, 2026-09-30. Nothing below is implemented yet.
**Basis:** [critical-review.md](critical-review.md); section references (§) point there.

## 0. Rules for this upgrade

1. **Pre-register before running.**
   - Every new calculation (Phase B) gets a §0-style outcome table, dated, **before** its first run.
   - The table goes in this file or the WP's own plan.
2. **Keep fixes and threshold changes apart.**
   - *Bug fix:* the code did not implement its own pre-registered rule (L1e, §4.3). Fix it and log it
     as a bug.
   - *Data update:* new measurements (WP6 masses, §3.8). Re-run under the **unchanged** rule and log
     old and new values side by side.
   - *Criterion change:* a pre-registered criterion rests on a wrong input (the "natural N_tot"
     band, §3.3). Log the reason in `docs/thesis-progress.md` and keep the old verdict visible next
     to the new one.
3. **Validation stays as it is:** every new feature is tested against an independent analytic or
   literature value.
4. **Language:**
   - commit messages and code comments are Hungarian;
   - `docs/*.md` notes for the author are English.

---

## Phase A: corrections and relabelling

Roughly 2–3 days on the i5. No new physics, no Ryzen.

| # | Task | Files | Test / acceptance |
|---|---|---|---|
| A1 | Update the neutron-star masses (J1614 1.937 +0.012/−0.013; J0348 1.806 ± 0.037; J0952 2.35 ± 0.11) with sources. Add a **leave-one-out** sensitivity and Smolin's ~2.4 M☉ reading to `cns.run()`. | `data/observations.json`, `thesis/cns.py`, `thesis/verdict.py` (text only) | New test: with the current masses P = 9.3e-5 (3.7σ) and 0.13 without J0952 (independent hand calculation, §3.8). Verdict still under the 3σ rule. |
| A2 | Relabel `efolds_distribution_peak` as **N_infl**. Remove 145 as an N_tot ceiling. Replace `LQC_NATURAL_N_TOT` with two sourced numbers: Zhu 2017's observational lower bound (141) and the N_tot implied by Linsefors–Barrau's N_infl ≈ 145 (N_onset + 145 + N_post, computed from WP1's history). | `data/observations.json`, `thesis/curvature.py`, `thesis/spin.py` | Test: implied N_tot = N_onset + N_infl + N_post, with the parts taken from `history.post_inflation`. |
| A3 | Rewrite WP3b's verdict as the statement actually computed: "N_edge(M) < N_hor for every M, with margin X". Keep the old pre-registered row visible and mark it "criterion rested on a mislabelled input" (rule 2c). | `thesis/verdict.py`, `docs/thesis-progress.md` | — |
| A4 | Fix L1e's mechanical rule to follow the plan's §5: Planck curvature → **neutral**; "against" only if a classical code run shows the shell ending at the singularity, shock or r = 0 *below* Planck curvature. Log it as a bug fix. | `thesis/verdict.py:457` | Test: a synthetic "meets Planck curvature" input gives neutral. |
| A5 | WP2: report Ω_σ as the band [0, 0.5625]. Keep 0.2 only as a labelled "classical extrapolation", and state that f(r_b) = 1 in LMYZ. | `thesis/anisotropy.py` docstring, `verdict.py` text, docs | Test: f_LMYZ(r_b) = 1 to 1e-12 for three masses (analytic identity). |
| A6 | Fix `rotation.py:10`'s docstring range (9e-8 for the 5.1e11 kg parent; 1e-14 and below for stellar masses). | `thesis/rotation.py` | — |
| A7 | Relabel the EHT numbers as a "units/GR sanity check". Note that M87\*'s δ = 0 is circular. | `README.md`, `CLAUDE.md`, `docs/are-we-in-a-black-hole.md` | — |
| A8 | Add a **"discriminates BH origin?"** column to the scorecard (WP1–WP6, 4b, L1a–e). | `thesis/verdict.py`, `scripts/run_thesis.py` | The scorecard markdown shows the column. |
| A9 | Put the inflaton-initial-state assumption (§3.1) and the matching problem (§3.2) in every affected verdict's text and in the limitations list. | `verdict.py`, `docs/thesis-progress.md` | — |
| A10 | Re-run `scripts/run_thesis.py` (~100 s) into `runs/thesis-<date>/`, and update the scorecard in CLAUDE.md. | — | All thesis tests pass. |

---

## Phase B: new calculations, in priority order

### B1. Where does the inflaton come from? The two-fluid bounce (§3.1). Most important.

- **Question:** starting from what a real black-hole interior contains (dust, with the inflaton at
  or near its minimum), does the bounce produce ≥ 60 e-folds?
- **Method:**
  - Effective LQC with ρ = ρ_dust + φ̇²/2 + V(φ), each fluid conserved separately. `inflation.py`
    already has the structure; add the dust term.
  - Scan the dust fraction at the bounce, f_d ∈ [0, 1), and the field's initial data near its
    minimum.
  - Then look for mechanisms that excite the field, starting with a literature pass: gravitational
    particle production at the bounce, non-minimal coupling ξRφ² (R changes sign through the LQC
    bounce), and Higgs inflation.
- **Validation:** f_d = 0 reproduces WP1; f_d → 1 reproduces the analytic dust bounce
  ρ(τ) = ρ_c/(1 + 6πρ_cτ²).
- **Pre-registered outcomes (fill in before running):**
  - *supports* if some mechanism that follows from the collapse gives ≥ 60 e-folds for a
    non-negligible set of parent states;
  - *against* if ≥ 60 e-folds needs the field placed on the plateau by hand;
  - *open* if it depends on an unconstrained coupling.
- **Effort:** 1–2 weeks, including the literature pass. Compute runs on the i5 in minutes.

### B2. Matching an inflating ball to the LMYZ exterior (§3.2)

- **Question:** does a scalar-field ball need a thin shell at its edge? Does LQC's violation of the
  null energy condition get around the Farhi–Guth–Guven singularity argument?
- **Method:** Israel junction conditions for a Friedmann interior with P ≠ 0 against the LMYZ
  exterior. Literature: Blau–Guendelman–Guth 1987; Farhi–Guth–Guven 1990; any LQC-bubble papers.
- **Output:** a chapter section. A calculation only if the literature leaves a gap.
- **Effort:** about 1 week.

### B3. WP4b under edge confinement (§4.1)

- **B3a.** Add the bound M_s ≥ 2(η/ε)³/α to `spin.allowed()` and the S1/S2 fractions, with
  ε ∈ {1, 0.1}. η comes from `ori_model.conformal_time_to_end_of_inflation`.
  - Test: a*_max = 1.9e-4 (ε = 1) and 1.9e-5 (ε = 0.1) at C = 1.23 (§4.1 table, a hand calculation).
- **B3b.** Estimate the disturbance's **amplitude**: a 1-D linear perturbation launched from the
  ball's edge, propagated through the kinetic phase into inflation. Does it change the seed's local
  expansion by O(1) or by ≪ 1?
- **B3c.** For the axial seed inside an n = 3 polytrope, estimate the Grishchuk–Zel'dovich
  quadrupole from an O(1) density gradient on the seed's scale. This bound does *not* apply to the
  top-hat WP3b (§4.1 correction).
- **Pre-registered outcomes:**
  - *supports* if the amplitude is ≪ 1 **and** the Grishchuk–Zel'dovich condition leaves spin
    populations inside the allowed N_tot;
  - *against* if either one fails for all observed populations.

### B4. L1c without the D heuristic (§4.2)

- Replace D = M/r₋ with the integrated tidal strain along the axis, using the Ori/Burko tidal
  integrals through the crossing.
- Keep the pre-registered D ≤ 10 verdict as the headline and report the strain as a check, so the
  change does not look post hoc.
- Add a double-null run in which the spark is the **first** pulse and the horizons form dynamically.
  The Brady–Smith setup already supports this.

### B5. The Hawking lifetime to ~5% (§3.10)

- A MacGibbon-style f(M) with greybody-weighted, spin-dependent thresholds (MacGibbon 1991; Carr et
  al. 2010, Table 1) in `core/src/radiation/`.
- Target: τ(5.1e11 kg) within 5% of 13.8 Gyr.
- New Rust test against Carr et al.'s M* for three ages.

### B6. BH-specific initial state for the CMB perturbations (§3.7). Research item

- A literature pass plus an order-of-magnitude estimate: what spectrum does a stellar density
  profile leave at k ~ k_LQC e^{−N_tot}?
- Worth doing only if B1 produces inflation. Otherwise the question is moot.

### B7. Optional: a real EHT prediction (§3.9)

- Kerr shadow with spin and inclination (Johannsen & Psaltis 2010 fitting formula, or a ray-trace)
  for the catalog objects, with the EHT's calibration spread.
- Only if the author wants EHT in the thesis as more than a sanity check.

---

## Phase C: Ryzen runs

1. `python scripts/run_inner_horizon.py --jobs 8`, as already planned. Commit `runs/inner-horizon-*`.
2. After A4, re-run the inner-horizon scorecard only (cheap) so L1e uses the corrected rule.
3. After A1–A3, B1 and B3a, run the full `scripts/run_thesis.py` again.
   - The WP5c MCMC does **not** need re-running: none of the changes touch the CMB likelihood or the
     k_c → N_tot mapping.

---

## Phase D: the thesis text

**Proposed structure:**

1. **The question and the model:** state the model precisely, including the inflaton
   initial-state assumption.
2. **Norbi's three claims, one verdict each:**
   - bounce → baby universe: possible, but only non-spinning;
   - feeding: no classical path;
   - information in Hawking radiation: fails.
3. **Methods and validation:** the Rust simulator, the thesis package, the literature
   reproductions.
4. **Results per WP:** each with its pre-registered row, the result, and **whether it
   discriminates a BH origin**.
5. **Internal-consistency limits:** spin (WP4/4b), inner horizon (L1), matching (B2), inflaton
   origin (B1). This chapter carries the real findings.
6. **What would change the verdict** (falsifiability):
   - a BH-specific CMB imprint (B6);
   - a rotating effective-LQG collapse calculation;
   - Smolin's test standing or falling with PSR J0952−0607's mass.
7. **Conclusion:**
   > "A black-hole origin is not excluded in its non-spinning, homogeneous form. It relies on an
   > unexplained inflaton initial state, its signatures are erased by inflation, and Norbi's
   > specific extensions (feeding, information return) fail."

**Wording rules:**
- say "tension at Nσ", not "falsified", below 5σ;
- a consistency check is not "support";
- every number in the text comes from a committed `runs/` file.

---

## Order of work and time estimate

| Step | Content | Time |
|---|---|---|
| 1 | Phase A (A1–A10) | 2–3 days |
| 2 | Ryzen C1 (parallel) | minutes of compute |
| 3 | B3a, then B1 (the two decisive questions) | 2–3 weeks |
| 4 | B2, B4 | 2 weeks |
| 5 | B5, B6, optionally B7 | 1–2 weeks |
| 6 | Phase C3 re-run, then the thesis text (Phase D) | 3–4 weeks |

**Decision point after step 3.** If B1 finds no mechanism for the inflaton, the thesis's positive
half becomes "*if* the inflaton starts on its plateau, then…". That is still defensible, but the
conclusion must say so up front.
