# Story converge-db-test-fixtures: Replace global DB session monkeypatches with explicit test fixtures

Status: ready-for-dev

## 1. Objective

Converger le harnais DB des tests backend vers un chemin explicite de session/engine de test.
La story reduit progressivement les imports directs de SessionLocal et les monkeypatches globaux.
Elle preserve l'alignement SQLite/Alembic decrit dans les consignes locales.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-003 identifie un risque d'isolation et de lisibilite lie aux rewiring globaux DB.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend tests DB harness
- In scope:
  - Inventorier les imports directs `SessionLocal` et `engine` dans les tests.
  - Creer ou documenter un helper/fixture DB canonique pour les tests backend.
  - Migrer un premier lot representatif de tests DB vers ce helper.
  - Ajouter une garde contre les nouveaux imports directs de `app.infra.db.session.SessionLocal` dans les tests.
  - Preserver `ensure_configured_sqlite_file_matches_alembic_head`.
- Out of scope:
  - ecarter tous les monkeypatches globaux si des tests restants en dependent encore.
  - Modifier les migrations Alembic ou les modeles SQLAlchemy.
  - Changer le comportement applicatif DB.
- Explicit non-goals:
  - Ne pas masquer les imports directs via un alias de compatibilite.
  - Ne pas creer de `create_all` contre `horoscope.db`.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: service-boundary-refactor
- Archetype reason: les tests doivent router l'acces DB via un helper de test explicite au lieu de la session de production.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les assertions des tests migres doivent rester equivalentes.
  - Les fichiers SQLite de test doivent rester alignes a Alembic head selon la fixture existante.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: ecarter le monkeypatch global casse des suites non migrees dans la meme story.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La preuve passe par les fixtures chargees par pytest et les sessions creees au runtime de test. |
| Baseline Snapshot | yes | Les imports directs et patterns SQLite doivent etre mesures avant/apres. |
| Ownership Routing | yes | Les tests doivent utiliser un proprietaire DB de test canonique. |
| Allowlist Exception | yes | Des imports directs restants peuvent etre temporairement allowlistes par lot. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | yes | La migration doit etre faite par lots representatifs. |
| Reintroduction Guard | yes | Une garde doit bloquer de nouveaux imports directs. |
| Persistent Evidence | yes | L'inventaire des imports et la liste des exceptions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard and loaded config evidence for this story.
  - Fixtures pytest effectives dans les conftests backend.
  - Execution de tests DB cibles.
- Secondary evidence:
  - `rg -n "from app\.infra\.db\.session import SessionLocal|from app\.infra\.db\.session import .*engine|db_session_module\.SessionLocal"`.
- Static scans alone are not sufficient for this story because:
  - l'isolation DB depend des fixtures chargees par pytest et du fichier SQLite utilise au runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/converge-db-test-fixtures/db-test-session-imports-before.md`
  - `_condamad/stories/converge-db-test-fixtures/db-fixture-topology-before.md`
- Comparison after implementation:
  - `_condamad/stories/converge-db-test-fixtures/db-test-session-imports-after.md`
  - `_condamad/stories/converge-db-test-fixtures/db-fixture-topology-after.md`
  - `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md`
- Expected invariant:
  - Aucun nouveau test ne peut importer `SessionLocal` de production directement.
- Allowed differences:
  - Diminution des imports directs; maintien temporaire d'exceptions exactes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Session DB de test | Fixture/helper backend tests dedie | Imports directs production `SessionLocal` |
| Alignement SQLite/Alembic | `ensure_configured_sqlite_file_matches_alembic_head` | `create_all` sur `horoscope.db` |
| Helpers integration partages | `tests/integration/app_db.py` when app test session is shared | Static import of production `SessionLocal` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/tests/conftest.py` | `db_session_module.SessionLocal` | Fixture globale actuelle. | Exit condition: direct imports migrated or listed by file. |
| `backend/tests/integration/test_llm_release.py` | `SessionLocal` | Representative direct import. | Exit condition: migrated or listed with owner/date. |
| `backend/app/tests/integration/test_admin_content_api.py` | `SessionLocal, engine` | Representative direct import. | Exit condition: migrated or listed with owner/date. |
## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 - Inventory | Direct `SessionLocal` imports | Import inventory | None | Guard only | Exact allowlist | Unknown fixture owner |
| 2 - Canonical helper | Repeated session setup | Test DB helper | Representative tests | Targeted DB tests | No production import | Alembic regression |
| 3 - Guard | Unguarded direct imports | Static/AST guard | Future tests | Guard test | New import fails | Too many unclassified exceptions |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Import baseline | `_condamad/stories/converge-db-test-fixtures/db-test-session-imports-before.md` | Capturer les imports directs. |
| Fixture topology after | `_condamad/stories/converge-db-test-fixtures/db-fixture-topology-after.md` | Documenter le proprietaire canonique. |
| Allowlist | `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` | Lister les exceptions restantes. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- un nouveau test importe directement `SessionLocal` ou `engine` de `app.infra.db.session`;
- un helper de test cree une DB secondaire sans passer par l'alignement Alembic applicable;
- `create_all` est applique a la DB principale `horoscope.db`.

Required architecture guard: pytest -q app/tests/unit/test_backend_architecture_guard.py with AST guard evidence.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-007 decrit les multiples strategies SQLite et le monkeypatch global.
- Evidence 2: `backend/app/tests/conftest.py` - remplace globalement `app.infra.db.session.engine` et `SessionLocal` pour des tests legacy.
- Evidence 3: `backend/tests/conftest.py` and `backend/app/tests/integration/conftest.py` - executent l'alignement SQLite/Alembic.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un helper ou une fixture DB de test explicite est le chemin canonique pour les tests migres.
- Les imports directs restants sont allowlistes par fichier avec raison et etape de migration.
- Une garde empeche toute croissance de dette DB harness.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-005` - la frontiere API/services ne doit pas etre contournee par tests qui masquent de la persistance incorrecte.
  - `RG-006` - les tests d'architecture API doivent rester fiables avec une DB de test explicite.
