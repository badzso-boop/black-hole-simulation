# Helyi ellenőrző futás (2026-09-30) — nem a hivatalos ítélet-futás

- Célja: a docs/upgrade-plan.md A fázis és a B1a/B3a kódjának végigfuttatása (A10).
- A hivatalos Planck-likelihoodok itt nincsenek telepítve, ezért a WP5b a saját Wishart-csővezetékre
  esik vissza. A hivatalos futás a Ryzenen jön: `python scripts/run_thesis.py`.
- Ellenőrzés: a 2026-09-29-es futáshoz képest minden szám 1e-9-en belül azonos, kivéve a WP6-ot. Az
  szándékosan változott (A1, 2025-ös neutroncsillag-tömegek): 3.2σ → 3.7σ.
