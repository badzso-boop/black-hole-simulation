"""WP4: örököl-e a bébiuniverzum forgást (kitüntetett tengelyt) a Kerr-szülőtől?

Planck-egységben (G = c = ħ = 1), m = GM/c²:
    J = a* m²,  a visszapattanáskor merev gömbként I = (2/5) m r_b²
    → ω_B = J/I = (5/2) a* m / r_b²
**Mekkora spin fér bele a visszapattanásba?** Két, egymással egyező nagyságrendű feltétel:
    (a) a forgás ne domináljon a visszapattanáskor: ω_B < H_max  →  a*_max = H_max r_b² / (2.5 m)
    (b) a centrifugális gát (Newtoni becslés r_c = j²/m, j = a* m) r_b alatt legyen:
        a*² m < r_b  →  a*_max = √(r_b/m)
A szigorúbb (a) ≈ 9·10⁻⁸ az 5.1e11 kg-os szülőre, ≈ 3·10⁻¹⁴ 10 M☉-re, és nagyobb tömegnél még
kisebb (∝ m^{−1/3}): a porgömb csak gyakorlatilag nem forgó szülőben jut el ρ_c-ig.
Valódi fekete lyukak a* ~ 0.1–0.998 → a forgó anyag nem homogén visszapattanással
éri el a Planck-sűrűséget; ez a modell korlátja, nem jóslat.

**Hígulás** (a forgást a szülő pora viszi, perdület-megmaradás (ρ+p) a⁵ ω = áll.):
    por: ω ∝ a⁻² → infláció alatt ω/H ∝ e^{−2N}; felmelegedés a^{−1/2}; sugárzás a⁰; anyag a^{−1/2}
Ha a forgás a sugárzásba kerül (felső becslés): sugárzáskor ω/H ∝ a^{+1}.
A skalármező maga örvénymentes (u ∝ ∂φ), nem hordozhat forgást.
"""
from __future__ import annotations

import math
from typing import Any

from thesis.history import PostInflation
from thesis.lqc import bounce_radius_m, h_max
from thesis.units import L_P, C, G

OMEGA_OVER_H_LIMIT = 7.6e-10  # Planck 2015 XVIII, 95%


def a_star_max(mass_kg: float) -> dict[str, float]:
    m = G * mass_kg / C**2 / L_P
    r_b = bounce_radius_m(mass_kg) / L_P
    return {"hubble_criterion": h_max() * r_b**2 / (2.5 * m),
            "centrifugal_criterion": math.sqrt(r_b / m)}


def log10_omega_over_h_today(a_star: float, mass_kg: float, n_onset: float, h_onset: float,
                             n_infl: float, post: PostInflation, carrier: str = "dust") -> float:
    m = G * mass_kg / C**2 / L_P
    r_b = bounce_radius_m(mass_kg) / L_P
    ln = math.log(2.5 * a_star * m / r_b**2)  # ln ω_B
    ln += -2 * n_onset - math.log(h_onset)  # a visszapattanástól a lassú gördülésig: por, ω ∝ a⁻²
    ln += -2 * n_infl  # infláció: H ≈ áll.
    if carrier == "dust":
        ln += -0.5 * post.n_reheat + 0.0 * post.n_radiation - 0.5 * post.n_matter
    elif carrier == "radiation":
        ln += -0.5 * post.n_reheat + 1.0 * post.n_radiation - 0.5 * post.n_matter
    else:
        raise ValueError(carrier)
    return ln / math.log(10)


def run(parents_kg: dict[str, float], n_onset: float, h_onset: float, n_infl: float,
        post: PostInflation) -> dict[str, Any]:
    rows = []
    for label, m in parents_kg.items():
        amax = a_star_max(m)
        a_use = min(amax.values())
        rows.append({
            "parent": label, "mass_kg": m, "a_star_max": amax,
            # a legnagyobb spin, ami még visszapattanhat, és egy valódi (0.9) is — a
            # 0.9-es sor csak formális: ekkora spinnél a modell nem érvényes
            "log10_omega_over_h_today_at_a_max": {
                c: log10_omega_over_h_today(a_use, m, n_onset, h_onset, n_infl, post, c)
                for c in ("dust", "radiation")},
            "log10_omega_over_h_today_formal_a0.9": {
                c: log10_omega_over_h_today(0.9, m, n_onset, h_onset, n_infl, post, c)
                for c in ("dust", "radiation")},
        })
    return {"rows": rows, "limit": OMEGA_OVER_H_LIMIT, "n_infl": n_infl, "n_onset": n_onset,
            "h_onset": h_onset}
