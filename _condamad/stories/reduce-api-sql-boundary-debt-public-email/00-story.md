# Story reduce-api-sql-boundary-debt-public-email: Réduire la dette SQL du routeur public email

Status: completed

## 1. Objective

Extraire le flux de persistance du routeur `backend/app/api/v1/routers/public/email.py`
vers un propriétaire applicatif hors API, sans changer le chemin public historique.
La story doit retirer les trois entrées SQL correspondantes de `router-sql-allowlist.md`
et prouver que la dette SQL API diminue sans régression du désabonnement email.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/api-adapter/2026-04-28-0046`
- Reason for change: le finding `F-001` indique 848 entrées SQL/session/DB actives dans l'allowlist API.
  Le routeur `public/email.py` contient un lot borné: `Depends(get_db_session)`,
  `db.execute` et `db.commit` sur le flux `unsubscribe`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- In scope:
  - Extraire uniquement la persistance du handler `unsubscribe` de `backend/app/api/v1/routers/public/email.py`.
  - Créer ou réutiliser un service applicatif email hors API pour marquer l'utilisateur comme désabonné.
  - Préserver la route runtime existante `GET /api/email/unsubscribe`.
  - Mettre à jour l'allowlist SQL exacte en supprimant seulement les lignes devenues obsolètes pour `public/email.py`.
  - Ajouter ou ajuster les tests ciblés du service et du flux HTTP de désabonnement.
- Out of scope:
  - Migrer ou supprimer l'URL historique `/api/email/unsubscribe`.
  - Refactorer les autres routeurs listés dans l'audit (`admin/llm/prompts.py`, `admin/users.py`, `ops/entitlement_mutation_audits.py`, `public/billing.py`).
  - Modifier les modèles SQLAlchemy, migrations Alembic, stratégie JWT ou templates HTML sauf adaptation minimale au service extrait.
  - Modifier le frontend.
- Explicit non-goals:
  - Ne pas créer de wrapper, alias, fallback, re-export ou deuxième endpoint de désabonnement.
  - Ne pas contourner `RG-006`: `backend/app/api` reste un adaptateur HTTP strict.
  - Ne pas contourner `RG-008`: toute dette SQL restante doit rester exacte dans `router-sql-allowlist.md`.
  - Ne pas toucher `RG-007`: les endpoints admin LLM observability restent propriétaires dans `admin/llm/observability.py`.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime une surface legacy interne précise.
  L'accès SQL direct du routeur `public/email.py` est conservé comme exception temporaire dans l'allowlist.
- Behavior change allowed: no
- Behavior change constraints:
  - Le chemin `GET /api/email/unsubscribe`, le paramètre `token`, les statuts d'erreur attendus et les réponses HTML existantes doivent rester équivalents.
  - Les différences autorisées se limitent au déplacement interne de la persistance et à la suppression des entrées SQL devenues obsolètes dans l'allowlist.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: l'extraction impose un changement de route, payload, statut HTTP ou HTML public.
  Une décision est aussi requise si une dette SQL de `public/email.py` doit rester sans justification temporaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le comportement de la route publique et l'absence de dette SQL doivent être prouvés par tests runtime et garde AST. |
| Baseline Snapshot | yes | La story promet une préservation OpenAPI/route et une réduction mesurable de l'allowlist. |
| Ownership Routing | yes | La persistance doit passer de l'adaptateur API vers un service applicatif. |
| Allowlist Exception | yes | `router-sql-allowlist.md` est la source exacte des exceptions SQL restantes. |
| Contract Shape | no | Aucun changement de forme HTTP n'est autorisé. |
| Batch Migration | yes | Le lot est borné au routeur public email et doit documenter l'ancien et le nouveau propriétaire. |
| Reintroduction Guard | yes | La garde doit échouer si `public/email.py` réintroduit SQLAlchemy, `get_db_session` ou des appels `db.*`. |
| Persistent Evidence | yes | Les inventaires avant/après et le diff d'allowlist doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - `app.main.app.openapi()` pour vérifier que `GET /api/email/unsubscribe` reste exposé.
  - `backend/app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` pour la dette SQL exacte.
  - `backend/tests/integration/test_email_unsubscribe.py` pour le comportement runtime du désabonnement.
- Secondary evidence:
  - `rg -n "get_db_session|Session|db\\.|sqlalchemy" backend/app/api/v1/routers/public/email.py`
  - Diff de `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`.
- Static scans alone are not sufficient for this story because:
  - La route est montée au runtime via le registre d'exceptions.
  - La persistance doit être prouvée par intégration, pas seulement par scans statiques.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract
changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-before.json`
  - `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-before.md`
