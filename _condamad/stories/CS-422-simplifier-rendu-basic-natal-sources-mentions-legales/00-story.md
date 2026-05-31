# Story CS-422 simplifier-rendu-basic-natal-sources-mentions-legales: Simplifier Rendu Basic Natal Sources Et Mentions Legales
Status: ready-to-dev

## Trigger / Source
- Source brief: `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md`.
- Selected mode: Repo-informed story.
- Fast Story Writer Mode: active; cheatsheet consulted before broad references.
- Source dependencies: CS-420 defines the frontend Basic V2 branch; CS-421 improves the Basic editorial payload.
- Bounded problem: `/natal` repeats Basic V2 sources inside themes, repeats sources near the end, then shows two legal areas.
- Source-alignment evidence: objective, stakes, ACs, tasks, validations, non-goals and guardrails map to the brief without scope drift.

## Objective
Simplify the React `/natal` Basic V2 rendering so the public reading is a continuous report with one source appendix and one legal area.

## Target State
- Basic V2 renders `title`, `introduction`, `themes` and `conclusion` as the main report, in that order.
- Public evidence is not rendered inside each Basic V2 theme.
- Public evidence is rendered once after the conclusion as a compact appendix.
- Duplicate evidence is merged with a stable key based on `source_id` or normalized public fields.
- Evidence used by several themes keeps compact usage metadata without duplicating the appendix item.
- Basic limitations, Basic disclaimers and global legal lines render once in one final Basic V2 legal area.
- Free short, `narrative_natal_reading_v1` and complete obsolete rendering keep their existing legal behavior.
- Public DOM guards prove source repetition, legal-title repetition, technical markers and inline styles stay controlled.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md` - source brief read for this story.
- Evidence 2: `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md` - upstream frontend Basic V2 rendering brief read.
- Evidence 3: `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md` - upstream Basic editorial contract brief read.
- Evidence 4: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-422` after existing `CS-421`.
- Evidence 5: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract applied.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-048`, `RG-073`, `RG-153`, `RG-154`, `RG-158`, `RG-168` and new `RG-170` checked.
- Evidence 7: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` renders `PublicEvidenceList` inside each Basic V2 theme.
- Evidence 8: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` renders Basic limitations, Basic disclaimers and a global legal footer.
- Evidence 9: `frontend/src/features/natal-chart/NatalReadingSources.tsx` already owns an accessible compact source pattern for narrative readings.
- Evidence 10: `frontend/src/tests/natalPublicDomGuard.test.tsx` already guards public DOM technical markers for `/natal`.
- Evidence 11: required frontend roots `frontend`, `frontend/src`, `frontend/src/tests` and named Basic V2 files exist.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `/natal` | in scope | AC1 through AC11, validation plan |
| `BasicV2Reading` | in scope | AC1 through AC7, tasks |
| `PublicEvidenceList` inside themes | in scope | AC2, AC3, tasks |
| Basic source appendix | in scope | AC3, AC4, AC5, tasks |
| `source_id` evidence key | in scope | AC4, Contract Shape |
| normalized public evidence key | in scope | AC4, Contract Shape |
| `used_in_sections` metadata | in scope | AC5, Contract Shape |
| Basic limitations | in scope | AC6, tasks |
| Basic disclaimers | in scope | AC6, tasks |
| global legal lines | constrained surface | AC6, AC8 |
| free short rendering | constrained surface | AC8 |
| `narrative_natal_reading_v1` | constrained surface | AC9 |
| obsolete legacy rendering | constrained surface | AC8 |
| inline styles | forbidden surface | AC10, Reintroduction Guard |
| technical DOM markers | forbidden surface | AC11, Reintroduction Guard |
| backend contract | out of scope | Non-goals |
| quotas, PDF exports and offers | out of scope | Non-goals |

## Domain Boundary
- Domain: frontend-natal
- In scope:
  - React rendering and frontend tests for the `/natal` Basic V2 public report.
  - Basic V2 evidence deduplication, source appendix placement and compact usage metadata.
  - Basic V2 legal-area merge and deduplication across limitations, disclaimers and global legal lines.
  - Existing CSS surfaces using `ni-*`, `natal-*` classes and existing variables.
  - Vitest, DOM guard, lint, build, targeted scans and bounded responsive QA.
- Out of scope:
  - Backend API, database schema, auth, i18n contract rewrites, quotas, PDF export, offers, provider prompts and migrations.
  - Free short structure changes beyond proving no legal regression.
  - Narrative v1 structure changes beyond proving accordions and sources remain modern.
- Explicit non-goals:
  - No backend serializer, API route, persistence or generated-content change.
  - No public evidence removal from the Basic V2 contract.
  - No old factual card restoration.
  - No inline style introduction.
  - No relocation of `NatalInterpretation` orchestration outside its feature owner.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this frontend public rendering contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only Basic V2 public rendering, Basic V2 source aggregation, Basic V2 legal merge, CSS and tests.
  - Preserve free short rendering, complete obsolete rendering and narrative v1 rendering outside the asserted non-regression checks.
  - Keep frontend API consumption on the existing `/v1/natal/interpretation` response.
  - Keep public evidence visible in a single Basic V2 appendix.
- Additional validation rules:
  - `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` proves rendered DOM behavior.
  - `AST guard` and targeted `rg` scans prove no inline style or forbidden public DOM marker is introduced.
  - Manual responsive QA proves long appendix and legal text blocks do not overlap on desktop or mobile.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: the required Basic V2 evidence fields are absent from the frontend data contract.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest rendering tests and Browser QA prove user-visible `/natal` Basic V2 behavior. |
| Baseline Snapshot | yes | DOM before and after artifacts prove the intended repetition reduction. |
| Ownership Routing | yes | Rendering, source aggregation, legal merge and CSS must stay in canonical frontend owners. |
| Allowlist Exception | no | No allowlist handling is authorized for DOM leaks or inline styles. |
| Contract Shape | yes | Basic V2 rendered DOM and evidence aggregation shape must be explicit. |
| Batch Migration | no | No batch migration or data conversion is in scope. |
| Reintroduction Guard | yes | Inline theme sources, duplicate legal titles, factual cards and technical markers must stay controlled. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic V2 renders report sections in reading order. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC2 | Basic V2 themes do not render inline evidence blocks. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC3 | Basic V2 renders one public source appendix. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC4 | Basic V2 deduplicates repeated evidence entries. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC5 | Shared Basic V2 evidence keeps compact usage metadata. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC6 | Basic V2 renders one final legal area. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC7 | Basic V2 main paragraphs exclude raw source text. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC8 | Free short keeps its existing public rendering. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation NatalChartPage`. |
| AC9 | Narrative v1 keeps accessible modern accordions. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading NatalChartPage`. |
| AC10 | Touched TSX surfaces do not add inline styles. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "style=\\{"` VC4. |
| AC11 | Public DOM excludes technical markers. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC7 and `pnpm --dir frontend test -- natalPublicDomGuard`. |

