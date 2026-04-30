# Audit CONDAMAD - backend-tests

## Perimetre

- Domaine audite: tests backend.
- Audit de reprise apres mise en oeuvre des stories proposees par `_condamad/audits/backend-tests/2026-04-29-1510/`.
- Archetype: `test-guard-coverage-audit`, avec dimensions obligatoires DRY, No Legacy, mono-domain ownership et dependency direction.
- Mode: read-only sur le code applicatif; creation d'artefacts d'audit sous `_condamad/audits/backend-tests/2026-04-30-1800/`.
- Date d'execution: 2026-04-30 18:00 Europe/Paris.

## Guardrails Consultes

- Source: `_condamad/stories/regression-guardrails.md`.
- Invariants applicables: `RG-010`, `RG-011`, `RG-012`, `RG-013`, `RG-014`, `RG-015`, `RG-016`.
- Decision: aucun nouvel invariant durable n'est ajoute par cet audit; les invariants actifs couvrent deja les corrections livrees.

## Etat Courant

La topologie backend est explicite dans `backend/pyproject.toml` et dans `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`. La collecte standard depuis `backend` reussit avec 3497 tests collectes. L'inventaire statique contient 433 fichiers `test_*.py`.

Les findings actifs du precedent audit sont resolus par preuves executables:

- F-101: les imports directs nominaux de `SessionLocal` / `engine` depuis les tests backend sont absents, l'allowlist DB est vide, et la garde DB passe.
- F-102: les racines pytest sont documentees et comparees a `backend/pyproject.toml` par une garde dediee.
- F-103: la garde anti imports croises scanne explicitement `backend/app/tests` et `backend/tests`.
- F-104: les 23 tests docs/scripts/secrets/security/ops sont classes dans le registre d'ownership et couverts par une garde.
- F-105: les tests de narration nominale ciblent l'adapter canonique; le retour a la classe depreciee `LLMNarrator` est bloque.

## Synthese Des Findings

| Severite | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

## Findings Actifs

Aucun finding actif n'a ete retenu dans le perimetre `backend-tests`.

## Validation

Toutes les commandes Python ont ete lancees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_pytest_collection.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_backend_noop_tests.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/unit/prediction/test_llm_narrator.py
pytest --collect-only -q --ignore=.tmp-pytest
```

Resultats:

- `ruff check .`: OK.
- Guards cibles: OK, 31 passed.
- `pytest --collect-only -q --ignore=.tmp-pytest`: OK, 3497 tests collected.

`ruff format` n'a pas ete lance car l'audit est read-only et le workflow du skill interdit les formatters pendant la collecte de preuves.

## Conclusion

Le domaine `backend-tests` ne presente plus de finding actif issu de l'audit du 2026-04-29. Le risque residuel principal est operationnel: maintenir les guards nouvellement ajoutes dans la validation standard, en particulier `RG-010` a `RG-016`.
