# Natal Feature Owner Before - CS-118

Snapshot captured from repository state before the active move, using the
pre-edit file reads and `git show HEAD:<path>` for line counts after the worker
started moving files.

| Item | Before owner/path | Line count | Imports / consumers | Classification | Decision |
|---|---|---:|---|---|---|
| Container | `frontend/src/components/NatalInterpretation.tsx` | 497 | Imports `../api/natalChart`, `../utils/authToken`, `../i18n/natalChart`, presentational children and `./natal-interpretation/NatalInterpretationPersonaSelector`; consumed by `NatalChartPage`. | API/feature owner under `components` | move/delete old path |
| Persona selector | `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | 69 | Imports `../../api/astrologers` and `../../features/astrologers`. | API/feature sub-container under `components` | move/delete old path |
| CSS | `frontend/src/components/NatalInterpretation.css` | 1059 | Side-effect import from the container. | owner-specific styles under old component path | move with feature owner |
| Production consumer | `frontend/src/pages/NatalChartPage.tsx` | n/a | `import { NatalInterpretationSection } from "../components/NatalInterpretation"` | active consumer of old path | replace-consumer |
| Allowlist entry | `frontend/src/tests/component-architecture-allowlist.ts` | n/a | `components/NatalInterpretation.tsx` | stale after move | delete |
| Allowlist entry | `frontend/src/tests/component-architecture-allowlist.ts` | n/a | `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | stale after move | delete |

## Applicable Guardrails

- `RG-069`: the old container and selector are exact API/feature ownership
  exceptions under `components`.
- `RG-071`: presentational children from CS-115 must remain API-free.
- `RG-073`: the new owner must be `frontend/src/features/natal-chart/**`.

## Required Move Outcome

The old paths must not remain as wrappers, aliases, fallback modules or
re-export files. All active consumers must import the canonical feature owner.
