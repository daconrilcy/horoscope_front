# Target Files

## Inspected before implementation

- `AGENTS.md`
- `_condamad/codex-runs/cs-381-*.log`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `backend/app/api/v1/routers/public/users.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`

## Modified files

- `backend/tests/integration/astrology/test_natal_generation_regression.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `frontend/e2e/natal-generation-regression.spec.ts`
- `frontend/playwright.config.ts`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/**`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
- `backend/alembic/**`
- `backend/app/infra/**`
- `frontend/src/styles/**`
- Real provider configuration or secrets
