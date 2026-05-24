# Governance Before

Source baseline:

- `_condamad/audits/astro-reference-governance/2026-05-23-1939/00-audit-report.md`
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/02-finding-register.md`
- `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`

CS-240 audited families used as baseline:

- `aspect_orbs`
- `dominance_weights`
- `combustion_thresholds`
- `cazimi_thresholds`
- `under_beams_thresholds`
- `speed_thresholds`
- `station_thresholds`
- `house_weights`
- `dignity_weights`
- `sign_profiles`
- `fixed_star_rules`
- `aspect_rules`
- `interpretation_rules`

Key unresolved baseline findings:

- F-001: solar proximity thresholds have mixed DB/Python ownership.
- F-002: motion and station rules have split DB/Python ownership.
- F-003: dominance, sign, house, and dignity weighting families need explicit ownership.
- F-004: interpretation rules have split DB/Python ownership.
- F-005: doctrine sources are partial and not consistently linked.
- F-006: no guard existed for new threshold, weight, profile, or school markers.

Expected after state: one internal runtime governance model classifies every family, preserves unresolved user decisions, and adds executable guard coverage without public API, frontend, DB, migration, seed, or narration changes.
