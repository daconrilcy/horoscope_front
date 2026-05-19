# Code Review CS-191

Review target: `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md`

Verdict: CLEAN

Review/fix loop iterations in this session: 1 fresh review, 1 evidence fix batch.

## Inputs Reviewed

- Story contract and AC1-AC8 in `00-story.md`.
- Final evidence and validation plan in `generated/10-final-evidence.md`, `generated/06-validation-plan.md` and `generated/07-no-legacy-dry-guardrails.md`.
- Regression guardrails `RG-095`, `RG-107`, `RG-108`, `RG-112`, `RG-114`, `RG-115`, `RG-116` and `RG-118`.
- Current diff and untracked CS-191 files.
- Runtime, mapper, domain calculators, natal integration, JSON projection and tests.

## Diff Summary

- Runtime reference now carries `PlanetDignityReferenceSet` and typed dignity reference contracts.
- Runtime repository loads dignity score profiles, weights, essential rules, triplicity rulers, terms, decans and accidental rules.
- Domain calculators under `backend/app/domain/astrology/dignities/**` compute sect, essential dignities, accidental dignities and aggregate scoring from runtime data only.
- `NatalResult` and chart JSON expose the new `dignities` block.
- Unit and guard tests cover runtime loading, calculator behavior, JSON projection and forbidden boundary regressions.

## Findings

No remaining actionable findings.

Fixed in this session:

- Low validation evidence freshness issue: targeted and full backend pytest
  counts in `generated/10-final-evidence.md` and
  `evidence/dignity-guard-evidence.md` still reflected the previous review run.
  The evidence now records the current successful run without changing
  implementation scope.

Previously fixed:

- Medium validation artifact issue: `00-story.md` Batch Migration Plan used
  `Required proof` instead of the CONDAMAD-required `No-shim proof` column, and
  strict story lint also rejected long AC evidence lines. The story artifact now
  validates and lints cleanly without changing the implementation scope.

The previous review findings remain resolved:

- Solar accidental dignities skip Sun self-distance.
- Participating triplicity rulers match runtime `sect_code = all`.
- Sect derives horizon houses from runtime accidental rules.
- AC5 tests cover house modality, direct/retrograde, planetary joy, solar priority and Sun self-exclusion.
- Score profiles and weights are loaded through `DignityReferenceRepository`.

## Acceptance Audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `AstrologyRuntimeReference.dignity_reference` is present and repository validation requires populated score profiles, weights and rule sets. |
| AC2 | PASS | `backend/app/domain/astrology/dignities/contracts.py` uses frozen dataclasses with tuple breakdowns and no mutable dict payload. |
| AC3 | PASS | `SectCalculator` returns explicit `day`/`night` from configured horizon rules and errors on missing Sun or missing rules. |
| AC4 | PASS | `EssentialDignityCalculator` reads essential rules, triplicity, terms, faces and weights from runtime reference. |
| AC5 | PASS | `AccidentalDignityCalculator` covers house modality, direct/retrograde, planetary joy and exclusive solar-distance rules required by story scope. |
| AC6 | PASS | `PlanetDignityScoringService` aggregates factual scores without interpretation, prediction or LLM dependency. |
| AC7 | PASS | Snapshot comparison confirmed `natal-payload-before.json` equals `natal-payload-after.json` after removing only the added `dignities` block. |
| AC8 | PASS | Runtime guard test and RG-118 scans show zero forbidden DB/service/API/scoring/LLM hits in dignity calculators. |

## Validation Audit

Commands run from repository root after `.\.venv\Scripts\Activate.ps1`:

- `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` - PASS, 51 passed.
- `Set-Location backend; ruff format --check .; ruff check .` - PASS.
- `Set-Location backend; pytest -q` - PASS, 2686 passed, 1 skipped, 1177 deselected.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` - PASS.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` - PASS.
- `python -B .agents/skills/condamad-code-review/scripts/condamad_review_validate.py .agents/skills/condamad-code-review` - PASS.
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- `rg -n "DIGNITY_SCORES|DOMICILE_SCORE|ACCIDENTAL_DIGNITY_SCORES|score_value\s*=\s*[-0-9]" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- `rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- Snapshot invariant check with venv Python: PASS, only `dignities` is added.
- Backend local startup smoke with `uvicorn app.main:app --host 127.0.0.1 --port 8019` from `backend` - PASS, `/docs` returned HTTP 200; process stopped.
- `git diff --check` - PASS, no whitespace errors.

## DRY / No Legacy Audit

- No compatibility wrapper, alias, fallback, re-export or duplicate active implementation found.
- Domain calculators do not import infra, services, API, SQLAlchemy, prediction or LLM surfaces.
- Scoring values used by production calculators come from runtime score weights, not local production mappings.
- No frontend surface is touched.

## Residual Risks

Aucun risque restant identifie.
