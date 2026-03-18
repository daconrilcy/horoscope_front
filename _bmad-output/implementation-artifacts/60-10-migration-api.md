# Story 60.10 : Versionner le contrat API public et sécuriser la migration

Status: ready-for-dev

## Story

En tant qu'opérateur du système,
je veux que la migration vers le nouveau payload V4 ne casse pas le front en production,
afin de pouvoir déployer le backend et le frontend indépendamment sans regression.

## Acceptance Criteria

1. Tous les nouveaux champs (`day_climate`, `domain_ranking`, `time_windows`, `turning_point` singulier, `best_window`, `astro_foundation`) sont optionnels dans `DailyPredictionResponse` (default `None`) — le payload V3 reste valide.
2. Un flag `payload_version: str` est ajouté dans `DailyPredictionMeta` (`"v4"` si nouveaux champs présents, `"v3"` sinon).
3. Le front consomme les nouveaux champs seulement si présents, avec fallback vers l'ancien affichage si `payload_version != "v4"`.
4. Les anciens champs (`summary`, `categories`, `timeline`, `turning_points` liste, `decision_windows`, `micro_trends`) sont conservés dans le payload.
5. Les tests d'intégration API existants dans `backend/app/tests/integration/test_daily_prediction_api.py` passent sans modification.
6. Un test vérifie que le payload V4 ne casse pas un client qui ignore les nouveaux champs.
7. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Vérifier l'optionalité de tous les nouveaux champs (AC: 1)
  - [ ] T1.1 Lire `backend/app/api/v1/routers/predictions.py`
  - [ ] T1.2 S'assurer que `day_climate: DailyPredictionDayClimate | None = None`
  - [ ] T1.3 S'assurer que `domain_ranking: list[...] | None = None`
  - [ ] T1.4 S'assurer que `time_windows: list[...] | None = None`
  - [ ] T1.5 S'assurer que `turning_point: ... | None = None` (singulier)
  - [ ] T1.6 S'assurer que `best_window: ... | None = None`
  - [ ] T1.7 S'assurer que `astro_foundation: ... | None = None`

- [ ] T2 — Ajouter `payload_version` dans `DailyPredictionMeta` (AC: 2)
  - [ ] T2.1 Ajouter `payload_version: str = "v3"` dans `DailyPredictionMeta(BaseModel)`
  - [ ] T2.2 Dans `PublicPredictionAssembler.assemble()`, si au moins un nouveau champ est présent → `payload_version = "v4"`
  - [ ] T2.3 Mettre à jour `DailyPredictionMeta` dans le DTO Pydantic

- [ ] T3 — Mettre à jour le type TypeScript (AC: 3)
  - [ ] T3.1 Ajouter `payload_version?: string` dans `DailyPredictionMeta` TypeScript
  - [ ] T3.2 Dans `DailyHoroscopePage.tsx`, wrapper le rendu des nouveaux composants :
    ```typescript
    const isV4 = data.meta?.payload_version === "v4";
    // Nouveaux composants : seulement si V4 ou fallback si champ présent
    {(isV4 && data.day_climate) && <DayClimateHero climate={data.day_climate} />}
    {(!isV4 || !data.day_climate) && <HeroSummaryCard ... />}  // fallback
    ```
  - [ ] T3.3 Appliquer la même logique pour chaque nouveau composant

- [ ] T4 — S'assurer que les anciens champs sont inchangés (AC: 4)
  - [ ] T4.1 `summary` dans `DailyPredictionResponse` : inchangé
  - [ ] T4.2 `categories` : inchangé (catégories internes)
  - [ ] T4.3 `timeline` : inchangé
  - [ ] T4.4 `turning_points` (liste) : inchangé
  - [ ] T4.5 `decision_windows` : inchangé
  - [ ] T4.6 `micro_trends` : inchangé

- [ ] T5 — Tests de non-régression (AC: 5, 6)
  - [ ] T5.1 Lire `backend/app/tests/integration/test_daily_prediction_api.py`
  - [ ] T5.2 Vérifier que ces tests passent sans modification
  - [ ] T5.3 Ajouter un test : payload avec `payload_version="v4"` contient tous les anciens champs
  - [ ] T5.4 Ajouter un test : un client qui ne lit que les champs V3 (`summary`, `categories`) ne plante pas sur un payload V4

- [ ] T6 — Documentation du contrat de migration (AC: 3)
  - [ ] T6.1 Créer ou mettre à jour `docs/agent/payload-migration-v3-v4.md` avec :
    - Champs ajoutés V4 (liste)
    - Champs supprimés (aucun à ce stade)
    - Procédure de déploiement (backend V4 first, puis front)
    - Plan de suppression du legacy (Story 60.12)

## Dev Notes

### Stratégie de migration (zero downtime)

**Phase 1 — Backend V4 déployé, Front V3 actif :**
- Backend retourne les nouveaux champs (`payload_version: "v4"`)
- Front V3 ignore les nouveaux champs (JSON inconnu = ignoré par TypeScript strict)
- Pas de régression

**Phase 2 — Front V4 déployé :**
- Front lit `payload_version` et switche les composants
- Si backend V3 encore actif quelque part → front reste sur anciens composants

**Phase 3 — Cleanup (Story 60.12) :**
- Supprimer le code fallback V3 du front
- Supprimer les anciens champs du payload si décision prise

### Compatibilité Pydantic
Pydantic v2 ignore par défaut les champs supplémentaires (`model_config = ConfigDict(extra="ignore")`). Vérifier que la config Pydantic du projet l'accepte.

### Tests existants
- `backend/app/tests/integration/test_daily_prediction_api.py` — tests existants à ne pas casser
- `backend/app/tests/integration/test_daily_prediction_flat_day.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `frontend/src/tests/dailyPredictionApi.test.ts` — tests TypeScript à mettre à jour

### Project Structure Notes
- Modification: `backend/app/api/v1/routers/predictions.py` — `payload_version` dans meta
- Modification: `backend/app/prediction/public_projection.py` — set payload_version
- Modification: `frontend/src/types/dailyPrediction.ts` — payload_version
- Modification: `frontend/src/pages/DailyHoroscopePage.tsx` — logique fallback V3/V4
- Nouveau doc: `docs/agent/payload-migration-v3-v4.md`

### References
- [Source: backend/app/api/v1/routers/predictions.py] — DailyPredictionResponse, DailyPredictionMeta
- [Source: backend/app/tests/integration/test_daily_prediction_api.py] — tests à préserver
- [Source: frontend/src/pages/DailyHoroscopePage.tsx] — page principale
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
