# Story CS-420 adapter-page-natal-rendu-free-basic-v2: Adapter Page Natal Au Rendu Free Et Basic V2
Status: ready-to-dev

## Trigger / Source
- Source brief: `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md`.
- Selected mode: Repo-informed story.
- Fast Story Writer Mode: active; cheatsheet consulted before broad references.
- Source dependency: CS-419 defines the backend public contract consumed by this frontend story.
- Bounded problem: `/natal` classifies a valid free short payload as a complete reading to regenerate.
- Source-alignment evidence: objective, stakes, ACs, tasks, validations, non-goals and guardrails map to the brief without scope drift.

## Objective
Adapt the React `/natal` interpretation rendering to display valid free short and Basic V2 public readings from the backend contracts.

## Target State
- Free short payloads render the public title, summary, sections, highlights, advice and disclaimers from `AstroFreeResponseV1`.
- Basic complete V2 payloads render title, introduction, themes, conclusion, public evidence, limitations and disclaimers.
- `basic_natal_interpretation_v2` is carried through frontend API types and `NatalInterpretationViewData`.
- `narrative_natal_reading_v1` keeps the existing `NatalNarrativeReading` rendering when present.
- Complete readings without `narrative_natal_reading_v1` or `basic_natal_interpretation_v2` keep the regeneration message.
- Public Basic V2 evidence renders only `label` and `meaning`.
- Technical markers, raw theme keys, hidden attributes and public DOM labels stay out of `/natal`.
- New presentation styles live in existing CSS surfaces and reuse existing design tokens first.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md` - source brief read for this story.
- Evidence 2: `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md` - upstream contract brief read.
- Evidence 3: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-420` after existing `CS-419`.
- Evidence 4: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract applied.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-153`, `RG-154`, `RG-158` and `RG-168` checked.
- Evidence 6: `frontend/src/api/natal-chart/index.ts` - free short types exist while Basic V2 fields are not yet exposed.
- Evidence 7: `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - view data carries `narrative_natal_reading_v1`.
- Evidence 8: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - current branch includes `ni-content-card--missing-narrative`.
- Evidence 9: required frontend roots `frontend`, `frontend/src`, `frontend/src/tests` and `frontend/src/styles` exist.
- Evidence 10: guardrail resolver ran for frontend natal scope; exact brief guardrails were selected after targeted registry search.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `/natal` | in scope | AC1 through AC10, validation plan |
| `AstroFreeResponseV1` | in scope | AC1, AC2, AC3, tasks |
| `basic_natal_interpretation_v2` | in scope | AC4, AC5, AC6, AC7, tasks |
| `BasicNatalInterpretationV2` | in scope | AC4, AC5, Contract Shape |
| `NatalInterpretationViewData` | in scope | AC4, tasks |
| `NatalInterpretationContent` | in scope | AC1 through AC7, tasks |
| Basic V2 presentation component | in scope | AC5, AC6, tasks |
| `NatalNarrativeReading` | constrained surface | AC8 |
| regeneration message | constrained surface | AC3, AC7 |
| public evidence `label` and `meaning` | in scope | AC6 |
| DOM technical denylist | forbidden surface | AC9, Reintroduction Guard |
| inline style | forbidden surface | AC10, Reintroduction Guard |
| backend pipeline and quotas | out of scope | Non-goals |

## Domain Boundary
- Domain: frontend-natal
- In scope:
  - React rendering and frontend TypeScript contracts for `/natal` interpretation content.
  - Presentational Basic V2 rendering under existing natal interpretation UI ownership.
  - Vitest, DOM guard, lint, build and targeted scans for the touched frontend surfaces.
- Out of scope:
  - Backend API, database schema, auth, i18n catalog rewrites, business quotas, provider calls and migrations.
  - Full `/natal` page redesign, commercial offer changes and unrelated style refactors.
- Explicit non-goals:
  - No backend serializer, API route, persistence or quota change.
  - No old factual card restoration.
  - No inline style introduction.
  - No broad page redesign beyond rendering the public interpretation contracts.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this frontend public rendering contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only `/natal` interpretation data typing, branch selection, presentational rendering, CSS and tests.
  - Preserve existing `NatalNarrativeReading` behavior when `narrative_natal_reading_v1` is present.
  - Keep the regeneration message only for complete readings with no modern public contract.
  - Keep frontend API consumption on the existing `/v1/natal/interpretation` response.
