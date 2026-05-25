# Source Checklist — CS-267 admin-answer-audit-api

## Sources checked

| Source | Coverage |
|---|---|
| `_story_briefs/cs-267-define-admin-answer-audit-api.md` | Objective, included scope, non-goals, validation and risk matched. |
| `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` | Audit identity, answer status, versions, provider, model and prompt provenance reused. |
| `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` | `evidence_refs` vocabulary reused for proof summary and detail linkage. |
| `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` | Rejected status and `rejection_reason` consultation kept explicit. |
| `backend/app/api/v1/routers/admin/users.py` | Existing `require_admin_user` admin protection pattern referenced in the contract. |
| `backend/app/api/v1/routers/admin/logs.py` | Existing protected admin diagnostic route family considered for namespace separation. |

## Scope decisions

- `docs/architecture/admin-answer-audit-api.md` is the single canonical contract document for this story.
- No runtime route, persistence model, repository, migration, replay workflow, frontend UI or generated client is created.
- Future runtime implementation must stay under `/v1/admin/answer-audits` and use the existing admin authentication dependency pattern.
- Default responses must not expose `birth_date`, `birth_time`, `birth_place`, `birth_lat`, `birth_lon` or `birth_timezone`.

## Review fixes recorded

- Added exact `birth_lat` and `birth_lon` forbidden-field coverage to the contract and tests.
- Extended forbidden runtime path checks to `/v1/users/me/answer-audits`,
  `/v1/admin/chart-diagnostics/answer-audits` and `/v1/admin/answer-audit-replay`.
- Replaced generated target-file placeholders with concrete CS-267 files and forbidden surfaces.
