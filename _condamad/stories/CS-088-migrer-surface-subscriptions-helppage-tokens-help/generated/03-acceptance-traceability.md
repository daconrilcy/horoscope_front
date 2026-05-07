# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Scope borne a subscriptions dans `HelpPage.css`. | Modifier uniquement le bloc subscriptions et les owners Help associes. | `hardcoded-values-before.md`, diff cible, scans Help. | Passed |
| AC2 | Chaque literal subscriptions a une decision finale. | Artefacts before/after listant migrated, registered-help-owner, typography-role, runtime-value ou kept-one-off-final. | `hardcoded-values-after.md` + scan AC7 limitation/deferred-work. | Passed |
| AC3 | Les valeurs repetables utilisent un owner Help documente. | Ajouter/consommer `--help-subscriptions-*` ou tokens globaux existants. | `npm run test -- design-system` + registre tokens/typographie. | Passed |
| AC4 | Aucun token tiers ni fallback non classe n'est introduit. | Ne pas utiliser namespaces page-scoped non Help, ni `var(--token, literal)`. | `npm run test -- css-fallback legacy-style` + scans namespaces interdits. | Passed |
| AC5 | La garde Help couvre la section subscriptions. | Etendre `design-system-guards.test.ts` avec une garde CS-088 ciblee. | `npm run test -- design-system`. | Passed |
| AC6 | Le rendu Help reste couvert. | Pas de changement React; conserver la route et la CSS chargee. | `npm run test -- visual-smoke HelpPage`, `npm run lint`, startup Vite. | Passed |
| AC7 | No Legacy respecte sans AC limitee. | Aucun deferred marker, shim, alias, fallback ou limitation dans les fichiers actifs touches. | Scans No Legacy, final evidence, registry RG-062. | Passed |
