# Plan: the spin problem (WP4b)

**Status:** plan, 2026-09-29. The first estimates below were computed while writing it.
Everything in §5 is still to do.

**Inputs:**
- Data: `data/observations.json` → `4b_spin`. It holds a research pass of 2026-09-29 with sources
  and a `verified` flag on every number.
- Earlier results: [thesis-progress.md](thesis-progress.md) (WP4), `thesis/rotation.py`.

---

## 1. The problem

WP4 found that the homogeneous Oppenheimer–Snyder + LQC bounce, the model under all of
WP1–WP5, works only if the parent black hole barely spins. The allowed spin is:

| Parent | Largest spin a* compatible with the bounce |
|---|---|
| Primordial, 5×10¹¹ kg | 3×10⁻⁷ |
| 1 M☉ | 2×10⁻¹³ |
| Sgr A* | 1×10⁻¹⁵ |
| M87* | 1×10⁻¹⁶ |
| 5×10²² M☉ | 5×10⁻²¹ |

**The same bound, stated geometrically.** For small spin, the centrifugal barrier of the infalling
matter, r_c = j²/GM = a*² GM/c², is about twice the Kerr inner horizon, r₋ ≈ a*² GM/2c².
So "a* below the bound" is equivalent to "the inner horizon lies inside the bounce radius r_b".

For real spins it doesn't, by a huge margin:

| | a* = 0.01 | a* = 0.1 | a* = 0.7 | a* = 0.998 |
|---|---|---|---|---|
| 10 M☉: r₋/r_b | 6×10²¹ | 6×10²³ | 3×10²⁵ | 1×10²⁶ |
| Sgr A*: r₋/r_b | 3×10²⁵ | 3×10²⁷ | 2×10²⁹ | 6×10²⁹ |
| M87*: r₋/r_b | 4×10²⁷ | 4×10²⁹ | 2×10³¹ | 8×10³¹ |

The average matter density inside r₋ is 10⁶⁶–10⁹⁶ times *below* the LQC critical density.
In a spinning hole, the collapsing star's matter never gets anywhere near the quantum regime
by being compressed.

## 2. What the universe tells us about real spins

All of these are in `data/observations.json` → `4b_spin`.

| Population | Spin | Source |
|---|---|---|
| X-ray binaries, reflection (36 BHs) | 86% consistent with a* ≥ 0.95; all with ≥ 0.7 | Draghis+ 2024 |
| Cyg X-1 | > 0.9985 (3σ, continuum fitting) | Zhao+ 2021 |
| X-ray binaries, continuum fitting | from 0.12 ± 0.19 (A0620−00) to > 0.95 | McClintock+ 2014 |
| LIGO/Virgo/KAGRA, GWTC-4 | distribution peaks at 0.01–0.23; 90% below 0.57 | LVK 2025 |
| Merger remnants | 0.67–0.72 (GW150914, GW190521, GW250114) | LVK |
| Supermassive, reflection | most with M < 3×10⁷ M☉ have > 0.9 (biased sample) | Reynolds 2021 |
| M87* | a* = 0 rejected by jet power | EHT 2021 |
| Newborn BH, single star, theory | ~0.01 | Fuller & Ma 2019 |
| Pre-supernova iron core, theory | 0.05–0.12 (derived from J) | Heger, Woosley & Spruit 2005 |
| Neutron-star birth spin (proxy) | ~2×10⁻³ (P₀ = 0.3 s), derived | Faucher-Giguère & Kaspi 2006 |
| Primordial BHs, theory | ~10⁻³–10⁻² (radiation era); ≈ 1 (matter era) | De Luca+ 2019; Harada+ 2017/21 |
| Supermassive-star collapse | 0.75 | Shibata & Shapiro 2002 |

**Bottom line:** no observed or predicted black hole has a* below about 10⁻³. The homogeneous
bounce needs 10⁻⁷ to 10⁻²¹. The problem is real and can't be argued away with data.

**What theory offers** (research pass, 2026-09-29):
- **No paper evolves a rotating collapse through an LQC bounce.** Only stationary rotating
  quantum metrics exist, built with the Newman–Janis trick (Brahma, Chen & Yeom 2021 and others).
  This is open territory, not a known failure.
- **Classically, the inner horizon of a spinning hole is unstable ("mass inflation").** Curvature
  grows toward the Planck value *at r₋*, and afterwards (in pure GR) the geometry collapses to a
  singularity (Hamilton & Avelino 2010; Hamilton 2017; Marolf & Ori 2012).
- **The Cauchy horizon is only a weak singularity** (Dafermos & Luk). Tidal distortion stays
  finite, so infalling matter may survive crossing it.
- **Other escape hatches:**
  - Einstein–Cartan torsion (Popławski) bounces at ~240 ρ_Pl, *denser* than LQC, so its centrifugal
    problem is worse, and it treats rotation only qualitatively.
  - "Inner-extremal" regular cores avoid mass inflation, but they are ad hoc.

## 3. Two ways out, and a first calculation for each

### Route A: the axial core

Matter near the rotation axis carries almost no angular momentum (j ∝ distance from the axis²).
Only that low-spin core needs to reach ρ_c. After the bounce, inflation makes the mass almost
irrelevant (WP1 energy budget).

