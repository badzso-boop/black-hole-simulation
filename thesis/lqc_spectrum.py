"""WP5b: a hibrid LQC primordiális spektrum (Guillén, Langer, Mena Marugán et al. 2026,
arXiv:2605.14657) — a cikk parametrizációjának fizikája, numerikusan.

Háttér (Planck-egység, a_B = 1): kinetikus visszapattanás, a(t) = (1 + 24πρ_c t²)^{1/6}.
A visszapattanási szakasz vége t0 = 0.4 (hibrid megközelítés, a cikk szerint), ott
    a0 = a(t0),  k0 = a0 H0 = √(8πρ_c/3)/a0²   (kinetikus GR-illesztés, a cikk Sec. III B),
    η0 = ∫₀^{t0} dt/a   (a cikk: ≈ 0.35).
Módusegyenlet: µ'' + (k² + s(η)) µ = 0. A visszapattanáskor Pöschl–Teller-tömeg
    s_PT = U0/cosh²(αη),  U0 = 8πρ_c/3,  α = arcosh(a0²)/η0   (a cikk Eq. 2.10),
a NO-AHD vákuum erre a tömegre éppen az η → −∞ síkhullám, µ → e^{−ikη}/√(2k) (Eq. A1,
M_k = 1/√(2k), N_k = 0). Ezt numerikusan integráljuk η0-ig, majd illesztjük a kinetikus
szakasz egzakt megoldásához (Eq. A4):
    µ = C √(πy/4) H0⁽¹⁾(ky) + D √(πy/4) H0⁽²⁾(ky),   y = η − η0 + 1/(2k0).
Az inflációban k ≫ k_i esetén mindkét bázis síkhullám, így |A_k| = |D|, |B_k| = |C| (a cikk
Eq. 3.7–3.8 aszimptotikája), és a spektrum (Eq. 3.5, az oszcillációt eltávolító
Bogoliubov-transzformáció után):
    P_R(k) = (|A_k| − |B_k|)² · P_R^ΛCDM(k)
Ma mért hullámszám: k_Planck = k_Mpc · e^{N_tot} · ℓ_P/Mpc.
A dressed-metric változat nincs implementálva (korlát).
"""
from __future__ import annotations

import functools
import math

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.special import hankel1, hankel2

from thesis.units import L_P, MPC, RHO_C

T0_HYBRID = 0.4


def scale_factor(t: float) -> float:
    return float((1 + 24 * math.pi * RHO_C * t * t) ** (1 / 6))


@functools.lru_cache(maxsize=1)
def background() -> dict[str, float]:
    a0 = scale_factor(T0_HYBRID)
    eta0 = quad(lambda t: 1 / scale_factor(t), 0, T0_HYBRID)[0]
    k0 = math.sqrt(8 * math.pi * RHO_C / 3) / a0**2
    alpha = math.acosh(a0**2) / eta0
    return {"a0": a0, "eta0": eta0, "k0": k0, "alpha": alpha, "U0": 8 * math.pi * RHO_C / 3}


def _integrate_pt(k: float, eta_end: float) -> tuple[complex, complex]:
    """µ(η_end), µ'(η_end) a PT-tömeggel, µ → e^{−ikη}/√(2k) a távoli múltban."""
    bg = background()
    al, u0 = bg["alpha"], bg["U0"]
    eta_start = -40.0 / al  # U0/cosh² ≈ 4U0 e^{−80}: elhanyagolható
    mu0 = np.exp(-1j * k * eta_start) / math.sqrt(2 * k)
    dmu0 = -1j * k * mu0

    def rhs(eta: float, y: np.ndarray) -> list[float]:
        w2 = k * k + u0 / math.cosh(al * eta) ** 2
        return [y[2], y[3], -w2 * y[0], -w2 * y[1]]

    sol = solve_ivp(rhs, (eta_start, eta_end), [mu0.real, mu0.imag, dmu0.real, dmu0.imag],
                    method="DOP853", rtol=1e-10, atol=1e-12)
    y = sol.y[:, -1]
    return complex(y[0], y[1]), complex(y[2], y[3])


def bogoliubov(k: float) -> tuple[float, float]:
    """(|A_k|, |B_k|) a kinetikus szakasz Hankel-bázisában, η0-ban illesztve."""
    bg = background()
    mu, dmu = _integrate_pt(k, bg["eta0"])
    y0 = 1 / (2 * bg["k0"])
    z = k * y0
    pref = math.sqrt(math.pi / 4)

    def basis(h: complex, dh: complex) -> tuple[complex, complex]:
        u = pref * math.sqrt(y0) * h
        du = pref * (h / (2 * math.sqrt(y0)) + math.sqrt(y0) * k * dh)
        return u, du

    u1, du1 = basis(hankel1(0, z), -hankel1(1, z))
    u2, du2 = basis(hankel2(0, z), -hankel2(1, z))
    det = u1 * du2 - u2 * du1
    c = (mu * du2 - u2 * dmu) / det
    d = (u1 * dmu - mu * du1) / det
    return abs(d), abs(c)  # |A_k| = |D| (pozitív frekvencia), |B_k| = |C|


def suppression(k: float) -> float:
    a, b = bogoliubov(k)
    return (a - b) ** 2


@functools.lru_cache(maxsize=1)
def suppression_table() -> tuple[np.ndarray, np.ndarray]:
    """F(k) táblázat log k-ban, k ∈ [1e-4, 1e2] (Planck-egység, a_B = 1); k > 100-ra F = 1
    (k = 100-nál már 1 − F < 1e-6, lásd a teszteket)."""
    ks = np.geomspace(1e-4, 1e2, 241)
    return ks, np.array([suppression(float(k)) for k in ks])


def suppression_today(k_mpc: np.ndarray, n_tot: float) -> np.ndarray:
    ks, fs = suppression_table()
    k_pl = np.asarray(k_mpc) * math.exp(n_tot) * L_P / MPC
    lk = np.log(np.clip(k_pl, ks[0], ks[-1]))
    out = np.interp(lk, np.log(ks), fs)
    return np.where(k_pl > ks[-1], 1.0, out)


def pt_exact_beta2(k: float) -> float:
    """Egzakt Pöschl–Teller-szórás (−∞ → +∞): |β|² = cos²(π/2·√(1+4U0/α²))/sinh²(πk/α).
    Csak a numerikus integrátor ellenőrzésére."""
    bg = background()
    al, u0 = bg["alpha"], bg["U0"]
    return math.cos(math.pi / 2 * math.sqrt(1 + 4 * u0 / al**2)) ** 2 / math.sinh(math.pi * k / al) ** 2


def pt_numeric_beta2(k: float) -> float:
    bg = background()
    eta_end = 40.0 / bg["alpha"]
    mu, dmu = _integrate_pt(k, eta_end)
    # µ = α e^{−ikη}/√(2k) + β e^{+ikη}/√(2k)
    s = math.sqrt(2 * k)
    beta = (dmu + 1j * k * mu) * s / (2j * k) * np.exp(-1j * k * eta_end)
    return float(abs(beta) ** 2)
