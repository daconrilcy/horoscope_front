<!-- Carte des wrappers publics conserves apres centralisation des erreurs CS-132. -->

# CS-132 - Error wrapper map

| Wrapper / helper | Owner | Decision | Preuve |
|---|---|---|---|
| `ApiError`, `ApiResponseEnvelope`, `parseApiErrorDetails` | `frontend/src/api/client.ts` | canonical | helper partage utilise par les modules migres |
| `B2BAstrologyApiError` | `b2bAstrology.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `B2BBillingApiError` | `b2bBilling.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `B2BEditorialApiError` | `b2bEditorial.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `B2BUsageApiError` | `b2bUsage.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `BillingApiError` | `billing.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `EnterpriseCredentialsApiError` | `enterpriseCredentials.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `HelpApiError` | `help.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `OpsMonitoringApiError` | `opsMonitoring.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `SupportApiError` | `support.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `AdminPromptsApiError` | `admin-prompts/index.ts` | public wrapper delegated | parse via `parseApiErrorDetails` |
| `ApiError` usages natal chart | `natal-chart/index.ts` | public transport error delegated | parse via `parseApiErrorDetails` |
| Autres wrappers API existants | module owner actuel | retained pending future domain slice | scans et tests ciblés conservent le comportement; pas modifies hors lot CS-131/132 |

## Classification

Le helper canonique existe et les modules touches par le lot transport/support
ainsi que les sous-domaines crees par CS-133 deleguent au helper. Les wrappers
non touches restent classes comme `retained pending future domain slice` et
doivent deleguer lors d'une prochaine story de domaine si leur fichier est
modifie.