## Implementation Tasks
- [ ] Task 1: Inspect current Basic V2 rendering, translations, source components, tests and existing `ni-*` CSS. (AC: AC1, AC2, AC6, AC10)
- [ ] Task 2: Remove the inline Basic V2 theme evidence rendering from the public report body. (AC: AC2, AC7)
- [ ] Task 3: Add a small evidence aggregation helper owned by the Basic V2 rendering surface. (AC: AC3, AC4, AC5)
- [ ] Task 4: Render the deduplicated Basic V2 source appendix after the conclusion. (AC: AC3, AC4, AC5)
- [ ] Task 5: Merge Basic limitations, Basic disclaimers and global legal lines into one Basic V2 final legal area. (AC: AC6)
- [ ] Task 6: Keep free short, narrative v1 and complete obsolete branch selection unchanged except for Basic V2 footer handling. (AC: AC8, AC9)
- [ ] Task 7: Add or update CSS in existing stylesheets for compact appendix and legal blocks. (AC: AC10)
- [ ] Task 8: Extend DOM tests with duplicate multi-theme evidence, duplicate legal text and clean Basic V2 payloads. (AC: AC2, AC3, AC4, AC6, AC7)
- [ ] Task 9: Extend non-regression tests for free short, narrative v1 and page-level `/natal` integration. (AC: AC8, AC9)
- [ ] Task 10: Run lint, build, targeted scans and bounded responsive QA. (AC: AC10, AC11)
- [ ] Task 11: Persist validation, scan and QA evidence artifacts for review handoff. (AC: AC1, AC3, AC6, AC10, AC11)

