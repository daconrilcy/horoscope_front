<!-- Baseline support/ops avant clarification d'ownership CS-135. -->

# CS-135 - Support / ops before

Commande executee depuis `frontend`:

```powershell
rg -n "useOpsRollbackPersona|opsPersona" src/api/support.ts src/features/support -g "*.ts" -g "*.tsx"
```

## Audit de suppression / remplacement

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `support.ts` import `useRollbackOpsPersonaConfig as useOpsRollbackPersona` | cross-domain facade | historical-facade | `SupportOpsPanel.tsx` via `@api` | import direct depuis `src/api/opsPersona.ts` | replace-consumer | scan support/ops initial | le panneau support casse si l'import n'est pas adapte |
| `support.ts` export `useOpsRollbackPersona` | cross-domain facade | historical-facade | `SupportOpsPanel.tsx` | `useRollbackOpsPersonaConfig` | delete | scan support/ops initial | reintroduction d'un owner ops dans support |
| `/v1/support/users/context?email={email}` | support endpoint client | canonical-active | `useOpsSearchUser` | reste dans `support.ts` apres classification | keep | endpoint nomme support et payload `SupportUserContext` | verification backend runtime hors scope de cette story |

## Hits initiaux

- `src/api/support.ts:199` importe le hook ops persona depuis `./opsPersona`.
- `src/api/support.ts:201` exporte `useOpsRollbackPersona`.
- `src/features/support/SupportOpsPanel.tsx:4` consomme `useOpsRollbackPersona` depuis `@api`.
- `src/features/support/SupportOpsPanel.tsx:24` utilise le hook rollback.
