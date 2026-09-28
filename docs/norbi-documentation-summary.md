# Norbi documentation — summary of `norbi_teljes_dokumentacio.pdf`

Source: `norbi_teljes_dokumentacio.pdf` (53 pages, "Norbi & Claude, 2026", written for v2.0).
This file keeps what matters from it and marks where the v3.0 code has since changed or tested each point.

The PDF has three parts:

| Part | Content | Still relevant? |
|---|---|---|
| I. Hypothesis and physics plan (ch. 1–11) | The hypothesis, formulas, planned modules, UI, validation plan | **Yes**, this is the core. |
| II. Software architecture (ch. 12–28) | Rust/Python/Tauri/Bevy stack, folder tree, traits, tests, CI, schema 2.0 | Mostly outdated. Bevy and Tauri were deleted, and v3.0 uses schema 3.0. |
| III. Scientific background | Research question, formal H₁/H₀, validation strategy, limitations, references | **Yes.** It defines what counts as a result. |

---

## 1. The hypothesis in Norbi's own words (ch. 1)

> "Amikor egy fekete lyuk keletkezik, belsejében egy ősrobbanáshoz hasonló folyamat indul el — egy belső
> univerzum születik. Ez a belső univerzum a fekete lyukba beesett anyagból táplálkozik: minden beeső csillag,
> bolygó, aszteroida újabb anyagot ad neki, és a belső univerzumban ütközések, struktúrák, bolygók keletkeznek.
> A belső univerzum tágul — ahogy kívülről látjuk a fekete lyuk eseményhorizontjának növekedését. A tágulás
> szélén lévő objektumok szétszakadnak, és a szétszakadáskor apró adatcsomagok szöknek ki — ezeket külső
> megfigyelőként Hawking-sugárzásnak érzékelünk."

In short:
1. **Inner Big Bang.** At the singularity a quantum bounce happens (LQC), and a new spacetime starts expanding inside.
2. **Feeding by infalling matter.** Every star, planet or asteroid that falls in enters the inner universe. There it
   forms collisions and structures, even planets. The inner universe is an *open* system fed from outside.
3. **Edge tearing as Hawking radiation.** The inner universe expands, and objects at its edge are torn apart
   (a local "Big Rip"). Energy and information escape *through the event horizon*, and the outside sees this as Hawking radiation.

Two ideas in the PDF are **not in the README**:
- **The inner expansion corresponds to the horizon growing as seen from outside.** As matter falls in, r_s grows, and
  this is interpreted as the inner universe expanding.
- **The escaping radiation carries "small data packets".** Information is emitted as discrete packets at tear-up events.

## 2. Physics as formulated (ch. 2, 5)

**Exterior (standard).** r_s = 2GM/c², T_H = ħc³/(8πGMk_B), S = A/(4ℓ_P²), P = ħc⁶/(15360πG²M²).
The PDF reinterprets T_H as *the temperature of the inner edge tearing* and P as *the energy of matter torn at the inner edge*.

**Phase 1, the inner Big Bang.** H² = (8πG/3)ρ(1 − ρ/ρ_P), with the bounce at ρ = ρ_P. It then assumes inflation
a(t) = a₀·e^(H_inf·t), with a₀ ≈ ℓ_P and "large" H_inf, both left as free parameters.

**Phase 2, infall feeding the interior.** The PDF uses dτ = dt·√(1 − r_s/r) for the proper time at the horizon.
An object "freezes" from the outside view but enters the inner universe from the inside view.
Energy balance: E_inner(t) = E₀ + ∫ Ṁ_infall·c² dt, so the inner energy only grows.

**Phase 3, edge tearing.**
- Condition: v = H_inner·r > c, or more precisely E_tidal = ½mH²r² > E_bind = 3Gm²/(5R).
- Released energy: E_tidal − E_bind, projected onto a horizon point (`project_to_horizon`).
- **Key formula:** P_Norbi = η · ρ_edge · v_tear · A_horizon, with 0 < η < 1 an unknown efficiency.
- **The central test (ch. 9):**
  - H₁: some η > 0 makes P_Norbi = P_standard, so the model is consistent.
  - H₀: no such η exists, so the model fails.
  - Sensitivity of η to M, infall density, H_inner and the number of edge objects.

**Clocks (ch. 3.2).** The inner time is independent of the outer time, with dt_inner ∝ 1/H_inner.
A link t_inner/t_outer = f(H_inner, r_s) was supposed to be set by the engine, but was never derived.

**Planned interior content (ch. 5).** N-body gravity between infallen objects, merging into structures, fragmentation animation.

## 3. Formal hypotheses (Part III, ch. 1–3)

Research question: if the inner baby universe's edge tearing is the source of Hawking radiation, does that radiation
differ significantly from the standard model? And can the structure of the infallen information be reconstructed from it?

| Claim | H₁ (Norbi) | Measurable criterion | H₀ |
|---|---|---|---|
| **A: Spectrum** | The spectrum differs significantly from the thermal Planck spectrum | \|S_norbi(ν) − S_planck(ν)\| / σ_noise > 3 | ≤ 3 for every ν |
| **B: Information** | More of the infallen information is recoverable than in standard mode | similarity_norbi − similarity_std > 0.05 (hash bit-match ratio) | ≤ 0.05 |
| **C: Baby-universe imprint** | The spectrum's time evolution correlates with a baby universe's CMB spectrum | \|Pearson(S_hawking(t), S_CMB(t))\| > 0.3 | ≤ 0.3 |

Decision rule: reject all three H₀ for a numerically consistent, distinguishable hypothesis. Rejecting none
means the models are equivalent. Rejecting some means partial confirmation, stated per claim.

