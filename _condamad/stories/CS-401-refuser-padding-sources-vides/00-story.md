# Story CS-401 refuser-padding-sources-vides: Refuser Padding Semantique Lecture Natale Sources Vides
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-396-refuser-padding-semantique-lecture-natale-et-sources-vides.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: une lecture natale Basic/Premium `complete` a ete acceptee avec cinq chapitres publics mais seulement trois contenus distincts.
- Source cause: le builder narratif pouvait remplir un chapitre manquant avec la premiere section LLM au lieu de rejeter la projection.
- Source stakes: integrite du contrat public, rejet audite des lectures incompletes, absence de sources astrologiques vides, fermeture complete de `RG-155`.
- Source-alignment evidence: objectifs, AC, taches, scans et guardrails couvrent les huit items du brief sans deplacer le sujet vers quota, UI ou calcul astrologique.

## Objective

Fermer le trou d'integrite entre la reponse LLM et `narrative_natal_reading_v1`: une lecture Basic/Premium `complete`
est acceptee uniquement avec cinq chapitres distincts et des sources astrologiques vulgarisees non vides.

## Target State

- `build_narrative_natal_reading_v1` echoue explicitement lorsqu'une source de chapitre requise manque.
- `validate_narrative_reading_public_text` controle ordre, unicite semantique et sources non vides avant persistance ou exposition.
- Les echecs d'integrite suivent le workflow de rejet/audit existant et restent hors POST/GET/LIST publics.
- Les fixtures V2/V3 couvrent cas incomplet, titres dupliques, narrations dupliquees, sources vides et nominal.
- `backend/docs/narrative-natal-reading-v1-contract.md` decrit la regle de rejet sans proposer de remplissage generique.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-396-refuser-padding-semantique-lecture-natale-et-sources-vides.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-401` after `CS-400`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-150`, `RG-152`, and `RG-155`.
- Evidence 4: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - builder source inspected.
- Evidence 5: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - validation entry point inspected.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` - rejection and public boundary flow inspected.
- Evidence 7: `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - semantic integrity helper surface inspected.
- Evidence 8: `backend/tests/unit/test_narrative_natal_reading_v1.py` - target unit suite inspected.
- Evidence 9: `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - public boundary suite inspected.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector: operation `change/remove-symbol`, domain `backend-domain`, path `backend/app/services/llm_generation/natal`, contract `narrative_natal_reading_v1`.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Builder and validator integrity for `narrative_natal_reading_v1`.
  - Rejection/audit routing for invalid Basic/Premium `complete` natal readings.
  - Backend unit, integration, architecture or static guard tests for the same contract.
  - Backend contract documentation for `narrative_natal_reading_v1`.
- Out of scope:
  - Frontend UI, CSS, generated client, DB schema, auth, i18n, style tokens, build tooling, migrations, quotas, and astrology calculations.
- Explicit non-goals:
  - No React route, screen, client generation, CSS change, quota change, astrology computation change, or public remediation flow.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes a historical source-padding facade and preserves the canonical projection contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Reject incomplete or duplicated Basic/Premium `complete` narrative readings.
  - Preserve nominal accepted readings with five ordered chapter keys and non-empty vulgarized sources.
  - Keep rejected readings outside public POST/GET/LIST interpretation surfaces.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: an external consumer depends on persisted padded readings remaining publicly readable.
- Additional validation rules:
  - Use `AST guard` or bounded `rg` scans to prove the forbidden builder padding symbol stays absent.
  - Use `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py` for chapter and source integrity.
  - Use `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` for public boundary proof.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime builder, validator and service tests prove accepted versus rejected behavior. |
| Baseline Snapshot | yes | Before/after artifacts prove the only allowed surface delta is semantic integrity hardening. |
| Ownership Routing | yes | Builder, validator, semantic helper and service responsibilities must remain canonical. |
| Allowlist Exception | yes | A zero-entry allowlist register proves no padding, duplicate chapter or empty-source tolerance is authorized. |
| Contract Shape | yes | `narrative_natal_reading_v1` has exact chapter order and required public source semantics. |
| Batch Migration | no | No data migration, quota remediation or batch conversion is in scope. |
| Reintroduction Guard | yes | The forbidden source-padding path must stay absent from backend natal generation code. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Missing chapter source raises an explicit projection error. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC2 | Chapter key order is exactly canonical. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC3 | Normalized chapter narratives are unique. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC4 | Normalized chapter titles are unique. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC5 | Basic/Premium public sources are non-empty. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC6 | Rejected semantic payloads stay private. | Evidence profile: route_absence_runtime; `pytest` integration public boundary test. |
| AC7 | Forbidden source padding stays absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal`. |
| AC8 | Contract documentation states the integrity rule. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks backend docs contract. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [x] Task 1: Remove the builder path that can reuse `response.sections[0]` for a missing chapter source. (AC: AC1, AC7)
- [x] Task 2: Keep or introduce a typed projection error for missing chapter source and route it to semantic rejection. (AC: AC1, AC6)
- [x] Task 3: Enforce exact chapter key order through `NARRATIVE_CHAPTER_ORDER` validation. (AC: AC2)
- [x] Task 4: Enforce normalized narrative uniqueness across the five chapters. (AC: AC3)
- [x] Task 5: Enforce normalized title uniqueness across the five chapters. (AC: AC4)
- [x] Task 6: Require non-empty `used_astrological_elements` for Basic/Premium accepted readings. (AC: AC5)
- [x] Task 7: Extend unit fixtures for V2/V3 incomplete, duplicated, empty-source and nominal cases. (AC: AC1, AC2, AC3, AC4, AC5)
- [x] Task 8: Extend integration coverage proving rejected semantic payloads stay out of public POST/GET/LIST. (AC: AC6)
- [x] Task 9: Update `backend/docs/narrative-natal-reading-v1-contract.md` with the integrity rule. (AC: AC8)
- [x] Task 10: Persist validation and scan output under this story evidence directory. (AC: AC9)

