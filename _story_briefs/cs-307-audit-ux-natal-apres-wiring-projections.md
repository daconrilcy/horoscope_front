# CS-307 — Audit UX /natal Après Wiring Projections

## Résumé

Auditer l'expérience utilisateur réelle de `/natal` après le branchement des projections B2C afin d'identifier et corriger les irritants de lecture, hiérarchie, états UI et responsive.

## Contexte

CS-303 a branché `/natal` sur `POST /v1/astrology/projections`, CS-305 a stabilisé la suite frontend complète et CS-306 a prouvé le rendu navigateur desktop/mobile. Il faut maintenant passer d'une preuve technique à une revue produit UX structurée pour vérifier que l'expérience est compréhensible, lisible et cohérente pour un utilisateur B2C.

## Objectif

Produire un audit UX actionnable de `/natal` après wiring projections, corriger les défauts évidents dans le périmètre UI existant, et documenter les arbitrages qui nécessitent une décision produit.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/pages/NatalChartPage.tsx`

## Périmètre inclus

1. Auditer la hiérarchie visuelle de `/natal` avec les blocs `beginner_summary_v1` et `client_interpretation_projection_v1`.
2. Vérifier la lisibilité des cartes, titres, états, messages d'erreur et disclaimers.
3. Vérifier desktop, tablette et mobile, avec captures avant/après si correction.
4. Corriger les défauts UI évidents : chevauchement, densité excessive, ordre confus, libellé de bouton ambigu, état vide mal placé.
5. Conserver les styles dans les fichiers CSS existants et réutiliser les variables/tokens disponibles.
6. Ajouter ou ajuster les tests frontend ciblés pour couvrir les états UX corrigés.
7. Produire une note d'audit avec les points corrigés, les points acceptés et les décisions produit restantes.

## Hors périmètre

- Reconcevoir entièrement `/natal`.
- Modifier les projections backend ou leurs payloads.
- Changer les plans free/basic/premium.
- Ajouter une nouvelle page marketing.
- Ajouter des styles inline.
- Ajouter une dépendance UI.

## Critères d'acceptation

1. Un audit UX daté liste les problèmes inspectés et leur décision : corrigé, acceptable, ou décision produit requise.
2. Les corrections UI restent dans les composants et CSS existants.
3. Aucun texte ou contrôle critique ne se chevauche sur desktop et mobile.
4. Les états loading, success, empty, error, entitlement et degraded restent visibles et compréhensibles.
5. Les disclaimers restent app-owned et visibles sans occulter la lecture principale.
6. Les tests ciblés `/natal` et `natalInterpretation` passent.
7. La suite frontend complète passe ou toute limite est documentée avec preuve.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Prévoir une vérification navigateur réelle desktop et mobile avec captures ou ledger QA.

## Dépendances

- CS-303.
- CS-305.
- CS-306.

## Risques

Le risque principal est de transformer un audit UX en refonte large. Cette story doit corriger uniquement les défauts prouvés et laisser les arbitrages produit non évidents dans une section de décisions restantes.
