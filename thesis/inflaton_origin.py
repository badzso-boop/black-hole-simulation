"""B1a: honnan jön az inflaton? Kétfolyadékos (por + skalármező) LQC-visszapattanás.

docs/critical-review.md §3.1, docs/upgrade-plan.md B1a (előre rögzítve 2026-09-30).

A WP1 a visszapattanáskor ρ_c 100%-át a skalármezőbe teszi; az összeomló csillag viszont POR.
Itt a mező a vákuum-minimumában indul (φ_B = 0, φ̇_B > 0) és ρ_c f_φ hányadát viszi, a többi por:
    ρ = ρ_d,B a⁻³ + φ̇²/2 + V(φ),   ρ + P = ρ_d + φ̇²
Kérdés 1: a legkisebb f_φ, amellyel még ≥ 60 e-redő infláció jön (f_φ,min).
Kérdés 2: mennyi mező-energia kell a szülő anyagában az összeomlás ELŐTT?
    Amíg H < m (m: az inflaton tömege), a mező a minimum körül oszcillál → átlagban por-szerű,
    ρ_φ/ρ_d állandó. H > m fölött (ρ_freeze = 3m²/(8π)) a sebessége merev (∝ a⁻⁶), a por ∝ a⁻³,
    tehát ρ_φ/ρ_d ∝ a⁻³ ∝ ρ_d nő, a visszapattanásig ρ_c/ρ_freeze-szeresére:
        r_freeze = [f_φ,min/(1 − f_φ,min)] · ρ_freeze/ρ_c
Ezt a számolás NEM állítja elő (nincs benne mechanizmus) — csak a követelményt adja meg.
Korlát: a klasszikus, homogén becslés a H > m szakaszt tisztán mereven kezeli; a mező
a potenciálban is mozog, ez a kis f_φ-nél elhanyagolható.
"""
from __future__ import annotations

import math
from typing import Any

from thesis.inflation import Potential, Quadratic, Starobinsky, evolve
from thesis.units import RHO_C

N_REQUIRED = 60.0


def inflaton_mass(pot: Potential) -> float:
    """m² = V″(0) a minimumban (Starobinsky: M; φ²: m)."""
    return math.sqrt(pot.d2v(0.0))


def rho_freeze(pot: Potential) -> float:
    """Az a sűrűség, ahol az összeomlás H-ja eléri az inflaton tömegét: 3m²/(8π)."""
    return 3 * inflaton_mass(pot) ** 2 / (8 * math.pi)


H_FLOOR_OVER_M = 0.1  # lásd inflation.evolve h_floor: alatta nincs lassú gördülés


def n_infl_at_vacuum(pot: Potential, field_fraction: float) -> float:
    r = evolve(pot, 0.0, 1, dust_fraction=1.0 - field_fraction,
               h_floor=H_FLOOR_OVER_M * inflaton_mass(pot))
    return float(r.n_infl) if r.inflated else 0.0


def min_field_fraction(pot: Potential, n_req: float = N_REQUIRED, lo: float = 1e-12,
                       hi: float = 1.0, iters: int = 40) -> float | None:
    """A legkisebb f_φ ∈ [lo, hi], amellyel N_infl ≥ n_req (log-biszekció); None, ha hi sem elég."""
    if n_infl_at_vacuum(pot, hi) < n_req:
        return None
    if n_infl_at_vacuum(pot, lo) >= n_req:
        return lo
    a, b = math.log(lo), math.log(hi)
    for _ in range(iters):
        mid = 0.5 * (a + b)
        if n_infl_at_vacuum(pot, math.exp(mid)) >= n_req:
            b = mid
        else:
            a = mid
    return math.exp(b)


def required_pre_collapse_ratio(pot: Potential, f_min: float) -> float:
    """r_freeze: a mező/por energia-arány a H = m pillanatban, ami f_min-t adja ρ_c-nél."""
    return f_min / (1 - f_min) * rho_freeze(pot) / RHO_C


def run() -> dict[str, Any]:
    out: dict[str, Any] = {"potentials": {}}
    for pot in (Starobinsky(), Quadratic()):
        scan = [{"field_fraction": f, "n_infl": n_infl_at_vacuum(pot, f)}
                for f in (1.0, 0.5, 0.1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-8)]
        f_min = min_field_fraction(pot)
        out["potentials"][pot.name] = {
            "inflaton_mass": inflaton_mass(pot),
            "rho_freeze": rho_freeze(pot),
            "amplification_rho_c_over_rho_freeze": RHO_C / rho_freeze(pot),
            "scan": scan,
            "f_field_min": f_min,
            "r_freeze_required": (required_pre_collapse_ratio(pot, f_min)
                                  if f_min is not None and f_min < 1 else None),
        }
    # validáció: tiszta por (a mező nyugalomban a minimumban) nem inflál
    out["validation_pure_dust_inflated"] = bool(
        evolve(Starobinsky(), 0.0, 1, dust_fraction=1.0).inflated)
    return out
