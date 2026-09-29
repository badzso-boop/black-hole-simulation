"""WP5: nyom a CMB-n — elnyomja-e a visszapattanás a legnagyobb skálák teljesítményét?

Primordiális spektrum (Planck 2018 X, Eq. 19 exponenciális levágás):
    P(k) = A_s (k/k*)^{n_s−1} [1 − exp(−(k/k_c)^λ)],   λ = 3.35 (Planck 2013 XXII)
CAMB: `set_initial_power_table` → C_ℓ^TT; a többi ΛCDM-paraméter a Planck 2018
legjobb illesztésén rögzített (a levágás csak ℓ ≲ 30-at érint).

Alacsony-ℓ likelihood (ℓ = 2…29): a Planck teljes-égbolt D_ℓ becslésein
    −2 ln L = Σ f_sky (2ℓ+1) [Ĉ/C − ln(Ĉ/C) − 1]     (Wishart / skálázott χ², f_sky = 0.86)
Keresztellenőrzés: aszimmetrikus Gauss (a fájl ±ΔD_ℓ hibái az eltérés oldala szerint).

S_{1/2} = ∫_{−1}^{1/2} C(θ)² d cosθ,  C(θ) = Σ_ℓ (2ℓ+1)/(4π) C_ℓ P_ℓ(cosθ),  ℓ = 2…100.

k_c → N_tot: a levágás a visszapattanás skálája, k_LQC = √(8πρ_c) = 3.21 ℓ_P⁻¹ (fizikai,
a visszapattanáskor; Ashtekar et al. 2020). Ma (a0 = 1) k_c = k_LQC e^{−N_tot}, tehát
    N_tot = ln(k_LQC / (k_c ℓ_P))   (k_c komoving, ℓ_P⁻¹-ben) — ±1 e-redő a sablon miatt.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial import legendre

from thesis.units import L_P, MPC, RHO_C

DATA = Path(__file__).resolve().parent.parent / "data" / "planck"
TT_FULL = DATA / "COM_PowerSpect_CMB-TT-full_R3.01.txt"
BESTFIT = DATA / "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"

# Planck 2018 VI, TT,TE,EE+lowE+lensing legjobb illesztés (a minimum-theory fájlhoz)
PLANCK_BF = {"H0": 67.32, "ombh2": 0.022383, "omch2": 0.12011, "tau": 0.0543,
             "As": math.exp(3.0448) * 1e-10, "ns": 0.96605, "mnu": 0.06}
K_PIVOT = 0.05
LAMBDA_CUT = 3.35
F_SKY = 0.86
LMAX_LOW = 29
K_LQC = math.sqrt(8 * math.pi * RHO_C)  # 3.21 ℓ_P⁻¹


def load_tt_full() -> np.ndarray:
    return np.loadtxt(TT_FULL)  # ℓ, D_ℓ, −ΔD, +ΔD


def load_bestfit_tt() -> np.ndarray:
    d = np.loadtxt(BESTFIT)
    return d[:, :2]  # ℓ, D_ℓ^TT


def _params(lmax: int, lensing: bool) -> Any:
    import camb

    p = camb.CAMBparams()
    p.set_cosmology(H0=PLANCK_BF["H0"], ombh2=PLANCK_BF["ombh2"], omch2=PLANCK_BF["omch2"],
                    mnu=PLANCK_BF["mnu"], omk=0.0, tau=PLANCK_BF["tau"])
    p.set_for_lmax(lmax, lens_potential_accuracy=1 if lensing else 0)
    p.DoLensing = lensing
    p.WantTensors = False
    return p


def power_cutoff(k: np.ndarray, k_c: float | None) -> np.ndarray:
    pk = PLANCK_BF["As"] * (k / K_PIVOT) ** (PLANCK_BF["ns"] - 1)
    if k_c is not None:
        pk = pk * -np.expm1(-((k / k_c) ** LAMBDA_CUT))
    return pk


def dl_tt(k_c: float | None, lmax: int = 200, lensing: bool = False,
          n_tot_lqc: float | None = None) -> np.ndarray:
    """D_ℓ^TT μK²-ben, ℓ = 0…lmax (k_c = None: tiszta hatványtörvény)."""
    import camb

    p = _params(lmax, lensing)
    k = np.logspace(-7, 1, 3000)
    pk = power_cutoff(k, k_c)
    if n_tot_lqc is not None:  # WP5b: a hibrid LQC-spektrum (thesis.lqc_spectrum)
        from thesis.lqc_spectrum import suppression_today

        pk = pk * suppression_today(k, n_tot_lqc)
    p.set_initial_power_table(k, pk, effective_ns_for_nonlinear=PLANCK_BF["ns"])
    res = camb.get_results(p)
    key = "total" if lensing else "unlensed_scalar"
    cl = res.get_cmb_power_spectra(p, CMB_unit="muK", lmax=lmax)[key]
    return np.asarray(cl[:, 0])


def validate_baseline() -> dict[str, Any]:
    """CAMB (levágás nélkül) vs a Planck minimum-theory fájl, ℓ = 2…2500."""
    import camb

    p = _params(2600, lensing=True)
    p.InitPower.set_params(As=PLANCK_BF["As"], ns=PLANCK_BF["ns"])
    res = camb.get_results(p)
    ours = res.get_cmb_power_spectra(p, CMB_unit="muK", lmax=2500)["total"][:, 0]
    ref = load_bestfit_tt()
    ells = ref[:, 0].astype(int)
    mask = (ells >= 2) & (ells <= 2500)
    rel = np.abs(ours[ells[mask]] / ref[mask, 1] - 1)
    # a táblázatos spektrum (set_initial_power_table) is ugyanazt adja-e
    tab = dl_tt(None, lmax=2500, lensing=True)
    rel_tab = np.abs(tab[2:2501] / ours[2:2501] - 1)
    return {"max_rel_dev": float(rel.max()), "median_rel_dev": float(np.median(rel)),
            "ell_of_max": int(ells[mask][rel.argmax()]), "D2_ours": float(ours[2]),
            "D2_ref": float(ref[ells == 2, 1][0]), "table_vs_param_max_rel": float(rel_tab.max())}


def _cl(dl: np.ndarray, ells: np.ndarray) -> np.ndarray:
    return np.asarray(dl * 2 * np.pi / (ells * (ells + 1)), dtype=float)


def chi2_low(dl_model: np.ndarray, data: np.ndarray) -> dict[str, float]:
    sel = (data[:, 0] >= 2) & (data[:, 0] <= LMAX_LOW)
    ells = data[sel, 0].astype(int)
    d_hat = data[sel, 1]
    d_mod = dl_model[ells]
    x = d_hat / d_mod
    wishart = float(np.sum(F_SKY * (2 * ells + 1) * (x - np.log(x) - 1)))
    err = np.where(d_hat < d_mod, data[sel, 3], data[sel, 2])  # a modell felé eső hiba
    gauss = float(np.sum(((d_hat - d_mod) / err) ** 2))
    return {"wishart": wishart, "gauss_asym": gauss}


def s_half(cl: np.ndarray, lmin: int = 2, lmax: int = 100) -> float:
    """S_{1/2} μK⁴-ben C_ℓ-ből (ℓ indexelés 0-tól)."""
    coef = np.zeros(lmax + 1)
    ells = np.arange(lmin, lmax + 1)
    coef[lmin:] = (2 * ells + 1) / (4 * np.pi) * cl[lmin:lmax + 1]
    x = np.linspace(-1, 0.5, 30001)
    c = legendre.legval(x, coef)
    return float(np.trapezoid(c * c, x))


def n_tot_from_kc(k_c_mpc: float) -> float:
    return math.log(K_LQC / (k_c_mpc / MPC * L_P))


def run(n_grid: int = 61) -> dict[str, Any]:
    data = load_tt_full()
    lmax_s = 100
    base = dl_tt(None, lmax=lmax_s)
    ells = np.arange(lmax_s + 1)
    base_cl = np.zeros_like(base)
    base_cl[2:] = _cl(base[2:], ells[2:])
    chi_base = chi2_low(base, data)
    # adat C_ℓ (teljes égbolt) S_1/2-höz
    data_cl = np.zeros(lmax_s + 1)
    sel = data[:, 0] <= lmax_s
    data_cl[data[sel, 0].astype(int)] = _cl(data[sel, 1], data[sel, 0])
    rows = []
    for k_c in np.geomspace(1e-5, 3e-3, n_grid):
        dl = dl_tt(float(k_c), lmax=lmax_s)
        cl = np.zeros_like(dl)
        cl[2:] = _cl(dl[2:], ells[2:])
        chi = chi2_low(dl, data)
        rows.append({"k_c_mpc": float(k_c), "n_tot": n_tot_from_kc(float(k_c)),
                     "dchi2_wishart": chi["wishart"] - chi_base["wishart"],
                     "dchi2_gauss": chi["gauss_asym"] - chi_base["gauss_asym"],
                     "S_half": s_half(cl), "D2": float(dl[2]), "D3": float(dl[3])})
    best = min(rows, key=lambda r: r["dchi2_wishart"])
    # az 1σ-intervallum (Δχ² ≤ min + 1) N_tot-ban, és a 95%-os alsó korlát (Δχ² ≤ min + 4):
    # túl nagy k_c (kis N_tot) a megfigyelt ℓ ≲ 30 teljesítményt is elnyomná
    ok = [r for r in rows if r["dchi2_wishart"] <= best["dchi2_wishart"] + 1]
    ok95 = [r for r in rows if r["dchi2_wishart"] <= best["dchi2_wishart"] + 4]
    best_dl = dl_tt(best["k_c_mpc"], lmax=60)
    return {
        "baseline_chi2": chi_base, "rows": rows, "best": best,
        "n_tot_1sigma": [min(r["n_tot"] for r in ok), max(r["n_tot"] for r in ok)],
        "n_tot_lower_95": min(r["n_tot"] for r in ok95),
        "k_c_upper_95_mpc": max(r["k_c_mpc"] for r in ok95),
        "S_half_lcdm": s_half(base_cl), "S_half_data_fullsky": s_half(data_cl),
        "S_half_observed_masked": 1209.2,
        "curves": {"ell": list(range(2, 61)), "lcdm": base[2:61].tolist(),
                   "best_cutoff": best_dl[2:61].tolist(),
                   "data": data[data[:, 0] <= 60].tolist()},
    }


def run_lqc_own(n_values: list[float]) -> dict[str, Any]:
    """WP5b keresztellenőrzés a saját csővezetékkel: a hibrid LQC-spektrum Wishart-Δχ²-e és
    S_1/2-je N_tot függvényében (ugyanaz, mint a WP5-sablonnál)."""
    data = load_tt_full()
    lmax_s = 100
    ells = np.arange(lmax_s + 1)
    base = dl_tt(None, lmax=lmax_s)
    chi_base = chi2_low(base, data)
    rows = []
    for n in n_values:
        dl = dl_tt(None, lmax=lmax_s, n_tot_lqc=n)
        cl = np.zeros_like(dl)
        cl[2:] = _cl(dl[2:], ells[2:])
        chi = chi2_low(dl, data)
        rows.append({"n_tot": n, "dchi2_wishart": chi["wishart"] - chi_base["wishart"],
                     "S_half": s_half(cl), "D2": float(dl[2])})
    best = min(rows, key=lambda r: r["dchi2_wishart"])
    return {"rows": rows, "best": best,
            "curve_best": dl_tt(None, lmax=60, n_tot_lqc=best["n_tot"])[2:61].tolist()}
