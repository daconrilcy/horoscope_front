# Execution Brief — CS-173-localiser-interface-langue-utilisateur

## Primary objective

Implement and validate interface language localization from browser locale, then account preference, with DB-backed language options from `languages`.

## Boundaries

- Backend: expose `/v1/reference-data/languages`; enrich `GET/PATCH /v1/users/me/settings` with optional detected localization metadata.
- Frontend: integrate a Header language selector backed by the languages API and user settings API.
- Evidence: persist AC traceability, validations, review findings, and final status in this capsule.

## Non-goals

- Do not translate new unsupported interface bundles.
- Do not modify astrology reference-data invariants RG-091 to RG-108 except citing RG-108.
- Do not add GPS/geolocation permission flows.
- Do not refactor existing landing navbar language controls in this story.

## Execution rules

- Use the Python venv for every backend Python command.
- Do not run the global backend suite with `--long`; targeted integration files may use `--long` because the repository deselects integration tests otherwise.
- Preserve the existing React/Vite stack and central API clients.
- No inline styles in Header/top-menu surfaces.
- No backend hardcoded language catalogue outside `LanguageModel`.
- No commit or push unless explicitly requested.

## Done when

- AC1-AC4 are `PASS` in `03-acceptance-traceability.md`.
- `10-final-evidence.md` records commands, skipped checks, files changed, and final worktree state.
- `11-code-review.md` reaches `CLEAN`.
- `_condamad/stories/story-status.md` is synchronized.
