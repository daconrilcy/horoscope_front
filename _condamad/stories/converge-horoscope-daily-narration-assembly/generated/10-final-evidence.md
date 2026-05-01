# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `converge-horoscope-daily-narration-assembly`
- Source story: `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md`
- Capsule path: `_condamad/stories/converge-horoscope-daily-narration-assembly`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- AGENTS.md considered: `AGENTS.md`
- Initial dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/audits/prompt-generation/`, `_condamad/stories/converge-horoscope-daily-narration-assembly/`, `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`
- Regression guardrails read: `RG-006`, `RG-016`, `RG-017`, `RG-019`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | source story |
| `generated/01-execution-brief.md` | yes | yes | PASS | updated |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 covered |
| `generated/04-target-files.md` | yes | yes | PASS | updated |
| `generated/06-validation-plan.md` | yes | yes | PASS | updated |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | updated |
| `generated/10-final-evidence.md` | yes | yes | PASS | this file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `AstrologerPromptBuilder` now emits daily facts and user context parameters only; before/after artifacts persisted. | Builder tests passed; forbidden marker scan returned zero hits. | PASS | |
| AC2 | `HOROSCOPE_DAILY_NARRATION_PROMPT` and plan rules own durable output/style/length instructions; seed wires free/premium assemblies to plan rules. | Seed tests passed; positive assembly ownership scan showed migrated text only in assembly-owned files. | PASS | |
| AC3 | Admin resolved detail integration test proves selected components, composition sources, and runtime artifacts expose migrated prompt and plan-rule text. | Admin targeted test passed. | PASS | |
| AC4 | `narration_service.py` unchanged for routing/retry; adapter guard added. | Narrator migration tests, RG-016 guard, provider direct-call scan passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/prediction/astrologer_prompt_builder.py` | modified | remove durable narration instructions from context builder | AC1 |
| `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` | modified | seed canonical durable narration prompt and plan-rule refs | AC2 |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | modified | add free/premium daily narration plan rules | AC2 |
| `backend/tests/unit/prediction/test_astrologer_prompt_builder.py` | modified | guard builder payload-only behavior | AC1 |
| `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py` | modified | guard assembly prompt and plan-rule ownership | AC2 |
| `backend/tests/integration/test_admin_llm_catalog.py` | modified | guard admin visibility of migrated text | AC3 |
| `backend/tests/llm_orchestration/test_narrator_migration.py` | modified | guard adapter non-ownership | AC4 |
| `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-before.md` | added | baseline before artifact | AC1 |
| `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-after.md` | added | after artifact | AC1 |
| `_condamad/stories/converge-horoscope-daily-narration-assembly/generated/*` | added/modified | CONDAMAD evidence | all |

## Files deleted

None.

## Tests added or updated

