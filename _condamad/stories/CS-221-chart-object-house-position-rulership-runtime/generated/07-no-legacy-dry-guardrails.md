# CS-221 No Legacy / DRY Guardrails

## Decisions

- No compatibility wrapper, shim, alias or fallback added.
- No second `HouseRulerResolver` added.
- No local sign-ruler table added in application code.
- No object-type eligibility branch added for house/rulership consumers.
- No API, DB, migration, JSON public or frontend surface changed.

## Evidence

| Guard | Evidence | Status |
|---|---|---|
| Reuse canonical house modality | `build_house_position_payload()` uses `resolve_house_kind`. | PASS |
| Reuse canonical house rulers | `RulershipPayloadEnricher.enrich()` receives `HouseRulerResult` and `sign_rulerships`. | PASS |
| Capability-based eligibility | `RulershipChartObjectSelector` selects `supports_rulership`. | PASS |
| No local modality constants | Modality scan zero-hit in builders/dignities/dominance. | PASS |
| No second resolver/table | Resolver/table scan zero active hits. | PASS |
| No public surface leak | Adjacent diff API/json_builder/infra/migrations/frontend is empty. | PASS |

## Classified Hits

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `ChartObjectType.LUMINARY` / `ChartObjectType.PLANET` | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | existing construction classification, not house/rulership eligibility | Kept; builder must still classify object families at creation. | PASS |
| `interpretation` / `prompt` hits | Existing runtime reference, aspect/house interpretation modules, `supports_interpretation` capability | pre-existing governed domain surfaces outside CS-221 payload text | Kept; no new narrative field added to house/rulership payloads. | PASS |
