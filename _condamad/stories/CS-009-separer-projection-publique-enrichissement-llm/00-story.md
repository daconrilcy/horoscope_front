# Story CS-009 separer-projection-publique-enrichissement-llm: Separer projection publique et enrichissement LLM

Status: ready-to-review

## 1. Objective

Faire de la projection publique prediction un assemblage deterministe sans appel LLM direct.
L'enrichissement narratif horoscope doit etre route vers un use case ou service explicite sous `services`, avec conservation du payload public existant.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-004` montre que `public_projection.py` assemble le payload public, lit `settings`, accepte `Session` et appelle `AIEngineAdapter`.

## 3. Domain Boundary

- Domain: `backend/app/services/prediction`
- In scope:
  - Retirer l'appel LLM direct de `backend/app/prediction/public_projection.py`.
  - Creer ou ajuster un use case d'enrichissement narratif sous `services`.
  - Conserver la forme OpenAPI et JSON du payload public.
  - Propager `request_id` et `trace_id` sans generation locale dans la projection.
- Out of scope:
  - Refonte du provider LLM.
  - Suppression du champ public `categories`.
  - Changement de format prompt horoscope daily.
  - Migration complete du namespace `app.prediction`.
- Explicit non-goals:
  - Ne pas contourner `RG-017` en appelant OpenAI directement.
  - Ne pas deplacer les consignes durables protegees par `RG-019`.
  - Ne pas creer un second assembleur public concurrent.

## 4. Operation Contract

- Operation type: move
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story route l'assemblage public et l'enrichissement LLM vers des owners distincts.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La forme publique V4 doit rester stable.
  - Le texte narratif peut changer seulement selon les effets du service LLM canonique.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le payload final doit etre owned par `services/api_contracts` au lieu de `services/prediction/public_predictions.py`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le payload public et l'appel LLM doivent etre prouves par tests runtime. |
| Baseline Snapshot | yes | La forme publique doit etre comparee avant apres. |
| Ownership Routing | yes | Projection et LLM ont des owners differents. |
| Allowlist Exception | yes | Les exceptions temporaires de projection doivent etre exactes. |
| Contract Shape | yes | Le payload public ne doit pas changer. |
| Batch Migration | no | Un seul flux projection publique est touche. |
| Reintroduction Guard | yes | `AIEngineAdapter` ne doit pas revenir dans la projection. |
| Persistent Evidence | yes | Baseline payload et exceptions doivent etre conservees. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - Tests API prediction via `TestClient` et tests unitaires de projection publique.
- Secondary evidence:
  - Scan exact `AIEngineAdapter`, `settings`, `uuid.uuid4()` dans `public_projection.py`.
- Static scans alone are not sufficient for this story because:
  - Un scan ne prouve pas que le JSON public reste equivalent.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/public-payload-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/public-payload-after.md`
- Expected invariant:
  - Les champs publics et status codes de prediction restent identiques.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Public prediction assembly | `backend/app/services/prediction/public_predictions.py` | direct LLM runtime |
| Horoscope narration generation | `backend/app/services/llm_generation/horoscope_daily` | `backend/app/prediction/public_projection.py` |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/prediction/public_projection.py` | deterministic projection helpers | Migration par etapes vers owner public. | Until CS-006 namespace convergence completes. |

Rules:

- no wildcard
- no folder-wide exception
- no implicit exception
- every exception must be validated by test or scan

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI contract, generated client, or frontend type.

- Contract type:
  - Payload JSON public prediction V4.
- Fields:
  - Tous les champs publics existants doivent rester presents.
  - `astro_foundation`, `daily_synthesis`, `categories` et narration gardent leurs noms de serialization.
- Required fields:
  - Les champs requis par les tests API prediction existants.
- Optional fields:
  - Les champs optionnels deja optionnels dans le contrat actuel.
- Status codes:
  - Aucun status code API ne change.
- Serialization names:
  - Les noms wire existants restent inchanges.
- Frontend type impact:
  - Aucun type frontend ne doit etre modifie sans preuve.
- Generated contract impact:
  - OpenAPI avant apres doit etre capture si le endpoint public est touche.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| payload baseline | `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/public-payload-before.md` | Capturer le JSON public actuel. |