- Non-applicable invariants:
  - `RG-001`, `RG-002`, `RG-003`, `RG-004`, `RG-007`, `RG-008`, `RG-009` - la story ne modifie pas ces surfaces, seulement le harnais DB de tests.
- Required regression evidence:
  - Tests DB cibles, garde d'import, collecte pytest, alignement SQLite.
- Allowed differences:
  - Reduction des imports directs et des monkeypatches; aucune modification de schema.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L inventaire des imports directs DB est complet. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. |
| AC2 | Un helper DB canonique est utilise par un lot. | Evidence profile: `runtime_openapi_contract`; `pytest -q tests/integration/test_backend_sqlite_alignment.py`. |
| AC3 | L'alignement SQLite/Alembic est preserve. | Evidence profile: `runtime_openapi_contract`; `pytest -q tests/integration/test_backend_sqlite_alignment.py`. |
| AC4 | Une garde bloque les nouveaux imports directs. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_db_test_harness.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire DB harness avant changement (AC: AC1)
- [ ] Task 2 - Definir le helper/fixture canonique (AC: AC2, AC3)
- [ ] Task 3 - Migrer un lot representatif de tests DB (AC: AC2)
- [ ] Task 4 - Ajouter allowlist et garde anti-reintroduction (AC: AC1, AC4)
- [ ] Task 5 - Executer validations dans le venv (AC: AC2, AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ensure_configured_sqlite_file_matches_alembic_head`.
  - `tests/integration/app_db.py` pour les tests partageant la session avec `app/tests`.
- Do not recreate:
  - Plusieurs factories SQLite incompatibles.
  - Un alias de `SessionLocal` de production dans un helper legacy.
- Shared abstraction allowed only if:
  - Elle remplace au moins deux patterns DB dupliques.

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

- Nouveaux `from app.infra.db.session import SessionLocal`.
- Nouveaux `from app.infra.db.session import engine`.
- Nouveau `Base.metadata.create_all` sur la DB principale.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Test DB session | Canonical test fixture/helper | Production `SessionLocal` imports |
| SQLite migration alignment | `ensure_configured_sqlite_file_matches_alembic_head` | Ad hoc create_all-only setup |

## 14. Delete-Only Rule

- Delete-Only Rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/conftest.py`
- `backend/tests/conftest.py`
- `backend/app/tests/integration/conftest.py`
- `backend/tests/integration/app_db.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/tests/conftest.py` - reduire ou documenter le monkeypatch global apres migration.
- `backend/tests/integration/app_db.py` or new helper under existing tests tree - helper canonique.
- `backend/app/tests/unit/test_backend_db_test_harness.py` or `backend/tests/unit/test_backend_db_test_harness.py` - garde.
- Representative DB test files selected from the import inventory.
- `_condamad/stories/converge-db-test-fixtures/*.md` - preuves.

Likely tests:

- `backend/tests/integration/test_backend_sqlite_alignment.py`
- Guard test for direct imports.
- Targeted migrated DB tests.

Files not expected to change:

- `backend/alembic` - pas de migration schema.
- `frontend/src` - aucun impact.
- `requirements.txt` - must not be created.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/integration/test_backend_sqlite_alignment.py
pytest -q app/tests/unit/test_backend_db_test_harness.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg -n "from app\.infra\.db\.session import SessionLocal|from app\.infra\.db\.session import .*engine" app/tests tests -g test_*.py -g conftest.py
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/converge-db-test-fixtures/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/converge-db-test-fixtures/00-story.md
```

## 21. Regression Risks

- Risk: les tests DB deviennent dependants d'une DB partagee.
  - Guardrail: fixtures explicites et alignement SQLite cible.
- Risk: un alias masque l'import production.
  - Guardrail: garde AST ou scan cible hors allowlist.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 23. References

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuve E-007.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-003.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-003.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
