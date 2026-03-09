# Story 41.4 : Contrat API et UI centrés sur l'aide à la décision intraday

Status: backlog

## Story

En tant qu'utilisateur consultant `/dashboard`,
je veux voir quelques fenêtres claires avec des libellés actionnables et des drivers humanisés,
afin de comprendre rapidement à quels moments de la journée lancer une action, prendre une décision ou rester prudent.

## Acceptance Criteria

### AC1 — Le contrat API expose des fenêtres lisibles

- [ ] Le payload `/v1/predictions/daily` expose un champ lisible et stable pour les fenêtres décisionnelles
- [ ] Les drivers techniques ne remontent plus tels quels dans le contrat utilisateur final

### AC2 — `TodayPage` met en avant l'aide à la décision

- [ ] L'UI affiche en priorité 3 à 6 fenêtres maximum
- [ ] Chaque fenêtre présente une période, un ton actionnable, des domaines clés et un message utile
- [ ] La hiérarchie visuelle distingue clairement `moment fort`, `prudence`, `fenêtre favorable`

### AC3 — La timeline détaillée devient secondaire

- [ ] La chronologie complète peut rester disponible, mais elle n'est plus la vue principale du produit
- [ ] Les répétitions techniques sont masquées ou condensées

### AC4 — Les libellés sont entièrement humanisés

- [ ] Aucun label technique type `enter_orb` n'est visible dans le rendu final
- [ ] Les drivers affichés sont limités aux éléments vraiment utiles à l'utilisateur

### AC5 — Les tests frontend sont réalignés

- [ ] Les tests `TodayPage` et composants prediction couvrent les nouvelles fenêtres et le rendu orienté décision

## Tasks / Subtasks

### T1 — Étendre les types backend/front

- [ ] Ajouter les types API/TS nécessaires pour les fenêtres décisionnelles
- [ ] Préserver la compatibilité des consommateurs existants si nécessaire

### T2 — Revoir la présentation de `TodayPage`

- [ ] Créer ou adapter les composants de fenêtres décisionnelles
- [ ] Réduire le poids visuel de la timeline brute

### T3 — Humaniser complètement les drivers

- [ ] Étendre `predictionI18n`
- [ ] Filtrer les drivers de faible valeur produit

### T4 — Tests

- [ ] Mettre à jour `TodayPage.test.tsx`
- [ ] Ajouter des tests ciblés sur les nouveaux composants si nécessaire

## Dev Notes

- Cette story dépend du contrat backend produit par 41.3.
- Le but n'est pas seulement esthétique: l'information affichée doit devenir plus utile, plus rare et mieux hiérarchisée.

### Fichiers probables à toucher

- `backend/app/api/v1/routers/predictions.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/components/prediction/*`
- `frontend/src/utils/predictionI18n.ts`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
