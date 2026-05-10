<!-- Classification frontend du endpoint support search-by-email pour CS-135. -->

# CS-135 - Classification endpoint support

Endpoint frontend: `/v1/support/users/context?email={email}`

| Surface | Classification | Owner frontend | Decision | Preuve | Limite |
|---|---|---|---|---|---|
| `useOpsSearchUser(email)` dans `frontend/src/api/support.ts` | canonical-active | `support.ts` | keep | le payload retourne `SupportUserContext` et le chemin appartient au namespace `/v1/support` | verification runtime backend differee par l'audit frontend-api |

## Decision

Le hook de recherche par email reste une responsabilite support frontend. Il ne
doit pas servir de facade pour les actions ops persona. Les actions ops persona
restent sous `frontend/src/api/opsPersona.ts`.