**Validation strategy (ch. 4).**
1. Standard mode reproduces the 7 known results: r_s(☉) = 2954 m, T_H(☉) = 6.17e-8 K, t ∝ M³, Wien peak, S ∝ M²,
   Page-curve peak near t_evap/2, and H² = 0 at the bounce.
2. Run both modes with identical inputs and compare them.
3. Sensitivity analysis: M₀ ×0.5/1/2/5, dt ×0.1/10, spectrum bins 100/1000/10000, a₀ = ℓ_P/10ℓ_P/100ℓ_P.
   The standard model should be insensitive, and the Norbi model only weakly sensitive to a₀.

**Stated limitations (ch. 5).**
- Island formula and HKLL are proven in AdS, not de Sitter.
- Schwarzschild only, no Kerr.
- LQC is homogeneous, but a black-hole interior is not.
- No full quantum gravity.
- Floating-point accumulation.

The PDF says the results can show *numerical consistency*, not physical truth.

**Future plans (ch. 10).** Kerr metric, island formula, soft hair, holographic complexity, multiple black holes,
real objects (Sgr A*, M87).

## 4. Status of each point in v3.0

| PDF point | v3.0 status |
|---|---|
| Bounce at ρ = ρ_P | Corrected: bounce at ρ_c ≈ 0.41 ρ_P (γ = 0.2375). |
| a(t) = a₀·e^(H_inf t), with a₀ and H_inf free | Replaced by the exact LQC dust solution a = (1 + τ²/τ_b²)^(1/3), which has no free a₀ or H_inf. The a₀ sensitivity test no longer applies. |
| Infalling matter feeds the interior; E_inner = E₀ + ∫Ṁc² | **Implemented in v3.1 as bookkeeping** (`interior_feeding`): CMB absorption, accretion (constant/Bondi/Eddington) and discrete infall events, with an energy ledger accurate to ~1e-14. Whether late infall reaches the *same* bounced region is not implied by the geometry (it heads for the inner/Cauchy horizon, which is unstable to late inflow: mass inflation, Poisson & Israel 1990). |
| Inner expansion = horizon growth seen from outside | **Contradicted by the geometry.** The horizon grows by accretion (Δr_s = 2GΔM/c²), while the interior bounce happens in proper time τ at r_b ≪ r_−. These are separate quantities, not two views of one process. |
| Energy "escapes through the event horizon" at tear-up (`project_to_horizon`) | **This is the step that fails.** Nothing can cross a horizon outward. v3.0 computes that the bounce edge lies inside the inner horizon and its light rays never reach r_+ (LMY 2023). |
| P_Norbi = η·ρ_edge·v_tear·A_horizon, find η | The old test only asserted η > 0, which is tautological, and it was deleted. The formula is also dimensionally wrong: kg/m³ · m/s · m² = kg/s, not W. Physically η_exterior = 0 because there is no causal channel. |
| E_tidal > E_bind tear condition | Removed as the coupling α. It compares two energies and is not a power fraction. v3.0 reports the interior Gibbons–Hawking luminosity instead, labeled as interior-only. |
| Clock link t_inner/t_outer = f(H, r_s) | Still undefined. It is only needed if a causal channel exists, and it doesn't. |
| N-body interior, structure formation | Not implemented. It was Bevy-only fake physics before and was deleted. |
| H₁.A (spectrum, 3σ) | **H₀ holds:** the exterior spectra are identical in both modes, bit for bit. The standard spectrum itself has a mass-independent greybody non-thermality of 0.267, which isn't information. |
| H₁.B (information, hash bit-matching) | **H₀ holds:** the proper measure (Hayden–Preskill mutual information) gives 0 bits for Norbi versus 2 bits for unitary evaporation. Hash bit-matching was replaced as a metric; it can't detect information. |
| H₁.C (CMB correlation > 0.3) | **Never implemented** in v2.0 or v3.0. With no causal channel the exterior can't correlate with the interior. |
| Validation step 1 (7 known results) | Done, with 3 fixes: the "Page-curve peak" test was tautological, the bounce density was wrong, and t ∝ M³ only holds for constant α. |
| Sensitivity analysis | M₀ covered by the mass scan (2 m_P to M_☉). Step count covered by convergence tests. Bin count affects only the display, and a₀ no longer exists. |
| Future: Kerr, island formula, soft hair, complexity | Kerr **implemented in v3.2** (geometry, Page 1976b spin-dependent emission, spin evolution, disk spin-up). Island formula / soft hair / complexity: stubs deleted; a real Page curve exists in the quantum toy model. |

## 5. Takeaways for future work

- By its own H₁/H₀ criteria, the PDF's hypothesis is **not supported** in v3.0: none of H₀.A, H₀.B or H₀.C can be rejected.
  That is exactly the "models numerically equivalent" outcome ch. 3 anticipates.
- The **one mechanism that would change this** is a way for energy to "escape through the event horizon". The PDF
  assumes it (`project_to_horizon`) but never derives it. Any revival of the hypothesis has to supply that, for example
  a geometry where the bounced matter re-emerges in our universe (HKSW 2022 shock, black-to-white-hole transition).
  Those change the prediction from "non-thermal Hawking spectrum" to "delayed burst".
- The realism upgrades from the PDF's future-plans chapter are done:
  - accretion feeding the black hole (v3.1): stellar-mass and larger black holes *grow* in today's CMB rather than evaporate;
  - Kerr spin (v3.2);
  - real objects Sgr A*, M87* and others (v3.2). Their EHT ring sizes are reproduced (Sgr A* δ = −0.08, as published).
