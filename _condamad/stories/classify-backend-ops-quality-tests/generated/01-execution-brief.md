# Execution Brief

- Story key: `classify-backend-ops-quality-tests`
- Objective: persist a backend docs/scripts/secrets/security/ops test inventory, classify every concerned test under one explicit owner, and add a pytest guard preventing unowned quality or ops tests.
- Boundaries: documentation/evidence artifacts and backend test guard only. Keep the standard backend pytest collection unchanged.
- Non-goals: do not move tests out of pytest backend, do not alter ops script behavior, do not refactor endpoint tests, do not create hidden CI commands.
- Preflight: read `AGENTS.md`, `00-story.md`, `_condamad/stories/regression-guardrails.md`, backend pytest config, audit F-104, and existing backend architecture guards.
- Write rules: no new dependency, no `requirements.txt`, no broad refactor, no compatibility shim or fallback.
- Done conditions: required artifacts exist, ownership guard passes, collect-only passes, lint passes, final evidence records AC-by-AC proof.
- Halt conditions: any attempted change to the standard backend pytest command or CI scope requires user approval.