- Comparison after implementation:
  - `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-after.json`
  - `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-after.md`
  - `_condamad/stories/reduce-api-sql-boundary-debt-public-email/allowlist-diff.md`
- Expected invariant:
  - `GET /api/email/unsubscribe` reste présent avec le même propriétaire runtime.
  - Les entrées SQL de `public/email.py` disparaissent de l'inventaire et de l'allowlist.
  - Aucune nouvelle entrée SQL n'apparaît dans `backend/app/api`.
- Allowed differences:
  - Diminution de trois entrées SQL connues dans `router-sql-allowlist.md`.
  - Ajout ou réutilisation d'un service applicatif email hors API.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP request parsing, token query parameter and HTML response mapping | `backend/app/api/v1/routers/public/email.py` | `backend/app/services/**` |
| JWT payload interpretation and unsubscribe use case orchestration | Existing or new email service under `backend/app/services/email/**` | `backend/app/api/**` |
| SQLAlchemy update/session operation | `backend/app/services/**` using existing infra session patterns | `backend/app/api/v1/routers/public/email.py` |
| Route exception metadata for `/api/email/unsubscribe` | `backend/app/api/route_exceptions.py` | Hidden test-only allowlist |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | `public/email.py` SQL rows | Dette SQL ciblée par ce lot. | Remove after extraction. |
| `backend/app/api/route_exceptions.py` | `/api/email/unsubscribe` | URL historique hors scope de suppression. | Keep unchanged. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

Use when the archetype or scope requires migration by independent batches.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Public email persistence | `public/email.py` DB update | `services/email/**` | `unsubscribe` only | email integration tests | Negative SQL scan | HTTP change |

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-before.json` | Prove route contract before extraction. |
| OpenAPI after snapshot | `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-after.json` | Prove route contract after extraction. |
| SQL before inventory | `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-before.md` | Record targeted debt before extraction. |
| SQL after inventory | `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-after.md` | Prove targeted debt was removed. |
| Allowlist diff | `_condamad/stories/reduce-api-sql-boundary-debt-public-email/allowlist-diff.md` | Prove only obsolete public email rows were removed. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- importable Python modules
- frontend route table
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `from app.infra.db.session import get_db_session` in `backend/app/api/v1/routers/public/email.py`
- `from sqlalchemy` or `from sqlalchemy.orm import Session` in `backend/app/api/v1/routers/public/email.py`
- `db.execute`, `db.commit`, `db.rollback`, `db.add`, `db.flush` in `unsubscribe`

Guard evidence:

- Evidence profile: `reintroduction_guard`.
- Command: `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist`.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/api-adapter/2026-04-28-0046/02-finding-register.md` - `F-001` records 848 active SQL/session/DB allowlist entries in the API layer.
- Evidence 2: `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` -
  `public/email.py` has three rows: `Depends(get_db_session)`, `db.execute`, `db.commit`.
- Evidence 3: `backend/app/api/v1/routers/public/email.py` - `unsubscribe` currently imports SQLAlchemy/session dependencies and updates `UserModel.email_unsubscribed` directly.
- Evidence 4: `backend/tests/integration/test_email_unsubscribe.py` -
  integration tests exercise success, invalid type, expired token and unknown user.
