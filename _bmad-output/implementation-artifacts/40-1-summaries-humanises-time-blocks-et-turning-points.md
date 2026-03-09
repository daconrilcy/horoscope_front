# Story 40.1 : Summaries humanisés pour time_blocks et turning_points

Status: done

## Story

En tant que développeur backend de l'application horoscope,
je veux que chaque `TimeBlock` et chaque `TurningPoint` du moteur de prédiction exposent un champ `summary` textuel humanisé (généré via le système de templates éditoriaux existant),
afin que le payload API soit directement lisible par le front sans traitement supplémentaire et que la DB persiste un contenu métier réel à la place de codes techniques.

## Acceptance Criteria

### AC1 — `TimeBlock` expose un champ `summary` textuel

- [x] Le dataclass `TimeBlock` (dans `backend/app/prediction/block_generator.py`) possède un champ `summary: str = ""`
- [x] Après un run complet avec `include_editorial_text=True`, chaque `TimeBlock` dans `engine_output.time_blocks` a un `summary` non vide et en français (ex : `"Entre 08:00 et 11:30, tonalité très porteuse — Travail, Énergie & Vitalité."`)
- [x] Le `summary` est cohérent avec `tone_code` et `dominant_categories` du bloc

### AC2 — `TurningPoint` expose un champ `summary` textuel humanisé

- [x] Le dataclass `TurningPoint` (dans `backend/app/prediction/turning_point_detector.py`) possède un champ `summary: str = ""`
- [x] Après un run complet avec `include_editorial_text=True`, chaque `TurningPoint` dans `engine_output.turning_points` a un `summary` non vide et en français (ex : `"À 14:15, un basculement notable : Amour & Relations, Humeur."`)
- [x] Le `summary` utilise des termes humains (pas les codes techniques `"delta_note"` / `"top3_change"` / `"high_priority_event"`)

### AC3 — Nouveaux templates éditoriaux ajoutés pour fr et en

- [x] Fichier `backend/app/prediction/editorial_templates/fr/resume_bloc_horaire.txt` créé avec les variables `{start_time}`, `{end_time}`, `{tone_label}`, `{categories_labels}`
- [x] Fichier `backend/app/prediction/editorial_templates/en/resume_bloc_horaire.txt` créé
- [x] Fichier `backend/app/prediction/editorial_templates/fr/resume_turning_point.txt` créé avec les variables `{pivot_time}`, `{pivot_severity_label}`, `{categories_labels}`
- [x] Fichier `backend/app/prediction/editorial_templates/en/resume_turning_point.txt` créé

### AC4 — `EditorialTextOutput` transporte les summaries

