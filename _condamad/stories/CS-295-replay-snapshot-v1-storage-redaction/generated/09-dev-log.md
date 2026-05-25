# Dev Log — CS-295

- 2026-05-25: Verified story registry row matches target path and source brief.
- 2026-05-25: Repaired missing generated capsule files with `condamad_prepare.py --repair-generated-only`; capsule validation passed.
- 2026-05-25: Extended canonical replay snapshot owner and writer with approved v1 fields, redacted metadata and 30-day retention.
- 2026-05-25: Added Alembic migration `20260525_0140` for `llm_replay_snapshots`.
- 2026-05-25: Added ownership, storage, redaction, retention, purge, DB redaction and schema invariant tests.
- 2026-05-25: Full backend lint and pytest passed.

