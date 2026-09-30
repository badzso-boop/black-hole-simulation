# CLAUDE.md — context for AI coding sessions on this repo

Claude Code reads this file automatically. It carries the project context
between machines and sessions. Keep it current when the state below changes.

## What this project is

A simulator for the **"Norbi hypothesis"** (author: Norbi; original write-up in
`norbi_teljes_dokumentacio.pdf`, summarised in `docs/norbi-documentation-summary.md`).

The hypothesis:
1. A black hole's collapsed interior bounces (loop quantum cosmology, LQC) into
   an expanding baby universe.
2. Infalling matter feeds that universe.
3. Matter torn apart at its edge is what the outside sees as Hawking radiation,
   so information would come back out.

The author's underlying question is **"do we live in a black hole?"**, and they
are preparing a thesis on it.
- They are not a professional physicist.
- Explain results in plain language with concrete numbers, and let the code do the heavy math.
- They converse in **English**.

## Current state (v3.2 simulator + thesis calculations, 2026-09-29): read these first

- **README.md**: model, formulas, install, CLI, output schema 3.2.
- **summary.md**: development log, phases 1–16. Phase 9 explains why v2.0's results were artifacts.
- **docs/are-we-in-a-black-hole.md**: what the project can and cannot say about the big question.
- **docs/thesis-plan.md**: the six-calculation thesis plan, with pre-registered outcomes in §0.
- **docs/thesis-progress.md** + **runs/thesis-2026-09-29/SCORECARD.md**: the implemented
  calculations (`thesis/` package, `scripts/run_thesis.py`) and their results.
- **docs/critical-review.md** (2026-09-30): critical review. **docs/upgrade-plan.md**: its fixes
  (Phase A, done) and new calculations (Phase B; B1a and B3a done). The scorecard below already
  reflects them. The official verdict run (`run_thesis.py` with the Planck likelihoods) is due on
  the Ryzen.
