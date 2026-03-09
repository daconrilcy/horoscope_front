# Story 41.5 : QA actionability et budget de bruit intraday

Status: backlog

## Story

En tant que QA engineer,
je veux mesurer automatiquement la qualité décisionnelle de la sortie intraday,
afin d'éviter qu'une timeline bruyante, répétitive ou techniquement correcte mais inutile n'atteigne l'utilisateur final.

## Acceptance Criteria

### AC1 — Les cas QA couvrent plusieurs journées contrastées

- [ ] Des fixtures couvrent des journées stables, contrastées, et à pivots réellement marqués
- [ ] Les attentes QA portent sur la valeur produit, pas seulement la validité technique du payload

### AC2 — Un budget de bruit est explicite

- [ ] Un budget de bruit intraday est défini (pivots max, répétitions max, drivers techniques visibles max)
- [ ] Les tests échouent si le budget est dépassé

### AC3 — L'actionnabilité est testée

- [ ] Les sorties QA permettent de vérifier qu'une journée utile contient quelques fenêtres claires et justifiées
- [ ] Les rapports distinguent `signal utile` et `bruit`

### AC4 — Le go/no-go intraday devient objectivable

- [ ] Le rapport QA produit des indicateurs simples pour décider si la sortie est exploitable côté utilisateur

## Tasks / Subtasks

### T1 — Définir les métriques QA intraday

- [ ] Définir les métriques de bruit et d'actionnabilité
- [ ] Documenter leurs seuils

### T2 — Étendre les fixtures et rapports QA

- [ ] Ajouter de nouveaux cas QA ciblés
- [ ] Mettre à jour les rapports et backlog produit associés

### T3 — Automatiser la vérification

- [ ] Ajouter des tests d'intégration / regression
- [ ] Vérifier la stabilité des résultats

## Dev Notes

- Cette story clôt le chantier en transformant les constats d'audit en garde-fous durables.
- Elle dépend des stories 41.1 à 41.4.

### Fichiers probables à toucher

- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `docs/qa/daily-prediction-qa-report-*.md`
- `docs/qa/product-adjustments-backlog.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