| payload after | `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/public-payload-after.md` | Prouver la conservation du contrat. |
| exception register | `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/projection-exceptions.md` | Documenter les exceptions restantes. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `AIEngineAdapter` dans `backend/app/prediction/public_projection.py`
- `settings` dans `backend/app/prediction/public_projection.py`
- `uuid.uuid4()` dans `backend/app/prediction/public_projection.py`
- `Session` dans `backend/app/prediction/public_projection.py`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` checks forbidden imports.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-007` montre le couplage LLM de `public_projection.py`.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-013` montre des policies publiques partagees avec `public_astro_daily_events.py`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-017` et `RG-019`.

## 6. Target State

- La projection publique assemble un payload deterministe.
- L'appel LLM appartient a un service explicite.
- Les IDs de correlation sont injectes depuis l'appelant.
- Les tests API prouvent la stabilite du contrat public.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-017` - aucun provider OpenAI direct ne doit revenir.
  - `RG-019` - les consignes durables restent dans l'assembly gouvernee.
  - `RG-029` - la projection publique ne doit pas redevenir proprietaire du runtime LLM.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Tests API prediction, tests narration, scans exacts `AIEngineAdapter`, OpenAPI ou snapshot JSON.
- Allowed differences:
  - Owner du code executant la narration LLM.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La projection publique ne depend plus du runtime LLM. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC2 | Le payload public reste stable. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_public_projection.py`. |
| AC3 | La narration passe par le service canonique. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_ai_engine_adapter.py`. |
| AC4 | Les exceptions restantes sont exactes. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC5 | Les snapshots avant apres sont conserves. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_public_projection.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le payload public actuel (AC: AC2, AC5)
- [x] Task 2 - Extraire l'appel LLM vers le service canonique (AC: AC1, AC3)
- [x] Task 3 - Injecter les IDs depuis l'appelant (AC: AC1)
- [x] Task 4 - Documenter les exceptions restantes (AC: AC4)
- [x] Task 5 - Executer les tests de contrat public (AC: AC2, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/llm_generation/horoscope_daily/narration_service.py`.
  - `backend/app/services/prediction/public_predictions.py`.
  - Tests existants de projection publique.
- Do not recreate:
  - Un second adapter LLM.
  - Un assembleur public concurrent.
  - Une generation locale de correlation IDs dans la projection.
- Shared abstraction allowed only if:
  - Elle devient le seul chemin pour l'enrichissement narratif public.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `AIEngineAdapter` dans `backend/app/prediction/public_projection.py`
- `uuid.uuid4()` dans `backend/app/prediction/public_projection.py`
- `Session` dans `backend/app/prediction/public_projection.py`
- `LLMNarrator`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Projection publique deterministe | `backend/app/services/prediction/public_predictions.py` | runtime LLM dans `public_projection.py` |
| Narration horoscope daily | `backend/app/services/llm_generation/horoscope_daily` | appel direct depuis projection |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI snapshot before/after when the endpoint prediction public is touched.
- Generated client/schema absence is not required unless generation exists in repo evidence.

## 18. Files to Inspect First

- `backend/app/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction/public_projection.py` - retirer runtime LLM direct.
- `backend/app/services/prediction/public_predictions.py` - owner use case public.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - chemin narratif canonique.
- `backend/app/api/v1/routers/public/predictions.py` - injection IDs depuis la requete.

Likely tests:

- `backend/app/tests/unit/test_public_projection.py` - contrat projection.
- `backend/app/tests/unit/test_daily_prediction_service.py` - orchestration service.
- `backend/app/tests/integration/test_daily_prediction_api.py` - contrat API public.

Files not expected to change:

- `frontend/src` - contrat frontend conserve.
- `backend/app/domain/llm` - assembly LLM hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app tests
pytest -q app/tests/unit/test_public_projection.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py
pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py
rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" app/prediction/public_projection.py
```

## 22. Regression Risks

- Risk: la sortie JSON publique derive pendant le deplacement.
  - Guardrail: `AC2` impose tests API et snapshot.
- Risk: la projection recree un chemin LLM direct.
  - Guardrail: `AC1` impose scan exact et garde AST.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuves `E-007`, `E-013`, `E-014`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-004` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
