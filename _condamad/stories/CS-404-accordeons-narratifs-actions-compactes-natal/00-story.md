# Story CS-404 accordeons-narratifs-actions-compactes-natal: Accordeons Narratifs Modernes Et Actions Compactes Natal
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-399-ajouter-accordeons-narratifs-modernes-et-compacter-actions-natal.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: la refonte `/natal` affiche les cinq chapitres narratifs trop deroules et place les actions secondaires avant le contenu.
- Source stakes: lisibilite progressive, accessibilite clavier, contrat `NatalNarrativeReading`, absence de rendu public legacy, preservation des parcours.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent les primitives du brief sans deplacer le sujet vers backend ou quotas.

## Objective

Restaurer une lecture progressive sur `/natal` avec des accordeons narratifs modernes portes par `NatalNarrativeReading`.
Compacter les actions PDF, historique et options secondaires avant la lecture sans perdre leurs parcours utilisateur.

## Target State

- `NatalNarrativeReading` rend les cinq chapitres de `narrative_natal_reading_v1` sous forme d'accordeons accessibles.
- Le premier chapitre est ouvert par defaut.
- Les quatre autres chapitres sont replies par defaut.
- Chaque chapitre replie affiche son titre et un apercu court derive du texte du chapitre.
- `NatalReadingSources` reste replie apres les chapitres narratifs.
- `NatalAstrologerMode` reste replie en fin de page publique.
- `NatalInterpretation` regroupe regeneration, historique, PDF et options secondaires dans `ni-actions--compact`.
- Les etats upsell, quota, loading, empty, error, regeneration et mode astrologue restent routables.
- Le DOM public ne montre pas `sections`, `highlights`, codes moteur ni evidence IDs bruts.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-399-ajouter-accordeons-narratifs-modernes-et-compacter-actions-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-404`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-129`, `RG-153`, `RG-154`, and `RG-158`.
- Evidence 4: guardrail resolver ran for frontend natal scope; exact local IDs were confirmed by targeted registry lookup.
- Evidence 5: `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` owns chapter rendering and imports its CSS file.
- Evidence 6: `frontend/src/features/natal-chart/NatalReadingSources.tsx` already provides a collapsed accessible source toggle model.
- Evidence 7: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` composes narrative reading before sources.
- Evidence 8: `frontend/src/features/natal-chart/NatalInterpretation.tsx` contains `ni-actions ni-actions--compact` around action controls.
- Evidence 9: `frontend/src/pages/NatalChartPage.tsx` keeps `NatalAstrologerMode` after the narrative synthesis surface.
- Repository structure alert: expected frontend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector:
  - operation `update`, domain `frontend-natal`
  - paths `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`, `frontend/src/pages/NatalChartPage.tsx`
  - contracts `accessibility`, `css-tokens`, `public-dom`, `narrative_natal_reading_v1`, `compact-actions`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `NatalNarrativeReading` accordion owner | in scope | AC1, Task 1 |
| five narrative chapters | in scope | AC1, Task 1 |
| first chapter open by default | in scope | AC2, Task 2 |
| four chapters collapsed by default | in scope | AC2, Task 2 |
| button, `aria-expanded`, `aria-controls` | in scope | AC3, Task 3 |
| keyboard navigation | in scope | AC4, Task 3 |
| mouse toggle | in scope | AC13, Task 3 |
| collapsed title and short preview | in scope | AC5, Task 4 |
| no duplicated preview content | in scope | AC5, Task 4 |
| CSS variables and no inline style | in scope | AC10, Task 7 |
| `NatalReadingSources` collapsed after chapters | in scope | AC6, Task 5 |
| compact PDF, history and secondary actions | in scope | AC8, Task 6 |
| upsell, quota, loading, empty, error, regeneration | in scope | AC11, Task 8 |
| astrologer mode collapsed | in scope | AC7, Task 5 |
| `RG-154` modern accordion wording | in scope | AC9, RG-154, RG-158 |
| backend, prompts, calculations and quotas | out of scope | Non-goals |
| legacy public body path | out of scope | Non-goals, RG-154 |

## Domain Boundary

- Domain: frontend-natal
- In scope:
  - React rendering and tests for the `/natal` public narrative reading surface.
  - Accessible accordion state in `NatalNarrativeReading`.
  - Compact action layout in `NatalInterpretation`.
  - CSS updates using existing variables in the relevant CSS files.
  - Public DOM guards for legacy-free narrative rendering.
- Out of scope:
  - Backend API, DB schema, auth, i18n dictionaries, build tooling, migrations, prompts, astrology calculations and quota logic.
- Explicit non-goals:
  - No backend route, prompt change, quota change, generated client, DB migration, public engine-code display or legacy body restoration.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested frontend natal UX contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only the public `/natal` narrative reading disclosure and action density.
  - Preserve the `NatalNarrativeReading` data contract based on `narrative_natal_reading_v1`.
  - Preserve current PDF preview, PDF download, history, regeneration, upsell, quota and error flows.
  - Keep technical data and astrologer details behind existing public boundaries.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: compacting the actions requires removing a currently reachable user action.
- Additional validation rules:
  - Use `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage` for component behavior.
  - Use `pnpm --dir frontend lint` and `pnpm --dir frontend build` for frontend validation.
  - Use `AST guard` or bounded static guards for component ownership and forbidden inline style attributes.
  - Use targeted `rg` scans for forbidden public DOM selectors, legacy component symbols and inline style attributes.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest and DOM queries prove React rendering, ARIA state and retained actions. |
| Baseline Snapshot | yes | Before/after artifacts prove the only allowed delta is narrative disclosure and action density. |
| Ownership Routing | yes | Narrative, sources, action orchestration and page composition owners must stay canonical. |
| Allowlist Exception | no | No tolerance entry is authorized for legacy public rendering or inline style drift. |
| Contract Shape | yes | The component contract has exact collapsed state, ARIA linkage and compact-action rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Legacy public DOM, raw evidence IDs and inline styles must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `NatalNarrativeReading` owns five chapter accordions. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC2 | The first chapter starts open. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC3 | Chapter buttons expose ARIA linkage. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC4 | Each chapter toggles by keyboard. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC5 | Collapsed chapters show a short unique preview. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC6 | Sources remain collapsed after narrative chapters. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC7 | Astrologer mode remains collapsed by default. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC8 | Secondary actions use the compact surface. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`; `rg` checks compact actions. |
| AC9 | Public DOM hides technical markers. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`; `rg` checks denylist. |
| AC10 | Styling uses CSS variables without inline style. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend lint`; `rg` checks `style=`. |
| AC11 | Existing natal interaction states stay reachable. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC13 | Each chapter toggles by mouse. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |

