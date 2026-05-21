# CS-206 Validation Summary

## Runtime Evidence

- Source of truth: `AstrologyRuntimeReference.planet_natures`.
- Added runtime support: `sect_nature_mitigation` condition type and weight.
- Detector evidence: injected runtime nature tests cover malefic, benefic, neutral, unknown and missing `PlanetSectCondition`.

## Snapshot Evidence

- Before: `sect-nature-mitigation-before.json` records absence of the CS-206 fact before implementation.
- After: `sect-nature-mitigation-after.json` records:
  - `malefic_mitigated_by_sect`
  - `malefic_aggravated_out_of_sect`
  - `benefic_supported_by_sect`
  - `benefic_weakened_out_of_sect`
  - `sect_nature_unknown`

## Dignity Score Invariants

- No dignity calculator file was modified.
- `sect_nature_mitigation` runtime weight is neutral (`score_effect=0.0`,
  `ranking_weight=0.0`) so supported, mitigated, weakened, aggravated, neutral
  and unknown facts do not receive a shared positive downstream score.
- Snapshot score fields remain copied from `PlanetDignityResult`:
  - `essential_score`
  - `accidental_score`
  - `total_score`
  - `functional_strength_score`
  - `expression_quality_score`
  - `intensity_score`

## Frontend

- No frontend file changed.
- Existing generic `advanced_conditions` projection can display additive condition facts.
- CS-206 did not introduce frontend doctrine, constants or derivation.

## Scan Hit Classification

| Command | Result | Classification |
|---|---|---|
| `rg -n "BENEFIC_PLANETS\|MALEFIC_PLANETS\|MIXED_PLANETS\|NEUTRAL_PLANETS\|DIURNAL_MALEFICS\|NOCTURNAL_MALEFICS\|SECT_MITIGATED_PLANETS\|MARS_SECT_RULE\|SATURN_SECT_RULE\|JUPITER_SECT_RULE\|VENUS_SECT_RULE" backend/app frontend -g "*.{py,ts,tsx,js,jsx}"` | zero hit | PASS. No production local nature constants. |
| `rg -n "if .*planet_code.*mars\|if .*planet_code.*saturn\|if .*planet_code.*jupiter\|if .*planet_code.*venus\|planet_code\s+in" backend/app/domain/astrology frontend -g "*.{py,ts,tsx,js,jsx}"` | five hits | PASS with classified pre-existing/non-CS-206 hits. `runtime/runtime_reference.py:64` is the canonical runtime membership lookup. `builders/sign_runtime_builder.py:104`, `builders/house_occupants_builder.py:41`, `dominance/planet_dominance_engine.py:55` and `dominance/planet_dominance_engine.py:267` are unrelated structural/dominance membership checks, not benefic/malefic doctrine and not modified by CS-206. |
| `rg -n "SectCalculator\|PlanetSectConditionCalculator\|SectNatureMitigationDetector\|AdvancedConditionEngine" backend/app/services/chart frontend -g "*.{py,ts,tsx,js,jsx}"` | zero hit | PASS. Projection/frontend do not import calculators or engines. |
| `rg -n "sect_mitigation_legacy\|legacy_sect_mitigation\|benefic_code\|malefic_code\|planet_nature_code_legacy" backend/app backend/tests frontend -g "*.{py,ts,tsx,js,jsx}"` | zero hit | PASS. No legacy public fields. |
| `rg -n "Session\|select\(\|from app\.infra\|from app\.services\|from app\.api\|from app\.domain\.prediction\|OpenAI\|AIEngineAdapter\|chat\.completions\|prompt" backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition backend/app/domain/astrology/interpretation_adapters -g "*.py"` | two hits | PASS with classified unrelated hits. `condition/contracts.py:69` and `condition/planet_condition_signal_builder.py:48` are existing `prompt_hint` contract fields for signal profiles, not prompts, LLM calls or CS-206 changes. |

## Review Finding Fixes

- CR-1/CR-2: parent weight made neutral and tests now prove CS-206 does not add shared positive support/ranking.
- CR-3: no-time JSON filters `sect_nature_mitigation` from public `advanced_conditions`; regression test added.
- CR-4: actual RG-133 scan hits are classified above.
- CR-5: no-time JSON also filters CS-206 `planet_condition_profiles.breakdown`
  and `explanation_facts`, preventing sect-dependent facts from leaking through
  profile evidence after `advanced_conditions` are hidden.

## Feedback Loop

- Review fixes were local to CS-206 projection and evidence. No reusable
  process learning requiring AGENTS, skill, or shared guardrail propagation was
  identified; routing decision: `no-propagation`.
