# Implementation Plan

## Findings

- `AstrologerPromptBuilder` owned factual context and durable narrative rules.
- `seed_horoscope_narrator_assembly.py` already seeds the canonical
  `horoscope_daily/narration` assembly but its prompt was too generic.
- Plan-specific assembly rules are already supported through `plan_rules_ref` and
  `PLAN_RULES_REGISTRY`.
- `narration_service.py` already owns post-gateway sentence validation and did not
  require changes.

## Patch plan

1. Persist before/after prompt builder artifacts.
2. Remove durable style, format, forbidden phrase, output contract, and length
   instructions from `AstrologerPromptBuilder`.
3. Add governed daily narration prompt constants to the horoscope narrator seed.
4. Add free/premium daily synthesis plan rules and wire the seeded assemblies to them.
5. Add tests proving builder payload-only behavior, assembly ownership, admin
   observability, and adapter non-ownership.
6. Run targeted tests, scans, lint/format, and evidence update.

## No Legacy stance

No shim, alias, fallback, or duplicate assembly path is introduced. The old active
instruction location is removed from the builder; the canonical owned path is the
existing governed assembly.

## Rollback

Revert the modified code/test files and remove the two prompt-builder evidence
artifacts for this story.
