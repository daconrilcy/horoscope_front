# Final Evidence — CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring`
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story tracker row: path and source brief verified against `_condamad/stories/story-status.md`
- Initial `git status --short`: clean
- Capsule generated and validated after `.venv` activation

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Target story. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `evidence/full-vitest-before.txt` | Initial logged full suite failed with 4 files and 18 tests failing. | PASS |
| AC2 | `evidence/failure-ledger.md` | Every initial failure group has owner, cause, and disposition. | PASS |
| AC3 | Frontend files keep existing patterns and required comments. | `pnpm lint` PASS. | PASS |
| AC4 | CS-303 API code unchanged. | `natalChartApi` logged Vitest PASS. | PASS |
| AC5 | CS-303 rendering code unchanged. | `natalInterpretation` logged Vitest PASS. | PASS |
| AC6 | No architecture bypass introduced. | `component-architecture-guards NatalChartPage natalChartApi` PASS. | PASS |
| AC7 | Shared i18n setup and stale fixtures corrected. | Full logged Vitest PASS: 116 files, 1271 passed, 8 skipped. | PASS |
| AC8 | Projection and style guards clean for CS-305 scope. | Internal scans PASS; global style matches are unchanged; touched TSX scan PASS. | PASS |
| AC9 | Delivery report and CS-303 addendum updated. | `evidence/report-status.md` records limitation removal and browser/manual gap. | PASS |

## Files changed

- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/setup.ts`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/ConsultationsPage.test.tsx`
- `_condamad/reports/CS-302-CS-304-delivery-report.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- CS-305 `evidence/` and `generated/` artifacts
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- `frontend/src/tests/setup.ts`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | `frontend` | FAIL then PASS | Before and after logs persisted. |
| `pnpm lint` | `frontend` | PASS | First attempt hit Windows EPERM; retry passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi` | `frontend` | PASS | 15 tests passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation` | `frontend` | PASS | 33 tests passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi` | `frontend` | PASS | 91 tests passed. |
| `rg -n "fetch\\(.*/v1/astrology/projections" src` | `frontend` | PASS | No direct projection fetch. |
| Forbidden projection internals `rg` scan | `frontend` | PASS | No forbidden internal field exposure. |
| `rg -n "style=" <touched TSX tests>` | `frontend` | PASS | No touched inline styles. |
| `python -B -c <evidence path check>` | repo root, `.venv` active | PASS | Required evidence paths exist. |

## Commands skipped or blocked

- `pnpm test:e2e`: NOT_RUN; out of CS-305 validation plan. Risk: browser-only interaction coverage remains outside this story.
- Local app startup: NOT_RUN; this story closes Vitest validation, not manual/browser QA. CS-306 remains the natural closure point for that gap.

## DRY / No Legacy evidence

- No skipped, narrowed, deleted, or renamed tests.
- No shim, alias, fallback projection client, or legacy path added.
- CS-303 projection API and rendering owners remained unchanged.
- No dependency or package script change.

## Diff review

- `git diff --check`: PASS; line-ending warnings only.
- `git diff --stat`: reviewed; tracked diff is limited to frontend test/i18n fixes, CS-303/report evidence, CS-305 handoff, and story status.

## Final worktree status

- Modified tracked files: delivery report, CS-303 final evidence, CS-305 code review handoff, story status, six frontend i18n/test files.
- Untracked CS-305 generated/evidence artifacts are present for review.
- No untracked `frontend/pnpm-lock.yaml` retained.

## Remaining risks

- Repository-wide inline-style scan still reports pre-existing allowlisted inline styles outside touched files; CS-305 introduced none and full inline-style policy tests pass.
- CS-303 browser/manual startup remains unproved by this story.

## Implementation review closure

- Review verdict: CLEAN after one review/fix iteration.
- Issues fixed by review phase: evidence status was corrected from review handoff / `PASS_WITH_LIMITATIONS` to final clean implementation review.
- Fresh validation on 2026-05-25:
  - `pnpm lint`: PASS after one Windows EPERM retry.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`: PASS, 15 tests.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`: PASS, 33 tests.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`: PASS, 91 tests.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run`: PASS, 116 files, 1271 passed, 8 skipped.
  - `rg -n "fetch\\(.*/v1/astrology/projections" src`: PASS, no matches.
  - `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src`: PASS, no matches.
  - `rg -n "style=" src -g "*.tsx"`: pre-existing allowlisted matches only, unchanged versus `HEAD^`; no CS-305 regression.
  - `condamad_validate.py --final`: PASS with `.venv` active.
  - `condamad_story_validate.py`: PASS with `.venv` active.
  - `condamad_story_lint.py --strict`: PASS with `.venv` active.
- Propagation decision: no-propagation; the review correction is local evidence closure, with no reusable guardrail or skill learning needed.

## Suggested reviewer focus

- Check that test language setup matches the intended `detectLang` precedence.
- Check `ConsultationsPage` wizard assertions around the newly localized `back_to_overview` key.
- Confirm the delivery report only removes the full Vitest limitation and does not overstate browser/manual QA.