## Files to Inspect First
- `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md` - source brief.
- `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md` - upstream frontend rendering contract.
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md` - upstream Basic editorial dependency.
- `_condamad/stories/regression-guardrails.md` - local guardrails `RG-048`, `RG-073`, `RG-153`, `RG-154`, `RG-158`, `RG-168`.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - Basic V2 branch and legal footer behavior.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - Basic V2 view data shape.
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - narrative v1 branch to preserve.
- `frontend/src/features/natal-chart/NatalReadingSources.tsx` - accessible compact source pattern to reuse conceptually.
- `frontend/src/i18n/natalChart.ts` - public labels for sources, limitations and legal text.
- `frontend/src/tests/natalInterpretation.test.tsx` - component rendering coverage.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - DOM repetition and technical marker guard coverage.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level integration coverage.
- Existing CSS files containing `ni-*`, `natal-*` classes and variables - style owner for new presentation classes.
- `frontend/src/styles/css-fallback-allowlist.md` - consult before touching CSS variable fallback values.

## Runtime Source of Truth
- Primary source of truth:
  - Vitest with Testing Library for rendered `/natal` Basic V2, free short and narrative v1 branches.
  - Browser QA on `/natal` using `daconrilcy@hotmail.com` for desktop and mobile visual checks.
  - `AST guard` through targeted `rg` scans for touched TSX and CSS surfaces.
- Secondary evidence:
  - `pnpm --dir frontend build` for TypeScript contract coverage.
  - Targeted `rg` scans for forbidden DOM markers, old factual cards, inline styles and CSS fallback drift.
- Static scans alone are not sufficient for this story because:
  - Source repetition and legal-title repetition must be proven from rendered DOM behavior.

## Contract Shape
- Contract type:
  - Frontend rendered DOM contract for Basic V2 public reading.
- Fields:
  - `title`: public Basic V2 title.
  - `introduction`: public Basic V2 introduction.
  - `themes`: public Basic V2 narrative sections.
  - `conclusion`: public Basic V2 conclusion.
  - `public_evidence`: public Basic V2 source entries.
  - `limitations`: public Basic V2 limitations.
  - `disclaimers`: public Basic V2 legal notices.
- Basic V2 report order:
  - `title`: rendered before the report body.
  - `introduction`: rendered before themes.
  - `themes`: rendered as main narrative sections without inline evidence blocks.
  - `conclusion`: rendered before the source appendix.
- Basic V2 source appendix:
  - Uses public evidence from reading-level and theme-level evidence inputs.
  - Deduplication key uses `source_id` when available.
  - Deduplication key falls back to normalized `label`, `meaning` and `source_type`.
  - Shared usage is represented with `used_in_sections` or an equivalent compact public metadata field.
- Basic V2 legal area:
  - Combines Basic `limitations`, Basic `disclaimers` and global legal notice lines.
  - Deduplicates repeated lines by normalized public text.
  - Renders one public legal title for the Basic V2 branch.
- Required fields:
  - Basic V2 requires existing public `title`, `introduction`, `themes` and `conclusion`.
- Optional fields:
  - `public_evidence`, `limitations`, `disclaimers`, `used_in_sections` or equivalent compact usage metadata.
- Status codes:
  - none; HTTP behavior is out of scope.
- Serialization names:
  - `basic_natal_interpretation_v2` remains `basic_natal_interpretation_v2`.
- Frontend type impact:
  - Touched TypeScript must compile under `pnpm --dir frontend build`.
- Generated contract impact:
  - none; no generated client update is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/dom-basic-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/dom-basic-after.md`
