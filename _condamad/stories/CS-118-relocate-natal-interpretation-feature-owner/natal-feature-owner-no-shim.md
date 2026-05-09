# Natal Feature Owner No-Shim Audit - CS-118

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `frontend/src/components/NatalInterpretation.tsx` | old container path | dead after consumer replacement | none active | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | delete | File deleted; old path scan under `frontend/src` returns zero active hits. | none |
| `frontend/src/components/NatalInterpretation.css` | old owner CSS path | dead after owner move | none active | `frontend/src/features/natal-chart/NatalInterpretation.css` | delete | File deleted; token registry/design-system guard point to feature CSS. | none |
| `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | old API/feature sub-container path | dead after owner move | none active | `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` | delete | File deleted; old path scan under `frontend/src` returns zero active hits. | none |
| `../components/NatalInterpretation` import in `NatalChartPage` | old runtime import | replaced | none active | `../features/natal-chart/NatalInterpretation` | replace-consumer | `rg -n "features/natal-chart" frontend/src/pages/NatalChartPage.tsx` finds canonical import. | none |
| `components/NatalInterpretation.tsx` allowlist entry | stale exception | dead | none active | no replacement exception | delete | `rg -n "NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src/tests/component-architecture-allowlist.ts` returns zero hits. | none |
| `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` allowlist entry | stale exception | dead | none active | no replacement exception | delete | Same allowlist scan returns zero hits. | none |

## Generated / External Contract Check

- No OpenAPI, generated schema, route manifest or generated API client is
  affected by this frontend component move.
- `rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"` returns zero active hits.
- No compatibility wrapper, alias, fallback, re-export or preserved old import
  path remains under `frontend/src`.

## Remaining Hit Classification

- Hits in `_condamad/**` are historical governance/evidence references.
- Hits in `frontend/src/features/natal-chart/**` are canonical-active.
- Hits in `frontend/src/components/natal-interpretation/**` are presentational
  API-free children and do not own API/feature orchestration.
