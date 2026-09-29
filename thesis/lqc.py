"""Effektív LQC-háttér (WP0) — Planck-egységben.

Lapos Friedmann–Lemaître–Robertson–Walker (FLRW), effektív egyenletek
(Ashtekar & Singh 2011):
    H² = (8π/3) ρ (1 − ρ/ρ_c)
    Ḣ  = −4π (ρ + P)(1 − 2ρ/ρ_c)
Por (P = 0) analitikus megoldása (τ a visszapattanástól):
    ρ(τ) = ρ_c / (1 + 6πρ_c τ²)
A LMY (2023) külső metrikában a porgömb visszapattanási sugara
    r_b = (α m/2)^{1/3},  α = 16√3πγ³ ℓ_P²,  m = GM/c².
"""
from __future__ import annotations

import math

from thesis.units import ALPHA_LMY, L_P, RHO_C, C, G


def hubble_squared(rho: float) -> float:
    return (8 * math.pi / 3) * rho * (1 - rho / RHO_C)


def h_max() -> float:
    """H² maximuma ρ = ρ_c/2-nél: H_max = √(2πρ_c/3) ≈ 0.926 /t_P."""
    return math.sqrt(2 * math.pi * RHO_C / 3)


def dust_density(tau: float) -> float:
    return RHO_C / (1 + 6 * math.pi * RHO_C * tau**2)


def raychaudhuri(rho: float, pressure: float) -> float:
    return -4 * math.pi * (rho + pressure) * (1 - 2 * rho / RHO_C)


def bounce_radius_m(mass_kg: float) -> float:
    """A porgömb visszapattanási sugara méterben (LMY 2023)."""
    m_geo = G * mass_kg / C**2 / L_P  # m = GM/c² ℓ_P egységben
    return float((ALPHA_LMY * m_geo / 2) ** (1 / 3) * L_P)
