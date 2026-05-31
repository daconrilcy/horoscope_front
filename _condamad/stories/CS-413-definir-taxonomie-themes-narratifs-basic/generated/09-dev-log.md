# Dev Log — CS-413

- 2026-05-31: Initial worktree had pre-existing `_condamad/run-state.json` modified.
- 2026-05-31: Required generated capsule files were absent; repaired with `condamad_prepare.py --repair-generated-only ... --story-key CS-413`, then capsule validation passed.
- 2026-05-31: Implemented `natal_theme_taxonomy.py` as the single canonical owner for Basic theme taxonomy and activation.
- 2026-05-31: Added taxonomy and activation unit tests; fixed tension `must_mention` preservation after first failing targeted test.
- 2026-05-31: Targeted lint/tests and public-boundary tests passed.
- 2026-05-31: Full backend pytest has two pre-existing architecture guard failures outside touched files; recorded as limitation, not fixed under this story.
