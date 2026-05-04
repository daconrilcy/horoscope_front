# Story CS-011 supprimer-partage-session-db-calcul-threade-prediction: Supprimer le partage de session DB dans le calcul threade prediction

Status: ready-to-review

## 1. Objective

Garantir que le calcul prediction soumis a timeout ne partage plus la meme session SQLAlchemy entre le thread appelant et le worker.
La solution doit utiliser soit un contexte precharge hors thread, soit une session worker dediee creee par factory explicite.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-006`
- Reason for change: le finding `F-006` indique que `PredictionComputeRunner` capture la session DB de l'appelant et peut continuer apres timeout.

## 3. Domain Boundary

- Domain: `backend/app/services/prediction/compute_runner.py`
- In scope:
  - Suppression du partage de session DB entre threads.
  - Test de timeout prouvant que la session appelante n'est pas consommee par le worker apres abandon.
  - Documentation du comportement choisi dans le fichier applicatif modifie.
- Out of scope:
  - Refonte du moteur prediction.
  - Changement de schema DB.
  - Suppression globale du timeout.
  - Migration namespace prediction.
- Explicit non-goals:
  - Ne pas contourner `RG-011` sur les imports directs `SessionLocal` dans les tests.
  - Ne pas introduire de pool ou queue externe.
  - Ne pas masquer le probleme par un fallback silencieux apres timeout.

## 4. Operation Contract

- Operation type: update
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime un chemin runtime dangereux de partage de session DB.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le timeout doit continuer a retourner l'erreur controlee actuelle.
  - La session appelante ne doit pas etre utilisee dans un worker survivant.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: la solution exige d'abandonner completement le timeout par thread.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le risque concerne le comportement effectif d'une session DB au runtime. |
| Baseline Snapshot | yes | Le comportement timeout doit etre compare avant apres. |
| Ownership Routing | yes | La session DB appartient a infra ou contexte applicatif explicite. |
| Allowlist Exception | no | Aucune exception de partage de session. |
| Contract Shape | no | Aucun payload public ne change. |
| Batch Migration | no | Un runner est touche. |
| Reintroduction Guard | yes | Le partage de session ne doit pas revenir. |
| Persistent Evidence | yes | Le choix technique et les preuves de timeout doivent etre persistes. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - AST guard et test timeout avec session instrumentee ou factory worker.
- Secondary evidence:
  - Scan du commentaire non-thread-safe dans `compute_runner.py`.
- Static scans alone are not sufficient for this story because:
  - La surete thread depend d'une execution concurrente.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-after.md`
- Expected invariant:
  - Le timeout reste controle et la session appelante n'est pas partagee avec le worker.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Prediction compute timeout | `backend/app/services/prediction/compute_runner.py` | DB session caller shared in worker |
| DB session lifecycle | `backend/app/infra/db` or injected factory | thread closure over caller session |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| timeout baseline | `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-before.md` | Documenter le risque initial. |
| timeout after | `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-after.md` | Prouver la correction runtime. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states
- AST guard
- test timeout runtime

Required forbidden examples:

- Closure worker capturant `db` appelant.
- Commentaire indiquant que la session reste non-thread-safe apres timeout.
- Appel a `ctx_loader` dans le worker avec session appelante.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_service.py` plus test runner timeout dedie.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-015` montre le `ThreadPoolExecutor` et la capture de session.
- Evidence 2: `backend/app/services/prediction/compute_runner.py` - fichier cible indique le comportement de timeout audite.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-011`.

## 6. Target State

- Le worker ne capture pas la session DB appelante.
- Le timeout retourne la meme categorie d'erreur controlee.
- Un test echoue si une session appelante est reutilisee dans le worker.
- Le comportement est documente en francais dans le fichier applicatif modifie.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-011` - les tests DB doivent utiliser les fixtures canoniques.
  - `RG-031` - le calcul threade prediction ne doit pas partager la session DB appelante.
- Non-applicable invariants:
  - `RG-017` - runtime LLM hors scope.
  - `RG-025` - Stripe hors scope.
- Required regression evidence:
  - Test timeout, tests daily prediction, scan du commentaire non-thread-safe.
- Allowed differences:
  - Creation d'une session worker dediee ou prechargement du contexte hors thread.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le worker ne capture pas la session appelante. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_prediction_compute_runner.py`. |
| AC2 | Le timeout reste controle. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_daily_prediction_service.py`. |
| AC3 | La solution documente le comportement DB. | Evidence profile: `targeted_forbidden_symbol_scan`; `pytest -q app/tests/unit/test_prediction_compute_runner.py`. |
| AC4 | Les preuves avant apres sont conservees. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_daily_prediction_service.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le risque initial (AC: AC4)
- [x] Task 2 - Choisir prechargement ou session worker (AC: AC1)
- [x] Task 3 - Modifier le runner (AC: AC1, AC2)
- [x] Task 4 - Ajouter le test timeout (AC: AC1, AC2)
- [x] Task 5 - Documenter et valider (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/prediction/compute_runner.py` comme owner du timeout.
  - Fixtures DB canoniques existantes.
  - `backend/app/tests/unit/test_daily_prediction_service.py`.
- Do not recreate:
  - Une nouvelle execution queue.
  - Une session globale.
  - Un fallback silencieux apres timeout.
- Shared abstraction allowed only if:
  - Elle centralise la creation d'une session worker deja necessaire.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- Capture de `db` appelant dans le worker.
- `SessionLocal` direct dans un nouveau test hors helper canonique.
- Commentaire affirmant un risque non corrige de session non-thread-safe.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Timeout calcul prediction | `backend/app/services/prediction/compute_runner.py` | logique timeout dupliquee |
| Lifecycle session DB | `backend/app/infra/db` ou factory injectee | session appelante capturee |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper
- adding a compatibility alias
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with the exact external evidence.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/services/prediction/compute_runner.py`
- `backend/app/prediction/context_loader.py`
- `backend/app/services/prediction/service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/tests/integration/app_db.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/services/prediction/compute_runner.py` - corriger la gestion thread/session.
- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-before.md` - preuve avant.
- `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-after.md` - preuve apres.

Likely tests:

- `backend/app/tests/unit/test_prediction_compute_runner.py` - nouveau test dedie du timeout.
- `backend/app/tests/unit/test_daily_prediction_service.py` - non-regression service.

Files not expected to change:

- `frontend/src` - aucun impact frontend.
- `backend/app/api/v1/routers/public/predictions.py` - API hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/services/prediction/compute_runner.py app/tests/unit/test_daily_prediction_service.py
pytest -q app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py
rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" app/services/prediction/compute_runner.py
rg -n "SessionLocal|engine" app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py
```

## 22. Regression Risks

- Risk: le timeout devient bloquant.
  - Guardrail: `AC2` impose le test daily prediction.
- Risk: le test introduit un import DB interdit.
  - Guardrail: `RG-011` et `AC1` imposent fixtures canoniques.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuve `E-015`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-006` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-006` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
