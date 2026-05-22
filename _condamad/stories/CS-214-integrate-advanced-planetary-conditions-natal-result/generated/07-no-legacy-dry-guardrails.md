# CS-214 No Legacy / DRY Guardrails

## Contraintes appliquees

- Un seul owner d'orchestration: `planetary_conditions/advanced_planetary_conditions_runtime.py`.
- Un seul owner des signaux CS-214: `planetary_conditions/signal_factory.py`.
- Reutilisation des calculateurs CS-209 a CS-213, sans duplication des
  algorithmes.
- Aucun alias, shim, wrapper legacy ou second chemin public concurrent.
- Aucun scoring, interpretation, API, DB, frontend ou JSON builder dans les
  nouveaux modules.

## Evidence

- Scans interdits dans les nouveaux modules: zero hit.
- Diff adjacent: vide.
- `natal_calculation.py`: uniquement mapping positions/vitesses, appel de
  l'orchestrateur et injection du resultat.
