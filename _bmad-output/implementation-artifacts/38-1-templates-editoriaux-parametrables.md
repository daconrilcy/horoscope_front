# Story 38.1 : Templates éditoriaux paramétrables

Status: done

## Story

As a développeur du moteur de prédiction,
I want un `EditorialTemplateEngine` qui produit des textes éditoriaux entièrement depuis des templates paramétrables par langue et tonalité, en injectant des variables dérivées mécaniquement du moteur,
so that la couche éditoriale est non-fataliste, versionnée, et ne génère jamais de texte libre hors template ni d'appel LLM.

## Acceptance Criteria

### AC1 — Aucun texte généré hors template

[x] Tout texte final est issu d'un template chargé depuis `backend/app/prediction/editorial_templates/`.

### AC2 — Variables injectées toutes dérivées du moteur

[x] Les variables injectées dans les templates sont toutes issues de `EditorialOutput` produit par `EditorialOutputBuilder`.

### AC3 — Templates santé et argent avec formulations prudentes dédiées

[x] Les templates `fr/prudence_sante.txt` et `fr/prudence_argent.txt` utilisent des formulations prudentes et non substituables.

### AC4 — Templates versionnés dans le dossier source, pas en base de données

[x] Les fichiers `.txt` de templates résident dans `backend/app/prediction/editorial_templates/`.

### AC5 — Le service produit un `EditorialTextOutput` avec les champs textuels finaux

[x] `EditorialTemplateEngine.render()` retourne un `EditorialTextOutput` (dataclass).

## Tasks / Subtasks

### T1 — Créer les 6 templates dans `backend/app/prediction/editorial_templates/fr/`

- [x] Créer le dossier `backend/app/prediction/editorial_templates/fr/`
- [x] Créer `fr/intro_du_jour.txt` avec placeholders : `{date_local}`, `{overall_tone_label}`, `{top3_labels}`
- [x] Créer `fr/resume_categorie.txt` avec placeholders : `{category_label}`, `{note_20}`, `{band}`
- [x] Créer `fr/phrase_pivot.txt` avec placeholders : `{pivot_time}`, `{pivot_severity_label}`
- [x] Créer `fr/meilleure_fenetre.txt` avec placeholders : `{window_start}`, `{window_end}`, `{dominant_category_label}`
- [x] Créer `fr/prudence_sante.txt` — formulation prudente sans diagnostic médical
- [x] Créer `fr/prudence_argent.txt` — formulation prudente sans injonction financière
- [x] S'assurer qu'aucun template ne contient de texte rédigé en dur sans placeholder significatif

### T2 — Créer `backend/app/prediction/editorial_template_engine.py`

- [x] Définir la dataclass `EditorialTextOutput` : `intro: str`, `category_summaries: dict[str, str]`, `pivot_phrase: str | None`, `window_phrase: str | None`, `caution_sante: str | None`, `caution_argent: str | None`
- [x] Créer la classe `EditorialTemplateEngine`
  - [x] Constante `TEMPLATE_BASE = Path(__file__).parent / "editorial_templates"`
  - [x] Méthode privée `_load_template(lang: str, name: str) -> str` — lit le fichier `.txt` correspondant
  - [x] Méthode `render(editorial: EditorialOutput, lang: str = "fr") -> EditorialTextOutput`
    - [x] Générer `intro` depuis `fr/intro_du_jour.txt`
    - [x] Générer `category_summaries` : un rendu de `fr/resume_categorie.txt` par catégorie dans `top3_categories`
    - [x] Générer `pivot_phrase` depuis `fr/phrase_pivot.txt` si `editorial.main_pivot` est non-None, sinon `None`
    - [x] Générer `window_phrase` depuis `fr/meilleure_fenetre.txt` si `editorial.best_window` est non-None, sinon `None`
    - [x] Générer `caution_sante` depuis `fr/prudence_sante.txt` si `editorial.caution_flags.get("sante")`, sinon `None`
    - [x] Générer `caution_argent` depuis `fr/prudence_argent.txt` si `editorial.caution_flags.get("argent")`, sinon `None`

### T3 — Intégration optionnelle dans `EngineOrchestrator`