**First estimate (done):**
- Model: a rigidly rotating uniform star with mean spin a*.
- The axial cylinder with mass fraction f has j_max = (5/3) j̄ f.
- It must bounce under its **own** mass fM, so j_max < √(G fM r_b(fM)).
- Its bounce must also be big enough that the edge ends up beyond our horizon (WP3b).
- **The parent mass cancels.** The largest spin that works is

  a*_max = 0.6 · √(α/2) · ℓ_P · e^{N_tot} / R_obs    (R_obs = 14.26 Gpc)

- So the answer depends only on N_tot, the e-folds from the bounce to today:

| Parent spin | N_tot needed | Predicted LQC mark on the CMB |
|---|---|---|
| 10⁻⁵ | ≥ 130.9 (just enough inflation) | — |
| 0.01 | ≥ 137.6 | k_c ≤ 1.1×10⁻² /Mpc (ℓ ≲ 150) |
| 0.1 | ≥ 139.9 | k_c ≤ 1.1×10⁻³ /Mpc (ℓ ≲ 15) |
| 0.5 | ≥ 141.5 | — |
| 0.7 | ≥ 141.9 | k_c ≤ 1.4×10⁻⁴ /Mpc (ℓ ≲ 2) |
| 0.998 | ≥ 142.2 | k_c ≤ 1.1×10⁻⁴ /Mpc (ℓ ≲ 1.5) |

**Compare with WP5:**
- The CMB prefers N_tot = 141.2 and requires N_tot > 140.8 (95%). LQC's natural range is 130–145.
- **So route A allows every observed spin, provided N_tot ≳ 142.**

**But it makes a sharp, testable prediction.** At our best CMB fit (N_tot = 141.2, ℓ ≈ 4), only
parents with a* ≲ 0.35 work.
- If the low-ℓ deficit is the bounce's mark, the parent was a slowly spinning black hole:
  typical of LIGO black holes, but not of X-ray binaries or supermassive ones.
- If the parent spun fast (a* ≳ 0.7), the mark is at ℓ ≲ 2, invisible, and the low-ℓ deficit
  has another cause.

**What this estimate ignores** (all addressed in §5):
- real, differentially rotating cores instead of rigid rotation;
- the shape of the core: a thin two-sided "needle" of infall is strongly anisotropic;
- **the axial matter must first cross the inner horizon r₋ ≫ r_b.** Route A therefore depends on
  surviving the weak Cauchy-horizon singularity. This is the critical link.

### Route B: the inner horizon

In a spinning hole, Planck-scale *curvature* is reached at the inner horizon through mass
inflation, driven by infalling and outflowing matter streams.
- A quantum bounce there would be fed by matter that keeps falling in. That is closer to the
  original Norbi idea ("infalling matter feeds it") than route A.
- Candidate frameworks:
  - de Sitter bubbles at Planck curvature (Barrabès & Frolov 1996);
  - the timelike transition region inside r₋ of the rotating LQG black hole (Brahma+ 2021).
- **Headwinds:**
  - the classical continuation is BKL collapse to a singularity;
  - regular cores are unstable at r₋.
- Route B needs a new interior geometry. Per the project rules it must be stated explicitly, and it
  may not reintroduce an exterior Norbi signal.

## 4. Where rotation leaves the universe (both routes)

**Scaling.** Perfect-fluid circulation gives ω ∝ a^{3w−2}, so:

| Phase | ω/H scales as |
|---|---|
| inflation | a⁻⁵ |
| radiation era | a |
| matter era | a^{−1/2} |

(WP4 used the more conservative dust carrier, e^{−2N} during inflation.)

**Consequence.** Even ω/H ~ 1 at the bounce is erased after ~15 e-folds, far below
(ω/H)₀ < 7.6×10⁻¹⁰. **Any version of the hypothesis with ≥ 130 e-folds predicts no rotation axis today.**

**Claims of a rotating universe or a preferred axis do not help, and must not be cited as support:**
- Szigeti et al. 2025, ω₀ ≈ 0.03 H₀: not tested against the CMB bound, which is 4×10⁷ times smaller.
- Galaxy-spin asymmetries: Iye+ 2021 found duplicate entries; Patel & Desmond 2024 found isotropy.

## 5. Calculations to do

Each item gets code in `thesis/`, tests against an independent value, and a line on the scorecard.

