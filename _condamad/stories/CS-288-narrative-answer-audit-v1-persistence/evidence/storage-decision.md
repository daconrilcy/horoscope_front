# Storage decision

Decision: extend `UserNatalInterpretationModel` / `user_natal_interpretations` as the canonical persistence owner for `narrative_answer_audit_v1`.

Rationale:
- `UserNatalInterpretationModel` already owns persisted narrative answer rows, `user_id`, `chart_id`, `level`, prompt-version FK, payload, and creation time.
- `LlmCallLogModel` already owns operational call observability, provider/model metadata and input hashes, but it is call-oriented and does not own persisted user answer identity or `evidence_refs`.
- `LlmPromptVersionModel` remains the prompt-version owner; the audit row stores `prompt_version`, `prompt_ref` and optional `prompt_snapshot_ref` references instead of prompt text.
- No new audit table was created. The repository `NarrativeAnswerAuditRepository` writes and reads through `UserNatalInterpretationModel`.

Backfill stance:
- Migration `20260525_0139` adds required columns to `user_natal_interpretations`.
- Existing rows receive deterministic `answer_id = user_natal_interpretation:<id>`, `answer_type` from `level`, `not_checked` grounding, and `legacy_unavailable`/zero-hash placeholders where historical audit metadata did not exist.
- New runtime writes in `NatalInterpretationService` fill audit metadata from gateway provenance and deterministic payload hashes.
