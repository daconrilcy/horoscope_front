# Story replace-direct-sessionlocal-test-imports: Replace direct SessionLocal test imports with an explicit DB fixture

Status: ready-for-dev

## 1. Objective

Converger le harnais DB des tests backend vers des helpers et fixtures explicites.
Les tests ne doivent plus importer directement `SessionLocal` ou `engine`.
La redirection globale de `backend/app/tests/conftest.py` doit etre remplacee.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Reason for change: F-101 signale que le harnais DB garde des imports directs `SessionLocal` et une redirection globale de session.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend tests DB harness
- In scope:
  - Inventorier les imports directs DB dans `backend/app/tests` et `backend/tests`.
  - Migrer les consommateurs vers `backend/app/tests/helpers/db_session.py` ou `backend/tests/integration/app_db.py`.
  - Remplacer la mutation globale de `db_session_module.SessionLocal` dans `backend/app/tests/conftest.py`.
  - Garder l'alignement SQLite Alembic via `ensure_configured_sqlite_file_matches_alembic_head`.
- Out of scope:
  - Modifier les modeles SQLAlchemy applicatifs.
  - Changer les migrations Alembic hors besoin prouve par un test existant.
  - Reorganiser la topologie generale des tests.
- Explicit non-goals:
  - Ne pas ajouter de dossier racine sous `backend/`.
  - Ne pas creer de facade de compatibilite pour `SessionLocal`.
  - Ne pas affaiblir `RG-011`, qui protege le harnais DB canonique.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la migration touche plusieurs groupes de tests DB et doit avancer par lots bornes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les assertions metier des tests migres doivent rester equivalentes.
  - La base `horoscope.db` ne doit pas recevoir de `create_all` ORM.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un test depend intentionnellement de la session de production ou d'un fichier SQLite non couvert par l'alignement Alembic.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le comportement DB doit etre prouve par une session de test et par le schema SQLite migre. |
| Baseline Snapshot | yes | L'inventaire des imports directs DB doit etre capture avant et apres migration. |
| Ownership Routing | yes | Les responsabilites DB de tests doivent etre routees vers les helpers canoniques. |
| Allowlist Exception | yes | Les exceptions temporaires existantes doivent rester exactes et auditees. |
| Contract Shape | no | Aucun contrat API, DTO, OpenAPI ou type frontend n'est modifie. |
| Batch Migration | yes | Les 89 fichiers signales par l'audit doivent etre traites par lots. |
| Reintroduction Guard | yes | Une garde doit refuser tout nouvel import direct `SessionLocal` ou `engine`. |
| Persistent Evidence | yes | L'inventaire, la migration par lot et les exceptions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Tests DB executant les sessions canoniques et la verification `ensure_configured_sqlite_file_matches_alembic_head`.
- Secondary evidence:
  - Scan AST des imports `app.infra.db.session` dans `backend/app/tests` et `backend/tests`.
- Static scans alone are not sufficient for this story because:
  - la migration doit prouver que les fichiers SQLite pertinents sont migres avant usage.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-imports-before.md`
- Comparison after implementation:
  - `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-imports-after.md`
- Expected invariant:
  - Aucun nouveau test ne consomme directement `SessionLocal` ou `engine` depuis `app.infra.db.session`.
- Allowed differences:
  - Baisse des entrees allowlistees jusqu'a zero ou vers une liste exacte avec condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| App test DB session | `backend/app/tests/helpers/db_session.py` | Import direct depuis `app.infra.db.session` |
| Integration DB session | `backend/tests/integration/app_db.py` | Import statique de `SessionLocal` |
| SQLite schema alignment | `backend/tests/conftest.py` and bootstrap helper | `Base.metadata.create_all` sur `horoscope.db` |
| DB harness guard | `backend/app/tests/unit/test_backend_db_test_harness.py` | Revue manuelle seule |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` | `SessionLocal`, `engine` | Dette RG-011. | Shrinks until zero direct imports remain. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | `tests/integration` | `tests/integration/app_db.py` | Integration DB | `pytest -q tests/integration/test_backend_sqlite_alignment.py` | Import scan | Production DB needed. |
| B2 | `app/tests/integration` | `app/tests/helpers/db_session.py` | App API | `pytest -q app/tests/integration/test_reference_data_api.py` | DB guard | Isolation breaks. |
| B3 | `app/tests/unit` | `app/tests/helpers/db_session.py` | Unit DB | `pytest -q app/tests/unit/test_reference_data_service.py` | Import scan | Engine identity needed. |
| B4 | `app/tests/conftest.py` patch | Explicit fixture injection | App harness | `pytest --collect-only -q --ignore=.tmp-pytest` | No global assignment | Legacy imports remain. |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Import baseline | `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-imports-before.md` | Capturer les imports directs DB actuels. |
| Batch mapping | `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-batches.md` | Tracer chaque lot migre et ses preuves. |
| Import after | `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-imports-after.md` | Prouver le zero-hit ou les exceptions restantes. |
| Harness decision | `_condamad/stories/replace-direct-sessionlocal-test-imports/global-db-redirection-decision.md` | Documenter la suppression de la redirection globale. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- AST imports in backend test files
- assignments to `db_session_module.SessionLocal`
- classified SQLite factories