- Expected invariant:
  - The only intended Basic V2 UI delta is fewer repeated source and legal blocks while public evidence and disclaimers remain visible.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic V2 branch rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Page-level ad hoc conditionals |
| Basic V2 view data shape | `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` | Untyped casts in render code |
| Narrative v1 rendering | `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` | Duplicate Basic renderer or narrative clone |
| Narrative source pattern | `frontend/src/features/natal-chart/NatalReadingSources.tsx` | New inaccessible source disclosure pattern |
| Natal copy | `frontend/src/i18n/natalChart.ts` | Hardcoded repeated labels in component bodies |
| Natal styles | Existing `ni-*` or `natal-*` stylesheet | Inline `style` props |

## Mandatory Reuse / DRY Constraints
- Reuse the existing Basic V2 rendering surface instead of creating a parallel Basic public report owner.
- Reuse small presentational helpers for public list and legal list rendering instead of duplicating list markup.
- Reuse existing `ni-*`, `natal-*` classes and CSS variables before adding new narrowly scoped classes.
- Reuse the existing narrative source accessibility pattern conceptually for a compact Basic source appendix.
- Keep evidence deduplication in one helper with a stable key; do not duplicate dedupe logic in tests and components.
- Keep legal-line deduplication in one helper; do not maintain separate merge logic for limitations and disclaimers.

## No Legacy / Forbidden Paths
- No legacy factual card component may be reintroduced into `/natal` public interpretation rendering.
- No compatibility renderer may retain per-theme Basic V2 evidence blocks.
- No fallback branch may render a second Basic V2 legal footer.
- No raw technical field may be rendered in text, `title`, `aria-label`, test ID, hidden content or tooltip.
- No inline style may be added to touched TSX surfaces.
- No old source marker class such as `.ni-evidence-tags` may be restored.

## Reintroduction Guard
- Forbidden public DOM markers:
  - `visibility_expression`, `audit_input`, `condition_axis:`, `interpretive_signal_ids`, `projection_version`.
  - `ranking_score`, `weighted_score`, `prompt_hint`.
  - `Luminaire: moon`, `Position planetaire: saturn, gemini`.
- Forbidden component symbols in public `/natal` rendering:
  - `NatalAstrologicalDna`, `NatalLifeDomains`, `NatalStrengths`, `NatalChallenges`, `NatalMajorAspects`.
- Forbidden style pattern:
  - `style={` in touched TSX surfaces.
- Required guards:
  - `pnpm --dir frontend test -- natalPublicDomGuard`.
  - Targeted `rg` scans VC4, VC5, VC6 and VC7.

## Regression Guardrails
| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-153 `/natal` public composition | `/natal` -> no factual cards in public reading -> `pnpm` tests and VC6 scan. |
| RG-154 public DOM denylist | Basic V2 public DOM -> no technical markers -> `pnpm` DOM guard and VC7 scan. |
| RG-158 narrative accordions | narrative v1 branch -> modern accordions unchanged -> `pnpm --dir frontend test -- natalNarrativeReading`. |
| RG-168 Basic V2 public contract | `basic_natal_interpretation_v2` -> canonical public contract remains consumed -> `pnpm` tests and build. |
| RG-048 CSS fallbacks | touched CSS -> no unclassified fallback value -> VC5 scan and CSS allowlist check. |
| RG-073 feature owner | `NatalInterpretation` owner -> orchestration stays under feature owner -> `pnpm` tests and review of owner paths. |
| RG-170 Basic V2 dedupe | Basic V2 DOM -> one source appendix and one legal area -> DOM guard and build. |

