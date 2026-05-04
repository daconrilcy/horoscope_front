# Story CS-012 ajouter-garde-anti-croissance-app-prediction: Ajouter une garde anti-croissance pour app.prediction

Status: ready-to-review

## 1. Objective

Ajouter une garde d'architecture qui bloque les nouveaux fichiers et les imports interdits sous `backend/app/prediction` pendant la convergence du namespace.
La garde doit utiliser une allowlist exacte des fichiers actuels et refuser les dependances infra, API et LLM runtime non autorisees.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-007`
- Reason for change: le finding `F-007` montre qu'aucun test d'architecture ne bloque la croissance du package racine `app.prediction`.

## 3. Domain Boundary

- Domain: `backend/app/tests/unit`
- In scope:
  - Test AST d'architecture prediction.
  - Allowlist exacte des fichiers actuels sous `backend/app/prediction`.
  - Interdiction des nouveaux imports infra, API, settings et LLM runtime.
  - Documentation des exceptions exactes avec condition de sortie.
- Out of scope:
  - Migration des fichiers prediction.
  - Correction du bug `astro_foundation`.
  - Refactor DB ou LLM.
  - Ajout de nouveaux dossiers racine backend.
- Explicit non-goals:
  - Ne pas affaiblir `RG-016` a `RG-019`.
  - Ne pas utiliser une exception dossier-wide.
  - Ne pas masquer la dette par un test qui accepte tout le package.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ajoute un test d'architecture et une allowlist anti-drift.
- Behavior change allowed: no
- Behavior change constraints:
  - Le code applicatif ne change pas sauf commentaire de preuve indispensable.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une dependance interdite actuelle doit rester sans condition de sortie.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde AST est la source executable de la regle. |
| Baseline Snapshot | yes | L'allowlist doit capturer l'etat initial des fichiers prediction. |
| Ownership Routing | yes | Les imports interdits representent des owners canoniques. |
| Allowlist Exception | yes | Les fichiers actuels doivent etre allowlistes exactement. |
| Contract Shape | no | Aucun schema public. |
| Batch Migration | no | Aucune migration. |
| Reintroduction Guard | yes | La garde bloque la reintroduction et la croissance. |
| Persistent Evidence | yes | L'allowlist doit etre persistante et auditable. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - AST guard sous `backend/app/tests/unit`.
- Secondary evidence:
  - `rg --files app/prediction` et scans d'import.
- Static scans alone are not sufficient for this story because:
  - La regle doit echouer automatiquement pendant pytest.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- Comparison after implementation:
  - `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`
- Expected invariant:
  - Aucun fichier prediction ou import interdit ne peut etre ajoute sans mise a jour explicite de l'allowlist.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Prediction package growth | owners cibles documentes | `backend/app/prediction` |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/prediction/context_loader.py` | current DB imports | Dette constatee par `F-002`. | Until CS-007 is implemented. |
| `backend/app/prediction/persistence_service.py` | current DB imports | Dette constatee par `F-002`. | Until CS-007 is implemented. |
| `backend/app/prediction/public_projection.py` | current LLM/settings imports | Dette constatee par `F-004`. | Until CS-009 is implemented. |

Rules:

- no wildcard
- no folder-wide exception
- no implicit exception
- every exception must be validated by test or scan

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
| prediction allowlist | `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md` | Lister les fichiers et exceptions exactes. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- Nouveau fichier Python sous `backend/app/prediction` absent de l'allowlist.
- `from app.api`
- `fastapi`
- `AIEngineAdapter` hors exception exacte.
- `from sqlalchemy` hors exception exacte.

Guard evidence:

- Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` checks the allowlist.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-016` indique qu'aucun guard global n'existe.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md` - `SC-007` demande une allowlist exacte.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-016` a `RG-019`.

## 6. Target State

- Un test AST echoue pour tout nouveau fichier prediction non allowliste.
- Les imports interdits sont controles avec exceptions exactes.
- L'allowlist est persistante et reference les stories de sortie.
- La garde rejoint la validation standard backend.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-016` - pas de retour nominal de `LLMNarrator`.
  - `RG-017` - pas de provider OpenAI direct hors provider canonique.
  - `RG-032` - `backend/app/prediction` ne doit pas croitre sans classification.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Test AST, allowlist persistante, scans exacts `app.prediction`.
- Allowed differences:
  - Ajout du fichier de test et de l'artefact d'allowlist.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'allowlist couvre les fichiers actuels. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC2 | La garde refuse les nouveaux fichiers. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC3 | La garde refuse les imports interdits. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC4 | Les exceptions ont une condition de sortie. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC5 | Les guards LLM restent passants. | Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'allowlist exacte (AC: AC1)
- [x] Task 2 - Ajouter le test AST fichier (AC: AC2)
- [x] Task 3 - Ajouter le test AST imports (AC: AC3)
- [x] Task 4 - Documenter les exceptions (AC: AC4)
- [x] Task 5 - Executer les guards LLM (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Patterns des tests d'architecture sous `backend/app/tests/unit`.
  - `_condamad/stories/regression-guardrails.md` pour les invariants.
- Do not recreate:
  - Un second registre hors dossier story.
  - Une exception wildcard.
  - Un guard grep-only sans AST.
- Shared abstraction allowed only if:
  - Elle reutilise une helper de parsing AST deja presente.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/prediction/*.py` non inscrit dans l'allowlist.
- `from app.api` dans `backend/app/prediction`.
- `AIEngineAdapter` hors exception exacte.
- `from sqlalchemy` hors exception exacte.
- `LLMNarrator`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Guard architecture backend | `backend/app/tests/unit` | script manuel non collecte |
| Exceptions prediction | artefact de story | memoire reviewer |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_backend_services_structure_guard.py`
- `backend/app/tests/unit/test_scope_separation_imports.py`
- `backend/app/prediction`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde anti-croissance.
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md` - allowlist exacte.

Likely tests:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - test AST nouveau ou modifie.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` - non-regression LLM.

Files not expected to change:

- `backend/app/prediction/*.py` - code applicatif hors scope.
- `frontend/src` - aucun impact frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/tests/unit/test_daily_prediction_guardrails.py
pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py
rg --files app/prediction
rg -n "from app\\.api|fastapi|AIEngineAdapter|from sqlalchemy|LLMNarrator" app/prediction -g "*.py"
```

## 22. Regression Risks

- Risk: l'allowlist fige une dette sans sortie.
  - Guardrail: `AC4` impose une condition par exception.
- Risk: un nouveau fichier prediction passe sans revue.
  - Guardrail: `AC2` impose un test AST.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuve `E-016`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-007` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-007` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
