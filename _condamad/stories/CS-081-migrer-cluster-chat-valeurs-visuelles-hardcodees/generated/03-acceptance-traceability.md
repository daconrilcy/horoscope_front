# Acceptance Traceability - CS-081

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le cluster est borne aux surfaces chat selectionnees. | Modifier uniquement les CSS chat, le registre token, le test guard et les artefacts de story. | `hardcoded-values-before.md`, `git diff --stat`, scans cibles. | PASS |
| AC2 | Chaque literal a une decision finale. | Centraliser les valeurs sous `--chat-*` ou tokens existants et classer les hits restants. | `hardcoded-values-after.md` et scan de vocabulaire interdit sur l'artefact. | PASS |
| AC3 | Les valeurs repetables utilisent un owner documente. | Ajouter le namespace `--chat-*` dans `token-namespace-registry.md` et consommer les variables. | `npm run test -- theme-tokens design-system`. | PASS |
| AC4 | Les guards de style interdit restent verts. | Ne pas elargir les allowlists inline-style ou css-fallback. | `npm run test -- css-fallback inline-style legacy-style`. | PASS |
| AC5 | Le rendu chat reste couvert. | Ne pas modifier React; garder les surfaces rendues par smoke/design-system. | `npm run test -- visual-smoke design-system`. | PASS |
| AC6 | Les literals migres ne peuvent pas revenir silencieusement. | Ajouter une garde CS-081 dans `design-system-guards.test.ts`. | `npm run test -- design-system` et scans after. | PASS |
| AC7 | Aucune AC partielle n'est acceptee. | Evidence finale complete sans statut incomplet. | Scan final sur `generated/10-final-evidence.md`. | PASS |