- Registry enrichment: `RG-170` is added for the durable Basic V2 source and legal deduplication guard.
- Non-applicable examples: backend DB migrations, auth guardrails and i18n extraction guardrails are out of scope for this frontend render-only story.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| DOM baseline | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/dom-basic-before.md` | Capture current Basic V2 repetition. |
| DOM result | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/dom-basic-after.md` | Capture final Basic V2 public DOM. |
| Validation output | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/validation.txt` | Keep command outputs for handoff. |
| Scan output | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/scans.txt` | Keep targeted scan outputs for handoff. |
| QA notes | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/qa-responsive.md` | Record desktop and mobile visual QA. |
| Review output | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register
- Allowlist handling: active empty register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No allowlist entry is authorized for this story. | Permanent zero-entry register for this story. |

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:

- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - simplify Basic V2 report, source appendix and legal area.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - refine public evidence usage metadata type only if required.
- `frontend/src/i18n/natalChart.ts` - adjust public appendix or legal labels only for existing copy keys.
- Existing CSS files containing `ni-*` or `natal-*` classes - add compact appendix and legal block styles without inline styles.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover Basic V2 order, shared evidence metadata and branch non-regression.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - cover one source appendix, one legal title and no raw source text in main content.
- `frontend/src/tests/NatalChartPage.test.tsx` - keep page-level branch behavior covered.
- `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/evidence/*` - persist validation artifacts.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - Basic V2 public report rendering and non-regression.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - DOM repetition and technical marker guards.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level `/natal` integration.
- `frontend/src/tests/natalNarrativeReading.test.tsx` - narrative v1 accordion non-regression.

Files not expected to change:

- `backend/**` - out of scope; the Basic V2 contract is consumed, not changed.
- `frontend/src/api/**` - out of scope unless a missing existing type prevents typed metadata usage.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - orchestration owner remains unchanged.
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - narrative v1 branch remains unchanged.
- `frontend/src/features/natal-chart/NatalReadingSources.tsx` - source pattern may be inspected but not required to change.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`.
- VC2: `pnpm --dir frontend lint`.
- VC3: `pnpm --dir frontend build`.
- VC4: `rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`.
  - Forbidden pattern: inline TSX `style={` props.
  - Allowed fixture pattern: none expected in touched runtime TSX.
  - Scan roots: listed frontend component, feature and page paths.
  - Expected false positives: none.
- VC5: `rg -n "var\\(--[^,)]+," frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/styles`.
  - Forbidden pattern: new CSS variable fallback values without classification.
  - Allowed fixture pattern: entries already classified in `frontend/src/styles/css-fallback-allowlist.md`.
  - Scan roots: listed frontend component, feature and style paths.
  - Expected false positives: existing allowlisted CSS fallback entries only.
- VC6: legacy UI scan.
  ```powershell
  rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" `
    frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
  ```
  - Forbidden pattern: old factual card and legacy evidence UI symbols.
  - Allowed fixture pattern: test names only outside listed runtime roots.
  - Scan roots: listed frontend component, feature and page paths.
  - Expected false positives: none in runtime roots.
- VC7: technical marker scan.
  ```powershell
  rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" `
    frontend/src/components/natal-interpretation frontend/src/features/natal-chart
  ```
  - Forbidden pattern: technical Basic or narrative markers in public DOM code paths.
  - Allowed fixture pattern: denylist constants inside test files, outside listed runtime roots.
  - Scan roots: listed frontend component and feature paths.
  - Expected false positives: none in runtime roots.
- VC8: Manual check: open `/natal` with `daconrilcy@hotmail.com`, then verify desktop and mobile show no overlapping source or legal blocks.

## Regression Risks
- Removing repeated source blocks could hide public traceability; AC3, AC4 and AC5 require a visible deduplicated appendix.
- Merging legal text could drop a Basic limitation or global legal line; AC6 requires merged deduplicated output.
- Branch-specific legal handling could alter free short or narrative v1; AC8 and AC9 preserve those branches.
- CSS changes could introduce inline style or fallback drift; AC10, VC4 and VC5 guard those surfaces.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep changes scoped to the Basic V2 public rendering and tests listed above.
- Preserve public evidence visibility through the final appendix.
- Persist validation and QA artifacts under this story directory.

## References
- `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md`
- `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
