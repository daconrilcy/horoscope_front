# Dev Log — CS-411-natal-fact-graph-basic-tracable

- Preflight: initial dirty worktree contained `_condamad/run-state.json`.
- Capsule: target generated files were missing; repaired target capsule after one helper invocation created an accidental parallel `_condamad/stories/cs-411` capsule. The accidental capsule was removed.
- Implementation: created canonical internal model and builder, added rich/date-only tests, extended architecture guard.
- Validation: first targeted pytest run failed on missing fixture house fact and node date-only marker; both fixed, rerun passed.
- Cleanup: removed known pytest/ruff caches and accidental helper capsule.
