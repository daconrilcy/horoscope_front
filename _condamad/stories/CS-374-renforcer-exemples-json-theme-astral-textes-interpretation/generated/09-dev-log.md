# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: pre-existing untracked `_condamad/run-state.json`.
- Story registry row matched `CS-374`, target `Path`, and source brief.
- Capsule generated files were missing; repaired with `condamad_prepare.py --repair-generated-only` and validated.

## Search evidence

- Inspected CS-371 generator and validator.
- Inspected runtime source repository and material contracts.
- Resolved scoped guardrail `RG-002`; no exact registry guardrail covers enriched example material by profile.

## Implementation notes

- Replaced generic DB seed summaries with richer production-like texts for planets, houses, and aspects.
- Kept DB-backed families routed through `InterpretationMaterialSourceRepository`.
- Renamed supplemental owner to `theme_astral_production_like_fixture` and documented it as non-production fixture material.
- Regenerated `intermediate-data.json`, `free`, `basic`, and `premium` provider payloads, README, structure comparison, source coverage, and no-provider proof.
- Strengthened `validate_examples.py` so known generic phrases fail validation.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Capsule structure. |
| `ruff format <modified scripts>` | PASS | Scoped Python formatting. |
| `python -B ..\_condamad\stories\CS-371...\evidence\generate_examples.py` | PASS | Regenerated examples. |
| `python -B ..\_condamad\stories\CS-371...\evidence\validate_examples.py` | PASS | Strengthened artifact validator. |
| `python -B -m json.tool <four JSON files>` | PASS | JSON validity. |
| `ruff check .` | PASS | Backend lint. |
| `python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_payload_builder.py --tb=short` | PASS | 10 tests. |
| `python -B -m pytest -q --long tests\integration\llm\test_theme_astral_provider_payload_handoff.py --tb=short` | PASS | 1 integration test; default run deselects integration without `--long`. |

## Issues encountered

- `condamad_prepare.py` refused ambiguous CS identifiers until an explicit capsule repair was used.
- The handoff test is auto-deselected by the repository fast-test hook without `--long`; rerun with `--long` passed.

## Decisions made

- No frontend, migration, provider client, backend runtime, or guardrail registry files were edited.
- No feedback-loop propagation needed; no reusable process or guardrail change was discovered.

## Final `git status --short`

- Modified expected CS-371 generator/validator/evidence and regenerated example artifacts.
- Added CS-374 evidence and generated capsule files.
- Updated `story-status.md` to `ready-to-review`.
- Pre-existing untracked `_condamad/run-state.json` remains unrelated.
