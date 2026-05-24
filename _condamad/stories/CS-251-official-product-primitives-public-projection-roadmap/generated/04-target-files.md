# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/00-story.md`
- `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md`
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/00-audit-report.md`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/03-story-candidates.md`
- `docs/architecture/astrology-runtime-surfaces.md`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Required searches before editing

```powershell
Select-String -Path _condamad\stories\regression-guardrails.md -Pattern 'RG-002|RG-003' -Context 0,4
rg -n "structured facts|beginner summary|expert technical projection|fixed-star contacts|LLM input" docs\architecture
rg -n "API contract|frontend client|UI component|needs-user-decision" docs\architecture\official-product-primitives-public-projections.md
```

## Likely modified files

- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/**`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/domain/astrology/**`
- `backend/migrations/**`
- `docs/db_seeder/**`
