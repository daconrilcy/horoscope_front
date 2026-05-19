# Execution Brief

## Story

- Key: `CS-193-planetary-condition-signals`
- Objective: add backend `PlanetConditionSignal` contracts derived from `PlanetConditionProfile`, governed by runtime DB table `astral_planet_condition_signal_profiles`, exposed on `NatalResult.condition_signals` and public JSON `planet_condition_signals`.

## Boundaries

- Touch only backend astrology condition/runtime/infra/chart JSON surfaces and story evidence.
- Do not touch `frontend/**`.
- Do not add LLM, narrative rendering, dominant planets, advanced condition rules, prompt templates, or UI.
- `domain/astrology/condition/**` must remain pure: no DB, API, services, prediction, SQLAlchemy, or local threshold table.

## Required Checks

- Preserve pre-existing dirty files unrelated to CS-193.
- Read `AGENTS.md`, `00-story.md`, and `_condamad/stories/regression-guardrails.md`.
- Apply `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`, `RG-118`, `RG-119`, `RG-120`.

## Done Conditions

- All AC1-AC10 pass with code and validation evidence.
- Final evidence is complete.
- Story registry is synchronized to `done` only after review is clean.

