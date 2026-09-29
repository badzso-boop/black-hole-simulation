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

## Current state (v3.2, 2026-09-28): read these first

- **README.md**: model, formulas, install, CLI, output schema 3.2.
- **summary.md**: development log, phases 1–12. Phase 9 explains why v2.0's results were artifacts.
- **docs/are-we-in-a-black-hole.md**: what the project can and cannot say about the big question.
- **docs/thesis-plan.md**: the six-calculation thesis plan. **Not implemented yet.**
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
  - First estimate (WP3b): the baby universe's edge is beyond our horizon if
    N_tot > 95–127 e-folds, depending on the parent mass.
  - LQC predicts 130–145, so no parent mass is excluded.
  - Smolin's cosmological natural selection is falsified at ~3σ by neutron stars above 2 M☉.

## Next step (thesis)

`docs/thesis-plan.md` defines the work packages:
- WP0: a Python `thesis/` package that first reproduces the Rust core's LQC results.
- WP1: inflation after the bounce.
- WP2: anisotropy.
- WP3 and WP3b: curvature, and the edge of the baby universe (novel).
- WP4: parent spin.
- WP5: CMB low-ℓ imprint with CAMB.
- WP6: natural selection.

Rules for this work:
- Implement in order, starting WP0 → WP1.
- Respect the **pre-registered outcomes table** in §0: the thesis tests a
  stated model and never claims "we live in a black hole".
- Before citing any `verified: false` entry in `data/observations.json`, check it against the paper.
- Only WP5's optional cobaya MCMC needs a big machine; everything else runs in
  minutes on a 4-core CPU.

## How to work in this repo (agreed with the author)

- **Commits:** commit directly to `main` with descriptive **Hungarian** commit
  messages, and push after each coherent phase. No branches or PRs. Check that
  CI is green afterwards (`gh run list`). End commit messages with the
  Co-Authored-By line used in the history.
- **Honest results:** report what the physics gives, even when it hurts the
  hypothesis. Keep assumptions and limitations explicit in code comments and docs.
- **Validation:** every new feature gets tests against an independent analytic or
  literature value, not against its own output. Current suite: 105 Rust + 22 Python tests.
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
