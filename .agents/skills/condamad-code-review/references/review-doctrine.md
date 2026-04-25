<!-- Doctrine de revue adversariale CONDAMAD. -->

# Review Doctrine

## Purpose

CONDAMAD Code Review is not a second implementation pass. It is an adversarial
quality gate after a story implementation. The reviewer must challenge whether
the implementation satisfies the story, protects architecture, and provides
honest validation evidence.

## Review Mindset

Assume the implementation may be subtly wrong even if tests pass.

Prefer concrete evidence over confidence:

- changed files;
- test assertions;
- command outputs;
- acceptance traceability;
- negative search results;
- deleted legacy paths;
- explicit failure behavior.

## Required Review Layers

### 1. Diff Integrity Review

Check:

- unexpected files;
- unrelated formatting churn;
- generated/cache/database artifacts;
- accidental deletions;
- broad changes outside story scope;
- secrets or local-only configuration.

### 2. Acceptance Audit

For each AC:

- identify the code that claims to satisfy it;
- identify the test/check that proves it;
- flag missing, partial, or contradicted evidence;
- verify non-goals were not implemented accidentally.

### 3. Validation Audit

Check whether validation commands are:

- exact;
- relevant;
- executed in the correct environment;
- passing;
- broad enough for the risk;
- honestly skipped when unavailable.

For Python repositories, prefer the repository command policy from `AGENTS.md`.
If a local venv exists, activate it when possible:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# POSIX shell
source .venv/bin/activate
```

When activation is uncertain, prefer invoking the venv interpreter directly:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# POSIX shell
.venv/bin/python -m pytest -q
```

Do not claim tests passed unless the exact command and environment were
recorded.

### 4. DRY / No Legacy Audit

Challenge:

- duplicate active paths;
- compatibility wrappers;
- aliases and re-exports;
- fallback logic;
- old imports still used by nominal code;
- tests preserving legacy behavior as supported;
- docs presenting old paths as current.

### 5. Edge Case and Failure Audit

Check:

- empty, null, malformed, boundary, and permission cases;
- transaction/error behavior;
- concurrency or idempotency risks;
- timeouts and external-client failures;
- migration/data-shape risks;
- frontend loading/error/empty states when UI is involved.

### 6. Security and Data Audit

Check:

- authentication and authorization boundaries;
- secret leakage;
- PII exposure;
- unsafe CORS or environment defaults;
- input validation;
- path traversal, injection, and unsafe deserialization;
- audit/logging safety.

## Reviewer Output Standard

Every actionable finding should answer:

- What is wrong?
- Where is it?
- Why does it matter?
- What evidence proves it?
- What category/severity is it?
- What is the smallest credible fix?

Do not pad the review with low-signal comments.

## False CLEAN Prevention

Do not return `CLEAN` when:

- the review target is ambiguous;
- the diff was not inspected;
- untracked files exist and were not inspected;
- AC-to-validation evidence is missing;
- claimed tests were not verified;
- required validation was skipped;
- No Legacy hits remain unclassified;
- exact changed files are unknown;
- `git diff --check` or equivalent was not run or explicitly skipped with risk.
