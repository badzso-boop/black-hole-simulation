# Kampány-eredmények — 2026-09-28

Automatikusan generálva: `python scripts/analyze_campaign.py runs/2026-09-28`. Az értelmezés: [ANALYSIS.md](ANALYSIS.md).

## Futtatás

```
dátum:     2026-09-28T19:42:47+00:00
os:        Debian GNU/Linux 13 (trixie) (6.12.86+deb13-amd64)
cpu:       Intel(R) Core(TM) i5-2500S CPU @ 2.70GHz
magok:     4
memória:   7,6Gi
python:    Python 3.13.5
rustc:     rustc 1.95.0 (59807616e 2026-04-14)
commit:    0723b94 (Dokumentáció és telepítés: Kerr, katalógus, lépésenkénti telepítési útmutató, mért hardver)
```

- 71 futás / 71 sikeres, 1 párhuzamosan, összesen 239 s
- futásonként: medián 1.93 s, max 12.28 s
- csúcs-RAM: {'sgr-a': 54.0, 'm87_norbi': 54.1, 'spin_pbh_300': 68.3} MB
- energiamérleg legnagyobb relatív hibája: 6.9e-14

## Ellenőrzések az irodalommal

| Ellenőrzés | Szimuláció | Irodalom / elvárt | Rendben |
|---|---|---|---|
| Ma elpárolgó PBH élettartama (5.1e11 kg) | 11.13 Gyr | 13.8 Gyr (Carr et al. 2010) | ✅ |
| EHT-gyűrű eltérés δ (sgr-a) | -0.082 | -0.08 ± 0.09 (EHT) | ✅ |
| EHT-gyűrű eltérés δ (m87) | -0.000 | +0.00 ± 0.09 (EHT) | ✅ |
| Forgó/nem forgó élettartam-faktor (γ+graviton) | 2.73× | 2.0–2.7× (Page 1976b) | ✅ |
| Bardeen-felpörgetés (korong, a*=0-ból) | a* = 0.9980 @ M/M0 = 7.703 | a* = 0.9980 (Bardeen 1970) | ✅ |
| Eddington-korlátos növekedés 100 Myr | M/M0 = 7.3730 | e^(t/t_S) = 7.3730 | ✅ |
| Konvergencia (25–1000 lépés), élettartam szórása | 8.2e-14 | < 1e-6 | ✅ |

## Tömeg-scan (mai CMB, 2.7255 K)

| M (kg) | T_H (K) | sors | élettartam / horizont (Gyr) | vákuumban (Gyr) | dM/dt kezdetben (kg/s) | ΔM (kg) | horizont→belső vég τ (s) |
|---|---|---|---|---|---|---|---|
| 4.35e-08 | 2.82e+30 | elpárolog | 9.76e-58 | 9.76e-58 | -4.37e+32 | -2.54e-08 | 1.2e-43 |
| 1e-06 | 1.23e+29 | elpárolog | 1.28e-53 | 1.28e-53 | -8.28e+29 | -9.82e-07 | 3.28e-42 |
| 1 | 1.23e+23 | elpárolog | 1.28e-35 | 1.28e-35 | -8.28e+17 | -1 | 3.3e-36 |
| 1e+03 | 1.23e+20 | elpárolog | 1.28e-26 | 1.28e-26 | -8.28e+11 | -1e+03 | 3.3e-33 |
| 1e+06 | 1.23e+17 | elpárolog | 1.28e-17 | 1.28e-17 | -8.28e+05 | -1e+06 | 3.3e-30 |
| 1e+09 | 1.23e+14 | elpárolog | 1.5e-08 | 1.5e-08 | -0.691 | -1e+09 | 3.3e-27 |
| 1e+11 | 1.23e+12 | elpárolog | 0.0316 | 0.0316 | -2.9e-05 | -1e+11 | 3.3e-25 |
| 5.1e+11 | 2.41e+11 | elpárolog | 11.1 | 11.1 | -4.07e-07 | -5.1e+11 | 1.68e-24 |
| 1e+12 | 1.23e+11 | elpárolog | 110 | 110 | -8.83e-08 | -1e+12 | 3.3e-24 |
| 1e+15 | 1.23e+08 | elpárolog | 1.94e+11 | 1.94e+11 | -5.43e-14 | -1e+15 | 3.3e-21 |
| 1e+18 | 1.23e+05 | elpárolog | 1.95e+20 | 1.95e+20 | -5.42e-20 | -1e+18 | 3.3e-18 |
| 1e+20 | 1.23e+03 | elpárolog | 2e+26 | 2e+26 | -5.24e-24 | -1e+20 | 3.3e-16 |
| 1e+22 | 12.3 | elpárolog | 3.89e+32 | — | -2.55e-28 | -1e+22 | 3.3e-14 |
| 5e+22 | 2.45 | elpárolog | 7.28e+34 | — | -4.25e-30 | -5e+22 | 1.65e-13 |
| 7e+22 | 1.75 | nő | 13.8 | — | 1.18e-29 | 5.13e-12 | 2.31e-13 |
| 1e+23 | 1.23 | nő | 13.8 | — | 4.47e-29 | 1.95e-11 | 3.3e-13 |
| 1e+25 | 0.0123 | nő | 13.8 | — | 6.51e-25 | 2.83e-07 | 3.3e-11 |
| 1.99e+30 | 6.17e-08 | nő | 13.8 | — | 2.58e-14 | 1.12e+04 | 6.57e-06 |

