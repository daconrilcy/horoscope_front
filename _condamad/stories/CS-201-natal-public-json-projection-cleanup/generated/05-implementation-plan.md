# Implementation Plan

## Findings

- The capsule was missing generated execution files; create them before code edits.
- `json_builder.py` already preserves `dignities.sect`, `sect_condition`, advanced conditions, condition profiles/signals, dominants and adapter facts.
- `NatalResult` contains `astral_points` and `signs_runtime`, but `build_chart_json()` does not expose them in the public payload.

## Changes

- Add narrow serializers for `astral_points` and `signs_runtime`.
- Neutralize time-dependent `house` fields inside those blocks when `degraded_mode` is no-time.
- Remove TODO-style legacy wording from the retained public `house.sign` compatibility field without changing the payload field.
- Add focused tests for structural blocks, empty advanced block conventions and persisted missing-block behavior.
- Add evidence snapshots and validation documentation.

## Rollback

- Revert the two serializer additions and tests if validation shows downstream contract breakage.
