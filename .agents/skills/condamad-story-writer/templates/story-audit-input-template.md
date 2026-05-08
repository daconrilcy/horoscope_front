# CONDAMAD Audit-To-Story Input

<!-- Gabarit d'entree pour convertir un audit ou une review en story. -->

## Audit Source

- Source type: audit | code-review | review-finding
- Source reference:
- Date or context:

## Findings To Convert

| Finding | Severity | Evidence | Desired correction | Closure intent |
|---|---|---|---|---|
| F1 | High | `relative/path.py` | ... | full-closure \| phased-with-map \| blocked \| non-domain |

## Prior Domain History

- Latest same-domain audit:
- Sibling stories already attempted:
- Findings already closed:
- Findings still active:
- Deferred non-domain concerns:

## Closure Requirements

- Exact affected surface:
- Before/after evidence required:
- Reintroduction guard required:
- Stop condition proving no repeated follow-up story is needed:
- User decision blocker, if any:

## Domain Boundary

- Domain:
- In scope:
- Out of scope:
- Explicit non-goals:

## Forbidden Legacy Patterns

- ...

## Required Validation

```bash
<targeted tests>
<negative rg scans>
<lint/type checks>
```
