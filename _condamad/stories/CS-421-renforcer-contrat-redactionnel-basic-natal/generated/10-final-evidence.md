# Final Evidence - CS-421-renforcer-contrat-redactionnel-basic-natal

## Story status

- Validation outcome: PASS
- Final status: done
- Story key: CS-421-renforcer-contrat-redactionnel-basic-natal
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story/status/brief alignment: CS-421 row matches story path and `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`.
- Initial dirty files: `_condamad/run-state.json`, `_condamad/stories/regression-guardrails.md`.
- Capsule generated and validated after venv activation.
- Fresh `generated/11-code-review.md`: implementation review CLEAN on 2026-06-01.
- Command hygiene note: one baseline command was attempted from `backend/` with an invalid relative venv activation path, then rerun from root with the venv activated before evidence was accepted.

## Capsule validation

- `condamad_prepare.py` repaired/generated required files after venv activation.
- `condamad_validate.py <capsule>` PASS before implementation context load.
- Final gate rerun after evidence synchronization.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `section_editorial_briefs` in provider payload. | Prompt payload pytest PASS. | PASS | |
| AC2 | Localized public labels/explanations in plan. | Public evidence pytest PASS. | PASS | |
| AC3 | `BasicNatalEditorialBrief` fields. | Prompt payload pytest PASS. | PASS | |
| AC4 | Report arc, glossary, source policy. | Prompt/provider payload tests PASS. | PASS | |
| AC5 | Source-listing rejection. | Validator pytest PASS. | PASS | |
| AC6 | Public `introduction` remains distinct from summary response. | Reading contracts PASS. | PASS | |
| AC7 | `synthesis` skipped as duplicate public theme. | Validator projection test PASS. | PASS | |
| AC8 | Two informative sentence minimum. | Validator pytest PASS. | PASS | |
| AC9 | Mechanical phrase denylist. | Validator pytest and scan classified PASS. | PASS | |
| AC10 | Raw English label rejection. | Validator/public evidence tests PASS. | PASS | |
| AC11 | Unaccented French form rejection. | Validator/public evidence pytest and refreshed snapshots PASS. | PASS | |
| AC12 | Fallback prose non-mechanical. | Validator and integration pytest PASS. | PASS | |
| AC13 | Disclaimer-only content rejection. | Validator pytest PASS. | PASS | |
| AC14 | Runtime fixture produces accepted Basic V2 contract. | Integration pytest with `--long` PASS. | PASS | |
| AC15 | CS-409 to CS-418 guards preserved. | Contract/provider/translation tests and scans PASS/classified. | PASS | |
| AC16 | Before/after snapshots and scan classification persisted. | Evidence file check PASS. | PASS | |

## Files changed

- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`: added `BasicNatalEditorialBrief`, localized public evidence labels/explanations, section-derived editorial brief builder, and corrected public French accents.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: added `report_arc`, `section_editorial_briefs`, `plain_language_glossary`, `forbidden_template_phrases`, and `source_usage_policy`; corrected provider-visible French accents.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`: rejects mechanical templates, raw English labels, unaccented French forms, source listings, one-sentence themes, and disclaimer-only content; fallback now produces two explanatory accented sentences.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: `synthesis` / `Fil conducteur` feeds introduction and is not duplicated as a public theme.
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_public_evidence.py`
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/**`
- `_condamad/stories/regression-guardrails.md`: added `RG-169`.

## Files deleted

- none

## Snapshot evidence

- `evidence/basic-payload-before.json`
- `evidence/basic-public-contract-before.json`
- `evidence/basic-payload-after.json`
- `evidence/basic-public-contract-after.json`
- `evidence/scan-classification.md`
- `evidence/validation-output.txt`

## Tests added or updated

- Payload shape and no raw-carrier tests updated.
- Public evidence localization and accented public-form tests updated.
- Validator tests added for mechanical phrases, source listings, weak themes, disclaimers, fallback prose and synthesis projection.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `ruff format <changed python files>` | `backend` | PASS | 2 files reformatted, then stable. |
| `ruff check .` | `backend` | PASS | All checks passed. |
| `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short` | `backend` | PASS | 6 passed. |
| `python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py tests/unit/test_basic_natal_reading_contracts.py --tb=short` | `backend` | PASS | 30 passed. |
| `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py --tb=short` | `backend` | PASS | 5 passed. |
| `python -B -m pytest -q --long tests/integration/test_basic_natal_v2_pipeline.py --tb=short` | `backend` | PASS | 1 passed; plain command without `--long` deselects integration tests by project hook. |
| `python -B -m pytest -q app/tests/unit/test_astrology_translation_resolver.py --tb=short` | `backend` | PASS | 4 passed. |
| `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short` | `backend` | PASS | 14 passed. |
| `python -B -c <evidence file check>` | repo root | PASS | JSON snapshots, scan classification, validation output and review artifact present. |

## Commands skipped or blocked

- Plain integration command without `--long`: blocked as final evidence because project hook deselects `tests/integration/**`; rerun with `--long` PASS.
- Full `python -B -m pytest -q --tb=short`: not run; scoped story validation covered touched surfaces.

## Diff review

- `git diff --stat -- <story paths>`: 9 implementation/test files plus CONDAMAD artifacts.
- `git diff --name-only -- <story paths>`: only backend Basic natal surfaces, tests, guardrail registry, and story capsule.
- `git diff --check`: PASS; Windows line-ending warnings only.

## Static scans

- Mechanical phrase scan: hits only in provider denylist, validator regexes, and negative tests.
- Snapshot unaccented-form scan: hits only in contract keys `theme`/`themes` and denylist entries, not public prose.
- Local astrology reference table scan: `rg -n "SIGN_NAMES_FR|SIGN_LABELS|PLANET_LABELS|NODE_LABELS|ASPECT_LABELS|\bSIGNS\s*=\s*\[" ...` returned exit 1, classified PASS/no matches.
- Basic public technical marker scan: hits limited to denylist guards in contracts/validator.
- `git diff --check`: PASS; line-ending warnings only for dirty files on Windows.

## DRY / No Legacy evidence

- No compatibility shim, alias, duplicate active path, legacy import path, frontend change, DB migration, or new dependency introduced.
- Provider payload remains derived from `BasicNatalReadingPlan`.
- New editorial material uses section labels and public evidence already produced by the plan; no local planet/sign/aspect reference mapping was introduced.

## Final worktree status

- Story files changed plus pre-existing `_condamad/run-state.json`.
- `_condamad/stories/story-status.md` updated to `done` after clean implementation review.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Verify that `section_editorial_briefs` gives enough controlled meaning for the prompt assembly story CS-424 without becoming a competing astrology reference owner.

Feedback loop routing: no-propagation; durable invariant captured as `RG-169`.
