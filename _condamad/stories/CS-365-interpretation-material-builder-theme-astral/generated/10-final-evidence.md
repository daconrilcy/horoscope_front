# CS-365 - Final Evidence

## Story status

- Story key: `CS-365-interpretation-material-builder-theme-astral`
- Status: `ready-to-review`
- Ready for review: yes
- Source brief: `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md`
- Source closure: full-closure for the scoped builder; DB source expansion remains outside this story because no migration or new source text was authorized.

## Preflight

- Story/status alignment verified: `CS-365` row points to `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` and `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md`.
- Initial worktree had unrelated untracked `_condamad/run-state.json`; left untouched.
- Scope classified as backend only; no frontend subagent or frontend validation required.
- CS-361 audit and CS-363 architecture deliverables were consulted through targeted source searches.

## Capsule validation

- Missing generated files were created with `condamad_prepare.py --story-key CS-365-interpretation-material-builder-theme-astral`.
- Final capsule validation: PASS with `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-365-interpretation-material-builder-theme-astral`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Canonical builder owner in `interpretation_material_builder.py`; AST guard test covers owner uniqueness. | Targeted pytest with `--long` PASS. | PASS |
| AC2 | Stable `INTERPRETATION_MATERIAL_KEYS` payload shape in DTO. | Unit shape test PASS. | PASS |
| AC3 | Planet-sign selection matches object code plus zodiac sign. | Unit source/fact matching test PASS. | PASS |
| AC4 | Planet-house selection matches object code plus house number. | Unit source/fact matching test PASS. | PASS |
| AC5 | Aspect selection matches aspect code and participant fact refs. | Unit source/fact matching test PASS. | PASS |
| AC6 | `InterpretationMaterialItem` carries `source_ref`. | Payload provenance test PASS. | PASS |
| AC7 | Candidate items are built from calculated `fact_ref`. | Payload provenance test PASS. | PASS |
| AC8 | Missing source text emits no material item. | Non-invention test PASS. | PASS |
| AC9 | Free/basic/premium policies limit section quantities. | Quantity limit test PASS. | PASS |
| AC10 | `ThemeAstralLLMInputV1Builder` writes `input_data.interpretation_material`. | Integration test PASS with `--long`. | PASS |
| AC11 | No provider, output schema, frontend, migration, or SQL owner change. | Diff check and protected-surface scans PASS. | PASS |
| AC12 | Capsule evidence and story-status row updated. | Capsule validation PASS. | PASS |
| AC13 | Payload emits `interpretive_text` or `writing_hint`. | Payload provenance test PASS. | PASS |

## Files changed

- `backend/app/domain/astrology/interpretation/interpretation_material_contracts.py`
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`
- `backend/app/domain/astrology/interpretation/theme_astral_llm_input_v1_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`
- `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/generated/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added unit tests for material keys, fact-to-source matching, provenance fields, missing-source behavior, profile limits, and AST ownership.
- Added integration test for `theme_astral_llm_input_v1.input_data.interpretation_material` handoff without provider call.

## Commands run

| Command | Result |
|---|---|
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents\\skills\\condamad-dev-story\\scripts\\condamad_prepare.py ... --story-key CS-365-interpretation-material-builder-theme-astral` | PASS |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format <modified python files>` | PASS |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check <modified python files>` | PASS |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; python -B -m pytest -q tests\\unit\\domain\\astrology\\interpretation\\test_interpretation_material_builder.py tests\\integration\\astrology\\test_theme_astral_interpretation_material_input.py --long --tb=short` | PASS, `6 passed` |
| `rg -n "class InterpretationMaterialBuilder" backend\\app backend\\tests -g "*.py"` | PASS: single production owner plus guard test reference |
| `rg -n "\\bsqlalchemy\\b|\\bselect\\s*\\(|\\bSession\\b|\\btext\\s*\\(" <modified files>` | PASS for production files; only the test assertion mentions `sqlalchemy` as forbidden import |
| `git diff --check` | PASS |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; python -B -c "from app.main import app; print('app import ok', len(app.routes))"` | PASS |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents\\skills\\condamad-dev-story\\scripts\\condamad_validate.py _condamad\\stories\\CS-365-interpretation-material-builder-theme-astral` | PASS |

## Commands skipped or blocked

- Full backend pytest suite skipped: capsule requires targeted unit/integration coverage; no API, migration, provider, or frontend surface changed.
- Frontend checks skipped: explicit non-goal and no frontend file touched.

## DRY / No Legacy evidence

- No compatibility shim, transitional alias, fallback text, legacy import path, duplicate active builder, provider gateway edit, output schema edit, frontend edit, or migration was introduced.
- Missing source material emits no item instead of fabricating `interpretive_text` or `writing_hint`.
- The builder is pure domain code and uses explicit `InterpretationMaterialSource` inputs; SQL remains outside this owner.

## Diff review

- Changed surface is limited to backend astrology interpretation domain files, backend tests, capsule evidence, and the exact `CS-365` story-status row.
- Protected surfaces unchanged: provider gateway, output schemas, frontend, migrations.
- Known unrelated untracked file remains: `_condamad/run-state.json`.

## Final worktree status

- New/modified story files and backend files are ready for review.
- `_condamad/run-state.json` was already untracked at preflight and was not modified intentionally.

## Remaining risks

- Production DB loading for planet/house/aspect source rows is intentionally not added here because the story forbids migrations and new source text. The builder contract is ready for existing repositories to provide `InterpretationMaterialSource` rows.

## Suggested reviewer focus

- Review the source matching contract and whether `InterpretationMaterialSource` is the right adapter boundary for existing DB/reference repositories.

## Feedback loop

- No reusable process learning required; no propagation to guardrails or AGENTS.md.
