# Story 38.4 : Analytics et instrumentation usage

Status: ready-for-dev

## Story

As a product owner de l'application horoscope,
I want que le parcours de la prédiction quotidienne soit instrumenté côté frontend (événements analytics) et côté backend (métriques et logs structurés),
so that je dispose de données d'usage réelles pour piloter les itérations produit sans stocker de données personnelles inutiles.

## Acceptance Criteria

### AC1 — 6 événements analytics frontend définis et envoyés

Les événements `prediction_viewed`, `category_clicked`, `timeline_opened`, `turning_point_opened`, `prediction_refreshed` et `history_viewed` sont définis dans `frontend/src/utils/analytics.ts` et appelés depuis les composants appropriés de la feature prédiction (story 36-4).

### AC2 — Métriques backend loggées via le système d'observabilité existant

Le `DailyPredictionService` logue les métriques (durée de calcul, `was_reused`, `has_pivots`, `overall_tone`) via le module `backend/app/infra/observability/` existant. Les compteurs `prediction.compute` et `prediction.reused` sont incrémentés.

### AC3 — Aucune donnée sensible inutile dans les événements frontend

Les événements analytics frontend ne contiennent ni `natal_chart`, ni scores bruts de catégories (`note_20`), ni aucun identifiant personnel directement exploitable. Les props se limitent à des codes de catégorie, des booléens et des codes de sévérité.

### AC4 — Client analytics frontend minimal sans dépendance externe lourde

`frontend/src/utils/analytics.ts` est un utilitaire autonome qui délègue à `window.analytics.track` si disponible, sans imposer aucune bibliothèque analytics tierce. La seule sortie garantie est `console.debug` en mode DEV.

### AC5 — Métriques backend visibles dans les logs structurés

Les logs produits par `DailyPredictionService` contiennent les champs `user_id`, `duration_ms`, `was_reused`, `has_pivots`, `overall_tone` sous forme de `extra={}` logging Python, visibles avec un formateur JSON.

## Tasks / Subtasks

### T1 — Créer `frontend/src/utils/analytics.ts` (AC1, AC3, AC4)

- [ ] Créer `frontend/src/utils/analytics.ts` :
  - [ ] Exporter `function trackEvent(name: string, props: Record<string, unknown> = {}): void`
  - [ ] Déléguer à `window.analytics.track` si disponible
  - [ ] Logger via `console.debug('[analytics]', name, props)` uniquement en `import.meta.env.DEV`
  - [ ] Exporter les constantes de noms d'événements :
    ```typescript
    export const EVENTS = {
      PREDICTION_VIEWED: 'prediction_viewed',
      CATEGORY_CLICKED: 'category_clicked',
      TIMELINE_OPENED: 'timeline_opened',
      TURNING_POINT_OPENED: 'turning_point_opened',
      PREDICTION_REFRESHED: 'prediction_refreshed',
      HISTORY_VIEWED: 'history_viewed',
    } as const
    ```

### T2 — Ajouter les 6 appels trackEvent dans les composants prediction (AC1, AC3)

- [ ] Dans le composant principal de prédiction quotidienne (story 36-4) :
  - [ ] `trackEvent(EVENTS.PREDICTION_VIEWED, { date: dateStr, was_reused: boolean })` — au montage du composant
  - [ ] `trackEvent(EVENTS.PREDICTION_REFRESHED)` — au clic sur le bouton de rafraîchissement
- [ ] Dans le composant de catégorie :
  - [ ] `trackEvent(EVENTS.CATEGORY_CLICKED, { category_code: string })` — au clic sur une catégorie (NE PAS inclure `note_20`)
- [ ] Dans le composant timeline :
  - [ ] `trackEvent(EVENTS.TIMELINE_OPENED)` — à l'ouverture de la section timeline
- [ ] Dans le composant turning point / pivot :
  - [ ] `trackEvent(EVENTS.TURNING_POINT_OPENED, { severity: string })` — à l'ouverture d'un pivot (severity = code de sévérité, pas de note brute)
- [ ] Dans le composant historique :
  - [ ] `trackEvent(EVENTS.HISTORY_VIEWED, { range_days: number })` — à l'ouverture de l'historique

### T3 — Ajouter logs structurés dans DailyPredictionService (AC2, AC5)

- [ ] Dans `backend/app/services/daily_prediction_service.py`, ajouter en début de `get_or_compute()` :
  ```python
  import logging, time
  logger = logging.getLogger(__name__)
  start = time.perf_counter()
  ```
