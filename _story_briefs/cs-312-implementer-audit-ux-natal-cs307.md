# CS-312 — Implémenter L'Audit UX /natal Resté Ouvert Après CS-307

## Résumé

CS-307 a été rédigée et relue, mais son implémentation n'est pas prouvée. Cette story exécute réellement l'audit UX `/natal`, capture les preuves navigateur attendues et corrige uniquement les irritants UI démontrés.

## Contexte

Le rapport `_condamad/reports/CS-307-CS-311-delivery-report.md` classe CS-307 en `Not evidenced`: la story est `ready-to-dev`, il n'existe pas de `generated/10-final-evidence.md`, ni d'artefacts `ux-audit-*`, `browser-qa.md`, screenshots ou validation CS-307.

## Objectif

Fermer CS-307 par une implémentation complète, traçable et validée de l'audit UX `/natal` après wiring des projections B2C.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-307-CS-311-delivery-report.md`
- `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Périmètre inclus

1. Générer ou compléter le capsule CS-307 manquant, dont `generated/10-final-evidence.md`.
2. Créer les artefacts `ux-audit-before.md`, `ux-audit-after.md`, `browser-qa.md`, `product-decisions.md` et `validation.txt`.
3. Ouvrir `/natal` en navigateur réel sur desktop, tablette et mobile, avec captures persistées.
4. Vérifier loading, success, empty, error, entitlement, degraded et disclaimer.
5. Corriger uniquement les défauts UX prouvés dans les owners existants React/CSS.
6. Ajouter ou ajuster les tests Vitest ciblés des états corrigés.
7. Mettre CS-307 et le registre en `done` uniquement si les validations passent.

## Hors périmètre

- Refaire le design complet de `/natal`.
- Modifier backend, contrats API, plans, prompts, providers, DB ou migrations.
- Ajouter des styles inline ou un nouveau système de composants.
- Décider une stratégie produit non validée dans le code.

## Critères d'acceptation

1. CS-307 possède un `generated/10-final-evidence.md` complet.
2. Les artefacts d'audit UX avant/après et le ledger navigateur sont présents.
3. Les captures desktop, tablette et mobile prouvent l'absence de chevauchement critique.
4. Tous les états projection/disclaimer restent visibles et compréhensibles.
5. Les corrections sont limitées aux owners existants et sans style inline.
6. Les tests ciblés, `pnpm lint` et les scans d'ownership passent.
7. Les décisions produit restantes sont documentées hors code dans `product-decisions.md`.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Scans depuis la racine :

```powershell
rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages -g "*.tsx"
rg -n "fetch\(.*/v1/astrology/projections|axios\(.*/v1/astrology/projections" frontend/src
```

## Risques

Le risque principal est de transformer un audit UX ciblé en redesign. Toute correction doit être reliée à une ligne du ledger navigateur ou à un test.
