# Target Files - CS-279

## Inspected Before Implementation

- `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md`
- `_condamad/stories/story-status.md`
- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/app/domain/astrology/runtime/astronomical_proof.py`
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Modified Application Files

- `backend/app/domain/astrology/runtime/transit_chart_manifest.py`
- `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Modified CONDAMAD Evidence Files

- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/manifest-after.json`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/api-neutrality.md`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/app-surface-status.txt`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/source-checklist.md`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/generated/10-final-evidence.md`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/generated/11-code-review.md`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/00-story.md`
- `_condamad/stories/story-status.md` row `CS-279`

## Forbidden Or Unchanged By CS-279

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- generated OpenAPI clients
- public transit projection contracts

## Review Notes

- No new dependency, route, serializer, migration, DB model, frontend file, projection builder or runtime runner is required.
- Existing unrelated dirty files in the repository are outside CS-279 and were not normalized by this review cycle.
