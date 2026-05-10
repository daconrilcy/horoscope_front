<!-- Inventaire initial des enveloppes et parsers d'erreur API avant centralisation CS-132. -->

# CS-132 - Centralisation erreurs before

Commande executee depuis `frontend`:

```powershell
rg -l "ErrorEnvelope|ResponseEnvelope|parseError|toTransportError|extractAdminApiErrorMessage|throw new Error" src/api -g "*.ts"
```

## Fichiers avec duplication potentielle

`authMe.ts`, `auth.ts`, `adminContent.ts`, `astrologers.ts`,
`adminPrompts.ts`, `adminUsers.ts`, `adminOperations.ts`,
`adminDashboard.ts`, `adminLogs.ts`, `b2bAstrology.ts`, `b2bBilling.ts`,
`b2bEditorial.ts`, `b2bReconciliation.ts`, `b2bUsage.ts`, `billing.ts`,
`chat.ts`, `dailyPrediction.ts`, `enterpriseCredentials.ts`, `guidance.ts`,
`help.ts`, `natalChart.ts`, `opsMonitoring.ts`, `opsPersona.ts`,
`privacy.ts`, `support.ts`, `userSettings.ts`, `useBirthData.ts`.

## Classification initiale

Ces hits melangent types d'enveloppe locaux, parsers JSON locaux, wrappers
publics `*ApiError` et conversions generiques. CS-132 doit garder les wrappers
publics seulement s'ils deleguent au helper canonique et sont listes dans
`error-wrapper-map.md`.