CMB-egyensúlyi tömeg (instabil): **M_eq = 5.562e+22 kg**

## Spin-scan (M = 1e12 kg, mai CMB — ennél a tömegnél elhanyagolható)

| modell | a*₀ | T_H (K) | élettartam (Gyr) | τ/τ(a*=0) |
|---|---|---|---|---|
| MacGibbon | 0 | 1.23e+11 | 110.4 | 1.000 |
| MacGibbon | 0.1 | 1.22e+11 | 109.5 | 0.992 |
| MacGibbon | 0.3 | 1.2e+11 | 104.9 | 0.950 |
| MacGibbon | 0.5 | 1.14e+11 | 95.5 | 0.865 |
| MacGibbon | 0.7 | 1.02e+11 | 80.98 | 0.734 |
| MacGibbon | 0.9 | 7.45e+10 | 59.87 | 0.542 |
| MacGibbon | 0.99 | 3.03e+10 | 45.2 | 0.410 |
| MacGibbon | 0.999 | 1.05e+10 | 42.67 | 0.387 |
| PageGammaGraviton | 0 | 1.23e+11 | 1474 | 1.000 |
| PageGammaGraviton | 0.1 | 1.22e+11 | 1453 | 0.986 |
| PageGammaGraviton | 0.3 | 1.2e+11 | 1363 | 0.925 |
| PageGammaGraviton | 0.5 | 1.14e+11 | 1205 | 0.818 |
| PageGammaGraviton | 0.7 | 1.02e+11 | 1001 | 0.679 |
| PageGammaGraviton | 0.9 | 7.45e+10 | 741.1 | 0.503 |
| PageGammaGraviton | 0.99 | 3.03e+10 | 569.5 | 0.386 |
| PageGammaGraviton | 0.999 | 1.05e+10 | 540 | 0.366 |

## Emissziós modellek (M = 5.1e11 kg)

| modell | élettartam (Gyr) | spektrális nem-termalitás |
|---|---|---|
| MacGibbon | 11.13 | 0.267 |
| PageGammaGraviton | 195.5 | 0.267 |
| PhotonBlackbody | 353.6 | 0.267 |

## Környezet-szcenáriók

