Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