| # | Calculation | Method | Output | Effort |
|---|---|---|---|---|
| **S1** | Realistic low-spin core | Replace rigid rotation with published j(m) profiles (Heger+ 2005 magnetic and non-magnetic; Fuller & Ma 2019) and PBH spin distributions; mass fraction below j_crit, self-consistently | f(M, a*) and required N_tot per population | 3–4 days |
| **S2** | Spin–e-fold relation vs data | a*_max(N_tot) against the measured distributions (X-ray binaries, GWTC-4, SMBH, predicted natal spins); combine with WP5's Δχ²(N_tot) | **Key figure:** required N_tot per population, overlaid on the LQC band and the CMB constraint; fraction of each population allowed at N_tot = 141.2 | 2 days |
| **S3** | Shape of the axial core | Bipolar infall gives Kasner-like anisotropy. Estimate the shear at ρ_c and check the LQC bound σ² ≤ 11.57. If Ω_σ > 0.56, upgrade WP2 to the full effective Bianchi-I LQC equations (Corichi–Singh Eqs. 30–32) | N_infl with the axial-core shear; threshold shift | 1–1.5 weeks |
| **S4** | Crossing the inner horizon | Order-of-magnitude mass-inflation estimates (Hamilton & Avelino 2010): curvature growth rate, proper time to Planck curvature, tidal distortion integrated across a weak null singularity, for the S2 populations | Does axial matter reach r_b intact (route A), or is Planck curvature reached first at r₋ (route B)? | 1 week |
| **S5** | Inherited rotation | Seed angular momentum → (ω/H)_B → today, both carriers (dust and perfect fluid) | (ω/H)₀ vs 7.6×10⁻¹⁰ | 1 day |
| **S6** | Torsion comparison | The same centrifugal test for Popławski's bounce (~240 ρ_Pl) | a*_max for Einstein–Cartan | 1 day |

**Total:** about 4 weeks at a steady pace. Everything runs on the i5 in minutes.

## 6. Pre-registered outcomes (fixed 2026-09-29, before running S1–S6)

| Question | Supports the hypothesis if… | Counts against it if… | Open / model-dependent if… |
|---|---|---|---|
| S1+S2: can observed spins bounce (route A)? | Required N_tot ≤ 145 for the bulk (≥ 50%) of *each* observed population, and ≤ 142 for at least the GW population (compatible with the WP5 best fit) | Required N_tot > 145 for the GW population (the lowest-spin one) | — |
| S3: does the axial core still inflate? | Shear within the LQC bound, and N_infl ≥ 60 reachable (as in WP2) | Shear exceeds the bound, or no φ_B gives 60 e-folds | Needs the full Bianchi-I LQC upgrade and it isn't done |
| S4: does axial matter survive r₋? | Estimated tidal distortion across r₋ stays O(1) or less | Planck curvature at r₋ is reached before the axial matter arrives, for all populations | **Expected:** no calculation in the literature decides it |
| S5: rotation today | (ω/H)₀ < 7.6×10⁻¹⁰ (expected: neutral) | Above the bound | — |
| CMB consistency | If the low-ℓ deficit is the bounce (N_tot ≈ 141), the parent's spin a* ≲ 0.35 is consistent with the GW population | — | Fast-spinning parent: the bounce's mark is invisible (ℓ ≲ 2) |

**Expected honest outcome from what is known now:**
- Route A passes S1/S2 comfortably if N_tot ≳ 142.
- S3 is uncertain.
- S4 stays **open**: the fate of matter crossing the inner horizon of a spinning black hole is an
  unsolved problem of quantum gravity, not something this project can settle.

**Likely thesis sentence:**
> "A spinning parent is compatible with the hypothesis only if the universe expanded by
> N_tot ≳ 140–142 e-folds after the bounce. That is inside the LQC range and consistent with the
> CMB. It also requires the low-angular-momentum axial matter to survive the inner horizon, which
> remains an open problem."

## 7. Risks

| Risk | Mitigation |
|---|---|
| The Newtonian centrifugal estimate is wrong inside Kerr | S4 covers the relativistic interior. State the Newtonian estimate as an order-of-magnitude bound |
| Real j(m) profiles are not published in tabular form | Use the published J, M values (Heger+ 2005, Table 4) with power-law profiles, and scan the exponent |
| Tuning the spin argument after seeing results | The §6 table is fixed now. Any change goes in a dated note |
| Over-reading preferred-axis claims | §4: with ≥ 130 e-folds the hypothesis predicts no axis; don't cite them as support |

## 8. Key references

- **Spins:** Zhao+ 2021 (2102.09093); McClintock+ 2014 (1303.1583); Draghis+ 2024 (2311.16225);
  Reynolds 2021 (2011.08948); LVK GWTC-4 (2508.18083), GWTC-3 (2111.03634); EHT M87* VIII (2105.01173).
- **Natal spin:** Heger, Woosley & Spruit 2005 (astro-ph/0409422); Fuller & Ma 2019 (1907.03714);
  De Luca+ 2019 (1903.01179); Harada+ 2017 (1707.03595); Shibata & Shapiro 2002 (astro-ph/0205091).
- **Interior:** Hamilton & Avelino 2010 (0811.1926); Hamilton 2017 (1703.01921); Marolf & Ori 2012
  (1109.5139); Dafermos & Luk (1710.01722); Brahma, Chen & Yeom 2021 (2012.08785); Carballo-Rubio+
  (2101.05006, 2205.13556); Barrabès & Frolov 1996 (hep-th/9511136).
- **Torsion:** Popławski (1007.0587, 1410.3881, 1910.10819).
- **Our universe:** Planck 2015 XVIII (1502.01593); Saadeh+ 2016 (1605.07178); Szigeti+ 2025
  (2503.13525); Patel & Desmond 2024 (2404.06617); Iye+ 2021 (2011.00662).
