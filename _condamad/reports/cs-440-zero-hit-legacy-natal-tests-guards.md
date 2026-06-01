# Rapport CS-440 zero-hit legacy natal

<!-- Commentaire global: ce rapport finalise la fermeture des anciens symboles natals cote tests, guards et preuves. -->

## Synthese

- Story: `CS-440-zero-hit-legacy-natal-tests-guards`
- Statut: `ready-to-review`
- Guardrail durable: `RG-174`
- Public generation canonique: `POST /v1/theme-natal/readings`
- Ancien endpoint public: `POST /v1/natal/interpretation` documente et teste en `410 Gone`.

## Resultats

| Controle | Resultat | Preuve |
|---|---|---|
| `natal_interpretation_short` | aucun hit generateur public non autorise | architecture guard + extinction tests |
| `natal_long_free` | aucun hit generateur public non autorise | architecture guard + adapter reject guard |
| `use_case_level` | absent du contrat public theme natal; present seulement en tests de rejet et API interne LLM QA admin-only | OpenAPI + `test_new_route_rejects_legacy_generation_fields` + architecture guard |
| `forceRefresh` | absent du runtime public; present seulement en tests de rejet/DOM denylist | scans bornes + frontend guard |
| `shouldRefreshShortAfterBasicUpgrade` | absent du runtime public; present seulement en DOM denylist | scans bornes + frontend guard |
| `variant_code` | conserve pour entitlement, prediction/daily, astrologie ou historique; jamais champ de commande theme natal | OpenAPI + tests product action |

## Scans attendus

Les scans negatifs doivent etre interpretes avec `rg` code 1 comme `PASS: no matches` quand le motif cherche une absence.

```powershell
rg -n "shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src
rg -n "use_case_level" backend/app/services/api_contracts/public backend/app/api/v1/routers/public frontend/src/api/natal-chart frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation|patch\.object\(AIEngineAdapter, `"generate_natal_interpretation`"" backend/app backend/tests
```

## Residus classes

- `natal_interpretation_short`: readonly historique ou garde de rejet uniquement.
- `natal_long_free`: readonly historique, admin-only metadata ou garde de rejet uniquement.
- `use_case_level`: API interne LLM QA admin-only et tests de rejet publics.
- `variant_code`: entitlement, prediction/daily, calcul astrologique et donnees historiques.
- Les preuves historiques `_condamad` restent conservees et ne sont pas des chemins runtime.

## Risques residuels

- Les stories CS-436 a CS-438 restent separees dans le tracker; CS-440 verrouille les retours non autorises mais ne supprime pas les compatibilites readonly historiques hors scope.