- Evidence 5: `backend/app/services/email/service.py` - email link generation currently emits the backend URL plus `/api/email/unsubscribe?token=`.
- Evidence 6: `backend/app/tests/unit/test_api_router_architecture.py` - `test_api_sql_boundary_debt_matches_exact_allowlist` enforces exact SQL debt entries.
- Evidence N: `_condamad/stories/regression-guardrails.md` - shared regression invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `backend/app/api/v1/routers/public/email.py` no longer imports SQLAlchemy, `Session`, `UserModel`, or `get_db_session`.
- The handler delegates the unsubscribe persistence to a single email service function.
- `/api/email/unsubscribe` remains mounted and tested with the same observable behavior.
- `router-sql-allowlist.md` no longer contains rows for `app/api/v1/routers/public/email.py`.
- Architecture guards fail if route-level SQL debt returns in that file.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-006` - la story touche la frontière adaptateur API et doit empêcher les couches non-API de dépendre de `app.api`.
  - `RG-008` - la story modifie la dette SQL directe des routeurs et l'allowlist exacte.
- Non-applicable invariants:
  - `RG-001` - aucune façade historique supprimée dans cette story.
  - `RG-007` - aucun endpoint admin LLM observability n'est modifié.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_api_router_architecture.py`
  - `pytest -q tests/integration/test_email_unsubscribe.py`
  - Negative scan on `backend/app/api/v1/routers/public/email.py` for SQL/session symbols.
- Allowed differences:
  - Suppression des lignes SQL de `public/email.py` dans l'allowlist.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `unsubscribe` n'a plus de SQL/session. | `python -B -c "from app.main import app; app.openapi()"`; API router architecture tests; `rg` SQL route. |
