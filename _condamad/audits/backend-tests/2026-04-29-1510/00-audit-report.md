# Audit CONDAMAD - backend-tests

## Perimetre

- Domaine audite: tests backend.
- Audit de reprise apres implementation des stories issues de `_condamad/audits/backend-tests/2026-04-28-1600/`.
- Mode: lecture du code applicatif, execution locale, creation d'artefacts d'audit sous `_condamad/audits/backend-tests/2026-04-29-1510/`.
- Date d'execution: 2026-04-29 15:10 Europe/Paris.

## Etat courant

La suite backend compte 431 fichiers de tests statiques sous les racines configurees et 3305 fonctions de tests statiques. La collecte standard depuis `backend` reussit et collecte 3488 tests. L'execution complete reussit avec 3476 tests passes, 12 skips et 7 warnings.

Les corrections principales du precedent audit sont validees:

- `backend/pyproject.toml` collecte maintenant `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration` et `tests/unit`.
- Aucun fichier `test_story_*.py` ne reste dans `backend`.
- Aucun import croise depuis un module executable `test_*.py` n'est trouve par scan repo.
- Le test seed no-op est remplace et une garde anti no-op existe.

## Synthese Des Findings

| Severite | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 1 |
| Info | 0 |

## Findings Actifs

| ID | Severite | Sujet | Statut |
|---|---|---|---|
| F-101 | High | Le harnais DB garde des imports directs `SessionLocal` et une redirection globale de session | actif |
| F-102 | Medium | La topologie reste partagee entre `app/tests` et `tests/*` sans registre canonique explicite | actif |
| F-103 | Medium | La garde anti import croise ne scanne pas `backend/tests` a cause d'un calcul de racine incorrect | actif |
| F-104 | Medium | Les tests docs/scripts/ops restent dans pytest backend sans decision d'ownership | actif |
| F-105 | Low | 7 warnings deprecation `LLMNarrator` persistent | actif |

## Stories Precedentes

| Ancien finding | Etat 2026-04-29 | Preuve |
|---|---|---|
| F-001 default discovery | resolu | `pytest --collect-only -q --ignore=.tmp-pytest` collecte 3488 tests |
| F-004 story-numbered guards | resolu | `rg --files backend -g test_story_*.py` retourne zero hit |
| F-005 cross-test imports | resolu par scan, garde a corriger | scan zero hit; F-103 couvre la faille de garde |
| F-006 seed validation no-op | resolu | `test_backend_noop_tests.py` passe et aucun test no-op collecte n'est detecte |
| F-002 canonical topology | partiel | toutes les racines sont collectees, mais l'ownership reste implicite |
| F-003 DB fixtures | non resolu | 89 fichiers importent encore directement `SessionLocal` |
| F-007 operational scope | non resolu | tests PowerShell/docs/secrets/security toujours dans pytest backend |

## Validation

Toutes les commandes Python ont ete lancees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format --check .
ruff check .
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q app/tests/unit/test_backend_noop_tests.py app/tests/unit/test_backend_story_guard_names.py app/tests/unit/test_backend_test_helper_imports.py
pytest -q
```

Resultats:

- `ruff format --check .`: OK, 1242 fichiers deja formates.
- `ruff check .`: OK.
- `pytest --collect-only -q --ignore=.tmp-pytest`: OK, 3488 tests collectes.
- Guards cibles: OK, 7 passed.
- Suite complete: OK, 3476 passed, 12 skipped, 7 warnings en 599.61s.

## Sequence Recommandee

1. Corriger la garde anti import croise pour scanner `backend/tests` en plus de `backend/app/tests`.
2. Converger le harnais DB: retirer les imports directs `SessionLocal` et remplacer la redirection globale par une fixture explicite.
3. Documenter et garder automatiquement la topologie canonique des racines de tests backend.
4. Decider si les tests docs/scripts/ops restent dans pytest backend ou deviennent une suite qualite/ops dediee.
5. Traiter ou classifier les warnings `LLMNarrator` pour eviter une dette deprecation silencieuse.
