"""WP2: a fekete lyuk belsejének anizotrópiája a visszapattanáson és az infláción át.

**A fekete-lyuk kezdeti nyírása.** A Schwarzschild-belső vákuum Kantowski–Sachs-tér:
areális sugárral (r < 2m) mint idővel a tágulási ráták
    H_x = (m/r²)/√(2m/r − 1),   H_Ω = −√(2m/r − 1)/r,
a nyírás σ² = (2/3)(H_x − H_Ω)² → r ≪ 2m-re σ² = 3m/r³ (és H² = σ²/6: vákuum).
Ha a visszapattanó porgömb a határán ezt a nyírást örökli, a visszapattanáskor
(r = r_b, ρ_c = m/(4π r_b³/3)):
    ρ_σ = σ²/(16π) = 3m/(16π r_b³) = ρ_c/4,   azaz  Ω_σ = ρ_σ/(ρ_σ + ρ_m) = 0.2,
**tömegtől függetlenül**. Ez felső becslés: a homogén Oppenheimer–Snyder-gömb
belseje pontosan izotróp (Ω_σ = 0); valódi, inhomogén csillag a kettő között van.

**Mai érték.** σ ∝ a⁻³ mindig; σ/H ∝ e^{−3N} infláció alatt (ezt az ODE adja),
utána a^{−3/2} (felmelegedés, w = 0), a⁻¹ (sugárzás), a^{−3/2} (anyag).
A Λ-korszakot elhanyagoljuk (az csak tovább csökkentené) — konzervatív.
"""
from __future__ import annotations

import math
from typing import Any

from thesis.history import max_reheat_temperature_gev, post_inflation
from thesis.inflation import Potential, Starobinsky, evolve
from thesis.units import GAMMA_BI, LAMBDA2, RHO_C
from thesis.wp1 import phi2_fraction, threshold_phi_b

SIGMA2_MAX = 10.125 / (3 * GAMMA_BI**2 * LAMBDA2)  # Gupt & Singh 2012, ≈ 11.57 ℓ_P⁻²
OMEGA_SIGMA_MAX = SIGMA2_MAX / (16 * math.pi * RHO_C)  # a merev-folyadék közelítés határa
SIGMA_OVER_H_VECTOR_LIMIT = 4.7e-11  # Saadeh et al. 2016, 95%


def kantowski_sachs_shear(r_over_m: float) -> dict[str, float]:
    """Vákuum Schwarzschild-belső (r < 2m) tágulási rátái és nyírása, m = 1 egységben."""
    f = 2 / r_over_m - 1
    if f <= 0:
        raise ValueError("csak a horizonton belül (r < 2m)")
    h_x = (1 / r_over_m**2) / math.sqrt(f)
    h_om = -math.sqrt(f) / r_over_m
    sigma2 = (2 / 3) * (h_x - h_om) ** 2
    theta = h_x + 2 * h_om
    return {"h_x": h_x, "h_omega": h_om, "sigma2": sigma2, "H2": (theta / 3) ** 2}


def bh_shear_fraction() -> float:
    """Ω_σ a visszapattanáskor, ha a gömb a vákuum-KS nyírást örökli (r_b ≪ 2m határ)."""
    rho_sigma_over_rho_c = 3 / (16 * math.pi) * (4 * math.pi / 3)  # = 1/4
    return rho_sigma_over_rho_c / (1 + rho_sigma_over_rho_c)


def log10_shear_today(log10_sh_end: float, rho_end: float, t_reh_gev: float) -> float:
    post = post_inflation(rho_end, t_reh_gev)
    ln_drop = 1.5 * post.n_reheat + post.n_radiation + 1.5 * post.n_matter
    return log10_sh_end - ln_drop / math.log(10)


def scan(pot: Potential, phi_b: float, sign: int, fractions: list[float]) -> list[dict[str, Any]]:
    out = []
    for om in fractions:
        r = evolve(pot, phi_b, sign, shear_fraction=om)
        row: dict[str, Any] = {"omega_sigma": om, "sigma2_b": 16 * math.pi * om * RHO_C,
                               "within_lqc_bound": om <= OMEGA_SIGMA_MAX, **r.as_dict()}
        if r.log10_shear_over_h_end is not None and r.v_end is not None:
            rho_end = 1.5 * r.v_end
            row["log10_shear_today"] = {
                "instant_reheat": log10_shear_today(r.log10_shear_over_h_end, rho_end,
                                                    max_reheat_temperature_gev(rho_end)),
                "T_reh_4MeV": log10_shear_today(r.log10_shear_over_h_end, rho_end, 4e-3),
            }
        out.append(row)
    return out


def run() -> dict[str, Any]:
    star = Starobinsky()
    om_bh = bh_shear_fraction()
    fractions = sorted({0.0, 1e-6, 1e-4, 1e-2, 0.05, 0.1, om_bh, 0.3, 0.4, 0.5, 0.56})
    cases = {
        # φ_B-k, amelyek nyírás nélkül 60–120 e-redőt adnak (nem érik el a plafont)
        "starobinsky_plus_-1.30": scan(star, -1.30, 1, fractions),
        "starobinsky_plus_-1.45": scan(star, -1.45, 1, fractions),
        "starobinsky_minus_3.70": scan(star, 3.70, -1, fractions),
    }
    # a fekete-lyuk nyírással eltolt küszöbök (60 e-redő) és a φ² mérték
    thresholds = {
        "plus_N60": threshold_phi_b(star, 1, 60.0, -1.8, 2.0, shear_fraction=om_bh),
        "minus_N60": threshold_phi_b(star, -1, 60.0, 3.3, 6.0, shear_fraction=om_bh),
    }
    frac = phi2_fraction(shear_fraction=om_bh)
    ks = kantowski_sachs_shear(1e-6)
    return {"omega_sigma_bh": om_bh, "omega_sigma_max_lqc": OMEGA_SIGMA_MAX,
            "sigma2_max": SIGMA2_MAX, "ks_check_H2_over_sigma2_6": ks["H2"] / (ks["sigma2"] / 6),
            "limit_vector": SIGMA_OVER_H_VECTOR_LIMIT, "cases": cases,
            "thresholds_bh_shear": thresholds, "phi2_fraction_bh_shear": frac}