## Implementation Tasks

- [ ] Task 1: Keep the five `narrative_natal_reading_v1` chapters rendered inside `NatalNarrativeReading`. (AC: AC1)
- [ ] Task 2: Initialize accordion state with only the first ordered chapter expanded. (AC: AC2)
- [ ] Task 3: Wire native buttons, ARIA linkage and input-safe toggling for every chapter. (AC: AC3, AC4, AC13)
- [ ] Task 4: Render a title and derived short preview for each collapsed chapter without duplicating full content. (AC: AC5)
- [ ] Task 5: Preserve source and astrologer-mode collapsed defaults after the narrative reading. (AC: AC6, AC7)
- [ ] Task 6: Compact PDF, history, regeneration and secondary action controls under the existing action owner. (AC: AC8, AC11)
- [ ] Task 7: Move all visual rules to CSS files and reuse existing design variables. (AC: AC10)
- [ ] Task 8: Preserve loading, empty, error, quota, upsell, regeneration and history flows in page tests. (AC: AC11)
- [ ] Task 9: Add or update DOM guards for public legacy markers and raw evidence identifiers. (AC: AC9)
- [ ] Task 10: Persist validation output and before/after evidence under this story directory. (AC: AC12)

## Files to Inspect First

- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.css`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/features/natal-chart/NatalAstrologerMode.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalNarrativeReading.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

## Runtime Source of Truth

- Primary source of truth:
  - React component tests, DOM queries, ARIA assertions, user-event interactions and `AST guard`.
- Runtime evidence:
  - `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage`.
- Secondary evidence:
  - Targeted `rg` scans and `AST guard` checks for public denylist terms, legacy component symbols and inline style attributes.
- Static scans alone are not sufficient for this story because:
  - Open default state, collapsed panels, keyboard toggling and action reachability must be proven in rendered React DOM.

## Contract Shape

- Contract type:
  - Frontend React presentation contract for `/natal` narrative reading.
- Fields:
  - `reading.chapters`: ordered narrative chapter list rendered as accordions.
  - `chapter.title`: visible heading for each collapsed and expanded chapter.
  - `chapter.narrative`: source for expanded body and short collapsed preview.
  - `reading.used_astrological_elements`: source material displayed only through `NatalReadingSources`.
- Required fields:
  - `chapters`, `chapter.key`, `chapter.title`, `chapter.narrative`, `used_astrological_elements`.
- Optional fields:
  - `chapter.key_points`, rendered only inside an expanded chapter.
- Status codes:
  - unchanged; this story changes frontend rendering only.
- Serialization names:
  - `narrative_natal_reading_v1` and public field names stay unchanged.
- Frontend type impact:
  - no generated client change; existing `NarrativeNatalReadingV1` types remain canonical.
- Generated contract impact:
  - no OpenAPI or generated manifest change.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/natal-public-dom-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/natal-public-dom-after.txt`