Required forbidden examples:

- `from app.infra.db.session import SessionLocal`
- `from app.infra.db.session import engine`
- `db_session_module.SessionLocal =`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_db_test_harness.py` checks the forbidden DB session surfaces.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - F-101 indique des imports directs `SessionLocal` et une redirection globale.
- Evidence 2: `backend/app/tests/unit/test_backend_db_test_harness.py` - la garde DB existe deja et s'appuie sur une allowlist persistante.
- Evidence 3: `backend/app/tests/conftest.py` - le fichier assigne globalement `db_session_module.SessionLocal`.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les tests DB consomment une fixture ou un helper explicite.
- L'allowlist DB est vide ou contient uniquement des exceptions exactes avec condition de sortie.
- La redirection globale de session est absente.
- La verification SQLite Alembic reste executee pour les fichiers pertinents.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-011` - la story touche directement le harnais DB des tests backend.
  - `RG-010` - les tests migres doivent rester sous les racines collectees.
- Non-applicable invariants:
  - `RG-001`, `RG-003`, `RG-009` - aucune route API ou package schema legacy n'est modifie.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_backend_db_test_harness.py`
  - `pytest --collect-only -q --ignore=.tmp-pytest`
- Allowed differences:
  - Les chemins d'import de session de test changent vers les helpers canoniques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Direct DB import inventory is persisted. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. |
| AC2 | Canonical DB helpers own test sessions. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. |
| AC3 | SQLite alignment still runs. | Evidence profile: `runtime_openapi_contract`; `pytest -q tests/integration/test_backend_sqlite_alignment.py`. |
| AC4 | Global DB redirection is absent. | Evidence profile: `targeted_forbidden_symbol_scan`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. |
| AC5 | Batch evidence is complete. | Evidence profile: `batch_migration_mapping`; `pytest --collect-only -q --ignore=.tmp-pytest`. |

## 8. Implementation Tasks

- [ ] Task 1 - Persist the direct import baseline (AC: AC1)
- [ ] Task 2 - Migrate integration DB consumers to canonical helpers (AC: AC2, AC3)
- [ ] Task 3 - Migrate app test DB consumers to canonical helpers (AC: AC2)
- [ ] Task 4 - Remove global DB session redirection from app test conftest (AC: AC4)
- [ ] Task 5 - Update guards and batch evidence (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/tests/helpers/db_session.py` for app test DB sessions.
  - `backend/tests/integration/app_db.py` for integration tests sharing the app DB session.
  - `ensure_configured_sqlite_file_matches_alembic_head` for SQLite file alignment.
- Do not recreate:
  - A second DB helper with the same responsibility.
  - A compatibility wrapper named `SessionLocal`.
- Shared abstraction allowed only if:
  - It replaces duplicate DB session setup across at least two migrated files and is covered by the DB harness guard.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `from app.infra.db.session import SessionLocal`
- `from app.infra.db.session import engine`
- `db_session_module.SessionLocal =`
- `Base.metadata.create_all` on `horoscope.db`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| App test DB session | `backend/app/tests/helpers/db_session.py` | Direct production session import |
| Integration app DB session | `backend/tests/integration/app_db.py` | Static `SessionLocal` import |
| DB harness guard | `backend/app/tests/unit/test_backend_db_test_harness.py` | Manual scan only |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/conftest.py`
- `backend/app/tests/unit/test_backend_db_test_harness.py`
- `backend/tests/integration/app_db.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/conftest.py` - remove global DB session mutation.
- `backend/app/tests/helpers/db_session.py` - expose canonical app test DB helper.
- `backend/tests/integration/app_db.py` - keep or refine canonical integration DB helper.
- `_condamad/stories/replace-direct-sessionlocal-test-imports/db-session-batches.md` - persist batch mapping.

Likely tests:

- `backend/app/tests/unit/test_backend_db_test_harness.py` - harden DB import guard.
- `backend/tests/integration/test_backend_sqlite_alignment.py` - prove SQLite alignment.

Files not expected to change:

- `frontend/src` - no frontend change.
- `backend/alembic` - no schema migration planned.
- `requirements.txt` - must not be created.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_db_test_harness.py
pytest -q tests/integration/test_backend_sqlite_alignment.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg -n "from app\.infra\.db\.session import (SessionLocal|engine)" app/tests tests -g "*.py"
rg -n "db_session_module\.(SessionLocal|engine) =" app/tests/conftest.py
```

## 22. Regression Risks

- Risk: un test perd son isolation DB.
  - Guardrail: test cible du lot migre plus collecte complete.
- Risk: la suppression de la redirection globale casse un import a la collecte.
  - Guardrail: migration par lots avant suppression finale.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 24. References

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - finding F-101.
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - candidat SC-101.
- `_condamad/stories/regression-guardrails.md` - invariants RG-010 et RG-011.
- `backend/app/tests/unit/test_backend_db_test_harness.py` - garde DB existante.
