#!/usr/bin/env python3
"""Back-of-the-envelope checks for the question "do we live in a black hole?"

Every number printed here comes from a formula stated next to it, so the
calculations can be defended line by line. Run:  python scripts/cosmology_checks.py

1. The "Hubble radius = Schwarzschild radius" coincidence — and why it is an
   identity of flat Friedmann cosmology, not evidence.
2. Energy budget: can a bounce inside a black hole of mass M make a universe
   like ours? How much inflation would be needed?
3. A hot bounce: how hot is matter at the LQC critical density, and how much
   expansion is needed before nuclei and atoms can form?
4. An asteroid falling into real black holes: tidal disruption, time to the
   centre, what an outside observer sees, entropy, information return.
"""
from __future__ import annotations

import math

# CODATA 2022 / IAU
C = 299_792_458.0
G = 6.674_30e-11
HBAR = 1.054_571_817_646_156_5e-34
K_B = 1.380_649e-23
SIGMA_SB = math.pi**2 * K_B**4 / (60 * HBAR**3 * C**2)
A_RAD = 4 * SIGMA_SB / C  # radiation constant, J m^-3 K^-4
M_SUN = 1.988_47e30
M_PROTON = 1.672_621_925_95e-27
YEAR = 3.155_76e7
GLY = 9.4607e24  # m
MPC = 3.085_677_581e22
RHO_PLANCK = C**5 / (HBAR * G**2)
RHO_CRIT_LQC = 0.4094 * RHO_PLANCK  # this project: sqrt(3)/(32 pi^2 gamma^3) rho_Pl

# Planck 2018 (TT,TE,EE+lowE+lensing+BAO)
H0 = 67.66 * 1e3 / MPC  # 1/s
OMEGA_K_PLANCK = (0.0007, 0.0019)  # curvature, mean ± 1σ


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def hubble_vs_schwarzschild() -> None:
    section("1. Is the universe 'inside its own Schwarzschild radius'?")
    r_h = C / H0
    rho_c = 3 * H0**2 / (8 * math.pi * G)
    m_h = 4 / 3 * math.pi * r_h**3 * rho_c
    r_s = 2 * G * m_h / C**2
    print(f"Hubble radius       R_H = c/H0                 = {r_h:.3e} m = {r_h / GLY:.2f} Gly")
    print(f"critical density    ρ_c = 3H0²/(8πG)            = {rho_c:.3e} kg/m³ (~5 protons/m³)")
    print(f"mass inside R_H     M_H = (4π/3) R_H³ ρ_c       = {m_h:.3e} kg = {m_h / M_SUN:.2e} M_☉")
    print(f"its Schwarzschild radius  r_s = 2GM_H/c²        = {r_s:.3e} m")
    print(f"ratio r_s/R_H = {r_s / r_h:.6f}")
    print("→ Exactly 1, for ANY value of H0: substitute ρ_c into r_s and it cancels:")
    print("  r_s = 2G(4π/3)(3H²/8πG)(c/H)³/c² = c/H = R_H.  It is an identity of a flat")
    print("  Friedmann universe, not a measurement. It is consistent with 'we are inside a")
    print("  black hole' but it would be equally true if we are not.")
    lo, hi = OMEGA_K_PLANCK[0] - 2 * OMEGA_K_PLANCK[1], OMEGA_K_PLANCK[0] + 2 * OMEGA_K_PLANCK[1]
    print(f"Measured spatial curvature Ω_k = {OMEGA_K_PLANCK[0]} ± {OMEGA_K_PLANCK[1]} (Planck 2018):")
    print(f"  95% range [{lo:+.4f}, {hi:+.4f}] — flat within errors. A closed universe (Ω_k < 0),")
    print("  which a collapsed-and-bounced star most naturally produces, is allowed but not seen.")


def energy_budget() -> None:
    section("2. Energy budget: can a bounce make a universe like ours?")
    r_h = C / H0
    m_h = 4 / 3 * math.pi * r_h**3 * 3 * H0**2 / (8 * math.pi * G)
    print("A bounce (LQC, this project) does NOT create matter: the expanding region")
    print("contains exactly the mass that collapsed. Compare with our Hubble volume:")
    print(f"{'parent black hole':<28}{'mass (kg)':>12}{'M_H / M':>12}{'galaxies*':>12}{'N_E needed':>12}")
    parents = [("10 M_☉ stellar", 10 * M_SUN), ("Sgr A* (4.3e6 M_☉)", 4.3e6 * M_SUN),
               ("M87* (6.5e9 M_☉)", 6.5e9 * M_SUN), ("TON 618-class (6.6e10 M_☉)", 6.6e10 * M_SUN)]
    for name, m in parents:
        ratio = m_h / m
        n_e = math.log(ratio) / 3
        print(f"{name:<28}{m:>12.2e}{ratio:>12.1e}{m / (1.5e12 * M_SUN):>12.1e}{n_e:>12.1f}")
    print("* in units of a Milky-Way-mass galaxy (1.5e12 M_☉ including dark matter)")
    print("N_E = ln(M_H/M)/3: e-folds of *inflation* needed to grow the energy that much.")
    print("  During inflation the vacuum energy density stays constant while volume grows")
    print("  as a³, so energy grows as e^(3N) (the 'free lunch' of Guth; energy is not")
    print("  globally conserved in an expanding spacetime). 13–17 e-folds would suffice for")
    print("  the energy — standard inflation already needs ~60 for flatness/horizon problems.")
    print("→ Without inflation: a bounce inside Sgr A* makes at most ~1/350 000 of a galaxy.")
    print("  With inflation after the bounce the mass of the parent becomes irrelevant.")


