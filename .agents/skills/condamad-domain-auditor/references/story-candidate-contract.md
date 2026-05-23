# Story Candidate Contract

Every story candidate must include:

- Candidate ID
- Source finding ID
- Suggested story title
- Suggested archetype
- Primary domain
- Required contracts
- Draft objective
- Closure intent: `full-closure`, `phased-with-map`, `blocked`, or `non-domain`
- Must include
- Validation hints
- Blockers / user decision

For implementation candidates, also include:

- exact files or exact selection rule for the full affected surface;
- before/after evidence artifacts required to prove closure;
- required reintroduction guard or existing guard that proves closure;
- allowlist/exception policy with no wildcard or broad folder exception;
- stop condition proving no follow-up story is needed for the same finding.

If the candidate is phased, it must include the remaining closure map in the
same audit. If the candidate cannot close the finding without a decision, mark
it `blocked` or `needs-user-decision` instead of emitting another
implementation slice.

Story candidates are not final ready-for-dev stories. They are structured proposals for `condamad-story-writer`.
