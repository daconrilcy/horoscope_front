# Final evidence - CS-422

<!-- Commentaire global: ce fichier rassemble les preuves finales d'implementation pour review CS-422. -->

## Story status

- Story: `CS-422-simplifier-rendu-basic-natal-sources-mentions-legales`
- Status: `ready-to-review`
- Source story: `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md`
- Source brief: `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md`
- Tracker row: `CS-422` path and brief source verified, status updated to `ready-to-review`.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Git repository: yes.
- Pre-existing dirty file: `_condamad/run-state.json`; not touched.
- Capsule initially incomplete; repaired with helper before reading generated files.
- Existing `generated/11-code-review.md`: classified as handoff-only pre-implementation editorial review.

## Capsule validation

| Command | Result |
|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-422-simplifier-rendu-basic-natal-sources-mentions-legales --root .` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-422-simplifier-rendu-basic-natal-sources-mentions-legales` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-422-simplifier-rendu-basic-natal-sources-mentions-legales --final` | PASS |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Basic V2 order in `BasicV2Reading`. | `natalInterpretation` targeted suite. | PASS |
| AC2 | Theme inline evidence removed. | DOM tests check no source inside `.ni-basic-theme-list`. | PASS |
| AC3 | One `PublicEvidenceList` after conclusion. | Tests check one source appendix title. | PASS |
| AC4 | `getEvidenceKey` dedupes by `source_id` or normalized public fields. | Tests check duplicated sources visible once. | PASS |
| AC5 | `usedInSections` metadata merged. | Test checks `Utilise dans : Axe personnel, Axe relationnel`. | PASS |
| AC6 | `mergePublicLegalLines` + Basic footer suppression. | Tests check one `Mentions legales` title and legal dedupe. | PASS |
| AC7 | Basic themes render only narrative paragraphs. | DOM tests and denylist scans. | PASS |
| AC8 | Free short branch unchanged. | `natalInterpretation` + `NatalChartPage` targeted suite. | PASS |
| AC9 | Narrative v1 files unchanged. | `natalNarrativeReading` + `NatalChartPage` targeted suite. | PASS |
| AC10 | CSS classes only, no inline styles. | Inline style scan + `git diff --check`. | PASS |
| AC11 | No technical marker rendering added. | Denylist scan + `natalPublicDomGuard`. | PASS |

## Files changed

- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Updated `natalInterpretation.test.tsx` for Basic V2 duplicated evidence, usage metadata and legal dedupe.
- Updated `natalPublicDomGuard.test.tsx` for no inline Basic theme evidence, source dedupe and legal title dedupe.

## Commands run

| Command | Result |
|---|---|
| `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` | PASS, 119 tests |
| `pnpm --dir frontend lint` | PASS |
| `pnpm --dir frontend build` | PASS |
| `rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx` | PASS no matches |
| `rg -n "ni-evidence-tags\|ni-projections\|LockedSection\|NatalAstrologicalDna\|NatalLifeDomains\|NatalStrengths\|NatalChallenges\|NatalMajorAspects" ...` | PASS no matches |
| `rg -n "visibility_expression\|audit_input\|condition_axis:\|interpretive_signal_ids\|projection_version\|ranking_score\|weighted_score\|prompt_hint" ...` | PASS no matches |
| `rg -n "var\\(--[^,)]+," frontend/src/features/natal-chart/NatalInterpretation.css` | PASS no matches |
| `git diff --check -- <fichiers touches>` | PASS |
| Controlled local startup with `pnpm.cmd --dir frontend dev` | PASS, Vite responded on `http://127.0.0.1:5173/`; process stopped |

## Commands skipped or blocked

| Command | Status | Reason | Risk |
|---|---|---|---|
| Playwright/browser QA desktop + mobile | NOT_RUN | Not required by minimal commands; no auth/network flow changed. | Low, compensated by DOM tests, build and Vite startup. |
| Backend Python tests | NOT_RUN | Frontend render-only story; no backend files changed. | Low. |

## DRY / No Legacy evidence

- No parallel Basic renderer, shim, alias or fallback branch added.
- Per-theme `PublicEvidenceList embedded` path removed.
- Source dedupe centralized in `collectBasicPublicEvidence`.
- Legal dedupe centralized in `mergePublicLegalLines`.
- Free short and narrative v1 branches preserved.

## Diff review

- `git diff --stat` limited to expected frontend runtime/tests and capsule/status files.
- `git diff --check` PASS.
- Story brief not modified.
- Registry `RG-170` already present; no new registry row needed.

## Final worktree status

- Expected modified files: frontend runtime/tests, capsule evidence, `00-story.md`, `story-status.md`, `generated/11-code-review.md`.
- Pre-existing unrelated dirty file remains: `_condamad/run-state.json`.

## Remaining risks

- Browser responsive QA not run; risk low and documented above.
- CSS fallback large scan has one preexisting hit in `frontend/src/styles/app/base.css:94`, outside touched CSS.

## Suggested reviewer focus

- Confirm the public UX wording for compact usage metadata: `Utilise dans`.
