# Review CS-414 - Implementation

Verdict: CLEAN

## Scope

- Reviewed story: `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/00-story.md`.
- Source brief: `_story_briefs/cs-409-resoudre-contradictions-themes-natals-basic.md`.
- Tracker row: `CS-414`, target path and source brief matched before closure.
- Guardrails reviewed: `RG-152`, `RG-154`, `RG-155`, `RG-156`, `RG-022`, `RG-163`.

## Iteration 1 Findings

- Validation evidence issue: `VC9` scan for public narrative leaks matched `confidence_wording` in
  `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`, while final evidence claimed no service
  boundary match.

## Fix Applied

- Kept the runtime support-element code unchanged through `SUPPORT_ELEMENT_QUALITY_LABEL_CODE`.
- Reused that constant from the narrative builder so `VC9` no longer reports a service-layer false positive.
- Did not change story ACs, source brief, public contract shape, frontend scope or prompt-provider scope.

## Fresh Review

- `SynthesisResolver` remains in the canonical backend domain owner.
- Resolver output includes the required internal fields and stays separated from public narrative rendering.
- Strong mixed signals force explicit nuance; weak single-fact themes are not autonomous.
- Redundant themes receive a stable merge group.
- Date-only context downgrades birth-time surfaces and avoids public interpretation of unavailable houses or angles.
- Public-boundary scans do not expose resolver symbols in frontend, API or natal LLM service surfaces.

## Validation

- PASS: `ruff check .` from `backend`.
- PASS: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py tests/unit/domain/astrology/test_client_interpretation_support_elements.py tests/unit/test_narrative_natal_reading_v1.py --tb=short` (`26 passed`).
- PASS: `rg -n "toujours|jamais|destin|oblige|doit absolument|medical|juridique|financier" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal` returned no matches.
- PASS: `rg -n "natal_synthesis|SynthesisResolver|ResolvedThemeSynthesis" frontend backend/app/api backend/app/services/llm_generation/natal` returned no matches.
- PASS: `rg -n "theme_code|confidence|merge_group|omission_reason" backend/app/services/llm_generation/natal` returned no matches.
- PASS with expected controlled hit: `rg -n "ascendant|maison|MC|Milieu du Ciel" backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py` matched only the controlled date-only omission wording.
- PASS: `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-414-resoudre-contradictions-themes-natals-basic`.
- PASS: `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-414-resoudre-contradictions-themes-natals-basic --final`.
- PASS: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-414-resoudre-contradictions-themes-natals-basic\00-story.md`.
- PASS: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-414-resoudre-contradictions-themes-natals-basic\00-story.md`.

## Propagation

- `no-propagation`: the correction is local to validation evidence and service scan hygiene; no reusable workflow update is needed.

## Residual Risk

- Full backend pytest suite was not run; targeted resolver, public-boundary and narrative tests cover this story surface.
