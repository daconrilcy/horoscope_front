# Implementation Plan

## Current Architecture Finding

- `FlaggedContentModel` existe dans `backend/app/infra/db/models/flagged_content.py`.
- Le registre racine `backend/app/infra/db/models/__init__.py` ne l'importe pas.
- `Base.metadata` charge le registre racine depuis `backend/app/infra/db/base.py`.
- Les modeles LLM sont regroupes dans `backend/app/infra/db/models/llm/__init__.py`; ce registre doit rester separe.

## Selected Approach

1. Ajouter `FlaggedContentModel` au registre racine non-LLM et a `__all__`.
2. Charger explicitement le registre LLM depuis `base.py` pour stabiliser `Base.metadata` sans dupliquer ses exports dans le registre racine.
3. Ajouter une garde pytest qui compare:
   - tables SQLite de `backend/horoscope.db`;
   - tables declarees dans les fichiers de modeles;
   - tables chargees dans `Base.metadata`;
   - exceptions exactes du registre de story.
4. Persister les audits avant/apres et le registre d'exceptions.

## Files To Modify

- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/base.py`
- `backend/app/tests/unit/test_db_model_registry_guard.py`
- artefacts et preuves sous `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/`

## Tests

- Ajouter `backend/app/tests/unit/test_db_model_registry_guard.py`.
- Executer `backend/app/tests/integration/test_admin_support_api.py`.

## Rollback Strategy

- Retirer uniquement les imports ajoutes et le test de garde si un blocage valide montre que le chargement metadata global doit rester incomplet.