- Additional validation rules:
  - `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` proves branch rendering.
  - `AST guard` and targeted `rg` scans prove no inline style or forbidden public DOM marker is introduced.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: the backend response omits every public free short and Basic V2 field required by CS-419.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest rendering tests and Browser QA prove the user-visible `/natal` branch behavior. |
| Baseline Snapshot | yes | DOM before and after artifacts prove the intended visible rendering delta. |
| Ownership Routing | yes | API types, view data, render selection and CSS must stay in canonical frontend owners. |
| Allowlist Exception | no | No allowlist handling is authorized for DOM leaks or inline styles. |
| Contract Shape | yes | Free short and Basic V2 frontend shapes must be explicit TypeScript contracts. |
| Batch Migration | no | No batch migration or data conversion is in scope. |
| Reintroduction Guard | yes | Factual cards, technical markers, raw evidence IDs and inline styles must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Free short renders its primary public reading. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC2 | Free short renders its supporting public blocks. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC3 | Free short never renders the regeneration message. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC4 | Frontend types expose Basic V2 on interpretation data. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend build`. |
| AC5 | Basic V2 renders its public reading structure. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC6 | Basic V2 evidence renders only public labels. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC7 | Complete legacy keeps the regeneration message. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC8 | Narrative v1 keeps accessible accordions. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading NatalChartPage`. |
| AC9 | Public DOM excludes technical markers. | Evidence: `natalPublicDomGuard`; `rg` VC5. |
| AC10 | Touched TSX surfaces do not add inline styles. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "style=\\{"` VC3. |

## Implementation Tasks
- [ ] Task 1: Add frontend TypeScript types for `BasicNatalInterpretationV2` public sub-objects. (AC: AC4)
- [ ] Task 2: Carry `basic_natal_interpretation_v2` through API response and `NatalInterpretationViewData`. (AC: AC4)
- [ ] Task 3: Implement explicit branch selection in `NatalInterpretationContent`. (AC: AC1, AC3, AC5, AC7, AC8)
- [ ] Task 4: Render free short sections, highlights, advice and disclaimers in simple public blocks. (AC: AC1, AC2, AC9, AC10)
- [ ] Task 5: Add reusable Basic V2 presentational rendering with centralized CSS classes. (AC: AC5, AC6, AC10)
- [ ] Task 6: Preserve `NatalNarrativeReading` rendering when `narrative_natal_reading_v1` exists. (AC: AC8)
- [ ] Task 7: Extend Vitest fixtures for free short, Basic V2, narrative v1 and complete legacy branches. (AC: AC1, AC2, AC3, AC5, AC7, AC8)
- [ ] Task 8: Extend public DOM guard tests for attributes, hidden content and Basic V2 evidence labels. (AC: AC6, AC9)
- [ ] Task 9: Run lint, build, targeted scans and Browser QA on `/natal`. (AC: AC4, AC9, AC10)
- [ ] Task 10: Persist validation and QA evidence artifacts for review handoff. (AC: AC1, AC4, AC9, AC10)

## Files to Inspect First
- `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md` - source contract.
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md` - backend contract dependency.
- `_condamad/stories/regression-guardrails.md` - local guardrails `RG-153`, `RG-154`, `RG-158`, `RG-168`.
- `frontend/src/api/natal-chart/index.ts` - API response and public interpretation types.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - view data contract.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - branch selection and public content rendering.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - page integration owner.
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - narrative v1 branch to preserve.
- `frontend/src/features/natal-chart/NatalReadingSources.tsx` - public sources rendering constraints.
- `frontend/src/tests/natalInterpretation.test.tsx` - component rendering coverage.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - DOM leak guard coverage.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level integration coverage.
- `frontend/src/styles` - existing tokens and `ni-*` style surfaces.

## Runtime Source of Truth
- Primary source of truth:
  - Vitest with Testing Library for rendered `/natal` interpretation branches.
  - Browser QA on `/natal` using the configured test user.
  - `AST guard` for touched TSX surfaces through targeted source scans.
- Secondary evidence:
  - `pnpm --dir frontend build` for TypeScript contract coverage.
  - Targeted `rg` scans for forbidden DOM markers and inline style syntax.
- Static scans alone are not sufficient for this story because:
  - Branch selection must be proven through rendered DOM behavior.

## Contract Shape
- Contract type:
  - Frontend TypeScript public response and rendered DOM contract.
