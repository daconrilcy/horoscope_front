<!-- Inventaire initial des appels fetch directs sous frontend/src/api avant convergence CS-131. -->

# CS-131 - Inventaire fetch before

Commande executee depuis `frontend`:

```powershell
rg -n "\bfetch\(" src/api -g "*.ts"
```

## Hits initiaux

| Fichier | Lignes | Classification | Endpoint / responsabilite |
|---|---:|---|---|
| `src/api/b2bAstrology.ts` | 49 | a migrer | `/v1/b2b/astrology/weekly-by-sign` |
| `src/api/b2bBilling.ts` | 84, 102 | a migrer | `/v1/b2b/billing/cycles/latest`, cycles history |
| `src/api/b2bEditorial.ts` | 75, 90 | a migrer | `/v1/b2b/editorial/config` GET/PATCH |
| `src/api/b2bUsage.ts` | 53 | a migrer | `/v1/b2b/usage/summary` |
| `src/api/billing.ts` | 262, 274, 286, 306, 326, 413, 429, 441, 453, 468, 482 | a migrer | billing, entitlements et Stripe sessions/actions |
| `src/api/client.ts` | 47 | owner canonique | transport HTTP central |
| `src/api/enterpriseCredentials.ts` | 81, 93, 105 | a migrer | credentials B2B |
| `src/api/geocoding.ts` | 50, 112, 147 | a migrer / classifier | appels geocoding et proxy backend; timeout 15s a preserver |
| `src/api/help.ts` | 65, 77, 93 | a migrer | help categories et tickets |
| `src/api/opsMonitoring.ts` | 42 | a migrer | ops monitoring KPIs |
| `src/api/support.ts` | 124, 153, 165, 184, 209 | a migrer | support context, incidents, search-by-email |

## Invariant attendu

Apres implementation, `fetch(` doit rester uniquement dans `src/api/client.ts`
pour les appels backend applicatifs, avec toute exception explicite classee.
