# Do we live in a black hole? What this project can and cannot say

Numbers in this note come from `python scripts/cosmology_checks.py` (formulas
printed next to each result) and from the simulation campaign in
[`runs/2026-09-28/`](../runs/2026-09-28/ANALYSIS.md).

## 1. Short answer

- **Is it proven?** No. Nothing in physics today proves or rules out that our
  universe was born inside a black hole. It is a real, published research line
  ("black hole cosmology": Pathria 1972; Frolov–Markov–Mukhanov 1989;
  Smolin 1992; Popławski 2010–), not a fringe idea — and not an accepted one either.
- **Is it mathematically possible?** In a limited but genuine sense, yes (§3).
- **What did this project test?** The *Norbi* version adds one specific claim:
  that the baby universe's edge is what we see outside as Hawking radiation.
  **That claim fails** in the model: the bounce happens behind the inner horizon,
  and no light ray from it reaches the outside.
- **The same result helps the other half of the idea.** If we lived inside a
  black hole, we would *have* to be causally cut off from the parent universe,
  or we would see it. Causal disconnection kills "the edge is Hawking radiation"
  but is exactly what "our Big Bang was a bounce inside a black hole" needs.

## 2. Data or playing with numbers?

| Kind of output | Examples from this project | Status |
|---|---|---|
| **Reproduction of known physics** | Hawking lifetimes, Page's spin-down, EHT ring sizes (Sgr A* δ = −0.08), CMB equilibrium mass, Eddington growth | Checked against measurements/literature. Useful as a validated tool, but not new science. |
| **Derived consequences of a stated model** | "In LQC + Lewandowski–Ma–Yang geometry the bounce edge is causally disconnected, so exterior radiation carries no information (0 bits)" | Legitimate theoretical result: *if* the assumptions hold, *then* this follows. It agrees with the existing baby-universe literature, so it is a confirmation rather than a discovery. |
| **Statements about reality** | "We live in a black hole" / "a new galaxy forms inside" | **Not tested.** There is no measurement here, and the interior of a black hole is currently unobservable. |

A computer simulation does not produce data about nature. It produces the
consequences of the equations you put into it. The value is that those
consequences can be checked (§2, first row) and can be compared with
observations (§4). This project is honest theoretical exploration. It is not
evidence either way on whether we live in a black hole.

## 3. What happens mathematically — the kernel of truth

1. **Inside a collapsing star is a piece of a (contracting) universe.** The
   Oppenheimer–Snyder solution used here describes the star's interior *exactly*
   as a patch of a homogeneous Friedmann universe running backwards. This is
   textbook general relativity (Oppenheimer & Snyder 1939).
2. **Loop quantum gravity makes it bounce.** With the effective LQC equations,
   the contraction stops at ρ_c ≈ 0.41 ρ_Planck ≈ 2×10⁹⁶ kg/m³ and turns into
   expansion: a(τ) ∝ (1 + τ²/τ_b²)^{1/3}. A contracting Friedmann patch that
   turns into an expanding Friedmann patch is mathematically what a
   "Big Bang inside a black hole" means. The simulation computes this for every
   mass; the region expands by 33–77 e-folds.
3. **What happens to an asteroid** (`cosmology_checks.py`, §4):

   | Black hole | Torn apart before the horizon? | Own time to the centre | Fades from outside view in | Page time |
   |---|---|---|---|---|
   | 10 M_☉ | yes | 66 μs | ~0.2 ms | 6×10⁶⁹ yr |
   | Sgr A* | yes | 28 s | ~85 s | 5×10⁸⁶ yr |
   | M87* | no, swallowed whole | 12 hours | ~36 hours | 2×10⁹⁶ yr |

   - **From outside:** the hole gains exactly the asteroid's mass-energy and
     1.6×10⁶⁰ to 10⁶⁹ bits of entropy. Everything else disappears from view (the no-hair theorem).
   - **At the bounce:** the density is ~10⁷⁹ times nuclear density, and if
     thermal, the temperature is 1.3×10³² K.
     **No atom, nucleus or proton survives. The asteroid is dissolved, not transported.**
   - **If the region then expands and cools** (T ∝ 1/a), the same sequence as
     our own Big Bang would repeat: protons after ~46 e-folds, nuclei after ~53,
     atoms after ~66. So "atoms start to form a new galaxy" is not absurd.
     The atoms would be *new* atoms made from reprocessed energy, not the asteroid's atoms.

## 4. Where the idea runs into trouble — what is missing

