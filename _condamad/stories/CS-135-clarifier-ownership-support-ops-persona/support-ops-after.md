<!-- Preuve finale support/ops apres clarification d'ownership CS-135. -->

# CS-135 - Support / ops after

## Resultat

- `frontend/src/api/support.ts` n'importe plus `opsPersona`.
- `frontend/src/api/support.ts` n'exporte plus `useOpsRollbackPersona`.
- `SupportOpsPanel.tsx` importe `useOpsSearchUser` depuis l'owner support et
  `useRollbackOpsPersonaConfig` depuis l'owner ops persona.
- Le endpoint `/v1/support/users/context?email={email}` reste classe support
  dans `support-endpoint-classification.md`.

## Scan final

Commande:

```powershell
rg -n "useOpsRollbackPersona|opsPersona" src/api/support.ts src/features/support -g "*.ts" -g "*.tsx"
```

Resultat attendu: aucun hit dans `src/api/support.ts`; un hit acceptable dans
`SupportOpsPanel.tsx` car le panneau compose explicitement les owners support et
ops persona.
