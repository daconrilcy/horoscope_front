# Dev Log

<!-- Commentaire global: ce journal resume les decisions et validations de l'implementation CS-359. -->

- 2026-05-28: Preflight git: only pre-existing `?? _condamad/run-state.json`.
- 2026-05-28: Required generated files were missing; capsule prepared with explicit `--story-key` then validated PASS.
- 2026-05-28: Product/runtime audit found no public trigger for `event_guidance`; decision persisted as `delete`.
- 2026-05-28: Removed `event_guidance` from contract, seed, taxonomy, prompt catalog, paid-use-case set, adapter branch and governance placeholders.
- 2026-05-28: Updated tests to guard absence and updated CS-350/RG-149 final classification.
- 2026-05-28: Full backend validation PASS: `3349 passed, 1 skipped, 1223 deselected`.
