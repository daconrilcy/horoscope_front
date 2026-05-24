# Step 02 - Evidence Collection

Collect facts before conclusions.

For each story:

1. Read `00-story.md` for goal, ACs, non-goals, source references, and key.
2. Read the capsule files listed in `workflow.md`; load optional files only to
   resolve gaps.
3. Inspect referenced implementation/test files only as needed to prove claims.
4. Use diff, changed-file, `git show`, or commit-range evidence when available.
5. Capture validation commands exactly, with workflow result and scope values.
6. Capture review verdicts and unresolved findings without softening them.

Separate evidence as code, test, documentation, or operational evidence. Each
entry must state what the anchor proves.

Do not run mutating commands. Read-only tests/checks are allowed when useful and
not prohibited; label new command results as `report-time` validation, distinct
from story-time or CI evidence.
