<!-- Journal de developpement CS-119 avec decisions et validations. -->

# Dev Log - CS-119

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md`
- Initial `git status --short`:
  - `M _condamad/stories/regression-guardrails.md`
  - `M _condamad/stories/story-status.md`
  - `?? _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/`
- Pre-existing dirty files: same as initial status; story capsule already existed
  as untracked directory and guardrail/status files were dirty before coding.
- AGENTS.md considered: `AGENTS.md`.
- Story sufficiency gate: PASS, `full-closure` with finite targets,
  before/after evidence, deterministic reintroduction guards and validation.

## Implementation Notes

- Frontend implementation delegated to `condamad-frontend-dev` worker with
  ownership limited to `frontend/**`.
- Main session owns capsule evidence, story status and review closure.
- Frontend worker deleted confirmed test-only components/CSS/tests, cleaned
  allowlists, adapted transverse guards and ran frontend validation.
- Main session reran targeted frontend tests, lint, negative scans and story
  validation commands.
- Independent review found incomplete before evidence, orphan kebab-case CSS,
  stale `.today-header` test selectors, and insufficient alias/re-export guard
  coverage.
- Accepted frontend review findings were fixed through `condamad-frontend-dev`:
  orphan CSS removed, tests rewritten to semantic assertions, RG-074 guard
  extended to scan active source symbols/module specifiers/selectors.
- Evidence finding on `ErrorBoundary/**` was fixed by classifying these files
  as `canonical-active` in before/after inventories.