- Builder payload-only and source marker guard.
- Seed prompt and plan-rule ownership guards.
- Admin resolved detail visibility guard for `horoscope_daily/narration`.
- Adapter non-ownership guard.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md` | `backend` | PASS | 0 | story validation PASS |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md` | `backend` | PASS | 0 | story lint PASS |
| `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_seed_horoscope_narrator_assembly.py tests/llm_orchestration/test_narrator_migration.py tests/integration/test_admin_llm_catalog.py::test_admin_llm_catalog_resolved_detail_exposes_horoscope_daily_narration_assembly` | `backend` | PASS | 0 | 19 passed |
| `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_seed_horoscope_narrator_assembly.py tests/llm_orchestration/test_narrator_migration.py tests/integration/test_admin_llm_catalog.py::test_admin_llm_catalog_resolved_detail_exposes_horoscope_daily_narration_assembly tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | PASS | 0 | post-fix reviewer rerun: 23 passed |
| `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py` | `backend` | PASS | 0 | post-fix seed rerun: 5 passed |
| `pytest -q` | `backend` | PASS | 0 | user-provided rerun: 3496 passed, 12 skipped in 737.63s |
| `ruff format app\domain\llm\configuration\assembly_resolver.py app\tests\unit\test_seed_horoscope_narrator_assembly.py tests\integration\test_admin_llm_catalog.py` | `backend` | PASS | 0 | 3 files reformatted |
| `ruff format --check .` | `backend` | PASS | 0 | 1243 files already formatted |
| `ruff check .` | `backend` | PASS | 0 | all checks passed |
| `python -B -c "from app.main import app; print(app.title)"` | `backend` | PASS | 0 | app import/startup smoke printed `horoscope-backend` |
| `rg -n "Format attendu\|Interdiction\|daily_synthesis : strictement" backend\app\prediction\astrologer_prompt_builder.py` | repo root | PASS | 1 | zero hits |
| `rg -n "Format attendu\|Interdiction\|daily_synthesis : strictement" backend\app\domain\llm\runtime\adapter.py backend\app\services\llm_generation\horoscope_daily` | repo root | PASS | 1 | zero hits |
| `rg -n "strictement 7 à 8\|strictement 10 à 12\|Ne produis pas de phrases creuses\|Génère uniquement du JSON valide" backend\app\ops\llm\bootstrap\seed_horoscope_narrator_assembly.py backend\app\domain\llm\configuration\assembly_resolver.py backend\app\prediction\astrologer_prompt_builder.py` | repo root | PASS | 0 | hits only in assembly-owned files |
| `rg -n "from app\.api\|import app\.api" backend\app\services backend\app\domain backend\app\infra backend\app\core` | repo root | PASS | 1 | zero hits |
| `rg -n "from app\.prediction\.llm_narrator import LLMNarrator\|LLMNarrator\(\|LLMNarrator\.narrate" backend\tests backend\app\tests -g "test_*.py"` | repo root | PASS | 1 | zero hits |
| `rg -n "LLMNarrator\(\|chat\.completions\.create\|openai\.AsyncOpenAI" backend\app backend\tests` | repo root | PASS | 1 | zero hits |
| `git diff --check` | repo root | PASS | 0 | no whitespace errors |
| `git status --short -- backend/horoscope.db` | repo root | PASS | 0 | no DB diff after restoration |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` initial Codex run | no | first attempt timed out after 10 minutes before user reran it successfully | none remaining | user-provided rerun passed: 3496 passed, 12 skipped |
| `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` | story-listed path | file does not exist in repository | none; equivalent test path differs | ran `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py` |

## DRY / No Legacy evidence

- Builder forbidden marker scan: zero hits.
- Adapter / horoscope daily service forbidden marker scan: zero hits.
- Migrated instruction positive scan: hits only in assembly-owned files.
- No new fallback, shim, alias, re-export, or duplicate assembly path introduced.
- `backend/horoscope.db` changed during validation and was restored.

## Diff review

- `git diff --check`: PASS.
- `git diff --stat`: reviewed; code/test/capsule files only, plus pre-existing guardrail story files outside this story still present in worktree.
- `backend/horoscope.db` was restored after validation side effect.

## Final worktree status

Final `git status --short`:

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/domain/llm/configuration/assembly_resolver.py
 M backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py
 M backend/app/prediction/astrologer_prompt_builder.py
 M backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py
 M backend/tests/integration/test_admin_llm_catalog.py
 M backend/tests/llm_orchestration/test_narrator_migration.py
 M backend/tests/unit/prediction/test_astrologer_prompt_builder.py
?? _condamad/audits/prompt-generation/
?? _condamad/stories/converge-horoscope-daily-narration-assembly/
?? _condamad/stories/formalize-consultation-guidance-prompt-ownership/
```

Notes:

- `_condamad/stories/regression-guardrails.md`,
  `_condamad/audits/prompt-generation/`, and
  `_condamad/stories/formalize-consultation-guidance-prompt-ownership/` were
  already dirty or untracked at preflight.
- `_condamad/stories/converge-horoscope-daily-narration-assembly/` includes the
  user-provided story plus the generated capsule/evidence and prompt baseline
  artifacts for this implementation.

## Remaining risks

- Existing pre-story dirty/untracked CONDAMAD audit/story files remain outside this story.

## Suggested reviewer focus

- Confirm plan-rule registry is the desired governed surface for free/premium daily synthesis lengths.
- Review the exact migrated narrative wording for product tone.
- Confirm the updated full-suite evidence is acceptable for merge.
