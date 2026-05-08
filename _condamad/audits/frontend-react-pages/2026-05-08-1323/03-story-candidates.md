<!-- Candidats de stories issus de l'audit de cloture des pages React frontend. -->

# Story Candidates - frontend-react-pages

## Candidate Summary

No implementation story candidate is emitted by this audit.

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|

## Exhaustive Files To Modify

For `F-001`: none.

Application files: none.

Governance/test files: none.

Reason: `F-001` is an Info closure record. The active guards and targeted validations already prove the prior remediation chain is closed.

## Deferred Non-Domain Context

- Numeric `toLocaleString()` calls in pages are not date/time formatting and should not be migrated into `formatDate.ts`.
- API-client consistency inside `frontend/src/api/**` should be audited separately if desired.
- Frontend design-system token, CSS fallback, inline-style, and legacy-style work remains governed by the existing design-system audit chain and guardrails.
