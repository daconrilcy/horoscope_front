<!-- Inventaire de la surface publique @api pour la decision CS-136. -->

# CS-136 - Inventaire surface publique API

## Exports actuels de `frontend/src/api/index.ts`

`client`, `auth`, `authMe`, `astrologers`, `birthProfile`,
`dailyPrediction`, `natalChart`, `chat`, `consultations`, `geocoding`,
`billing`, `privacy`, `support`, `guidance`, `opsMonitoring`, `opsPersona`,
`adminPrompts`, `adminContent`, `adminDashboard`, `adminLogs`,
`adminOperations`, `adminUsers`, `b2bAstrology`, `b2bBilling`,
`b2bEditorial`, `b2bReconciliation`, `b2bUsage`, `enterpriseCredentials`,
`useBirthData`, `useDailyPrediction`.

## Consommateurs observes

Commande executee depuis `frontend`:

```powershell
rg -n 'from [''"]@api|from [''"]../api|from [''"]../../api' src -g "*.ts" -g "*.tsx"
```

Constats:

- `@api` global est consomme par auth, admin prompts, pages admin/content,
  pages publiques, tests B2B, tests daily/natal et composants de consultation.
- Des entrypoints de domaine `@api/<module>` sont deja utilises pour billing,
  geocoding, help, userSettings, authMe, astrologers, consultations et chat.
- Des imports relatifs directs vers `../api/<module>` et `../../api/<module>`
  coexistent dans les pages, features, hooks, utils et tests.
- Un import interne interdit etait present dans `src/api/useDailyPrediction.ts`
  avant CS-134.

## Modules ambigus demandes par CS-136

Commande executee depuis `frontend`:

```powershell
rg -n "b2bAstrology|b2bBilling|b2bEditorial|b2bUsage|guidance|opsMonitoring" src -g "*.ts" -g "*.tsx"
```

Constats:

- `guidance.ts` a des tests runtime sous `src/tests/guidanceApi.test.ts`.
- `b2bEditorial.ts` a des tests runtime sous `src/tests/b2bEditorialApi.test.ts`.
- `b2bAstrology`, `b2bBilling` et `b2bUsage` sont exports par `@api` et testes
  via les tests B2B correspondants.
- `opsMonitoring.ts` est exporte par `@api`; aucun consommateur runtime hors
  barrel n'a ete observe dans ce scan.