| Problem | Why it matters | What would fix it |
|---|---|---|
| **Energy budget** | A bounce creates no matter. Sgr A* contains ~1/350 000 of a galaxy; our Hubble volume holds 9×10⁵² kg, i.e. 10¹⁶ Sgr A*'s. | **Inflation after the bounce.** Vacuum energy grows as e^{3N}, so only 10–17 e-folds are needed for the energy. LQC is reported to make inflation very likely after a bounce (Ashtekar & Sloan 2011). |
| **Shape of the interior** | Inside a Schwarzschild hole spacetime is anisotropic: stretched in one direction, squeezed in two (Kantowski–Sachs). Our universe is isotropic to 1 part in 10⁵. | Show that inflation, or the bounce itself, isotropizes the region. This project avoids the problem by using a homogeneous dust star. |
| **Where is the new universe?** | In the Lewandowski–Ma–Yang geometry the bounced region lies beyond the inner (Cauchy) horizon, in a new asymptotic region. Inner horizons are unstable to anything falling in later (mass inflation, Poisson & Israel 1990). | A stable causal structure: a full quantum-gravity collapse calculation, not an effective model. |
| **"Hubble radius = Schwarzschild radius"** | Often quoted as evidence, but it is an identity of any flat Friedmann universe: r_s = c/H exactly, for every H (§1 of the script). | Do not use it as evidence. |
| **Testable predictions** | Without them the idea cannot be defended scientifically. | See §5. |

## 5. If you want to defend a thesis: what to calculate

**The detailed plan is in [thesis-plan.md](thesis-plan.md)** — work packages, equations,
data ([`data/observations.json`](../data/observations.json)), pass/fail criteria.

A defensible thesis does **not** claim "we live in a black hole". It claims
something like: *"If our Big Bang was an LQC bounce inside a black hole, then
we should observe X; current data give Y."* The calculations for that:

1. **Replace dust with a scalar field** (inflaton) in the bounce: the effective
   LQC Friedmann equation with a φ² or Starobinsky potential. Compute the
   number of inflation e-folds after the bounce, and check that it is ≥ 60 and
   that the energy budget closes. This project already has the LQC equations
   and an ODE solver (`core/src/quantum/lqc.rs`, `time_evolution/ode.rs`).
2. **Anisotropy:** start from a Kantowski–Sachs interior (not Friedmann) and
   show whether the shear decays through the bounce and inflation.
3. **Curvature prediction:** a bounced star is most naturally a *closed*
   universe. Compute the predicted Ω_k after N e-folds and compare with
   Planck: Ω_k = 0.0007 ± 0.0019.
4. **Imprint of the parent's spin:** Popławski argues a rotating parent
   (a* ≠ 0 — which the Kerr part of this project now tracks) leaves a preferred
   axis in the child universe. Compute its size and compare with CMB
   large-angle anomalies and galaxy-spin asymmetry claims (reported by Shamir;
   contested).
5. **Imprint of the bounce on the CMB:** pre-inflationary LQC dynamics
   suppress/modify the largest-scale power (Agullo, Ashtekar & Nelson 2012–13).
   Compute the predicted power spectrum and compare with the observed low-ℓ deficit.
6. **Statistics (Smolin's cosmological natural selection):** if universes
   reproduce through black holes, physical constants should be near values that
   maximize black hole production. That is falsifiable. Smolin predicted no
   neutron stars above ~1.6 M_☉, and ~2 M_☉ pulsars have since been found.
   Check how that prediction stands.

Each of these gives a number you can compare with a measurement. That is the
difference between a defended thesis and "playing with numbers".

## 6. Key references (verify page numbers before citing)

- Oppenheimer & Snyder, Phys. Rev. 56, 455 (1939) — collapse interior is Friedmann
- Pathria, Nature 240, 298 (1972) — "The universe as a black hole"
- Frolov, Markov & Mukhanov, Phys. Lett. B 216, 272 (1989); PRD 41, 383 (1990)
- Smolin, Class. Quantum Grav. 9, 173 (1992); hep-th/0407213 (2004)
- Farhi & Guth, Phys. Lett. B 183, 149 (1987); Farhi, Guth & Guven, Nucl. Phys. B 339, 417 (1990) — creating a universe from a small region needs inflation (and a singularity or tunnelling)
- Popławski, Phys. Lett. B 694, 181 (2010) — torsion bounce, universe in a black hole
- Ashtekar & Sloan, Gen. Rel. Grav. 43, 3619 (2011) — probability of inflation in LQC
- Agullo, Ashtekar & Nelson, PRL 109, 251301 (2012) — LQC extension of inflation, CMB imprints
- Lewandowski, Ma, Yang & Zhang, PRL 130, 101501 (2023) — quantum Oppenheimer–Snyder
- Poisson & Israel, PRD 41, 1796 (1990) — mass inflation at inner horizons
- Planck Collaboration, A&A 641, A6 (2020) — Ω_k, H0
- Almheiri et al., Rev. Mod. Phys. 93, 035002 (2021) — how information *can* leave a black hole (islands, Page curve)
