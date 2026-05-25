# Source Alignment

Story: `CS-304-design-admin-audit-and-replay-flows`

Source brief: `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md`

Tracker row verified: `_condamad/stories/story-status.md` row `CS-304` points to:

- Path: `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/00-story.md`
- Source: `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md`

## Brief expectations preserved

- Admin flows for rejected answers, authorized audit review and replay snapshot are described.
- Read, review-status, replay attempt and purge actions name audit expectations.
- Raw prompt, raw provider payload, raw AI answer, raw birth data, exact coordinates, secrets and unmasked direct identifiers are excluded.
- Runtime endpoints consumed by the future UI are named from `app.routes` and `app.openapi()`.
- Future frontend/admin implementation is blocked without internal admin AuthN/AuthZ, audit logs and redaction proof.

## Scope preserved

No source brief edit was made. No React screen, route, schema, migration, role, generated client or public/support surface was added.