- Expected invariant:
  - The only intended UI delta is progressive narrative disclosure and compact secondary action density.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Narrative chapter disclosure | `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` | `NatalInterpretationContent.tsx` or page-level branching |
| Narrative accordion styling | `frontend/src/features/natal-chart/NatalNarrativeReading.css` | inline styles or global page CSS |
| Reading source disclosure | `frontend/src/features/natal-chart/NatalReadingSources.tsx` | narrative chapter component |
| Interpretation actions | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | page header or narrative reading component |
| Interpretation action styling | `frontend/src/features/natal-chart/NatalInterpretation.css` | inline styles or unrelated CSS files |
| Public page composition | `frontend/src/pages/NatalChartPage.tsx` | legacy interpretation body components |
| Public DOM guard tests | `frontend/src/tests/natalPublicDomGuard.test.tsx` | manual-only QA notes |

## Mandatory Reuse / DRY Constraints

- Reuse `NatalReadingSources` as the source disclosure interaction model.
- Reuse existing `narrative_natal_reading_v1` data and public copy helpers.
- Reuse existing CSS tokens, spacing variables, border variables and motion variables.
- Keep accordion state local to `NatalNarrativeReading`; do not duplicate chapter state in page or parent containers.
- Keep action compaction inside the existing interpretation action owner.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy public body path may be restored for the complete public narrative flow.
- No compatibility rendering path may consume `sections` or `highlights` for public complete readings.
- No fallback UI may show raw engine codes, raw evidence IDs, `LockedSection`, `.ni-evidence-tags` or `.ni-projections`.
- Do not add a shim, alias, broad tolerance register, hidden residual path, inline style, duplicated accordion owner or backend-side UI workaround.
- Forbidden public component: `NatalInterpretationLegacyBody` in the modern complete narrative path.
- Forbidden public content: `visibility_expression`, `audit_input`, `condition_axis:`, `interpretive_signal_ids`, `projection_version`.

## Reintroduction Guard

- Guard source:
  - `rg -n "NatalInterpretationLegacyBody|style=" frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
  - `rg -n "ni-evidence-tags|ni-projections|LockedSection" frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- Runtime guard:
  - `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage`.
- CSS guard:
  - `pnpm --dir frontend lint`.
- Forbidden reintroduction:
  - public rendering of legacy sections or highlights.
  - public raw evidence IDs or engine markers.
  - inline styles in the touched React components.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 | scope -> TSX styling -> no static inline style in touched frontend files. | `pnpm` lint; targeted `rg`. |
| RG-052 | scope -> CSS tokens -> action and accordion styles reuse canonical variables. | CSS review; `pnpm` build. |
| RG-071 | scope -> interpretation owner -> `NatalInterpretation` keeps orchestration responsibilities. | `pnpm` tests; ownership review. |
| RG-073 | scope -> feature owner -> natal orchestration stays under `features/natal-chart`. | `pnpm` tests; targeted `rg`. |
| RG-129 | scope -> public natal UI -> React must not calculate astrology rules. | `rg` anti-derivation scan. |
| RG-153 | scope -> `/natal` composition -> narrative and astrologer-mode layers stay ordered. | `pnpm` `NatalChartPage` test. |
| RG-154 | scope -> public DOM denylist -> modern accordion allowed, legacy markers absent. | `pnpm` DOM guard; targeted `rg`. |
| RG-158 | scope -> modern accordions -> ARIA chapters and compact actions stay present. | `pnpm` tests; targeted `rg`. |

