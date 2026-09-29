"""Az infláció utáni tágulás a mai napig (WP1/WP3 közös).

N_post = ln(a_0/a_end) = N_reh + ln(a_0/a_reh):
    felmelegedés (w = 0, oszcilláló inflaton): a_reh/a_end = (ρ_end/ρ_reh)^{1/3}
    utána entrópia-megmaradás:  a_0/a_reh = (g_s,reh/g_s,0)^{1/3} · T_reh/T_0
ρ_reh = (π²/30) g_* T_reh⁴ (Planck-egységben k_B = ħ = c = 1).
Az egyenlőségi korszak: a_eq/a_0 = 1/(1 + z_eq), z_eq = 3402 (Planck 2018).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

from thesis.units import G_STAR_S_TODAY, T_CMB, Z_EQ, gev_to_planck, kelvin_to_planck

G_STAR_REH = 106.75  # Standard Modell, T ≫ 100 GeV


@dataclass
class PostInflation:
    t_reh_gev: float
    n_reheat: float  # infláció vége → felmelegedés (anyag-szerű)
    n_radiation: float  # felmelegedés → egyenlőség
    n_matter: float  # egyenlőség → ma
    n_post: float  # összesen: infláció vége → ma

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def rho_radiation(t_planck: float, g_star: float = G_STAR_REH) -> float:
    return math.pi**2 / 30 * g_star * t_planck**4


def max_reheat_temperature_gev(rho_end: float) -> float:
    """Azonnali felmelegedés: ρ_reh = ρ_end."""
    t = (rho_end / (math.pi**2 / 30 * G_STAR_REH)) ** 0.25
    return float(t / gev_to_planck(1.0))


def post_inflation(rho_end: float, t_reh_gev: float) -> PostInflation:
    t_reh = gev_to_planck(t_reh_gev)
    rho_reh = rho_radiation(t_reh)
    if rho_reh > rho_end * (1 + 1e-9):
        raise ValueError("T_reh nagyobb, mint az azonnali felmelegedés hőmérséklete")
    n_reh = max(math.log(rho_end / rho_reh) / 3, 0.0)
    n_after = math.log((G_STAR_REH / G_STAR_S_TODAY) ** (1 / 3) * t_reh / kelvin_to_planck(T_CMB))
    n_mat = math.log(1 + Z_EQ)
    return PostInflation(t_reh_gev=t_reh_gev, n_reheat=n_reh, n_radiation=n_after - n_mat,
                         n_matter=n_mat, n_post=n_reh + n_after)
