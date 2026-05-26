# Audit de retrait CS-323

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `AnalyticsProvider` value for removed provider | frontend type value | historical-facade | Aucun consommateur actif apres scan `frontend/src`, `.env.example`, `docs` et `backend` | `noop` local et `plausible` prepare | delete | `provider-scan-before.txt` puis `provider-scan-after.txt`; `pnpm lint` | none |
| Hook branch using provider queue | frontend hook branch | historical-facade | Aucun appel direct hors `useAnalytics` apres scan `plausible\\(` | `useAnalytics` avec branche `plausible` et branche `noop` | delete | `provider-scan-after.txt`; `vitest run useAnalytics` | none |
| Example active configuration | env/doc surface | dead | `.env.example` ne decrit aucun provider retire actif | Provider vide pour `noop`, host Plausible prepare | keep | `provider-scan-after.txt` | none |

## Decision

- Aucun usage externe actif n'a ete trouve sur les surfaces requises.
- Les elements amovibles ont ete supprimes sans redirection, shim, alias, re-export ou soft-disable.