- Fields:
  - `interpretation`: carries free short public content for `AstroFreeResponseV1`.
  - `basic_natal_interpretation_v2`: carries Basic V2 public content.
  - `narrative_natal_reading_v1`: carries the existing narrative v1 public content.
- Free short fields:
  - `title`: rendered as public title text.
  - `summary`: rendered as public summary text.
  - `sections`: rendered as public section blocks.
  - `highlights`: rendered as public highlight list.
  - `advice`: rendered as public advice list.
  - `disclaimers`: rendered as public disclaimer text.
- Basic V2 fields:
  - `title`: rendered as Basic V2 title.
  - `introduction`: rendered as public introduction.
  - `themes`: rendered with public narrative content.
  - `conclusion`: rendered as public conclusion.
  - `public_evidence`: rendered through `label` and `meaning`.
  - `limitations`: rendered only as public limitations text.
  - `disclaimers`: rendered as public disclaimer text.
- Required fields:
  - Free short requires public `title`, `summary` and `sections`.
  - Basic V2 requires public `title`, `introduction`, `themes` and `conclusion`.
- Optional fields:
  - Free short `highlights`, `advice` and `disclaimers`.
  - Basic V2 `public_evidence`, `limitations` and `disclaimers`.
- Status codes:
  - none; HTTP behavior belongs to CS-419.
- Serialization names:
  - `basic_natal_interpretation_v2` is carried as `basic_natal_interpretation_v2`.
  - `narrative_natal_reading_v1` is carried as `narrative_natal_reading_v1`.
- Frontend type impact:
  - API and view data types must compile under `pnpm --dir frontend build`.
