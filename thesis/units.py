"""Planck-egységek és konverziók (WP0).

Planck-egységben G = ħ = c = k_B = 1: hossz ℓ_P, idő t_P, tömeg m_Pl,
sűrűség ρ_Pl = m_Pl/ℓ_P³, hőmérséklet T_Pl. A redukált Planck-tömeg
M_Pl = m_Pl/√(8π). CODATA 2022 — azonos a Rust mag core/src/constants.rs-ével.
"""
from __future__ import annotations

import math

# SI (CODATA 2022)
C = 299_792_458.0
H_PLANCK = 6.626_070_15e-34
HBAR = H_PLANCK / (2 * math.pi)
K_B = 1.380_649e-23
G = 6.674_30e-11
EV = 1.602_176_634e-19  # J

L_P = math.sqrt(HBAR * G / C**3)  # m
T_P = L_P / C  # s
M_P = math.sqrt(HBAR * C / G)  # kg
RHO_PL = M_P / L_P**3  # kg/m³
TEMP_PL = M_P * C**2 / K_B  # K
M_PL_GEV = M_P * C**2 / EV / 1e9  # 1.2209e19 GeV
REDUCED_M_PL = 1.0 / math.sqrt(8 * math.pi)  # Planck-egységben

M_SUN = 1.988_47e30
MPC = 3.085_677_581_491_367e22  # m
GPC = 1e3 * MPC
YEAR = 3.155_76e7

# LQC (Ashtekar–Singh 2011; LMY 2023): γ, a terület-rés λ² = 4√3πγ ℓ_P²,
# ρ_c = 3/(8πγ²λ²) = √3/(32π²γ³) ρ_Pl ≈ 0.4094 ρ_Pl
GAMMA_BI = 0.2375
LAMBDA2 = 4 * math.sqrt(3) * math.pi * GAMMA_BI  # ℓ_P² egységben
RHO_C = 3 / (8 * math.pi * GAMMA_BI**2 * LAMBDA2)  # Planck-egységben
ALPHA_LMY = 16 * math.sqrt(3) * math.pi * GAMMA_BI**3  # ℓ_P² egységben

# Kozmológia (Planck 2018 VI, TT,TE,EE+lowE+lensing)
T_CMB = 2.7255  # K
H0_KM_S_MPC = 67.32
Z_EQ = 3402.0
G_STAR_S_TODAY = 3.909  # entrópia-szabadsági fokok ma


def gev_to_planck(e_gev: float) -> float:
    """Energia/hőmérséklet GeV-ben → Planck-egység."""
    return e_gev / M_PL_GEV


def kelvin_to_planck(t_k: float) -> float:
    return t_k / TEMP_PL


def meters_to_planck(x_m: float) -> float:
    return x_m / L_P


def hubble0_planck() -> float:
    """H0 Planck-egységben (1/t_P)."""
    return H0_KM_S_MPC * 1e3 / MPC * T_P


def hubble_radius_m() -> float:
    return C / (H0_KM_S_MPC * 1e3 / MPC)


# A megfigyelhető Univerzum komóving sugara (részecskehorizont), Planck 2018 ΛCDM
PARTICLE_HORIZON_M = 14.26 * GPC
