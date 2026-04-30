# Evidence Log - backend-tests

## E-001 - Inventaire statique

- Commande: `rg --files backend -g test_*.py -g *_test.py -g !backend/.tmp-pytest/** | Measure-Object`
- Resultat: 431 fichiers.
- Comptage AST apres activation venv: 3305 fonctions statiques dont le nom commence par `test_`.

Repartition principale:

| Count | Racine |
|---:|---|
| 211 | `backend/app/tests/unit` |
| 119 | `backend/app/tests/integration` |
| 40 | `backend/tests/llm_orchestration` |
| 25 | `backend/tests/integration` |
| 12 | `backend/tests/unit` |
| 12 | `backend/tests/unit/prediction` |
| 3 | `backend/tests/evaluation` |

## E-002 - Configuration pytest

`backend/pyproject.toml` configure:

- `app/tests`
- `tests/evaluation`
- `tests/integration`
- `tests/llm_orchestration`
- `tests/unit`

Le chemin absent `app/ai_engine/tests` du precedent audit n'est plus configure.

## E-003 - Collecte pytest

Commande:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest --collect-only -q --ignore=.tmp-pytest
```

Resultat: OK, 3488 tests collectes en 2.55s.

## E-004 - Execution complete

Commande:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q
```

Resultat: OK, 3476 passed, 12 skipped, 7 warnings en 599.61s.

Warnings observes: 7 `DeprecationWarning` dans `tests/unit/prediction/test_llm_narrator.py`, indiquant que `LLMNarrator` est deprecie au profit de `AIEngineAdapter.generate_horoscope_narration`.

## E-005 - Lint et format

Commandes:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format --check .
ruff check .
```

Resultats:

- `ruff format --check .`: OK, 1242 fichiers deja formates.
- `ruff check .`: OK.

## E-006 - Story-numbered guards

Commande: `rg --files backend -g test_story_*.py`

Resultat: zero hit.

Guard cible:

```powershell
pytest -q app/tests/unit/test_backend_story_guard_names.py
```

Resultat inclus dans le lot de guards: OK.

## E-007 - Cross-test-module imports

Commande:

```powershell
rg -n "from app\.tests\.integration\.test_|from app\.tests\.unit\.test_|from app\.tests\.regression\.test_|from tests\.integration\.test_" backend/app/tests backend/tests -g test_*.py
```

Resultat: zero hit.

Limite identifiee: `backend/app/tests/unit/test_backend_test_helper_imports.py` calcule `BACKEND_ROOT = Path(__file__).resolve().parents[2]`, ce qui pointe vers `backend/app`. Sa racine `BACKEND_ROOT / "tests"` pointe donc vers `backend/app/tests` au lieu de `backend/tests`; la garde ne couvre pas `backend/tests`.

## E-008 - No-op tests

Commande: `rg -n "assert True|pass$" backend/app/tests backend/tests -g test_*.py`

Resultat: les `pass` restants sont dans des blocs de controle ou exceptions, pas des corps de tests vides. La garde AST `test_backend_noop_tests.py` passe.

## E-009 - Harnais DB

Commandes:

- `rg -l "from app\.infra\.db\.session import .*SessionLocal|from app\.infra\.db\.session import SessionLocal" backend/app/tests backend/tests -g test_*.py | Measure-Object`
- `rg -l "db_session_module\.SessionLocal|monkeypatch\.setattr\([^\r\n]*SessionLocal" backend/app/tests backend/tests -g test_*.py | Measure-Object`

Resultats:

- 89 fichiers importent encore directement `SessionLocal`.
- 17 fichiers utilisent encore `db_session_module.SessionLocal` ou une forme de monkeypatch cible.

`backend/app/tests/conftest.py` redirige globalement `app.infra.db.session.engine`, `SessionLocal` et `_local_schema_ready` pour tout le process pytest.

## E-010 - Tests operationnels dans pytest backend

Exemples encore collectes:

- `backend/app/tests/integration/test_backup_restore_scripts.py`
- `backend/app/tests/integration/test_pipeline_scripts.py`
- `backend/app/tests/integration/test_secrets_scan_script.py`
- `backend/app/tests/integration/test_security_verification_script.py`
- tests de gouvernance docs LLM sous `backend/tests/integration`

Ces tests passent, mais leur ownership reste une decision produit/architecture.