- [ ] En fin de `get_or_compute()`, avant le `return` :
  ```python
  duration_ms = int((time.perf_counter() - start) * 1000)
  logger.info("prediction.run", extra={
      "user_id": user_id,
      "duration_ms": duration_ms,
      "was_reused": result.was_reused,
      "has_pivots": bool(result.engine_output and result.engine_output.pivots),
      "overall_tone": result.engine_output.overall_tone if result.engine_output else None,
  })
  ```
- [ ] Vérifier que le logger est nommé par module (`__name__`) et non hardcodé

### T4 — Ajouter les compteurs observabilité backend (AC2)

- [ ] Dans `DailyPredictionService.get_or_compute()` :
  - [ ] Importer depuis `backend/app/infra/observability/metrics.py` : `increment_counter`
  - [ ] Appeler `increment_counter("prediction.compute")` à chaque appel de `get_or_compute()`
  - [ ] Appeler `increment_counter("prediction.reused")` uniquement si `result.was_reused is True`

### T5 — Tests unitaires métriques backend (AC2, AC5)

- [ ] Créer `backend/app/tests/unit/test_daily_prediction_metrics.py` :
  - [ ] `test_compute_counter_incremented` — mocker `increment_counter`, appeler le service, vérifier que `increment_counter("prediction.compute")` a été appelé exactement une fois
  - [ ] `test_reused_counter_incremented` — mocker `increment_counter` et service en mode réutilisation, vérifier que `increment_counter("prediction.reused")` est appelé
  - [ ] `test_log_includes_tone_and_pivot_count` — utiliser `caplog` pytest, vérifier que le log contient les champs `duration_ms`, `was_reused`, `overall_tone`, `has_pivots`

## Dev Notes

### Pattern analytics frontend

```typescript
// frontend/src/utils/analytics.ts
export function trackEvent(name: string, props: Record<string, unknown> = {}): void {
  if (typeof window !== 'undefined' && (window as any).analytics?.track) {
    (window as any).analytics.track(name, props)
  }
  // Uniquement en développement
  if (import.meta.env.DEV) {
    console.debug('[analytics]', name, props)
  }
}
```

### Règle de confidentialité des events frontend

- INTERDIT dans les props d'events : `note_20`, `natal_chart`, `scores`, `birth_date`, `user_id`
- AUTORISE : `category_code` (ex: `"amour"`), `was_reused` (bool), `severity` (code string), `range_days` (int), `date` (string YYYY-MM-DD)

### Exemple d'utilisation dans un composant React

```typescript
import { trackEvent, EVENTS } from '@/utils/analytics'

// Au montage
useEffect(() => {
  trackEvent(EVENTS.PREDICTION_VIEWED, {
    date: prediction.date_local,
    was_reused: prediction.was_reused,
  })
}, [])

// Au clic sur une catégorie
const handleCategoryClick = (categoryCode: string) => {
  trackEvent(EVENTS.CATEGORY_CLICKED, { category_code: categoryCode })
  // ... ouvrir le détail
}
```

### Compteurs observabilité existants

Utiliser `increment_counter` depuis `backend/app/infra/observability/metrics.py` :

```python
from app.infra.observability.metrics import increment_counter

increment_counter("prediction.compute")
increment_counter("prediction.reused")
```

Vérifier la signature exacte de `increment_counter` dans le module avant implémentation.

### Test avec caplog pytest

```python
import logging

def test_log_includes_tone_and_pivot_count(caplog, mock_service):
    with caplog.at_level(logging.INFO, logger="app.services.daily_prediction_service"):
        mock_service.get_or_compute(...)
    record = next(r for r in caplog.records if "prediction.run" in r.message)
    assert "duration_ms" in record.__dict__
    assert "overall_tone" in record.__dict__
```

### Project Structure Notes

- Module analytics à créer : `frontend/src/utils/analytics.ts`
- Composants prediction (story 36-4) : `frontend/src/` — chercher les composants liés à `DailyPrediction`
- `DailyPredictionService` : `backend/app/services/daily_prediction_service.py`
- Module observabilité : `backend/app/infra/observability/metrics.py`
- NE PAS ajouter de dépendance npm externe pour l'analytics

## References

- [Story: 36-1 — DailyPredictionService]
- [Story: 36-4 — DTO front et mapping UI v1 — composants à instrumenter]
- [Story: 38-1 — EditorialTemplateEngine — overall_tone dans EngineOutput]
- [Source: backend/app/infra/observability/metrics.py — increment_counter]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: frontend/src/i18n/astrology.ts — pattern fichier utils frontend]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-08: Story créée pour Epic 38.