- Needs-investigation: none; targeted lookup found the brief-specific modern accordion guardrail.
- Registry gap: none; `RG-154` already distinguishes modern `NatalNarrativeReading` accordions from legacy public accordions.
- Non-applicable example: backend quota guardrails are out of scope because no backend file is listed.
- Non-applicable example: DB migration guardrails are out of scope because no schema change is authorized.
- Non-applicable example: auth guardrails are out of scope because no authentication model change is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/natal-public-dom-before.txt` | Record initial public DOM and action density. |
| Baseline after | `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/natal-public-dom-after.txt` | Record final public DOM and action density. |
| Validation output | `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/validation.txt` | Keep final lint, test, build and scan output. |
| Browser QA | `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/browser-qa.md` | Record desktop and mobile manual checks. |
| Review output | `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for public legacy markers, raw evidence IDs or inline styles. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - own accordion state, ARIA attributes and preview rendering.
- `frontend/src/features/natal-chart/NatalNarrativeReading.css` - style modern accordion states with existing variables.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - keep action controls grouped in compact layout.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - style compact action density with existing variables.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - preserve narrative then sources composition.
- `frontend/src/pages/NatalChartPage.tsx` - preserve mode astrologue placement and page-level flows.
- `_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/**` - persist proof artifacts.

Likely tests:

- `frontend/src/tests/natalNarrativeReading.test.tsx` - cover default state, ARIA linkage, previews and toggles.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - cover public denylist, collapsed sources and allowed modern accordion.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover compact actions and retained page states.

Files not expected to change:

- `backend/**` - out of scope; no backend, prompt, calculation, quota or DB behavior is touched.
- `frontend/src/api/**` - out of scope; no generated client or API contract is changed.
- `frontend/src/i18n/**` - out of scope; no copy dictionary change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story generation; existing IDs are referenced only.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage`
- VC2: `pnpm --dir frontend lint`
- VC3: `pnpm --dir frontend build`
- VC4: `rg -n "ni-evidence-tags|ni-projections|LockedSection" frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- VC5: `rg -n "NatalInterpretationLegacyBody|style=" frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- VC6: `rg -n "natal-narrative-reading__toggle|aria-expanded|aria-controls" frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- VC7: `rg -n "ni-actions--compact" frontend/src/features/natal-chart/NatalInterpretation.tsx frontend/src/features/natal-chart/NatalInterpretation.css`
- VC8: `python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-404-accordeons-narratifs-actions-compactes-natal/evidence/validation.txt').exists()"`
- VC9: `Manual check: open /natal desktop and mobile with daconrilcy@hotmail.com; verify accordion, compact actions, sources and astrologer mode.`

`rg` scan details:

- VC4 forbidden pattern: `ni-evidence-tags|ni-projections|LockedSection`.
- VC4 allowed fixture pattern: none in `NatalInterpretationContent.tsx`.
- VC4 roots: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`.
- VC4 expected false positives: zero.
- VC5 forbidden pattern: `NatalInterpretationLegacyBody|style=`.
- VC5 allowed fixture pattern: none in `NatalNarrativeReading.tsx`.
- VC5 roots: `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`.
- VC5 expected false positives: zero.
- VC6 required pattern: `natal-narrative-reading__toggle|aria-expanded|aria-controls`.
- VC6 allowed fixture pattern: the modern narrative accordion implementation.
- VC6 roots: `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`.
- VC6 expected false positives: none.
- VC7 required pattern: `ni-actions--compact`.
- VC7 allowed fixture pattern: compact action owner and CSS rule.
- VC7 roots: `frontend/src/features/natal-chart/NatalInterpretation.tsx`, `frontend/src/features/natal-chart/NatalInterpretation.css`.
- VC7 expected false positives: none.

## Regression Risks

- Accordion state can hide all chapters by default; AC2 keeps the first chapter open.
- Preview rendering can duplicate full chapter content; AC5 requires a short derived preview only for collapsed chapters.
- Action compaction can break PDF or history flows; AC8 and AC11 keep the existing controls reachable.
- Public DOM guards can be weakened while allowing modern accordions; `RG-154` and `RG-158` separate allowed modern UI from forbidden legacy UI.
- CSS changes can drift into inline styles or local hardcoded values; `RG-047` and `RG-052` keep styling centralized.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.
- Preserve CS-396 behavior before changing the narrative reading surface.

## References

- `_story_briefs/cs-399-ajouter-accordeons-narratifs-modernes-et-compacter-actions-natal.md`
- `_condamad/stories/regression-guardrails.md#RG-047`
- `_condamad/stories/regression-guardrails.md#RG-052`
- `_condamad/stories/regression-guardrails.md#RG-071`
- `_condamad/stories/regression-guardrails.md#RG-073`
- `_condamad/stories/regression-guardrails.md#RG-129`
- `_condamad/stories/regression-guardrails.md#RG-153`
- `_condamad/stories/regression-guardrails.md#RG-154`
- `_condamad/stories/regression-guardrails.md#RG-158`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.css`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
