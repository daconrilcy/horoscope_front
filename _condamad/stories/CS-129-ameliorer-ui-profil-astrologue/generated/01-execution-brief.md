# Execution Brief

## Story

- Key: `CS-129-ameliorer-ui-profil-astrologue`
- Status at start: `ready-to-dev`
- Scope type: frontend UI update for `/astrologers/:id`

## Objective

Improve the astrologer profile UI while preserving route, API, payload, navigation semantics and the current soft premium visual identity.

## Boundaries

- Change only the local profile route, profile sections, profile CSS, i18n labels, profile tests, static guards, visual smoke and the profile e2e spec.
- Do not modify backend code, API contracts, route registration, cache behavior or `/astrologers` list owners.
- Do not add dependencies.
- Do not add active profile styles to `frontend/src/App.css`.

## Required checks

- Read `AGENTS.md`, the story, regression guardrails and the target frontend files before editing.
- Preserve pre-existing dirty files.
- Use `condamad-frontend-dev` for the frontend slice.
- Keep evidence in this capsule synchronized with status.

## Done conditions

- AC1 through AC12 have code and validation evidence.
- Before/after artifacts exist.
- Required frontend tests, static scans, lint and build are run or honestly classified.
- Review reaches clean or acceptable state without unresolved required validation.
- `_condamad/stories/story-status.md` is updated consistently.

## Halt conditions

- New dependency or route/API change becomes necessary.
- Horizontal overflow cannot be fixed locally without a broader layout decision.
- Validation repeatedly fails without a safe scoped fix.
