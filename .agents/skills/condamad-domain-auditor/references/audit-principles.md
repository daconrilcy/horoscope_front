# Audit Principles

A CONDAMAD domain audit verifies whether an implementation domain respects its intended ownership, boundaries, contracts, and operational guarantees.

The audit must answer:

1. What is the audited domain?
2. What is the expected responsibility of this domain?
3. What evidence proves the actual implementation?
4. Where are the deviations?
5. Which deviations require stories?
6. Which deviations require user decisions?

## Doctrine

- Audit one domain per run unless the user explicitly asks for a comparative audit.
- Stay read-only by default and never modify application code.
- Do not audit without a clear boundary.
- Evidence comes before conclusions.
- No finding is valid without proof.
- Static scans are secondary evidence.
- Runtime, structural, or contract evidence is preferred when available.
- Findings must be actionable or explicitly marked `needs-user-decision`.
- Story candidates are proposals for `condamad-story-writer`, not final implementation stories.
- DRY, No Legacy, mono-domain ownership, and dependency direction are mandatory dimensions.