def hot_bounce() -> None:
    section("3. A hot bounce: when could atoms form in the new region?")
    t_bounce = (RHO_CRIT_LQC * C**2 / A_RAD) ** 0.25
    print(f"LQC bounce density ρ_c = {RHO_CRIT_LQC:.2e} kg/m³ (nuclear density is ~2.3e17)")
    print(f"If that energy is thermal radiation: T = (ρ_c c²/a_rad)^(1/4) = {t_bounce:.2e} K")
    print("Everything that fell in — asteroid, star, atoms, nuclei — is dissolved into a")
    print("Planck-temperature plasma. Nothing of its structure survives.")
    for label, t in [("quark–gluon plasma → protons/neutrons", 2e12), ("Big-Bang-like nucleosynthesis", 1e9),
                     ("atoms form (recombination)", 3000.0)]:
        n = math.log(t_bounce / t)
        print(f"  {label:<40} T ≈ {t:.0e} K after N = ln(T_b/T) = {n:5.1f} e-folds of expansion")
    print("In a radiation-filled expanding region T ∝ 1/a, so after ~66 e-folds the same")
    print("physics as our own Big Bang (hadrons → nuclei → atoms) would run again, IF the")
    print("region keeps expanding and is big enough. Our dust simulation expanded 33–77")
    print("e-folds before reaching its starting radius, i.e. the right order of magnitude —")
    print("but it contains only the parent's mass (see section 2).")


def asteroid() -> None:
    section("4. An asteroid (1 km, 2000 kg/m³ ≈ 1e12 kg) falls into a black hole")
    r_ast, rho_ast = 500.0, 2000.0
    m_ast = 4 / 3 * math.pi * r_ast**3 * rho_ast
    print(f"asteroid mass m = {m_ast:.2e} kg, radius {r_ast:.0f} m")
    print(f"{'black hole':<20}{'r_s':>11}{'tidal r_t':>11}{'shredded':>10}{'τ fall':>11}"
          f"{'fade':>10}{'ΔS (bits)':>11}{'Page time':>12}")
    for name, m in [("10 M_☉", 10 * M_SUN), ("Sgr A*", 4.3e6 * M_SUN), ("M87*", 6.5e9 * M_SUN)]:
        r_s = 2 * G * m / C**2
        r_t = r_ast * (m / m_ast) ** (1 / 3)  # tidal radius for a self-gravitating body
        tau = 4 * G * m / (3 * C**3)  # proper time horizon → centre, radial fall from rest at ∞
        fade = 4 * G * m / C**3  # e-folding time of the redshift seen from outside
        # ΔS = dS/dM · ΔM = 8πGMΔM/(ħc) k_B  (Bekenstein–Hawking), in bits
        ds_bits = 8 * math.pi * G * m * m_ast / (HBAR * C) / math.log(2)
        # Page time ≈ half the vacuum Hawking lifetime (τ ≈ 8895 M³ Planck units, photons+gravitons)
        t_page_yr = 0.5 * 8895 * (m / 2.176434e-8) ** 3 * 5.391247e-44 / YEAR
        print(f"{name:<20}{r_s:>11.2e}{r_t:>11.2e}{('yes' if r_t > r_s else 'no'):>10}"
              f"{tau:>10.2e}s{fade:>9.1e}s{ds_bits:>11.1e}{t_page_yr:>10.0e} yr")
    print("• shredded: the tidal radius r_t = R(M/m)^(1/3) is outside the horizon, so the")
    print("  asteroid is torn into a stream before it enters (stellar BH, Sgr A*); a giant")
    print("  like M87* swallows it whole. (Real asteroids also have material strength.)")
    print("• τ fall: the asteroid's own clock from horizon to the centre / bounce region.")
    print("• fade: seen from outside it never 'enters' — its light is redshifted by e every")
    print("  4GM/c³ and it dims away within a few such times.")
    print("• ΔS: entropy increase of the black hole = the information capacity it gains.")
    print("• The asteroid's mass/energy adds to M (horizon grows by 2GΔM/c²); everything else")
    print("  about it (composition, shape) disappears from the outside (no-hair theorem).")
    print("  If quantum mechanics is unitary it returns in Hawking radiation only after the")
    print("  Page time — and today these black holes grow instead of evaporating (CMB).")


if __name__ == "__main__":
    hubble_vs_schwarzschild()
    energy_budget()
    hot_bounce()
    asteroid()
