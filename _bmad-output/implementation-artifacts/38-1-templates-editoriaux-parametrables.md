# Story 38.1 : Templates éditoriaux paramétrables

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want un `EditorialTemplateEngine` qui produit des textes éditoriaux entièrement depuis des templates paramétrables par langue et tonalité, en injectant des variables dérivées mécaniquement du moteur,
so that la couche éditoriale est non-fataliste, versionnée, et ne génère jamais de texte libre hors template ni d'appel LLM.

## Acceptance Criteria

### AC1 — Aucun texte généré hors template

Aucune f-string libre ne produit de texte visible pour l'utilisateur dans le code. Tout texte final est issu d'un template chargé depuis `backend/app/prediction/editorial_templates/`.

### AC2 — Variables injectées toutes dérivées du moteur

Les variables injectées dans les templates (`overall_tone`, `top1_category`, `top1_note`, `top1_band`, `pivot_time`, `window_start`, `window_end`, `caution_level`, etc.) sont toutes issues de `EditorialOutput` produit par `EditorialOutputBuilder`. Aucun texte n'est inventé dans le code.

### AC3 — Templates santé et argent avec formulations prudentes dédiées

Les templates `fr/prudence_sante.txt` et `fr/prudence_argent.txt` utilisent des formulations qui n'émettent ni diagnostic médical ni injonction financière. Ces templates sont distincts des autres et non substituables par un template générique.

### AC4 — Templates versionnés dans le dossier source, pas en base de données

Les fichiers `.txt` de templates résident dans `backend/app/prediction/editorial_templates/` versionné dans le dépôt Git. Aucun template n'est stocké en base de données.

### AC5 — Le service produit un `EditorialTextOutput` avec les champs textuels finaux

`EditorialTemplateEngine.render()` retourne un `EditorialTextOutput` (dataclass) contenant : `intro`, `category_summaries`, `pivot_phrase`, `window_phrase`, `caution_sante`, `caution_argent`.

## Tasks / Subtasks

### T1 — Créer les 6 templates dans `backend/app/prediction/editorial_templates/fr/`

- [ ] Créer le dossier `backend/app/prediction/editorial_templates/fr/`
- [ ] Créer `fr/intro_du_jour.txt` avec placeholders : `{date_local}`, `{overall_tone_label}`, `{top3_labels}`
- [ ] Créer `fr/resume_categorie.txt` avec placeholders : `{category_label}`, `{note_20}`, `{band}`
- [ ] Créer `fr/phrase_pivot.txt` avec placeholders : `{pivot_time}`, `{pivot_severity_label}`
- [ ] Créer `fr/meilleure_fenetre.txt` avec placeholders : `{window_start}`, `{window_end}`, `{dominant_category_label}`
- [ ] Créer `fr/prudence_sante.txt` — formulation prudente sans diagnostic médical
- [ ] Créer `fr/prudence_argent.txt` — formulation prudente sans injonction financière
- [ ] S'assurer qu'aucun template ne contient de texte rédigé en dur sans placeholder significatif

### T2 — Créer `backend/app/prediction/editorial_template_engine.py`

- [ ] Définir la dataclass `EditorialTextOutput` : `intro: str`, `category_summaries: dict[str, str]`, `pivot_phrase: str | None`, `window_phrase: str | None`, `caution_sante: str | None`, `caution_argent: str | None`
- [ ] Créer la classe `EditorialTemplateEngine`
  - [ ] Constante `TEMPLATE_BASE = Path(__file__).parent / "editorial_templates"`
  - [ ] Méthode privée `_load_template(lang: str, name: str) -> str` — lit le fichier `.txt` correspondant
  - [ ] Méthode `render(editorial: EditorialOutput, lang: str = "fr") -> EditorialTextOutput`
    - [ ] Générer `intro` depuis `fr/intro_du_jour.txt`
    - [ ] Générer `category_summaries` : un rendu de `fr/resume_categorie.txt` par catégorie dans `top3_categories`
    - [ ] Générer `pivot_phrase` depuis `fr/phrase_pivot.txt` si `editorial.main_pivot` est non-None, sinon `None`
    - [ ] Générer `window_phrase` depuis `fr/meilleure_fenetre.txt` si `editorial.best_window` est non-None, sinon `None`
    - [ ] Générer `caution_sante` depuis `fr/prudence_sante.txt` si `editorial.caution_flags.get("sante")`, sinon `None`
    - [ ] Générer `caution_argent` depuis `fr/prudence_argent.txt` si `editorial.caution_flags.get("argent")`, sinon `None`

### T3 — Intégration optionnelle dans `EngineOrchestrator`

