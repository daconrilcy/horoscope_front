# Story 60.3 : Séparer clairement le climat global du classement des domaines

Status: ready-for-dev

## Story

En tant qu'utilisateur,
je veux voir un bloc hero qui résume le climat global de ma journée en 3 secondes,
afin de comprendre le ton général sans avoir à parcourir la liste des domaines.

## Acceptance Criteria

1. Le payload expose un objet `day_climate` structuré (non inclus dans `summary` existant).
2. `day_climate` contient : `label: str`, `tone: str`, `intensity: float`, `stability: float`, `summary: str`, `top_domains: list[str]` (max 2), `watchout: str | None` (max 1), `best_window_ref: str | None`.
3. `label` est un texte court non technique (ex: "Climat stable et fluide", "Journée de progression soutenue") — jamais "équilibré" seul.
4. `tone` reprend les valeurs existantes : `"positive"`, `"mixed"`, `"neutral"`, `"negative"`.
5. `intensity` et `stability` sont dérivés de `V3DailyMetrics` (via `aggregator.py`) — normalisés [0-10].
6. `top_domains` contient les clefs publiques (60.1) des 2 domaines les mieux classés.
7. `watchout` est le domaine public le moins bien classé si `score_10 < 5.0`, sinon `None`.
8. `best_window_ref` pointe vers le créneau horaire de la meilleure fenêtre (format "HH:MM–HH:MM") si disponible.
9. Le `summary` existant dans `DailyPredictionSummary` est conservé (rétrocompat).
10. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Créer `PublicDayClimatePolicy` dans `public_projection.py` (AC: 1, 2)
  - [ ] T1.1 Lire entièrement `backend/app/prediction/public_projection.py` (classes: PublicSummaryPolicy, PublicCategoryPolicy)
  - [ ] T1.2 Créer classe `PublicDayClimatePolicy` avec méthode `build(engine_output, domain_ranking, decision_windows) -> dict`
  - [ ] T1.3 `label` : choisir parmi un dictionnaire statique selon `tone + intensity` combinés
  - [ ] T1.4 `top_domains` : prendre les 2 premiers items de `domain_ranking` (Story 60.1 → keys publics)
  - [ ] T1.5 `watchout` : dernier domaine si score_10 < 5.0
  - [ ] T1.6 `best_window_ref` : formatter `start_local` de la meilleure `decision_window`

- [ ] T2 — Dériver `intensity` et `stability` depuis les métriques V3 (AC: 5)
  - [ ] T2.1 Lire `backend/app/prediction/aggregator.py` — `V3DailyMetrics.intensity_day`, `V3DailyMetrics.stability_day`
  - [ ] T2.2 `intensity = round(avg_intensity_day / 2, 1)` — normalise [0-20] → [0-10]
  - [ ] T2.3 `stability = round(avg_stability_day / 2, 1)` — idem
  - [ ] T2.4 Si métriques V3 absentes → fallback depuis `summary.overall_tone` avec valeurs nominales

- [ ] T3 — Dictionnaire de labels (AC: 3)
  - [ ] T3.1 Créer `CLIMATE_LABELS: dict[(tone, intensity_bucket), str]` dans `public_domain_taxonomy.py` ou nouveau fichier `public_label_catalog.py`
  - [ ] T3.2 `intensity_bucket` : "low" (0–3.9), "medium" (4.0–6.9), "high" (7.0–10.0)
  - [ ] T3.3 Exemples de labels (à compléter exhaustivement) :
    - (positive, high) → "Journée de forte progression"
    - (positive, medium) → "Élan favorable"
    - (positive, low) → "Douceur portante"
    - (neutral, medium) → "Climat stable et fluide"
    - (mixed, medium) → "Journée en relief"
    - (negative, high) → "Journée exigeante"
    - Fallback → "Journée en cours"

- [ ] T4 — Intégrer dans `PublicPredictionAssembler.assemble()` (AC: 1, 9)
  - [ ] T4.1 Appeler `PublicDayClimatePolicy.build()` après `PublicCategoryPolicy` et `PublicDecisionWindowPolicy`
  - [ ] T4.2 Ajouter `day_climate: dict` dans le dict de retour de `assemble()`
  - [ ] T4.3 Ne pas supprimer `summary` existant

- [ ] T5 — Mettre à jour le DTO Pydantic (AC: 1)
  - [ ] T5.1 Créer `DailyPredictionDayClimate(BaseModel)` dans `predictions.py`
  - [ ] T5.2 Ajouter `day_climate: DailyPredictionDayClimate | None = None` dans `DailyPredictionResponse`

- [ ] T6 — Tests (AC: 10)
  - [ ] T6.1 Test : `build()` retourne un `day_climate` avec tous les champs requis
  - [ ] T6.2 Test : `top_domains` ≤ 2 items
  - [ ] T6.3 Test : `watchout = None` si tous les scores > 5.0
  - [ ] T6.4 Test : `watchout` renseigné si domaine public score_10 < 5.0

## Dev Notes

### Contexte — Problème actuel
`HeroSummaryCard` actuel (front) affiche le `summary` + les `top_categories` (codes internes) + le `best_window`. Cela duplique les informations du bloc domaines. Le nouveau `day_climate` sépare la narration globale de la liste exhaustive des domaines.

### PublicPredictionAssembler — données disponibles
La méthode `assemble()` reçoit `engine_output` qui contient :
- `snapshot` avec `V3EvidencePack` (themes, time_windows, turning_points)
- `V3EvidencePack.day_profile` → contient overall_tone, avg_score
- Résultats de `V3ThemeAggregator` → `V3DailyMetrics` par catégorie (intensity_day, stability_day)

### Label catalog — règle de fallback
Si aucun label n'est trouvé dans le dictionnaire → retourner `"Journée en cours"`. Jamais retourner `None` pour `label`.

### Champ `summary` dans day_climate
Ce résumé est distinct du `summary.overall_summary` existant (texte IA long). Le `day_climate.summary` est une courte phrase synthétique (max 15 mots) générée par règles statiques, non par LLM.

### Project Structure Notes
- Modification: `backend/app/prediction/public_projection.py` (nouvelle classe `PublicDayClimatePolicy`)
- Nouveau fichier optionnel: `backend/app/prediction/public_label_catalog.py` (dictionnaire labels)
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Dépend de: Story 60.1 (domaines publics), Story 60.2 (score_10)

### References
- [Source: backend/app/prediction/public_projection.py#PublicSummaryPolicy] — logique résumé actuelle
- [Source: backend/app/prediction/aggregator.py#V3DailyMetrics] — intensity_day, stability_day
- [Source: backend/app/api/v1/routers/predictions.py#DailyPredictionSummary] — à conserver
- [Source: frontend/src/utils/heroSummaryCardMapper.ts] — logique front actuelle à remplacer
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