- [x] Le dataclass `EditorialTextOutput` (dans `backend/app/prediction/editorial_template_engine.py`) inclut deux nouveaux champs :
  - `time_block_summaries: list[str]` (indexé dans l'ordre des blocs)
  - `turning_point_summaries: list[str]` (indexé dans l'ordre des turning_points)
- [x] La méthode `EditorialTemplateEngine.render()` peuple ces champs en appliquant les nouveaux templates

### AC5 — `EngineOrchestrator` injecte les summaries dans les objets moteur

- [x] Après le rendu éditorial (`include_editorial_text=True`), `EngineOrchestrator.run()` met à jour les `time_blocks` et `turning_points` de l'`EngineOutput` avec leurs summaries respectifs (via `dataclasses.replace` ou mutation contrôlée)
- [x] Quand `include_editorial_text=False`, les summaries restent à `""` (pas de régression)

### AC6 — `PredictionPersistenceService` persiste les summaries réels

- [x] `_save_time_blocks()` utilise `block.summary` (qui est maintenant non-vide) au lieu de `None`
- [x] `_save_turning_points()` utilise `tp.summary` (textuel humanisé) au lieu de `tp.reason` (code technique)
- [x] La colonne SQL `summary` des tables `daily_prediction_time_block` et `daily_prediction_turning_point` contient maintenant du texte lisible

### AC7 — Le contrat API `/v1/predictions/daily` est lisible sur fresh run ET run réutilisé

- [x] Sur un calcul frais, `timeline[].summary` n'est plus `null` pour les blocs persistés
- [x] Sur un calcul frais, `turning_points[].summary` n'est plus un code technique (`delta_note`, `top3_change`, `high_priority_event`)
- [x] Sur une relecture d'un run déjà persisté (`was_reused=true`), les mêmes champs restent lisibles et non nuls

### AC8 — Les runs cache hérités sont régénérés ou exclus de la réutilisation

- [x] Si un run en cache existe avec `overall_summary` présent mais `time_blocks.summary` ou `turning_points.summary` encore techniques / nuls, le service ne doit pas le servir tel quel comme version canonique
- [x] Le mécanisme de réutilisation détecte ce cache incomplet et force un recalcul contrôlé, sans casser le fallback de disponibilité existant

### AC9 — Tests unitaires et d'intégration couvrant les nouveaux chemins

- [x] Tests dans `backend/app/tests/unit/test_editorial_template_engine.py` : vérifier que les nouveaux templates sont rendus correctement pour un `TimeBlock` et un `TurningPoint` mock
- [x] Tests de non-régression : les tests existants sur `EngineOrchestrator`, `BlockGenerator` et `TurningPointDetector` passent sans modification
- [x] Test d'intégration API : `/v1/predictions/daily` retourne des `timeline[].summary` non nuls et des `turning_points[].summary` humanisés
- [x] Test service : un run cache incomplet (overall_summary OK mais summaries blocs/pivots absents) est invalidé puis recalculé

## Tasks / Subtasks

### T1 — Enrichir les dataclasses (AC1, AC2)

- [x] Dans `backend/app/prediction/block_generator.py` : ajouter `summary: str = field(default="")` au dataclass `TimeBlock`
- [x] Dans `backend/app/prediction/turning_point_detector.py` : ajouter `summary: str = field(default="")` au dataclass `TurningPoint`
- [x] Vérifier qu'aucun test existant n'instancie ces dataclasses avec des arguments positionnels qui casseraient le nouvel ordre (utiliser `field(default=...)`)

### T2 — Créer les templates éditoriaux (AC3)

- [x] Créer `backend/app/prediction/editorial_templates/fr/resume_bloc_horaire.txt` :
  ```
  Entre {start_time} et {end_time}, tonalité {tone_label} — {categories_labels}.
  ```
- [x] Créer `backend/app/prediction/editorial_templates/en/resume_bloc_horaire.txt` :
  ```
  From {start_time} to {end_time}, {tone_label} mood — {categories_labels}.
  ```
- [x] Créer `backend/app/prediction/editorial_templates/fr/resume_turning_point.txt` :
  ```
  À {pivot_time}, un basculement {pivot_severity_label} : {categories_labels}.
  ```
- [x] Créer `backend/app/prediction/editorial_templates/en/resume_turning_point.txt` :
  ```
  At {pivot_time}, a {pivot_severity_label} turning point: {categories_labels}.
  ```

### T3 — Enrichir `EditorialTextOutput` et `EditorialTemplateEngine.render()` (AC4)

- [x] Dans `backend/app/prediction/editorial_template_engine.py` :
  - Ajouter `time_block_summaries: list[str]` et `turning_point_summaries: list[str]` au dataclass `EditorialTextOutput`
  - Dans `render()`, accepter deux nouveaux paramètres optionnels :
    ```python
    def render(
        self,
        editorial: EditorialOutput,
        lang: str = "fr",
        time_blocks: list | None = None,
        turning_points: list | None = None,
    ) -> EditorialTextOutput:
    ```
  - Implémenter `_render_time_block_summary(block, lang)` : charge le template `resume_bloc_horaire`, formate `{start_time}`, `{end_time}`, `{tone_label}` (via `TONE_LABELS`), `{categories_labels}` (via `_get_category_label`)
  - Implémenter `_render_turning_point_summary(tp, lang)` : charge le template `resume_turning_point`, formate `{pivot_time}` (via `tp.local_time.strftime("%H:%M")`), `{pivot_severity_label}` (via `_get_severity_label`), `{categories_labels}` (via `_get_category_label` sur `tp.categories_impacted`)
  - Populer `time_block_summaries` et `turning_point_summaries` dans le retour

### T4 — Mettre à jour `EngineOrchestrator` (AC5)

- [x] Dans `backend/app/prediction/engine_orchestrator.py`, dans la méthode `run()` :
  - Passer `time_blocks=time_blocks` et `turning_points=turning_points` à l'appel de `self._editorial_template_engine.render(editorial, lang=editorial_text_lang, time_blocks=..., turning_points=...)`
  - Après le rendu, créer des copies mises à jour des `time_blocks` et `turning_points` avec leurs summaries injectés :
    ```python
    # Injecter les summaries dans les TimeBlock
    updated_time_blocks = [
        dataclasses.replace(block, summary=summary)
        for block, summary in zip(time_blocks, editorial_text.time_block_summaries)
    ]
    # Injecter les summaries dans les TurningPoint
    updated_turning_points = [
        dataclasses.replace(tp, summary=summary)
        for tp, summary in zip(turning_points, editorial_text.turning_point_summaries)
    ]
    ```
  - Inclure `updated_time_blocks` et `updated_turning_points` dans le `dataclasses.replace(output, ...)` final

### T5 — Mettre à jour `PredictionPersistenceService` (AC6)

- [x] Dans `backend/app/prediction/persistence_service.py`, méthode `_save_time_blocks()` :
  - Remplacer `summary = None  # TimeBlock has no summary field` par `summary = block.summary or None` (pour ne pas stocker une chaîne vide)
- [x] Dans `_save_turning_points()`, branche `else` (real `TurningPoint`) :
  - Remplacer `summary = tp.reason` par `summary = tp.summary or tp.reason` (fallback sur `tp.reason` si `summary` est vide, pour compatibilité ascendante)

### T6 — Gérer la compatibilité cache des runs déjà persistés (AC7, AC8)

- [x] Dans `DailyPredictionService.get_or_compute()`, étendre la détection de "stale cached run" : un run avec `overall_summary` présent mais `time_blocks.summary` ou `turning_points.summary` absents/techniques ne doit pas être réutilisé tel quel
- [x] Utiliser `DailyPredictionRepository.get_full_run()` ou un helper équivalent pour inspecter les summaries persistés avant réutilisation
- [x] Recalculer proprement le run incomplet puis persister la version enrichie
- [x] Préserver le comportement actuel de fallback sur dernier run disponible si le recalcul échoue

### T7 — Tests (AC9)

- [x] Dans `backend/app/tests/unit/test_editorial_template_engine.py` (créer si inexistant) :
  - Test `test_render_time_block_summary_fr` : mock d'un `TimeBlock` avec `tone_code="positive"`, `dominant_categories=["work", "energy"]`, `start_local=datetime(2026,3,8,8,0)`, `end_local=datetime(2026,3,8,11,30)` → vérifier que le summary contient "Travail" et "Énergie"
  - Test `test_render_turning_point_summary_fr` : mock d'un `TurningPoint` avec `reason="high_priority_event"`, `severity=0.9`, `categories_impacted=["love"]`, `local_time=datetime(2026,3,8,14,15)` → vérifier que le summary contient "14:15" et "Amour" (severity=0.9 → label "critique", pas "notable")
  - Test `test_render_fallback_when_no_blocks` : appel de `render()` sans `time_blocks` ni `turning_points` → `time_block_summaries=[]`, `turning_point_summaries=[]`
- [x] Relancer `backend/app/tests/unit/test_daily_prediction_service.py` pour vérifier la non-régression
- [x] Ajouter un test unitaire service "stale cached run with missing block summaries triggers recompute"
- [x] Ajouter / mettre à jour un test d'intégration dans `backend/app/tests/integration/test_daily_prediction_api.py` ou `test_daily_prediction_qa.py` pour vérifier le contrat API final

## Dev Notes

### Architecture et patterns établis

- **Système de templates** : `EditorialTemplateEngine` charge des fichiers `.txt` via `_load_template(lang, name)`. Pattern strict : si le template est absent → `FileNotFoundError`. Les templates n'utilisent que la syntaxe `{variable}` Python standard (pas Jinja).
- **Dataclasses frozen** : `TurningPoint` et `TimeBlock` sont des dataclasses **non-frozen** (mutables). Attention : `TurningPoint` a `driver_events: list[Any] = field(default_factory=list)` — même pattern à suivre pour `summary`.
- **Chaîne d'injection** : `EngineOrchestrator.run()` est le seul point d'assemblage final. La mutation des `time_blocks` et `turning_points` doit se faire APRÈS le rendu éditorial, dans le `dataclasses.replace(output, ...)` final (lignes 322-327 du fichier actuel).
- **`include_editorial_text`** : Les summaries ne doivent être générés QUE quand ce flag est `True`. Le `DailyPredictionService` appelle toujours avec `include_editorial_text=True` (ligne 251 de `daily_prediction_service.py`).

### Fichiers à toucher

| Fichier | Opération |
|---------|-----------|
| `backend/app/prediction/block_generator.py` | Ajouter `summary: str = field(default="")` à `TimeBlock` |
| `backend/app/prediction/turning_point_detector.py` | Ajouter `summary: str = field(default="")` à `TurningPoint` |
| `backend/app/prediction/editorial_template_engine.py` | Enrichir `EditorialTextOutput` + méthode `render()` |
| `backend/app/prediction/engine_orchestrator.py` | Injecter les summaries après rendu éditorial |
| `backend/app/prediction/persistence_service.py` | Utiliser `block.summary` et `tp.summary` |
| `backend/app/prediction/editorial_templates/fr/resume_bloc_horaire.txt` | Créer |
| `backend/app/prediction/editorial_templates/en/resume_bloc_horaire.txt` | Créer |
| `backend/app/prediction/editorial_templates/fr/resume_turning_point.txt` | Créer |
| `backend/app/prediction/editorial_templates/en/resume_turning_point.txt` | Créer |
| `backend/app/tests/unit/test_editorial_template_engine.py` | Créer/enrichir |

### Colonne DB `summary` déjà présente

La migration DB n'est **pas nécessaire** — les colonnes `summary` existent déjà dans les deux tables cibles :
- `DailyPredictionTimeBlockModel.summary` (voir `persistence_service.py:231`)
- `DailyPredictionTurningPointModel.summary` (voir `persistence_service.py:196`)

### Contraintes de cohérence

- La liste `time_block_summaries` doit avoir la même longueur que la liste `time_blocks` passée en entrée. Utiliser `zip()` est sûr car les deux listes sont générées en même temps.
- Si un `TurningPoint.categories_impacted` est vide, générer `{categories_labels}` = `"plusieurs domaines"` (fr) / `"several areas"` (en).
- Ne pas changer le champ `reason` sur `TurningPoint` — il reste utile pour le debug et l'explicabilité.
- Les nouveaux summaries ne doivent pas supprimer ni écraser les `driver_events` / `reason` déjà utiles au debug.
- Le contrat "payload lisible" doit être tenu en lecture cache autant qu'en fresh compute, sinon l'amélioration restera invisible après la première persistance.

### Tests existants à surveiller

- `backend/app/tests/unit/test_daily_prediction_service.py` — tests de haut niveau, ne créent pas de `TimeBlock`/`TurningPoint` directement
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` — idem
- `backend/app/tests/integration/test_daily_prediction_api.py` — bon candidat pour verrouiller le contrat HTTP final
- Tout test qui instancie `TimeBlock(block_index=..., start_local=..., ...)` ou `TurningPoint(local_time=..., ...)` restera compatible car `summary` a une valeur par défaut

### Source hints

- Behaviour de `_save_time_blocks()` : [Source: backend/app/prediction/persistence_service.py#L201-L240]
- Behaviour de `_save_turning_points()` : [Source: backend/app/prediction/persistence_service.py#L147-L199]
- Pattern templates : [Source: backend/app/prediction/editorial_template_engine.py#L133-L138]
- Assemblage final dans orchestrator : [Source: backend/app/prediction/engine_orchestrator.py#L297-L327]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/block_generator.py` — Ajout `summary: str = field(default="")` à `TimeBlock`
- `backend/app/prediction/turning_point_detector.py` — Ajout `summary: str = field(default="")` à `TurningPoint`
- `backend/app/prediction/editorial_template_engine.py` — Ajout `time_block_summaries`/`turning_point_summaries` à `EditorialTextOutput`, nouvelles méthodes `_render_time_block_summary` et `_render_turning_point_summary`, paramètres `time_blocks`/`turning_points` dans `render()`
- `backend/app/prediction/engine_orchestrator.py` — Injection des summaries dans `time_blocks` et `turning_points` après rendu éditorial
- `backend/app/prediction/persistence_service.py` — Utilisation de `block.summary` et `tp.summary` à la place de `None`/`tp.reason`
- `backend/app/services/daily_prediction_service.py` — Détection des runs stale (missing summaries) et recalcul forcé
- `backend/app/infra/db/repositories/daily_prediction_repository.py` — Ajout `get_run_by_hash_with_details()` avec eager loading
- `backend/app/prediction/editorial_templates/fr/resume_bloc_horaire.txt` — Nouveau template
- `backend/app/prediction/editorial_templates/en/resume_bloc_horaire.txt` — Nouveau template
- `backend/app/prediction/editorial_templates/fr/resume_turning_point.txt` — Nouveau template
- `backend/app/prediction/editorial_templates/en/resume_turning_point.txt` — Nouveau template
- `backend/app/tests/unit/test_editorial_template_engine.py` — Tests `test_render_time_block_summary_fr`, `test_render_turning_point_summary_fr`, `test_render_fallback_when_no_blocks`, `test_render_full_with_blocks`, etc.
- `backend/app/tests/unit/test_daily_prediction_service.py` — Tests stale cache (`test_stale_cached_run_with_missing_block_summaries_is_recomputed`, `test_stale_cached_run_with_technical_tp_summary_is_recomputed`)
- `backend/app/tests/unit/test_daily_prediction_metrics.py` — Mise à jour pour `get_run_by_hash_with_details`
- `backend/app/tests/integration/test_daily_prediction_api.py` — Tests contrat API AC9 (`test_daily_prediction_timeline_summary_non_null`, `test_daily_prediction_turning_points_summary_humanized`, `test_daily_prediction_reused_run_summaries_readable`)

## Change Log

- 2026-03-08 : Story créée pour Epic 40 — enrichissement payload prédiction.
- 2026-03-09 : Code review adversarial — corrigé type annotations `any`→`Any` (M1), ajouté 3 tests intégration API (H2), 3 tests unitaires supplémentaires (L1), rempli File List (H1), status → done (M2), exemples story corrigés (L2/L3).