| szcenárió | M0 (kg) | elpárolgott | idő (Gyr) | végtömeg (kg) | ΔM (kg) | a* vég | mérleg-hiba |
|---|---|---|---|---|---|---|---|
| pbh_asteroid_infall | 1e+12 | igen | 968.1 | 1.809e-08 | -1e+12 | 0.0000 | 1.5e-14 |
| pbh_two_infalls | 1e+12 | igen | 5064 | 1.809e-08 | -1e+12 | 0.0000 | 2.8e-14 |
| stellar_bondi_eddington_100myr | 1.99e+31 | nem | 0.1 | 1.466e+32 | 1.27e+32 | 0.0000 | 0.0e+00 |
| stellar_disk_spinup_from_0 | 1.99e+31 | nem | 6.021e-07 | 1.532e+32 | 1.33e+32 | 0.9980 | 1.1e-15 |
| sun_in_vacuum_10gyr | 1.99e+30 | nem | 10 | 1.988e+30 | -1.82e-27 | 0.0000 | 0.0e+00 |

## Valódi fekete lyukak

| objektum | M (M_☉) | a* | T_H (K) | horizont (Gyr) | ΔM (kg) | ΔM/M | a* vég | árnyék (μas) | várt gyűrű (μas) | mért gyűrű (μas) | δ | L/L_Edd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cyg-x1 | 21.2 | 0.998 | 3.46e-10 | 0.005 | 2.03e+28 | 4.80e-04 | 0.9980 | 0.00098 | 0.00104 | — | — | 2.05e-02 |
| gw150914 | 63.1 | 0.69 | 8.21e-10 | 13.79 | 4.46e+07 | 3.56e-25 | 0.6900 | 1.47e-08 | 1.56e-08 | — | — | 0.00e+00 |
| gw250114 | 62.7 | 0.68 | 8.33e-10 | 13.79 | 4.41e+07 | 3.53e-25 | 0.6800 | 1.46e-08 | 1.55e-08 | — | — | 0.00e+00 |
| m87 | 6.5e+09 | 0.9 | 5.76e-18 | 13.79 | 2.47e+37 | 1.91e-03 | 0.8966 | 39.7 | 42 | 42 | -0.000 | 6.93e-06 |
| pbh-today | 2.565e-19 | 0 | 2.41e+11 | 11.13 | -5.1e+11 | -1.00e+00 | 0.0000 | — | — | — | — | 0.00e+00 |
| sgr-a | 4.3e+06 | 0.9 | 8.71e-15 | 13.79 | 1.92e+32 | 2.24e-05 | 0.9000 | 53.3 | 56.4 | 51.8 | -0.082 | 1.47e-09 |

## Norbi vs. Standard

| objektum | külső spektrum azonos | kauzális csatorna | bébiuniverzum e-redők | H_max (1/s) | I(Ref:R) Standard (bit) | I(Ref:R) Norbi (bit) | I(Ref:R) unitér ref. (bit) |
|---|---|---|---|---|---|---|---|
| cyg-x1 | igen | nem | 63.5 | 1.71e+43 | 0 | 0 | 2 |
| gw150914 | igen | nem | 64.2 | 1.7e+43 | 0 | 0 | 2 |
| gw250114 | igen | nem | 64.2 | 1.7e+43 | 0 | 0 | 2 |
| m87 | igen | nem | 76.5 | 1.61e+43 | 0 | 0 | 2 |
| pbh-today | igen | nem | 32.9 | 1.69e+43 | 0 | 0 | 2 |
| sgr-a | igen | nem | 71.6 | 1.66e+43 | 0 | 0 | 2 |

## Konvergencia a lépésszámban (M = 1e12 kg)

| mintapont | élettartam (s) | mérleg-hiba | futási idő (s) |
|---|---|---|---|
| 25 | 3.48316545328e+18 | 1.7e-14 | 1.18 |
| 50 | 3.48316545328e+18 | 1.4e-14 | 1.47 |
| 100 | 3.48316545328e+18 | 5.1e-15 | 2.09 |
| 400 | 3.48316545328e+18 | 1.6e-14 | 5.45 |
| 1000 | 3.48316545328e+18 | 3.1e-14 | 12.28 |