- [x] Ajouter un paramètre `include_editorial_text: bool = False` dans la signature de `EngineOrchestrator.run()`
- [x] Si `include_editorial_text=True` : instancier `EditorialTemplateEngine` et appeler `render()` après la construction de l'`EditorialOutput`
- [x] Stocker le résultat dans un champ optionnel `editorial_text: EditorialTextOutput | None` dans `EngineOutput`
- [x] Par défaut (`False`) : comportement inchangé, pas d'appel au moteur de templates

### T4 — Tests `backend/app/tests/unit/test_editorial_template_engine.py`

- [x] `test_no_free_text_generated` — vérifie qu'aucun texte n'est produit hors template
- [x] `test_variables_from_engine` — vérifie que les variables injectées correspondent aux valeurs de `EditorialOutput` fourni
- [x] `test_caution_sante_prudent_wording` — le rendu de `prudence_sante.txt` ne contient ni "diagnostic" ni "médecin" ni impératif médical
- [x] `test_caution_argent_prudent_wording` — le rendu de `prudence_argent.txt` ne contient ni "investissez" ni "achetez" ni injonction financière directe
- [x] `test_template_renders_correctly` — rendu complet avec un `EditorialOutput` valide, vérifie les champs non-None attendus
- [x] `test_missing_pivot_none` — `editorial.main_pivot = None` → `pivot_phrase` est `None` dans l'output

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] Revenir au contrat story pour `EditorialTemplateEngine.render(editorial: EditorialOutput, lang: str = "fr")` et supprimer l'injection externe de `date_local`, actuellement hors `EditorialOutput`.
- [x] [AI-Review][HIGH] Ajouter le test promis `test_variables_from_engine` et aligner la story avec la réalité de la suite (`7 passed`).
- [x] [AI-Review][MEDIUM] Faire échouer explicitement le rendu si un template est introuvable au lieu de retourner une chaîne vide silencieuse.
- [x] [AI-Review][MEDIUM] Exposer la langue côté orchestration au lieu de hardcoder `lang="fr"` quand `include_editorial_text=True`.
- [x] [AI-Review][MEDIUM] Corriger les écarts qualité signalés par `ruff check` sur les fichiers modifiés avant de considérer la story terminée.

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Unit tests pass: `7 passed in 0.06s`
- Ruff check: `All checks passed!`

### Completion Notes List
- Création de `EditorialTemplateEngine` pour le rendu mécanique de textes astrologiques.
- Implémentation des 6 templates de base en français.
- Intégration optionnelle dans `EngineOrchestrator` via le flag `include_editorial_text`.
- Ajout de `editorial_text` dans le schéma `EngineOutput`.
- Fix review: ajout de `local_date` dans `EditorialOutput` et `EffectiveContext`.
- Fix review: la langue du rendu textuel est configurable via `editorial_text_lang` dans `EngineOrchestrator.run()`.
- Validation par tests unitaires couvrant les contraintes de prudence (santé/argent), l'intégrité du rendu et la gestion des erreurs de chargement.
- 2026-03-08: correctif post-intégration — le rendu `editorial_text` est désormais demandé systématiquement par `DailyPredictionService` pour les calculs quotidiens et persisté dans la table des runs (`overall_summary` + résumés de catégories), afin que le texte éditorial survive au cache et aux relectures API.

### File List

- `backend/app/prediction/editorial_template_engine.py`
- `backend/app/prediction/editorial_templates/fr/intro_du_jour.txt`
- `backend/app/prediction/editorial_templates/fr/resume_categorie.txt`
- `backend/app/prediction/editorial_templates/fr/phrase_pivot.txt`
- `backend/app/prediction/editorial_templates/fr/meilleure_fenetre.txt`
- `backend/app/prediction/editorial_templates/fr/prudence_sante.txt`
- `backend/app/prediction/editorial_templates/fr/prudence_argent.txt`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/editorial_builder.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/context_loader.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/tests/unit/test_editorial_template_engine.py`
- `backend/app/tests/unit/test_persistence_explainability.py`

## Change Log

- 2026-03-08: Story créée pour Epic 38.
- 2026-03-08: Implémentation complète du moteur de templates éditoriaux et intégration dans l'orchestrateur.
- 2026-03-08: Correction des retours de revue Senior AI (traçabilité date, langue dynamique, robustesse erreurs, lint).
- 2026-03-08: Durcissement runtime — persistance effective des textes éditoriaux dans les runs quotidiens et réutilisation cache cohérente côté API `/v1/predictions/daily`.
