# Dev Log

## 2026-05-23

- Preflight found an existing dirty worktree unrelated to CS-247: CS-246 story/evidence changes, architecture candidate edits, existing backend tests and untracked CS-246/brief files.
- Capsule generated files were missing in the target folder; `condamad_prepare.py` created a derived-key capsule. Generated artifacts were copied into the target CS-247 capsule and the temporary derived capsule was removed.
- Capsule validation passed for `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract`.
- Implemented internal graph manifest, node IO schema, manifest validator, natal manifest factory and comparison behavior.
- First targeted pytest run failed because manifest construction assumed graph declaration order was topological. Fixed by pre-indexing all node outputs before deriving node input schemas.
- Re-ran targeted tests, backend tests and lint successfully.
- Feedback-loop routing decision: `no-propagation`; the validation failure was local to this new manifest implementation and is now covered by tests.
