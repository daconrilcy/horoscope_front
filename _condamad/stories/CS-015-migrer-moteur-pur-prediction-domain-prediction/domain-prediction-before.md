# Inventaire avant implementation CS-015

## Contexte

Cet inventaire capture l'etat observe au debut de cette execution Codex. Le code suivi par Git montre deja `backend/app/domain/prediction` comme owner actif et aucun dossier `backend/app/prediction`. Aucun etat pre-migration historique n'a ete reconstruit.

## Constats

- `backend/app/prediction`: absent.
- `backend/app/domain/prediction`: present.
- `backend/app/services/prediction`: importe deja `app.domain.prediction`.
- Imports actifs `app.prediction` sous `backend/app` et `backend/tests`: aucun, hors chaines de guard tests attendues.
- Dependances interdites detectees sous `backend/app/domain/prediction`: aucune au scan cible.

## Commandes d'observation

- `git ls-tree -r --name-only HEAD backend/app/prediction`: zero fichier.
- `git ls-tree -r --name-only HEAD backend/app/domain/prediction`: fichiers domaine presents.
- `rg -n "from app\.prediction|import app\.prediction|app\.prediction" backend/app backend/tests -g "*.py"`: uniquement des chaines de garde dans `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- `rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api|from app\.services" backend/app/domain/prediction -g "*.py"`: zero hit.
