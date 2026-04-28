# Dev Log

## Preflight

- Initial dirty status contained untracked CONDAMAD audit/story directories and unreadable pytest temp directories reported by Git.
- Applicable `AGENTS.md`: repository root `AGENTS.md`.
- Applicable guardrails: `RG-001`, `RG-003`, `RG-006`, `RG-008`.
- Capsule generated manually because the story directory existed but `generated/` was absent.

## Decision

- The route remains externally active because generated email links use `/api/email/unsubscribe` and previously sent emails may still reference it.
- Selected decision: `needs-user-decision`.
- Runtime behavior must remain unchanged.
