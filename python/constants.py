"""Fizikai állandók — CODATA 2022 (SI). A Rust mag `core/src/constants.rs` tükre."""
from __future__ import annotations

import math

C = 299_792_458.0
H_PLANCK = 6.626_070_15e-34
HBAR = H_PLANCK / (2.0 * math.pi)
K_B = 1.380_649e-23
G = 6.674_30e-11

L_P = math.sqrt(HBAR * G / C**3)
M_PLANCK = math.sqrt(HBAR * C / G)
T_PLANCK = L_P / C
RHO_PLANCK = C**5 / (HBAR * G**2)
M_SUN = 1.988_47e30