- [ ] Ajouter un paramètre `generate_editorial_text: bool = False` dans la signature de `EngineOrchestrator.run()` (ou dans `EngineInput`)
- [ ] Si `generate_editorial_text=True` : instancier `EditorialTemplateEngine` et appeler `render()` après la construction de l'`EditorialOutput`
- [ ] Stocker le résultat dans un champ optionnel `editorial_text: EditorialTextOutput | None` dans `EngineOutput`
- [ ] Par défaut (`False`) : comportement inchangé, pas d'appel au moteur de templates

### T4 — Tests `backend/app/tests/unit/test_editorial_template_engine.py`

- [ ] `test_no_free_text_generated` — vérifie qu'aucun texte n'est produit hors template (mock les templates, vérifie que la sortie provient de `_load_template`)
- [ ] `test_variables_from_engine` — vérifie que les variables injectées correspondent aux valeurs de `EditorialOutput` fourni
- [ ] `test_caution_sante_prudent_wording` — le rendu de `prudence_sante.txt` ne contient ni "diagnostic" ni "médecin" ni impératif médical
- [ ] `test_caution_argent_prudent_wording` — le rendu de `prudence_argent.txt` ne contient ni "investissez" ni "achetez" ni injonction financière directe
- [ ] `test_template_renders_correctly` — rendu complet avec un `EditorialOutput` valide, vérifie les champs non-None attendus
- [ ] `test_missing_pivot_none` — `editorial.main_pivot = None` → `pivot_phrase` est `None` dans l'output

## Dev Notes

### Format des templates (string Python avec placeholders)

```
# fr/intro_du_jour.txt
Votre journée du {date_local} s'annonce {overall_tone_label}.
Vos points forts : {top3_labels}.
```

```
# fr/prudence_sante.txt
Une vigilance particulière est de mise côté santé aujourd'hui.
```

```
# fr/prudence_argent.txt
Prudence dans vos décisions financières, mieux vaut différer les engagements importants.
```

### Chargement des templates

```python
from pathlib import Path

TEMPLATE_BASE = Path(__file__).parent / "editorial_templates"

def _load_template(self, lang: str, name: str) -> str:
    path = TEMPLATE_BASE / lang / f"{name}.txt"
    return path.read_text(encoding="utf-8")
```

### Contrainte absolue : pas de LLM

`EditorialTemplateEngine` n'appelle aucun service LLM, aucune API externe, aucun modèle de langage. Les templates sont des fichiers texte statiques avec des placeholders Python standard (`str.format()`).

### Structure des dossiers à créer

```
backend/app/prediction/
  editorial_template_engine.py
  editorial_templates/
    fr/
      intro_du_jour.txt
      resume_categorie.txt
      phrase_pivot.txt
      meilleure_fenetre.txt
      prudence_sante.txt
      prudence_argent.txt
backend/app/tests/unit/
  test_editorial_template_engine.py
```

### Champs `EditorialTextOutput`

| Champ | Type | Source template |
|---|---|---|
| `intro` | `str` | `fr/intro_du_jour.txt` |
| `category_summaries` | `dict[str, str]` | `fr/resume_categorie.txt` × top3 |
| `pivot_phrase` | `str \| None` | `fr/phrase_pivot.txt` ou `None` |
| `window_phrase` | `str \| None` | `fr/meilleure_fenetre.txt` ou `None` |
| `caution_sante` | `str \| None` | `fr/prudence_sante.txt` ou `None` |
| `caution_argent` | `str \| None` | `fr/prudence_argent.txt` ou `None` |

## References

- [Source: backend/app/prediction/editorial_builder.py — EditorialOutput, EditorialOutputBuilder]
- [Source: _bmad-output/implementation-artifacts/35-4-couche-editoriale.md — contrat EditorialOutput, champs top3_categories, main_pivot, best_window, caution_flags, overall_tone]
- [Source: backend/app/prediction/engine_orchestrator.py — EngineOrchestrator.run(), EngineOutput]
- [Source: frontend/src/i18n/ — référence pour la cohérence terminologique FR]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/editorial_template_engine.py`
- `backend/app/prediction/editorial_templates/fr/intro_du_jour.txt`
- `backend/app/prediction/editorial_templates/fr/resume_categorie.txt`
- `backend/app/prediction/editorial_templates/fr/phrase_pivot.txt`
- `backend/app/prediction/editorial_templates/fr/meilleure_fenetre.txt`
- `backend/app/prediction/editorial_templates/fr/prudence_sante.txt`
- `backend/app/prediction/editorial_templates/fr/prudence_argent.txt`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_editorial_template_engine.py`

## Change Log

- 2026-03-08: Story créée pour Epic 38.