- Generated contract impact:
  - none; no generated client update is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/dom-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/dom-after.md`
- Expected invariant:
  - The only intended UI behavior delta is that valid free short and Basic V2 public readings render their public content.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| API response types | `frontend/src/api/natal-chart/index.ts` | Component-local duplicate backend contracts |
| View data contract | `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` | Untyped object casts in render code |
| Branch rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Page-level ad hoc conditionals |
| Narrative v1 rendering | `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` | New duplicate narrative renderer |
| Natal interpretation styles | Existing `frontend/src/styles` or existing `ni-*` stylesheet | Inline `style` props |

## Mandatory Reuse / DRY Constraints
- Reuse existing `AstroFreeResponseV1` frontend shape instead of duplicating free short field definitions.
- Reuse `NatalNarrativeReading` for `narrative_natal_reading_v1`; do not clone its accordion behavior.
- Reuse existing `ni-*` class naming and CSS variables before adding new `ni-basic-*` classes.
- Keep branch selection in one explicit helper or compact decision block owned by `NatalInterpretationContent`.
- Do not create separate renderers that duplicate title, disclaimer or list markup without a shared small presentational helper.

## No Legacy / Forbidden Paths
- No legacy factual card component may be reintroduced into `/natal` public interpretation rendering.
- No compatibility route, hidden fallback branch or alias renderer may classify free short as complete obsolete content.
- No fallback UI may expose `.ni-evidence-tags`, `.ni-projections` or locked-section style technical summaries.
- No raw technical field may be rendered in text, `title`, `aria-label`, test ID, hidden content or tooltip.
- No inline style may be added to touched TSX surfaces.

## Reintroduction Guard
- Forbidden component symbols:
  - `LockedSection`, `NatalAstrologicalDna`, `NatalLifeDomains`, `NatalStrengths`, `NatalChallenges`, `NatalMajorAspects`.
- Forbidden public DOM markers:
  - `visibility_expression`, `audit_input`, `condition_axis:`, `interpretive_signal_ids`, `projection_version`, `ranking_score`, `weighted_score`.
- Forbidden style syntax:
  - `style={` in touched natal interpretation TSX surfaces.
- Required deterministic guard:
  - `pnpm --dir frontend test -- natalPublicDomGuard`.
  - Targeted `rg` scans VC3, VC4 and VC5 in the validation plan.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-153 | `/natal` composition -> no factual legacy cards -> `pnpm --dir frontend test -- NatalChartPage`; `rg` VC4. |
| RG-154 | public DOM -> no technical markers or legacy fallback UI -> `pnpm --dir frontend test -- natalPublicDomGuard`; `rg` VC5. |
| RG-158 | narrative v1 -> accessible modern accordions remain -> `pnpm --dir frontend test -- natalNarrativeReading NatalChartPage`. |
| RG-168 | Basic V2 contract -> canonical public Basic payload drives rendering -> `pnpm --dir frontend test -- natalInterpretation`; build VC2. |

Needs-investigation and registry gap:
- The resolver returned broad frontend IDs unrelated to `/natal`; targeted registry IDs above are used because they exactly match the brief scope.

Non-applicable examples:
- Backend DB, migration and auth guardrails are out of scope because this story changes only React rendering and frontend contracts.
- Backend provider or LLM guardrails are out of scope because CS-419 owns the backend public contract.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| DOM before | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/dom-before.md` | Capture the current misclassified free short branch. |
| DOM after | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/dom-after.md` | Capture final public rendering. |
| Validation output | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/validation.txt` | Keep lint, build, tests and scans output. |
| Browser QA | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/browser-qa.md` | Record `/natal` QA with the test user. |
| Review output | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/generated/11-code-review.md` | Keep separate review evidence. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for public DOM leaks, old factual cards or inline style syntax.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-file data conversion is in scope.

## Expected Files to Modify
Likely files:

- `frontend/src/api/natal-chart/index.ts` - add Basic V2 public TypeScript response types.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - carry Basic V2 into view data.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - implement explicit render branches.
- `frontend/src/components/natal-interpretation/NatalBasicInterpretationV2.tsx` - expected reusable Basic V2 presentational component.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - pass through Basic V2 data only through existing integration points.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover free short, Basic V2 and complete legacy rendering.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - extend DOM leak guards.
- `frontend/src/tests/NatalChartPage.test.tsx` - preserve page-level branch coverage.
- Existing `frontend/src/styles` natal stylesheet - add centralized `ni-*` classes for new public blocks.
- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/validation.txt` - persist validation output.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - branch rendering fixtures and assertions.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - technical marker and attribute guards.
- `frontend/src/tests/NatalChartPage.test.tsx` - page integration non-regression.
- `frontend/src/tests/natalNarrativeReading.test.tsx` - narrative accordion preservation.

Files not expected to change:

- `backend/**` - out of scope; CS-419 owns backend contract behavior.
- `frontend/src/api/**` outside `frontend/src/api/natal-chart/index.ts` - out of scope.
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - inspect and preserve unless test repair proves a narrow edit.
- `frontend/src/features/natal-chart/NatalReadingSources.tsx` - inspect and preserve unless public evidence routing requires a narrow edit.
- `.env`, `.venv`, `node_modules` and build output directories - never edit.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`
- VC2: `pnpm --dir frontend lint`
- VC3: `pnpm --dir frontend build`
- VC4: `rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
- VC4 scope note: forbidden pattern `style=\\{`; allowed fixture pattern none; roots are touched TSX surfaces; expected false positives none.
- VC5: old factual and fallback UI scan.
  - Command:
    ```powershell
    rg -n `
      "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" `
      frontend/src/components/natal-interpretation `
      frontend/src/features/natal-chart `
      frontend/src/pages/NatalChartPage.tsx
    ```
- VC5 scope note: forbidden pattern is old factual or fallback UI symbols; allowed fixture pattern none; expected false positives none.
- VC6: technical marker scan.
  - Command:
    ```powershell
    rg -n `
      "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" `
      frontend/src/components/natal-interpretation `
      frontend/src/features/natal-chart
    ```
- VC6 scope note: forbidden pattern is technical public DOM markers; allowed fixture pattern none in production roots; expected false positives none.
- VC7: Manual check: start the local app, log in as `daconrilcy@hotmail.com`, open `/natal`, verify free short content renders without regeneration copy.
- VC8: Manual check: record Browser QA in `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/browser-qa.md`.

## Regression Risks
- Free short may remain hidden behind the complete-reading regeneration condition.
- Basic V2 may render raw theme keys or internal evidence IDs instead of public labels.
- New Basic V2 markup may duplicate narrative v1 rendering instead of preserving the existing component boundary.
- DOM guard fixtures may miss hidden content, `title` attributes or `aria-label` leaks.
- CSS additions may bypass existing variables or introduce inline styles.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep markdown evidence artifacts concise and store full command output in `evidence/validation.txt`.
- Use the existing frontend stack and do not touch backend files for this story.
- Preserve CS-419 backend contract assumptions; frontend must consume the public contract without heuristic field invention.

## References
- `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md`
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
