<!-- Candidats stories issus de l'audit CONDAMAD de continuite frontend components. -->

# Story Candidates - frontend-components

## Candidate Summary

| Candidate | Source finding | Closure intent | Priority |
|---|---|---|---|
| None | None | none | none |

No new in-domain implementation story is recommended for the audited `frontend-components` continuity surface. This is not a claim that the full `frontend/src/components/**` tree has been freshly re-audited.

## Exhaustive Files To Modify

### F-001

Application files: none for the component domain.

Governance/test files: none.

Rationale: the residual API/feature-owning component files are already exact, owned, guarded, and have exit conditions in `frontend/src/tests/component-architecture-allowlist.ts`. Moving them now would create feature/page-domain work, not component-domain closure work.

### F-002

Application files: none.

Governance/test files: none.

Rationale: zero `@ts-nocheck` hits remain under `frontend/src/components/**`; the guard is active.

### F-003

Application files: none.

Governance/test files: none.

Rationale: `NatalInterpretation` has been decomposed enough to close the component-domain finding. Future relocation to a natal feature owner is deferred non-domain context.

### F-004

Application files: none.

Governance/test files: none.

Rationale: usage classifications and guards exist; representative remove-classified files are absent.

### F-005

Application files: none.

Governance/test files: none.

Rationale: validation is already executable and passing.

## Deferred Non-Component Context

Potential future stories should be opened only under their owning domains:

- `frontend-features` or `frontend-enterprise`: move B2B and enterprise panels out of `components`.
- `frontend-admin-ops`: move ops and support panels out of `components`.
- `frontend-auth`: move `SignInForm` and `SignUpForm` under an auth feature owner.
- `frontend-settings`: move `PrivacyPanel` and `DeleteAccountModal` under settings/privacy.
- `frontend-layouts`: replace layout auth hook ownership with route-level data/provider ownership.
- `frontend-natal`: move the `NatalInterpretation` container and persona selector to a canonical natal feature owner.

These are not emitted here because the continuity stop condition is met: no unclassified component API import, TypeScript suppression, monolithic natal surface, or unused component surface remains in the surfaces opened by the prior audit findings. A future full-domain audit may still choose to classify every current component file individually.
