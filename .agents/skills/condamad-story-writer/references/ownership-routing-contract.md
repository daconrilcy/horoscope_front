# Ownership Routing Contract

<!-- Contrat transverse pour router chaque responsabilite vers son proprietaire canonique. -->

Use this contract for boundary, namespace, service, API adapter, core, domain,
infra, and convergence refactors.

## Rule

The story must classify each responsibility before choosing a destination. A
move is invalid when it only follows file shape or convenience.

## Canonical Routing

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |

## Required Story Content

The story must include:

- responsibility table;
- canonical owner for each moved or protected responsibility;
- forbidden destination;
- validation evidence proving imports/routes still respect ownership.