- **runs/2026-09-28/ANALYSIS.md**: 71-run validation campaign and interpretation.
- **data/observations.json**: observational numbers with sources, plus a `verified` flag.
- **data/planck/**: Planck 2018 CMB spectra, with checksums.

**Model:**
- MacGibbon/Carr Hawking emission, with massive neutrino eigenstates.
- Oppenheimer–Snyder dust collapse with an LQC bounce at ρ_c ≈ 0.409 ρ_Pl.
- Lewandowski–Ma–Yang–Zhang 2023 exterior metric, with a mass gap of 0.83 m_P.
- Kerr spin, using Page 1976b f/g tables.
- Environment: CMB absorption on by default; accretion (constant, or Bondi with
  an Eddington cap; optional thin disk with Bardeen spin-up to 0.998); discrete infall events.
- Real-object catalog: `--object sgr-a|m87|cyg-x1|gw250114|gw150914|pbh-today`.
- A quantum-information toy model in Python (Page curve, Hayden–Preskill).

**Key results. Do not quietly contradict these; any change needs new evidence and must be documented.**
- **The Norbi claim fails.** The bounce lies below the inner horizon, so the
  baby universe is causally disconnected. The exterior spectrum is identical in
  Standard and Norbi mode, and the recovered information is 0 bits.
  - Never reintroduce an exterior Norbi signal without a real causal channel.
  - Any extension must use a geometry that actually connects inside and outside
    (for example the HKSW 2022 shock or a black-to-white-hole transition), and say so.
- **Real black holes grow today.** Above M_eq ≈ 5.6e22 kg they absorb more CMB
  than they radiate. Evaporation matters only for primordial black holes. The
  hole that evaporates today (5.1e11 kg) has a lifetime of 11.1 Gyr in this
  model; the literature value is 13.8, and the gap comes from the approximate
  species thresholds.
- **EHT: a units/GR sanity check, not a prediction.** Ring offsets δ(Sgr A*) = −0.082 (the EHT
  reports −0.08 ± 0.09) and δ(M87*) = 0.000. The calculation is plain GR with a fixed α = 11: no
  spin, no LMYZ correction. M87*'s mass comes from the ring itself, so its δ = 0 is circular
  (critical-review.md §3.9).
- **"Do we live in a black hole?" remains open.** Causal disconnection is
  *required* for it.
  - WP3b (computed 2026-09-29): the baby universe's edge is beyond our horizon if
    N_tot > 95–127 e-folds, depending on the parent mass. Any inflation that solves the
    horizon problem gives N_tot ≈ 131, so no parent mass is excluded.
  - This is a *consistency check*, not evidence: it is nearly automatic, since r_b ≫ 1/H at the bounce.
  - Open problem: the homogeneous bounce only works for spin a* ≲ 1e-7 (WP4). The spin route (WP4b)
    fails edge confinement (a* ≲ 1e-4) unless the edge disturbance turns out to be weak (B3b).
  - **The inflaton has no source in a black hole (B1a, 2026-09-30).** Next to the star's dust, the
    field must carry ≥ 99% of ρ_c at the bounce (Starobinsky; φ² never reaches 60 e-folds). WP1's
    "inflation is almost certain" holds for cosmological LQC, not for a black-hole interior.
  - Smolin's cosmological natural selection is in ~3.7σ tension with 2025 neutron-star masses, but
    almost all of it comes from PSR J0952−0607 (1.1σ without it). Say "tension", not "falsified".
- **Norbi's feeding claim (infalling matter feeds the baby universe) has no classical path.** Late
  matter meets a Planckian inner horizon (L1e). Whether quantum gravity changes that is open.

## Thesis calculations (implemented 2026-09-29)

- **Code:** the `thesis/` Python package (WP0–WP6). Run it with `python scripts/run_thesis.py`
  (~100 s on the i5) and test it with `python -m pytest thesis/tests`.
- **Verdict:** `thesis/verdict.py` applies the §0 criteria mechanically. Do not change a
  threshold after seeing results; if one must change, document why in `docs/thesis-progress.md`.

**Scorecard (2026-09-29):**

| WP | Outcome | Numbers |
|---|---|---|
| 1 | **mixed, conditional** | With the whole bounce in the field, inflation is almost certain (φ² failing fraction 5.6e-6). Starobinsky n_s = 0.9653 is inside Planck 95% but 2.9σ from ACT DR6; that tension belongs to the potential, not to the black-hole origin. **Conditional on B1a:** a dust star gives no such initial state. |
| 2 | **neutral** | The initial shear is unknown, in the band 0 ≤ Ω_σ ≤ 0.5625. (0.2 was a classical extrapolation to r_b, where f_LMYZ = 1.) It shortens inflation but is erased; (σ/H)₀ ≤ 1e-113. |
| 3 | **neutral** | \|Ω_K\| ≤ 2.4e-5. |
| 3b | **consistency check: passes** | Any inflation that solves the horizon problem puts the baby universe's edge beyond our horizon for every parent mass, with ≥ 4.2 e-folds to spare. The old §0 rule said "supports", but its "natural 130–145" band read Linsefors–Barrau's *inflationary* e-folds as N_tot. |
| 4 | **neutral + model limit** | A homogeneous bounce works only for a* ≲ 1e-7, so spinning black holes are not described. This is an open problem. |
| 5 | **neutral** | Best N_tot = 141.2, Δχ² = −1.2 (not significant); N_tot > 140.8 at 95%. |
| 6 | **against** | 3.7σ with 2025 masses (3.2σ before), but only 1.1σ without J0952−0607; none under Smolin's ~2.4 M☉ reading. |
| B1a (pre-registered 2026-09-30) | **against** | Field at its vacuum minimum next to dust: ≥ 60 e-folds needs a field fraction ≥ 0.9895 of ρ_c (Starobinsky), i.e. 1.7e-10 of the dust energy as coherent inflaton velocity when the collapse's H reaches m; φ² fails even at 100%. |
| 1b (add-on) | **supports** | Polynomial α-attractor: n_s 0.972, inside Planck and ACT 95%; the bounce inflates outside φ_B ∈ [−3.45, −1.64]. The ACT tension was Starobinsky's. |
| 5b (add-on) | **neutral** | Real hybrid-LQC spectrum (Guillén+ 2026) with the official Planck likelihoods (cobaya native, data in `~/cobaya_packages`): best N_tot = 141.0, Δχ² = −0.53; N_tot > 140.25 at 95%. |
| 5c (add-on) | **neutral** | Full Planck MCMC on the Ryzen (2026-09-30, `runs/mcmc-2026-09-30/`): ΛCDM reproduces Planck 2018 within 0.06σ (pipeline validated); Δχ²_min = −0.23 (minimizer scatter ~1); N_tot > 140.71 at 95%, flat above ~142 (the mean is prior-dominated, don't cite it). |

**Open items:**
- a spinning (Kerr) parent: **WP4b is implemented** (`thesis/spin.py`, `docs/spin-plan.md` §9).
  - Idea: an axial low-j seed with M_s ≤ C³√(α/2)/a*³ m_P, independent of mass and N_tot. It must
    be at least the mass gap (0.83 m_P), and needs N_tot ≈ 137–142.
  - Fiducial n = 3 profile, C = 1.23. Scorecard: S1+S2 supports (at the old 145 ceiling, which was a
    mislabelled input), S3 supports, S4 **open**, S5 neutral, CMB consistency supports,
    **S7 edge confinement (B3a): against, unless the disturbance amplitude is ≪ 1.** With
    η = 9.55e3 ℓ_P, the seed must weigh ≥ 33 t, so a* ≲ 9.8e-5 and no observed population survives.
  - Catch: fast spin gives a Planck-mass seed; slow (natal ~0.01) spin loses to mass inflation at
    r₋ (crude S4). The former "comfortable window" a* ≈ 0.44–0.52 does not survive S7.
  - The decisive missing piece is a rotating collapse in effective LQG, which is not in the literature;
- **WP5c MCMC: done** (see the 5c row above). To rerun: `bash scripts/run_mcmc.sh` on the Ryzen
  (~3 h total; as root in WSL, set `OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1`),
  then `python scripts/analyze_mcmc.py`. `chains/` is gitignored.
- **Inner horizon (S4, Level 1): code implemented 2026-09-30, waiting for the full Ryzen run.**
  - Code: `thesis/ori_model.py`, `thesis/doublenull.py`, `thesis/inner_horizon.py`, and the runner
    `scripts/run_inner_horizon.py`. See `docs/inner-horizon-plan.md` §8.
  - The local smoke test passes the validation gate. Its preview: L1a supports, L1c open (GW 22%,
    natal 0%; set by the D ≤ 10 cutoff, not by the timing race), L1d info, L1e **neutral**. The
    old code said "against" for L1e; that misapplied plan §5 and is fixed.
  - New findings:
    - the LMYZ inner horizon is unstable in the Ori model;
    - edge confinement: η = 9.55e3 ℓ_P (kinetic phase 4.4e3 plus inflation), which covers
      Planck-mass seeds entirely. Now scored as WP4b S7.
- With this, the planned calculations are complete. The remaining open physics question is S4
  (matter crossing a spinning parent's inner horizon), for which no calculation exists in the
  literature. Thesis writing is next, if the author asks for it.

## How to work in this repo (agreed with the author)

- **Commits:** commit directly to `main` with descriptive **Hungarian** commit
  messages, and push after each coherent phase. No branches or PRs. Check that
  CI is green afterwards (`gh run list`). End commit messages with the
  Co-Authored-By line used in the history.
- **Honest results:** report what the physics gives, even when it hurts the
  hypothesis. Keep assumptions and limitations explicit in code comments and docs.
- **Validation:** every new feature gets tests against an independent analytic or
  literature value, not against its own output. Current suite: 105 Rust + 22 Python + 50 thesis tests.
- **Literature data:** use a background research agent with "cite everything,
  mark UNVERIFIED" instructions. Then check its numbers for internal
  consistency before use; this caught a typo in Dong et al. 2016's neutrino column.
- **Language:** code comments, repo docs and commit messages are Hungarian. The
  exceptions are `docs/*.md` analysis notes written for the author, which are
  English. Chat is in English.

## Environment notes

- **Setup:** run `bash scripts/setup_dev.sh`. It creates `.venv` (PEP 668 forbids
  system pip), builds the Rust core via maturin, and runs the tests. For the
  thesis add `pip install -e '.[dev,thesis]'` (camb, getdist, matplotlib).
- **Conda:** under Conda, run `unset CONDA_PREFIX` before `pip install -e`.
- **Console scripts:** if the venv's console scripts have broken shebangs, use
  `python -m pytest` / `python -m mypy`.
- **ode_solvers 0.6.2:** its Dense output interpolates with ~1e-4 error. Use the
  Sparse wrapper in `core/src/time_evolution/ode.rs`.
- **Log files:** `.gitignore` ignores `*.log` except `runs/**/*.log`; campaign
  logs are meant to be committed.
- **Clippy:** `cargo clippy --features python-ext` shows 3 "useless conversion"
  false positives from the PyO3 0.22 macros. CI lints without that feature.
- **Performance:** one run takes 1–2 s and ~55 MB on a 2011 i5. The full
  campaign is `python scripts/run_campaign.py [--jobs N]`, then
  `python scripts/analyze_campaign.py runs/<id>`.
