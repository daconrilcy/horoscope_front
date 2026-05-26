# Dev Log

## Preflight

- Initial `git status --short`: clean.
- Current branch: `main`.
- Existing dirty files: none observed before implementation.
- Capsule was incomplete; repaired with `condamad_prepare.py --repair-generated-only` after one unintended parallel `_condamad/stories/cs-308` capsule was generated and removed.

## Search evidence

- Story registry row matched `CS-308`, target path, and source brief path.
- Scoped copy owners inspected: `frontend/src/i18n/natalChart.ts`, `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`, `frontend/src/features/natal-chart/NatalInterpretation.tsx`, targeted natal tests, disclaimer policy, and public projection contract.
- Guardrails inspected: RG-047 inline styles and RG-052 CSS namespace scope.

## Implementation notes

- Projection panel/card copy is now owned by `natalChartTranslations[lang].interpretation.projections`.
- The panel passes locale-aware copy into projection cards and renders one description per reading level.
- No backend projection builder, prompt, provider, entitlement, or API contract changed.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | PASS | Run after venv activation. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Capsule structure valid. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation astrology-i18n natalChartApi` | PASS | 119 targeted tests passed. |
| `pnpm lint` | PASS | TypeScript lint projects passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | PASS | 1271 passed, 8 skipped. |
| `rg` payload disclaimers / direct transport / inline style scans | PASS | No matches; exit 1 expected. |
| `rg -n "medical\|juridique\|financier\|garanti\|certain\|diagnostic\|traitement" frontend/src` | PASS_WITH_LIMITATIONS | Existing disclaimers/unrelated copy only. |
| `git diff --check` | PASS | Line-ending warnings only. |
| `pnpm dev -- --host 127.0.0.1 --port 5179` | PASS | Vite ready smoke observed, then stopped. |

## Issues encountered

- `pnpm exec prettier --write ...` attempted an install/status operation and failed with EPERM on `node_modules\.pnpm\lock.yaml.*`; the unintended untracked `frontend/pnpm-lock.yaml` was removed.

## Decisions made

- Kept app-owned disclaimers unchanged because they are the expected exception to regulated-advice term scans.
- Did not add a new guardrail registry row because the story-local wording guard is captured in tests and capsule evidence.

## Final `git status --short`

- Pending at evidence update time: frontend wording/test/style files plus CS-308 generated/evidence files and story registry update.
