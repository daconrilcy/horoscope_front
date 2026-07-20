<!-- Story de refonte editoriale et visuelle du guide debutant de la page natal. -->

# Refonte éditoriale de `natal-chart-guide`

Status: implemented

## Goal

Aligner le guide de lecture de `/natal` sur les interprétations Astral récentes et fournir
aux débutants un parcours progressif, ludique, accessible et lisible sur mobile.

## Current State Evidence

- Evidence 1: `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage.
- Evidence 2: `_condamad/reports/natal-chart-guide-editorial-analysis.md` - comparaison
  anonymisée des lectures récentes, contrats et ancien guide.
- Evidence 3: `frontend/src/i18n/natalChart.ts` - propriétaire canonique du contenu du guide ;
  aucun contenu équivalent n'est stocké dans le backend.

## Acceptance Criteria

1. Le guide explique la synthèse, les chapitres, les quatre clés de lecture, les dominantes,
   les axes, les maîtres de maisons, les rôles cœur/appui/nuance et la confiance.
2. Les contenus et contrôles sont disponibles en FR, EN et ES avec fallback FR.
3. Le panneau est replié par défaut et conserve `aria-expanded` et `aria-controls`.
4. Toutes les sous-grilles passent en une colonne à 360, 390 et 430 px sans débordement.
5. Une lecture partielle affiche une note qui nuance les repères dépendant de données de
   naissance complètes ou précises.
6. Les thèmes clair et sombre conservent un contraste d'au moins 4,5:1 sur les petits
   libellés et le bouton.
7. Aucun style inline, changement backend ou changement du lancement Astral n'est introduit.

## Explicit non-goals

- Ne pas modifier les contrats, routes, calculs ou données persistées du backend.
- Ne pas modifier la soumission, le polling ou la reprise des jobs Astral (`RG-180`).
- Ne pas modifier la composition progressive des chapitres publics (`RG-182`).
- Ne pas réduire les garanties mobile et typographiques de `/natal` (`RG-183`, `RG-184`).

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-180` - la page conserve son comportement de soumission Astral.
  - `RG-182` - le guide reste dans la lecture progressive existante.
  - `RG-183` - le guide développé ne déborde pas sur mobile.
  - `RG-184` - le guide réutilise les tokens et la largeur de la lecture.
  - `RG-186` - les textes éditoriaux continuent de passer par `EditorialText`.
  - `RG-187` - le nouveau contrat du guide est protégé par des preuves dédiées.
- Non-applicable invariants:
  - `RG-175` - aucune route ou capacité backend n'est remontée.
  - `RG-178` - aucun appel direct à Astral n'est ajouté au frontend.
- Required regression evidence:
  - Tests Vitest du guide, de la page, des tokens et de la politique de styles.
  - E2E desktop, clair/sombre et mobile 360/390/430.
  - Scan zéro style inline dans `NatalChartGuide.tsx`.
- Allowed differences:
  - Contenu, structure interne, traductions et styles de `natal-chart-guide`.

## Validation Plan

```powershell
pnpm --dir frontend lint
pnpm --dir frontend build
pnpm --dir frontend test -- src/tests/NatalChartGuide.test.tsx src/tests/NatalChartPage.test.tsx src/tests/editorial-text-coverage.test.ts src/tests/theme-tokens.test.ts src/tests/inline-style-policy.test.ts
pnpm --dir frontend test:e2e -- cs-423-natal-basic-readable.spec.ts cs-445-natal-mobile.spec.ts
rg -n "style=\{\{" frontend/src/components/NatalChartGuide.tsx
```
