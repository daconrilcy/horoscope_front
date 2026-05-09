<!-- Matrice de tracabilite des criteres d'acceptation CS-119. -->

# Acceptance Traceability - CS-119

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Inventorier tous les composants courants avant suppression. | `test-only-component-removal-before.md` ajoute. | `npm run test -- component-usage component-architecture design-system visual-smoke` PASS et artefact before. | PASS |
| AC2 | Supprimer physiquement tous les candidats confirmes test-only. | Composants, CSS orphelins et tests focalises supprimes. | `Test-Path` inventory all `False`; scans negatifs PASS. | PASS |
| AC3 | Supprimer les tests focalises et conserver les guards transverses utiles. | `design-system-guards.test.ts` et `visual-smoke.test.tsx` adaptes. | `npm run test -- component-usage component-architecture design-system visual-smoke` PASS. | PASS |
| AC4 | Nettoyer les allowlists sans exception stale ou large. | `component-usage-allowlist.ts` et `component-architecture-allowlist.ts` nettoyes. | `npm run test -- component-usage component-architecture` inclus dans suite ciblee PASS. | PASS |
| AC5 | Retirer toute reference active aux symboles/modules supprimes. | Type-only import, imports tests, imports CSS et allowlist rows retires. | Scans `rg` cibles zero-hit sous `frontend/src`. | PASS |
| AC6 | Garder la validation frontend verte. | Code TypeScript et tests coherents apres suppression. | `npm run test -- component-usage component-architecture design-system visual-smoke` PASS; `npm run lint` PASS. | PASS |
| AC7 | Proteger contre la reintroduction des chemins interdits. | Guard CS-119 ajoute dans `component-usage-guards.test.ts`. | `npm run test -- component-usage` inclus dans suite ciblee PASS. | PASS |
| AC8 | Prouver la fermeture sans residu cache. | `test-only-component-removal-after.md` et `validation-evidence.md` ajoutes. | Artefact after, scans negatifs et tests ciblees PASS. | PASS |
