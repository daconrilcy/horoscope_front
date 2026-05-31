# CS-421 Implementation Review

Verdict: CLEAN

## Scope

- Story: `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md`
- Brief: `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- Tracker row: `_condamad/stories/story-status.md`
- Review target: backend implementation, CONDAMAD evidence, tests, guardrails, snapshots, and AC alignment.

## Findings

Iteration 1 found four proof/alignment issues, now fixed:

- Final review evidence was still the obsolete pre-implementation drafting review.
- Required persistent validation proof `evidence/validation-output.txt` was missing.
- Required persistent scan classification `evidence/scan-classification.md` was missing.
- Public/provided CS-421 strings and after snapshots still exposed unaccented French forms such as `repere`, contrary to AC11.

Fresh review after correction found no remaining actionable implementation issue.

## AC / Guardrail Alignment

- AC1-AC4: provider payload exposes `report_arc`, `section_editorial_briefs`, `plain_language_glossary`,
  `forbidden_template_phrases`, and `source_usage_policy` from `BasicNatalReadingPlan`.
- AC5-AC13: validator rejects mechanical templates, raw English labels, unaccented forms, source-listing content,
  weak themes, and disclaimer-only sections; public CS-421 strings now use accented French forms and fallback remains audited with `fallback_used=True`.
- AC14: integration pipeline validates the plan-bounded Basic public contract with the long test enabled.
- AC15: scoped guardrails RG-109, RG-112, RG-152, RG-154, RG-155, RG-156, RG-164, RG-165, RG-166, RG-167,
  RG-168, and RG-169 are covered by tests or classified scans.
- AC16: before/after JSON snapshots, scan classification, and validation evidence are present.

## Validation Evidence

- `ruff format .`: PASS, 1764 files left unchanged.
- `ruff check .`: PASS.
- `pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`: PASS, 6 passed.
- `pytest -q tests/unit/test_basic_natal_narrative_validator.py tests/unit/test_basic_natal_reading_contracts.py --tb=short`: PASS, 30 passed.
- `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py --tb=short`: PASS, 5 passed.
- `pytest -q --long tests/integration/test_basic_natal_v2_pipeline.py --tb=short`: PASS, 1 passed.
- `pytest -q app/tests/unit/test_astrology_translation_resolver.py --tb=short`: PASS, 4 passed.
- `pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`: PASS, 14 passed.
- `condamad_validate.py`: PASS.
- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
- Story evidence file check: PASS, including `scan-classification.md`.

## Scan Classification

- Mechanical phrase scan: hits are limited to provider denylist constants, validator regexes, and negative tests.
- Unaccented/form scan: broad hits are expected in existing tests, domain terminology, denylist constants, contract keys, and non-public code.
- Snapshot unaccented-form scan: remaining hits are only contract keys `theme`/`themes` and denylist entries under `forbidden_template_phrases`.
- Technical marker scan: hits are limited to runtime carriers outside public Basic payload, validator denylist, and contract guards.
- Astrology local table scan: zero hits on scoped story surfaces.

## Residual Risk

Aucun risque restant identifie.

Propagation decision: no-propagation; durable learning already captured in RG-169.
