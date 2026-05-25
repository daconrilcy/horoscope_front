# Astrology Disclaimer Projection Policy Audit

## Audit Target

- Domain key: `astrology-disclaimer-projection-policy`
- Archetype: custom contract-shape / service-boundary audit
- Story audited: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md`
- Brief source: `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md`
- Read-only mode: application code, migrations, routes, frontend and tests were not modified.
- Domain closure status: `open`

## Scope

In scope:

- Existing astrology disclaimer inventory across backend, frontend and docs.
- Static disclaimer ownership and injection points.
- B2C free/basic/premium projection policy readiness.
- LLM disclaimer authorship boundary.
- Degraded mode and missing birth time disclaimer coverage.
- Public API and application-surface neutrality evidence.

Out of scope:

- Implementing CS-284 as code or documentation under `docs/architecture`.
- Refactoring guidance, natal, API, frontend, DB or prompt code.
- Creating routes, UI, migrations, generated clients or legal doctrine.

## Closure Analysis

Prior audit folders consulted: none for this exact domain. `E-004` found no older same-domain folder under `_condamad/audits/astrology-disclaimer-projection-policy/` before `2026-05-25-0306`.

Related stories consulted:

- `CS-257-beginner-summary-v1-b2c-projection` for `beginner_summary_v1` and degraded/no-time terminology.
- `CS-258-client-interpretation-projection-v1-by-plan` for free/basic/premium interpretation projection terminology.
- `CS-283-b2c-projection-entitlement-policy` for B2C projection plan policy.
- `CS-286` and `CS-287` as downstream stories that depend on CS-284 disclaimer references.

Prior findings classification:

- No previous same-domain findings were found.
- CS-284 story status is `ready-to-dev`, not implemented; current evidence classifies its expected policy deliverables as absent.

Active findings after current evidence:

- `F-001`: open; canonical policy and evidence artifacts are absent.
- `F-002`: deferred non-domain runtime risk; guidance can preserve LLM-authored disclaimer text, but changing guidance code is outside the documentation-only CS-284 audit/policy scope.
- `F-003`: open; degraded/no-time states are not mapped to static disclaimer attachment.
- `F-004`: closed observation; API neutrality currently holds and does not require an implementation story.

Closed findings and guardrail IDs:

- None. No new regression guardrail was added because the audit did not discover a durable invariant already enforced by a complete CS-284 implementation. Candidate guards are listed in `03-story-candidates.md`.

Deferred non-domain context:

- Existing unrelated dirty worktree entries under backend, docs, tests and migrations are not attributed to this audit. See `E-015`.
- Broader legal policy wording remains product/legal decision scope if new disclaimer text is requested.
- Runtime guidance convergence for `backend/app/services/llm_generation/guidance/guidance_service.py` remains a follow-up service-boundary concern after CS-284 defines the canonical disclaimer owner; it must not be implemented by the CS-284 documentation-only story.

## Findings Summary

- High: 2
- Medium: 1
- Info: 1
- Story candidates: 2

The most important issue is ownership: a static natal disclaimer registry exists and is used, but the CS-284 projection policy does not yet exist. Guidance also has a direct LLM-output disclaimer path; this is relevant evidence for the policy boundary, but its runtime correction is deferred outside the CS-284 documentation-only scope.

## DRY, No Legacy, Mono-Domain And Dependency Direction

DRY:

- `backend/app/services/resources/templates/disclaimer_registry.py` is the canonical static disclaimer source for natal and PDF paths (`E-006`, `E-007`).
- `guidance_service.py` contains an active alternate disclaimer source by accepting LLM structured fields (`E-009`), creating duplicate responsibility risk.

No Legacy:

- No compatibility policy document, route alias, shim or public disclaimer route was found for `astrology_disclaimer_projection_policy` (`E-004`, `E-013`).
- Legacy prompt seed surfaces still mention older disclaimer generation requirements (`E-012`); they are classified as out-of-domain historical/bootstrap context unless a future prompt governance audit targets them.

Mono-domain ownership:

- Static disclaimer text currently belongs to the backend services resources registry.
- Projection policy ownership is missing and should live in a single documentation/evidence owner, not in API routers, prompt templates, frontend copy or provider responses.

Dependency direction:

- Natal API/service paths consume registry text in the allowed direction (`E-007`, `E-008`).
- Guidance output path depends on LLM-produced disclaimer fields before fallback, which violates the desired authorship direction (`E-009`).

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/services/resources/templates/disclaimer_registry.py` | used | E-006, E-007 | Canonical static localized disclaimer registry consumed by natal route, natal service and PDF export. | Usage is proven for current repository consumers, not external packages. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | used | E-007, E-008 | Injects static registry disclaimers into natal cached/generated/free_short/formatted responses and tracks degraded mode. | Audit did not execute every natal runtime branch. |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | used | E-007, E-012 | Public natal route applies registry disclaimers to responses. | Route behavior was inspected by source scan, not by endpoint call. |
| `backend/app/services/natal/pdf_export_service.py` | used | E-007, E-012 | PDF export consumes registry disclaimers. | PDF rendering was not executed. |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | used | E-009, E-012 | Guidance service owns daily/contextual guidance responses and current disclaimer field population. | Audit did not change or execute guidance flows beyond existing tests evidence. |
| `backend/app/services/llm_generation/shared/natal_context.py` | used | E-010 | Shared owner of degraded natal mode values `no_time`, `no_location`, `no_location_no_time`. | It owns mode terminology, not disclaimer attachment. |
| `backend/app/services/api_contracts/public/natal_interpretation.py` | used | E-012 | Public response contract includes API-level `disclaimers`. | Contract impact was scanned only for disclaimer fields. |
| `backend/app/domain/llm/runtime/output_validator.py` | used | E-012 | Strips V3 `disclaimers`, supporting application-level disclaimer injection for one LLM schema path. | Applies to V3 normalization only. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | needs-user-decision | E-012 | Registry still declares `disclaimers` required in one schema area; decide whether this remains historical, LLM contract, or should converge. | Full prompt/use-case governance is outside this audit. |
| `backend/app/domain/llm/prompting/schemas.py` | needs-user-decision | E-012 | Older schema versions include disclaimer fields while V3 excludes them; retention requires explicit compatibility decision. | Schema removal cannot be decided from disclaimer policy alone. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | out-of-domain | E-012 | Bootstrap prompt text states V3 disclaimers are application-managed. | Prompt seed governance is separate from B2C projection policy. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | out-of-domain | E-012 | Historical seed text asks LLM for disclaimers and may be legacy prompt context. | Needs prompt-generation audit before deletion or rewrite recommendation. |
| `frontend/src/api/natal-chart/index.ts` | used | E-012 | Frontend consumes API-level natal `disclaimers` and maps them into data when needed. | Frontend rendering behavior was not browser-tested. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | used | E-012 | Renders natal disclaimer list from API data. | UI was not modified or visually tested. |
| `frontend/src/api/guidance.ts` | used | E-012 | Types guidance `disclaimer` field consumed by guidance UI/state. | Does not prove disclaimer source ownership. |
| `frontend/src/pages/ConsultationResultPage.tsx` | used | E-012 | Displays consultation/guidance disclaimer string. | Source of text is backend response. |
| `docs/architecture/official-product-primitives-public-projections.md` | used | E-011 | Canonical public projection registry, but not yet aligned to CS-284 disclaimer policy. | File has unrelated pre-existing modifications in worktree. |
| `docs/architecture/b2c-projection-entitlement-policy.md` | used | E-011 | Existing B2C plan matrix mentions disclaimers for `beginner_summary_v1`. | File is untracked/pre-existing in current worktree. |
| `docs/architecture/beginner-summary-v1-contract.md` | used | E-010 | Documents no-time degraded behavior for beginner projection. | File is untracked/pre-existing in current worktree. |
| `docs/architecture/astrology-disclaimer-projection-policy.md` | needs-user-decision | E-001, E-005 | Expected CS-284 policy owner is absent; create it as documentation-only or block dependent stories. | Missing file, so no source content can be classified as used. |
| `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md` | used | E-001 | Governing story contract for the audit. | Story is not implementation evidence. |
| `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md` | used | E-002 | Source brief for audit alignment. | Brief is not implementation evidence. |
| `_condamad/stories/regression-guardrails.md` | used | E-003 | Required registry consulted before findings. | No exact CS-284 guardrail exists yet. |

## Exhaustive Active Implementation Surface

For `F-001`, application files to modify: none. Governance/docs/evidence surfaces: `docs/architecture/astrology-disclaimer-projection-policy.md`, `docs/architecture/official-product-primitives-public-projections.md`, CS-284 evidence folder.

For `F-003`, application files to modify: none unless product chooses runtime behavior now. Governance/docs/evidence surfaces: CS-284 policy and inventory artifacts; optional future runtime tests when a projection builder is implemented.

Deferred non-domain implementation surface for `F-002`: `backend/app/services/llm_generation/guidance/guidance_service.py`; tests likely under `backend/app/tests/unit/test_guidance_service.py` and `backend/app/tests/integration/test_guidance_api.py`. This surface belongs to a future guidance service-boundary story, not to CS-284.

## Validation Notes

Python commands were run only after activating `.\.venv\Scripts\Activate.ps1`. The first attempted runtime check with `python -S` could not import FastAPI because `-S` disables site packages; it was not used as final evidence. The successful runtime check used activated venv Python without `-S` and is recorded as `E-013`. Skill artifact validation commands are recorded after report generation.
