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
- **EHT consistency.** Predicted ring offsets: δ(Sgr A*) = −0.082 (the EHT
  reports −0.08 ± 0.09) and δ(M87*) = 0.000.
- **"Do we live in a black hole?" remains open.** Causal disconnection is
  *required* for it.
  - WP3b (computed 2026-09-29): the baby universe's edge is beyond our horizon if
    N_tot > 95–127 e-folds, depending on the parent mass. Any inflation that solves the
    horizon problem gives N_tot ≈ 131, so no parent mass is excluded.
  - Open problem: the homogeneous bounce only works for spin a* ≲ 1e-7 (WP4).
  - Smolin's cosmological natural selection is falsified at ~3σ by neutron stars above 2 M☉.

## Thesis calculations (implemented 2026-09-29)

- **Code:** the `thesis/` Python package (WP0–WP6). Run it with `python scripts/run_thesis.py`
  (~100 s on the i5) and test it with `python -m pytest thesis/tests`.
- **Verdict:** `thesis/verdict.py` applies the §0 criteria mechanically. Do not change a
  threshold after seeing results; if one must change, document why in `docs/thesis-progress.md`.

**Scorecard (2026-09-29):**

| WP | Outcome | Numbers |
|---|---|---|
| 1 | **mixed** | Inflation is almost certain (φ² failing fraction 5.6e-6). Starobinsky n_s = 0.9653 is inside Planck 95% but 2.9σ from ACT DR6; that tension belongs to the potential, not to the black-hole origin. |
| 2 | **neutral** | Black-hole interior shear Ω_σ = 0.2 (mass-independent). It shortens inflation but is erased; (σ/H)₀ ≤ 1e-113. |
| 3 | **neutral** | \|Ω_K\| ≤ 2.4e-5. |
| 3b | **supports** | Any inflation that solves the horizon problem puts the baby universe's edge beyond our horizon for every parent mass, with ≥ 4.2 e-folds to spare. |
| 4 | **neutral + model limit** | A homogeneous bounce works only for a* ≲ 1e-7, so spinning black holes are not described. This is an open problem. |
| 5 | **neutral** | Best N_tot = 141.2, Δχ² = −1.2 (not significant); N_tot > 140.8 at 95%. |
| 6 | **against** | 3.2σ. |
| 1b (add-on) | **supports** | Polynomial α-attractor: n_s 0.972, inside Planck and ACT 95%; the bounce inflates outside φ_B ∈ [−3.45, −1.64]. The ACT tension was Starobinsky's. |
| 5c (add-on) | **neutral** | Full Planck MCMC on the Ryzen (2026-09-30, `runs/mcmc-2026-09-30/`): ΛCDM reproduces Planck 2018 within 0.06σ (pipeline validated); Δχ²_min = −0.23 (minimizer scatter ~1); N_tot > 140.71 at 95%, flat above ~142 (the mean is prior-dominated, don't cite it). |
| 5b (add-on) | **neutral** | Real hybrid-LQC spectrum (Guillén+ 2026) with the official Planck likelihoods (cobaya native, data in `~/cobaya_packages`): best N_tot = 141.0, Δχ² = −0.53; N_tot > 140.25 at 95%. |

**Open items:**
- a spinning (Kerr) parent: **WP4b is implemented** (`thesis/spin.py`, `docs/spin-plan.md` §9).
  - Idea: an axial low-j seed with M_s ≤ C³√(α/2)/a*³ m_P, independent of mass and N_tot. It must
    be at least the mass gap (0.83 m_P), and needs N_tot ≈ 137–142.
  - Fiducial n = 3 profile, C = 1.23. Scorecard: S1+S2 supports, S3 supports, S4 **open**,
    S5 neutral, CMB consistency supports.
  - Catch: fast spin gives a Planck-mass seed; slow (natal ~0.01) spin loses to mass inflation at
    r₋ (crude S4). The comfortable window is a* ≈ 0.44–0.52.
  - The decisive missing piece is a rotating collapse in effective LQG, which is not in the literature;
- **WP5c MCMC: done** (see the 5c row above). To rerun: `bash scripts/run_mcmc.sh` on the Ryzen
  (~3 h total; as root in WSL, set `OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1`),
  then `python scripts/analyze_mcmc.py`. `chains/` is gitignored.
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
  literature value, not against its own output. Current suite: 105 Rust + 22 Python + 30 thesis tests.
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
