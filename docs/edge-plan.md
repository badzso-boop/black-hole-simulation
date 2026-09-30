# Plan: what the edge disturbance does to the seed's interior (S4, Level 1b)

**Status:** plan, 2026-09-30. §4 is fixed **before** any number below §5 is computed.

**Background:** [inner-horizon-plan.md](inner-horizon-plan.md) §9.
- The inner horizon of the bounced ball's own quantum (LMYZ) exterior is unstable.
- A disturbance from the ball's edge can travel η_total ≈ 9.6×10³ ℓ_P inward by the end of
  inflation.
- The spinning-parent route (WP4b) only allows tiny axial seeds: 16 m_P at a* = 0.44,
  1.4×10³ m_P at a* = 0.1, with radius r_b of a few ℓ_P.
- So the disturbance can cover the whole seed. The question here is whether that actually
  **destroys** it.

---

## 1. The question

Take a seed of mass m_s that bounces as a homogeneous LQC ball of comoving radius χ_b = r_b(m_s),
with a_B = 1 at the bounce. At the bounce, its edge starts to feel the unstable inner horizon of its
own exterior.

**Does the disturbance reach the seed's centre, and become nonlinear there, before inflation
starts?** If it does, the homogeneous interior that is supposed to become our universe no longer
exists.

## 2. Model (all in Planck units)

**E1. Causal reach.** The disturbance front leaves the edge at the bounce and moves inward at the
speed of light: χ_front(η) = χ_b − η, with η = ∫dt/a.
- Background: the kinetic LQC bounce a(t) = (1 + 24πρ_c t²)^{1/6} up to the onset of inflation
  (a_on = e^{n_on}, with n_on, H_on taken from the WP1 trajectory used by the runner).
- After onset, the comoving reach grows by at most 1/(a_on H_on).
- Outputs:
  - η_c, the time the front reaches the centre (η_c = χ_b), compared with η_on;
  - the undisturbed core at onset, χ_core = χ_b − η_on, compared with the inflationary Hubble
    radius 1/(a_on H_on). A patch inflates only if it is larger than its Hubble radius.

**E2. Amplification.** At the edge the disturbance is driven by the inner-horizon instability. The
edge amplitude grows at the rate κ₀(m_s) of the seed's LMYZ inner horizon, as measured by the Ori
model in L1a (0.94–0.98 κ₀). Its log-growth by the time the front reaches the centre is
N_amp = κ₀·Δt, where Δt is the proper time to reach η_c (or η_on, if onset comes first).
- Using proper time rather than conformal time is conservative, since a ≥ 1 gives larger growth.
- The interior then transports it inward causally, without further growth. This is optimistic for
  the seed. It is stated as an assumption.

**E3. Seed amplitude.** The disturbance cannot start below the quantum floor. We use the metric
fluctuation at the seed's scale, δ_q = ℓ_P/r_b (≈ m_P/m_s)^{1/3}-type). A classical δ is scanned
from δ_q up to 0.1.

**E4. Destroyed or not.**
- A seed counts as **destroyed** if δ₀·e^{N_amp} ≥ 1 (the disturbance is nonlinear) by the time
  the front reaches its centre, and that happens before the onset of inflation.
- It **survives** if the undisturbed core at onset is larger than the inflationary Hubble radius.

**E5. Validity.** The effective (quantum-corrected classical) LQC description needs the seed to be
well above the Planck scale. We take **r_b ≥ 10 ℓ_P**, which means m_s ≳ 1.7×10³ m_P. Below that,
neither "destroyed" nor "survives" is trustworthy.

**E6. Combine with WP4b.**
- For each spin in the populations (GW, natal), take the **largest** seed WP4b allows. This is
  the most favourable choice: M_s,max = C³√(α/2)/a*³ with the fiducial C = 1.23.
- Classify each: survives, destroyed, or out of validity.

## 3. Assumptions stated openly

- **Homogeneous ball.** The seed is a homogeneous LQC ball with a vacuum LMYZ exterior of mass m_s.
  Its real surroundings are the interior of the spinning parent, which is not modelled.
- **Amplification only at the edge.** The disturbance is amplified at the rate of the edge's inner
  horizon and only transported inside the ball. A real interior could damp or amplify further.
- **Nonlinear means lost.** "Nonlinear" (δ ≥ 1) is taken to mean the homogeneous description is
  lost. It does not prove that no universe forms.

## 4. Pre-registered outcomes (fixed 2026-09-30, before computing)

| Question | Supports the hypothesis if… | Counts against it if… | Open if… |
|---|---|---|---|
| Does the seed interior survive the edge disturbance? | For the bulk (≥ 50%) of the GW population, the largest allowed seed **survives** (an undisturbed core larger than the inflationary Hubble radius at onset) **and** is within validity (r_b ≥ 10 ℓ_P) | For **every** member of both the GW and the natal populations, the seed is within validity and **destroyed**, even starting from the quantum floor δ_q | Otherwise, in particular if the verdict hinges on seeds with r_b < 10 ℓ_P, where effective LQC cannot decide |

Also reported, but not part of the verdict:
- the smallest seed mass that survives;
- the largest spin whose seed survives.

## 5. Results

(to be filled by `scripts/run_edge.py` → `runs/edge-<date>/`)
