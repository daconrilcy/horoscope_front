# Inventaire apres implementation CS-015

## Etat cible

- `backend/app/domain/prediction` reste l'owner canonique du moteur pur.
- `backend/app/prediction` reste absent.
- Les services prediction consomment `app.domain.prediction`.
- Les guards AST bloquent la recreation du namespace legacy et les dependances interdites du domaine.

## Modules domaine observes

Voir la validation `rg --files app/domain/prediction` executee depuis `backend`: le package contient les modules moteur, schemas metier, projection publique deterministe, persisted DTO deja presents dans l'owner domaine, et templates editoriaux.

## Scans attendus

- `rg -n "from app\.prediction" app/services/prediction -g "*.py"`: zero hit.
- `rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api|from app\.services" app/domain/prediction -g "*.py"`: zero hit.
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`: PASS attendu.

## Difference autorisee

Les chemins d'import canoniques sont `app.domain.prediction`. Aucun changement de resultat moteur n'est attendu.