## Files to Inspect First

- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/docs/narrative-natal-reading-v1-contract.md`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Runtime Source of Truth

- Primary source of truth:
  - `build_narrative_natal_reading_v1`, `validate_narrative_reading_public_text`, and `NatalInterpretationService`.
- Runtime evidence:
  - `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`.
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
- Secondary evidence:
  - `AST guard` or targeted `rg` scan over backend natal generation files.
- Static scans alone are not sufficient for this story because:
  - The service must prove that invalid readings are rejected and not exposed as public interpretations.

## Contract Shape

- Contract type:
  - Backend public narrative payload `narrative_natal_reading_v1`.
- Fields:
  - `editorial_profile`: one of `free`, `basic`, `premium`.
  - `chapters`: exactly five chapter objects.
  - `used_astrological_elements`: non-empty for Basic/Premium accepted readings.
- Required chapter keys:
  - `personality`, `emotional_world`, `relationships`, `vocation`, `evolution_path`.
- Required fields:
  - `editorial_profile`, `chapters`, `used_astrological_elements`.
- Optional fields:
  - none for this story delta.
- Status codes:
  - unchanged; this story changes backend acceptance before public exposure, not route status codes.
- Serialization names:
  - `narrative_natal_reading_v1`, `chapters`, and `used_astrological_elements` keep their existing JSON names.
- Required source semantics:
  - Basic/Premium accepted readings contain at least one vulgarized astrological source.
- Invalid conditions:
  - Missing required chapter source, duplicated normalized narrative, duplicated normalized title, empty Basic/Premium sources.
- Frontend type impact:
  - none.
- Generated contract impact:
  - no generated API client or OpenAPI path is changed.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/semantic-integrity-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/semantic-integrity-after.txt`
- Expected invariant:
  - The only intended behavior delta is rejection of incomplete, duplicated or empty-source Basic/Premium `complete` readings.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chapter source selection | `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` | API routers or frontend code |
| Semantic integrity checks | `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` | UI components or DB models |
| Public text validation | `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` | Prompt schema definitions |
| Rejection persistence | `backend/app/services/llm_generation/natal/interpretation_service.py` | Public response serializers |
| Contract documentation | `backend/docs/narrative-natal-reading-v1-contract.md` | Story-only notes |

## Mandatory Reuse / DRY Constraints

- Reuse `NARRATIVE_CHAPTER_ORDER` as the single source for chapter order.
- Reuse the existing rejection/audit workflow instead of creating a second persistence path.
- Reuse existing Pydantic schemas for `NarrativeNatalReadingV1` and chapter models.
- Keep normalization logic centralized in one helper to avoid divergent duplicate checks.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy source-padding route may remain for this projection.
- No compatibility builder path may preserve missing chapter completion.
- No fallback section copy may fill a required chapter.
- Do not add a generic chapter, shim, alias, broad allowlist, or hidden residual path.
- Forbidden symbol: `response.sections[0]` inside `backend/app/services/llm_generation/natal`.
- Forbidden behavior: accepted Basic/Premium `complete` reading with duplicate normalized chapter narrative.
- Forbidden behavior: accepted Basic/Premium `complete` reading with empty `used_astrological_elements`.

## Removal Classification Rules

- `canonical-active`: current canonical builder, validator, semantic helper, service and docs surfaces listed in ownership routing.
- `historical-facade`: any code path that copies the first LLM section solely to complete a missing required chapter.
- `dead`: tests or fixtures that assert padded chapter acceptance after the canonical rejection path exists.
- `external-active`: no known external consumer is authorized by this story to keep padded readings public.
- `needs-user-decision`: persisted historical padded readings require a separate remediation decision outside this story.

## Removal Audit Format

The implementation must record the removal audit in:
`_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/removal-audit.md`.

