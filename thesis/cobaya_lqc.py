"""cobaya-bővítmény: a hibrid LQC primordiális spektrum (thesis.lqc_spectrum) mint
`primordial_scalar_pk` szolgáltató a CAMB-nak (`external_primordial_pk: true`).

Paraméterek: As, ns (a szokásos ΛCDM), n_tot (e-redők a visszapattanástól máig).
`model: lcdm` esetén n_tot hatástalan (ellenőrző futás ugyanazzal a láncolattal).
A WP5b i5-ös N_tot-rácsa (`grid_scan`) és a Ryzenes MCMC (scripts/cobaya/*.yaml)
ugyanezt az osztályt használja, így a helyi rács a Ryzen-konfigurációt is teszteli.
"""
from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

import numpy as np
from cobaya.theory import Theory

from thesis.lqc_spectrum import suppression_today

K_PIVOT = 0.05
PACKAGES_PATH = os.environ.get("COBAYA_PACKAGES_PATH", str(Path.home() / "cobaya_packages"))
LIKELIHOODS = ["planck_2018_lowl.TT", "planck_2018_lowl.EE",
               "planck_2018_highl_plik.TTTEEE_lite_native"]


class LQCPrimordialPk(Theory):  # type: ignore[misc]
    model: str = "lqc"
    params = {"As": None, "ns": None, "n_tot": None}  # noqa: RUF012 (cobaya konvenció)

    def initialize(self) -> None:
        self.kmin, self.kmax, self.nk = 1e-6, 10.0, 1200
        self.ks = np.logspace(math.log10(self.kmin), math.log10(self.kmax), self.nk)

    def get_can_provide(self) -> list[str]:
        return ["primordial_scalar_pk"]

    def calculate(self, state: dict[str, Any], want_derived: bool = True,
                  **params: Any) -> None:
        pk = params["As"] * (self.ks / K_PIVOT) ** (params["ns"] - 1)
        if self.model == "lqc":
            pk = pk * suppression_today(self.ks, params["n_tot"])
        state["primordial_scalar_pk"] = {"kmin": self.kmin, "kmax": self.kmax, "Pk": pk,
                                         "log_regular": True}

    def get_primordial_scalar_pk(self) -> dict[str, Any]:
        out: dict[str, Any] = self.current_state["primordial_scalar_pk"]
        return out


# Planck 2018 TT,TE,EE+lowE+lensing legjobb illesztés (a WP5 alapvonala)
BESTFIT = {"ombh2": 0.022383, "omch2": 0.12011, "H0": 67.32, "tau": 0.0543,
           "logA": 3.0448, "ns": 0.96605, "A_planck": 1.0}


LOW_ELL = ["planck_2018_lowl.TT", "planck_2018_lowl.EE"]


def model_info(model: str = "lqc", fixed: dict[str, float] | None = None,
               likelihoods: list[str] | None = None) -> dict[str, Any]:
    """cobaya `info` szótár: rögzített kozmológia (a rácshoz) vagy mintavételezett (MCMC-hez)."""
    params: dict[str, Any] = {k: v for k, v in (fixed or BESTFIT).items()}
    params["logA"] = {"value": params["logA"], "drop": True}
    params["As"] = {"value": "lambda logA: 1e-10*np.exp(logA)"}
    params["n_tot"] = {"prior": {"min": 130.0, "max": 160.0}}
    params["mnu"] = 0.06
    return {
        "theory": {
            "camb": {"external_primordial_pk": True,
                     "extra_args": {"lens_potential_accuracy": 1, "num_massive_neutrinos": 1,
                                    "nnu": 3.046, "theta_H0_range": [20, 100]}},
            "thesis.cobaya_lqc.LQCPrimordialPk": {"model": model},
        },
        "likelihood": {name: None for name in (likelihoods or LIKELIHOODS)},
        "params": params,
        "packages_path": PACKAGES_PATH,
    }


def grid_scan(n_values: list[float], likelihoods: list[str] | None = None) -> dict[str, Any]:
    """Δχ²(N_tot) a hivatalos Planck-likelihoodokkal (a többi paraméter a legjobb illesztésen).
    Ha a spektrum a Gibbs-likelihood tartományán kívül esik (−∞), Δχ² = ∞ (kizárt)."""
    from cobaya.model import get_model

    lcdm = get_model(model_info("lcdm", likelihoods=likelihoods))
    names = list(lcdm.likelihood)
    base = dict(zip(names, (-2 * np.asarray(lcdm.loglikes({"n_tot": 141.0})[0])).tolist(),
                    strict=True))
    lqc = get_model(model_info("lqc", likelihoods=likelihoods))
    rows = []
    for n in n_values:
        chi2 = dict(zip(names, (-2 * np.asarray(lqc.loglikes({"n_tot": float(n)})[0])).tolist(),
                        strict=True))
        by = {k: chi2[k] - base[k] for k in names}
        rows.append({"n_tot": float(n), "dchi2_total": float(sum(by.values())),
                     "dchi2_by_likelihood": by})
    return {"likelihoods": names, "lcdm_chi2": base, "rows": rows}


def run(n_values: list[float] | None = None) -> dict[str, Any]:
    """WP5b: alacsony-ℓ rács (gyors), majd a teljes likelihood-készlet a legjobb ponton."""
    n_values = n_values or [139.0, 139.5, 140.0, 140.25, 140.5, 140.75, 141.0, 141.25,
                            141.5, 141.75, 142.0, 142.5, 143.0, 144.0, 146.0]
    low = grid_scan(n_values, LOW_ELL)
    finite = [r for r in low["rows"] if math.isfinite(r["dchi2_total"])]
    best = min(finite, key=lambda r: r["dchi2_total"])
    ok95 = [r["n_tot"] for r in finite if r["dchi2_total"] <= best["dchi2_total"] + 4]
    full = grid_scan([best["n_tot"], min(ok95)])
    return {"low_ell": low, "best": best, "n_tot_lower_95": min(ok95), "full_check": full,
            "packages_path": PACKAGES_PATH}


def available() -> bool:
    """Telepítve vannak-e a likelihood-adatok (cobaya-install … -p PACKAGES_PATH)."""
    return (Path(PACKAGES_PATH) / "data" / "planck_2018_lowT_native").exists()
