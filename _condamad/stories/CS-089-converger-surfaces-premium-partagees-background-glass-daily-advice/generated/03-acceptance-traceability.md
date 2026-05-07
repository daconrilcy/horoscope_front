<!-- Matrice de tracabilite AC pour la story CS-089. -->

# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Scope borne aux quatre fichiers premium exacts. | `hardcoded-values-before.md`, diff borne aux surfaces premium et registres/tests. | Scans cibles des quatre fichiers executes. | PASS |
| AC2 | Chaque valeur premium a un owner final documente. | Owners `--premium-*` et `--glass-*`, `hardcoded-values-after.md`. | Evidence finale sans statut limite ni TODO. | PASS |
| AC3 | Les backgrounds premium partages convergent vers `premium-theme.css`. | `premium-theme.css`, `backgrounds.css`, `token-namespace-registry.md`. | `npm run test -- theme-tokens design-system` PASS via suite cible. | PASS |
| AC4 | Les surfaces glass convergent vers `glass.css` sans double owner local. | Registre namespaces, absence de double owner local daily glass. | `npm run test -- css-fallback legacy-style` PASS via suite cible. | PASS |
| AC5 | Daily Horoscope et Daily Advice consomment les owners partages. | `DailyHoroscopePage.css` et `DailyAdviceCard.css` consomment `--premium-*` et `--glass-*`. | `npm run test -- DailyHoroscopePage visual-smoke theme-tokens` PASS via suite cible. | PASS |
| AC6 | Guard anti-retour durable pour CS-089. | Guard CS-089 dans `design-system-guards.test.ts`, `RG-063`. | `npm run test -- design-system` PASS via suite cible et suite complete. | PASS |
| AC7 | No Legacy respecte sans limitation. | No Legacy scans et evidence finale. | Scan vocabulaire interdit zero-hit et story lint PASS. | PASS |
