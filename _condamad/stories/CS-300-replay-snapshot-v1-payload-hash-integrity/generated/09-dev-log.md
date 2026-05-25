# Dev Log

- Preflight: story/status/brief alignment verified for `CS-300`; initial worktree clean.
- Capsule was incomplete and repaired with `condamad_prepare.py --repair-generated-only`; capsule validation passed.
- Before evidence captured: creation encrypted sanitized replay payload while replay compared against original call-log hash.
- Implementation: added canonical replay payload/hash helpers in `ReplaySnapshotV1Service`, made snapshot storage hash and encryption use the same payload, and made replay compare against `snapshot.input_hash`.
- Test repair: replay success setup now uses `log_call`; fabricated `encrypt_input(user_input)` success path removed.
- Validation fix: normalized naive SQLite expiration timestamps for replay snapshot expiry checks.
- Audit fix: allowed `purged_count` as operational audit metadata so purge evidence remains bounded and testable.
- Final validation: targeted replay tests, expanded replay suite, Ruff, negative scans, runtime exposure checks, diff check, and capsule validation passed.
