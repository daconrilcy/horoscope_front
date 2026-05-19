# Dev Log - CS-195

## Preflight

- Initial dirty file: `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md`.
- Sequencing gate: CS-192, CS-193 and CS-194 were `done`.
- Capsule was generated and then normalized under the canonical CS-195 path.
- Applicable guardrails: RG-107, RG-108, RG-112, RG-115, RG-116, RG-118,
  RG-119, RG-120, RG-121, RG-122.

## Implementation notes

- Added `astral_advanced_condition_types`,
  `astral_advanced_condition_score_profiles` and
  `astral_advanced_condition_weights`.
- Added runtime contracts, mapper and repository validation for the advanced
  reference set.
- Added pure calculators under
  `backend/app/domain/astrology/advanced_conditions`.
- Integrated advanced conditions into natal orchestration before condition
  signal generation and dominance scoring.
- Kept JSON builder as a strict projection from `NatalResult.advanced_conditions`.

## Review/fix notes

- Three read-only review subagents were used after the initial implementation.
- Findings accepted and fixed:
  - Advanced aspect target selection now chooses a partner compatible with the detected condition.
  - CS-195 accidental source rules are now evaluable by the real dignity pipeline for stationary,
    speed, orientation, sect and hayz sources.
  - Accidental score weights were added for CS-195 source types so runtime dignity breakdowns can
    carry the required facts.
  - A natal pipeline test now proves advanced conditions are emitted without synthetic dignity
    fixtures.
  - Before/after payload evidence now uses the same natal fixture with stable field counts.
- Findings partially accepted:
  - Aspect bonification/maltreatment can be inferred from actual aspects when no upstream
    accidental fact exists; the relation target is explicit and guarded by tests.

## Validation notes

- One broad `pytest -q` attempt from `backend/` is not counted as valid final
  evidence because the venv activation path was wrong for that working
  directory. A full root-level rerun with `.\.venv\Scripts\Activate.ps1`
  passed.
- Review/fix targeted rerun passed: 30 tests.