| AC2 | La persistance est hors API. | `pytest -q tests/integration/test_email_unsubscribe.py`; `rg -n "email_unsubscribed=True|update\\(UserModel\\)" app/services`. |
| AC3 | L'allowlist retire les lignes `public/email.py`. | `python -B -c "from app.main import app; app.openapi()"`; API router architecture tests; `allowlist-diff.md`. |
| AC4 | `GET /api/email/unsubscribe` conserve son comportement. | Evidence profile: `integration_test`; `pytest -q tests/integration/test_email_unsubscribe.py` passes. |
| AC5 | Le contrat runtime de route reste stable. | `python -B -c "from app.main import app; app.openapi()"`; API router architecture tests; snapshots. |
| AC6 | Les garde-fous API existants passent. | `python -B -c "from app.main import app; app.openapi()"`; `pytest -q app/tests/unit/test_api_router_architecture.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline ciblé (AC: AC3, AC5)
  - [x] Subtask 1.1 - Sauvegarder `openapi-before.json`.
  - [x] Subtask 1.2 - Sauvegarder `router-sql-public-email-before.md` depuis l'inventaire ou l'allowlist actuelle.

- [x] Task 2 - Extraire le use case de désabonnement hors API (AC: AC1, AC2, AC4)
  - [x] Subtask 2.1 - Identifier le service email existant le plus proche sous `backend/app/services/email/**`.
  - [x] Subtask 2.2 - Déplacer la mise à jour `email_unsubscribed=True` dans une fonction de service typée avec docstring française.
  - [x] Subtask 2.3 - Faire déléguer `unsubscribe` au service sans changement de route ni réponse.

- [x] Task 3 - Mettre à jour les preuves et l'allowlist (AC: AC1, AC3, AC5)
  - [x] Subtask 3.1 - Supprimer uniquement les lignes `app/api/v1/routers/public/email.py` devenues stale dans `router-sql-allowlist.md`.
  - [x] Subtask 3.2 - Sauvegarder `router-sql-public-email-after.md` et `allowlist-diff.md`.
  - [x] Subtask 3.3 - Sauvegarder `openapi-after.json` et comparer avec le baseline.

- [x] Task 4 - Couvrir le comportement et la non-réintroduction (AC: AC2, AC4, AC6)
  - [x] Subtask 4.1 - Ajouter ou ajuster un test de service si le service extrait n'est pas couvert par les tests d'intégration.
  - [x] Subtask 4.2 - Exécuter les tests d'intégration du désabonnement.
  - [x] Subtask 4.3 - Exécuter le test d'architecture SQL exact et le fichier complet d'architecture API.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/email/service.py` or another existing `backend/app/services/email/**` module for email use-case ownership if it fits the existing structure.
  - `backend/app/api/errors.raise_api_error` for HTTP mapping in the router.
  - `backend/app/tests/unit/test_api_router_architecture.py` for architecture guards.
- Do not recreate:
  - A second unsubscribe endpoint.
  - A second JWT token format.
  - A repository or service namespace if an existing email service module can own the use case.
- Shared abstraction allowed only if:
  - It removes the concrete `unsubscribe` persistence duplication and has at least one current consumer in this story.

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

- `backend/app/api/v1/routers/public/email.py` importing `sqlalchemy`, `sqlalchemy.orm.Session`, `app.infra.db.session.get_db_session`, or `app.infra.db.models.user.UserModel`.
- `backend/app/api/v1/routers/public/email.py` calling `db.execute`, `db.commit`, `db.rollback`, `db.add`, `db.flush`, or `db.refresh`.
- New HTTP route replacing `/api/email/unsubscribe`.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions for the `Decision` column:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/route-consumption-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public unsubscribe HTTP route | `backend/app/api/v1/routers/public/email.py` | None in this story |
| Unsubscribe persistence use case | Existing or new `backend/app/services/email/**` function | Direct SQL in `backend/app/api/v1/routers/public/email.py` |
| Historical non-v1 route exception | `backend/app/api/route_exceptions.py` | Hidden route allowlist in tests |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

For this story, the public route `/api/email/unsubscribe` is treated as external-active and must not be deleted. Only the route-level SQL debt entries are removable.

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI before/after proves `GET /api/email/unsubscribe` remains present.
- No generated client/schema update is expected unless the repository already generates one during validation.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/app/services/email/public_email.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/email.py` - delegate persistence to service and remove SQL/session imports.
- `backend/app/services/email/service.py` or another existing `backend/app/services/email/**` file - own the unsubscribe persistence use case.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` - remove stale rows for `public/email.py`.

Likely tests:

- `backend/tests/integration/test_email_unsubscribe.py` - preserve public behavior.
- `backend/app/tests/unit/test_api_router_architecture.py` - guard no SQL debt reintroduction.
- `backend/app/tests/unit/**` or `backend/tests/unit/**` for the targeted email service unit test when a new service function is added.

Files not expected to change:

- `backend/app/api/route_exceptions.py` - route exception remains unchanged in this story.
- `backend/migrations/**` - no schema change.
- `frontend/**` - no frontend contract change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_api_router_architecture.py
pytest -q tests/integration/test_email_unsubscribe.py
python -B -c "from app.main import app; assert '/api/email/unsubscribe' in app.openapi()['paths']"
rg -n "get_db_session|Session|UserModel|sqlalchemy|db\\." app/api/v1/routers/public/email.py
```

## 22. Regression Risks

- Risk: le routeur garde une dépendance DB cachée après extraction.
  - Guardrail: `RG-008`, exact allowlist test and negative scan.
- Risk: le service extrait change les erreurs publiques du lien email.
  - Guardrail: integration tests in `tests/integration/test_email_unsubscribe.py`.
- Risk: une couche service importe `app.api` pour réutiliser une erreur HTTP.
  - Guardrail: `RG-006` and `test_non_api_layers_do_not_import_api_package`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not migrate or remove `/api/email/unsubscribe`; that belongs to a separate story.

## 24. References

- `_condamad/audits/api-adapter/2026-04-28-0046/00-audit-report.md` - audit summary.
- `_condamad/audits/api-adapter/2026-04-28-0046/02-finding-register.md` - `F-001` source finding.
- `_condamad/audits/api-adapter/2026-04-28-0046/03-story-candidates.md` - `SC-001` candidate.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` - exact SQL allowlist source.

## 25. Completion Evidence

- Final validation: `ruff format --check .`, `ruff check .`, and `pytest -q` passed in the activated backend venv.
- Full test result: 3151 passed, 12 skipped.
- Code review: `_condamad/stories/reduce-api-sql-boundary-debt-public-email/generated/11-code-review.md` returned `CLEAN`.
- Remaining tracked diff is limited to the story scope; `backend/horoscope.db` was restored after test runs.