Allowed decisions for audit rows: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `response.sections[0]` padding | symbol | historical-facade | builder only | explicit projection error | delete | `rg` scan | silent bad readings |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Required chapter resolution | `narrative_natal_reading_builder.py` | prompt schemas, frontend |
| Duplicate semantics | `narrative_semantic_integrity.py` | public serializer, UI |
| Audit-only rejection | `interpretation_service.py` and repository boundary | public interpretation rows |
| Contract wording | `backend/docs/narrative-natal-reading-v1-contract.md` | brief-only documentation |

## Delete-Only Rule

- A removable source-padding symbol must be deleted, not repointed.
- Do not preserve a wrapper that returns another chapter source.
- Do not replace deletion with a soft-disable flag.
- Do not preserve an old path through re-export or alias.

## External Usage Blocker

- External usage blocker: cleared for the builder symbol after bounded repository scans.
- Required proof: `rg -n "response\\.sections\\[0\\]" backend/app backend/tests backend/docs`.
- Any `external-active` consumer must not be deleted without explicit user decision and recorded risk.
- Reason: the removed item is internal Python projection code, not a public route, generated client, webhook, email template or documented API.
- User-decision blocker: historical padded readings may require CS-398 remediation and must not be solved in this story.

## Generated Contract Check

- Generated contract check: required
- Required proof: `rg -n "response\\.sections\\[0\\]|used_astrological_elements" backend/docs backend/app/domain/llm/prompting`.
- Expected result: generated or documented public contracts keep `used_astrological_elements` and never document source padding.

## Reintroduction Guard

- Guard source:
  - `rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal`.
- Architecture guard required:
  - Add or update a deterministic backend architecture guard that fails if `response.sections[0]` is reintroduced.
  - The guard must be an architecture guard against reintroduction of source padding.
- Architecture guard against reintroduction:
  - `backend/tests/architecture/test_narrative_semantic_integrity_guard.py` must fail on the forbidden padding symbol.
- Deterministic source:
  - forbidden symbols.
- Runtime guard:
  - `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`.
- Public boundary guard:
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
- Forbidden reintroduction:
  - any source-padding code path that converts missing chapter source into accepted public chapter content.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-150 | Rejected natal payloads stay outside public POST/GET/LIST surfaces. | `pytest` integration public boundary. |
| RG-152 | Accepted `narrative_natal_reading_v1` remains public-safe. | `pytest` unit validator coverage. |
| RG-155 | Padding, duplicates and empty sources stay forbidden. | `pytest` unit coverage; targeted `rg`. |
| RG-041 | Non-applicable example: entitlement docs are out of scope. | Manual check: no entitlement file is listed. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/semantic-integrity-before.txt` | Record initial scan and test baseline. |
| Baseline after | `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/semantic-integrity-after.txt` | Record final scan and targeted tests. |
| Removal audit | `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/removal-audit.md` | Record classified removed symbol and proof. |
| Validation output | `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/validation.txt` | Keep final lint and test command output. |
| Review output | `_condamad/stories/CS-401-refuser-padding-sources-vides/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No allowlist entry is authorized for semantic padding, duplicated chapters or empty sources. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - reject missing chapter sources.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - enforce public integrity before exposure.
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - centralize semantic integrity checks.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - route projection failures to rejected audit flow.
- `backend/docs/narrative-natal-reading-v1-contract.md` - document accepted versus rejected reading contract.
- `_condamad/stories/CS-401-refuser-padding-sources-vides/evidence/**` - persist proof artifacts.

Likely tests:

- `backend/tests/unit/test_narrative_natal_reading_v1.py` - cover builder, validator, duplicates, empty sources and nominal fixtures.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - cover audit-only rejection visibility.
- `backend/tests/architecture/test_narrative_semantic_integrity_guard.py` - fail on forbidden source-padding reintroduction.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/domain/astrology/**` - out of scope; no astrology calculation is changed.
- `backend/app/api/**` - out of scope unless an existing public-boundary test reveals a direct routing defect.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py`
- VC6: `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- VC7: `rg -n "response\\.sections\\[0\\]" app/services/llm_generation/natal`
- VC8: `rg -n "fallback = response\\.sections\\[0\\]" app/services/llm_generation/natal`
- VC9: `rg -n "padding|used_astrological_elements" docs/narrative-natal-reading-v1-contract.md`
- VC10: `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Regression Risks

- Existing padded readings may become invalid and require the separate CS-398 remediation path.
- A too-broad scan can flag comments or evidence text; bounded production paths must drive the blocking guard.
- Rejecting a provider response before persistence may alter user-facing generation outcomes, but this is the intended contract delta.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.

## References

- `_story_briefs/cs-396-refuser-padding-semantique-lecture-natale-et-sources-vides.md`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-155`
- `backend/docs/narrative-natal-reading-v1-contract.md`
