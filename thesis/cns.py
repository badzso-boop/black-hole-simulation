"""WP6: Smolin kozmológiai természetes szelekciója vs neutroncsillag-tömegek.

Smolin jóslata: M_max(NS) < 2 M☉ (2012; korábban 1.5, 1.6). Ha a legnagyobb
neutroncsillag-tömeg M_max, akkor minden mért csillag M_i ≤ M_max, így
    P(M_max < M_lim) ≤ Π_i P(M_i < M_lim)   (független Gauss-hibák)
Ez egyszerű, konzervatív (mértékfüggetlen) felső korlát; a Romani et al. 2022-féle
EoS-marginalizált korlát (M_max > 2.09 M☉ 3σ-n) a data/observations.json-ból jön.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import norm

OBS = Path(__file__).resolve().parent.parent / "data" / "observations.json"


def load() -> dict[str, Any]:
    d: dict[str, Any] = json.loads(OBS.read_text())["6_cosmological_natural_selection"]
    return d


def p_all_below(stars: dict[str, dict[str, float]], m_lim: float) -> float:
    return math.prod(float(norm.cdf((m_lim - s["value"]) / s["err"])) for s in stars.values())


def sigma_equiv(p: float) -> float:
    """Egyoldali p → Gauss-σ."""
    return float(-norm.ppf(p))


def run() -> dict[str, Any]:
    d = load()
    stars = {k: {"value": v["value"], "err": v["err"]}
             for k, v in d["neutron_star_masses_Msun"].items()
             if isinstance(v, dict) and "value" in v and "err" in v}
    out = []
    for label, m_lim in (("Smolin 2004", 1.5), ("Smolin 2006", 1.6), ("Smolin 2012", 2.0)):
        p = p_all_below(stars, m_lim)
        out.append({"prediction": label, "M_max_limit": m_lim, "p_all_below": p,
                    "sigma": sigma_equiv(p) if p > 0 else float("inf")})
    heaviest = {k: stars[k] for k in ("PSR_J0740+6620", "PSR_J0952-0607") if k in stars}
    p2 = p_all_below(heaviest, 2.0)
    return {"stars": stars, "tests": out,
            "two_heaviest_p_below_2": p2, "two_heaviest_sigma": sigma_equiv(p2),
            "romani_bound": d.get("M_max_lower_bound")}
