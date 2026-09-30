# Újrapontozás a javított ítélet-szabállyal (2026-09-30)

A Ryzen-futás nyers eredményei (`results.json`) és az eredeti `SCORECARD.md` változatlanok.
Ez a lap ugyanazokat a számokat a javított `thesis/verdict.py`-jal pontozza újra.
A javítás (docs/upgrade-plan.md A4): a terv §5 szerint a Planck-görbület elérése „neutral”, nem „against”.

| Kérdés | Eredeti futás | Újrapontozva | BH-specifikus? |
|---|---|---|---|
| L1b validation gate | passed | **passed** | n/a |
| L1a star's own bounce vs inner horizon | supports | **supports** | yes |
| L1c the spark crosses r_- | open (mixed) | **open (mixed)** | yes |
| L1d quantum vs classical | info | **info** | n/a |
| L1e the asteroid | against | **neutral (quantum-gravity dependent)** | yes (Norbi's feeding claim) |

Újrafuttatás nélkül előállítva: `python -c "from thesis.verdict import inner_horizon_scorecard; ..."` a `results.json`-on.
