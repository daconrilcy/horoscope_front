# Story 42.2: Construire la susceptibilité natale structurelle

Status: review

## Story

As a prediction engine designer,
I want calculer une susceptibilité natale structurelle robuste par thème,
so that la composante `B(c)` reflète réellement le thème natal au lieu d'un simple modulateur décoratif.

## Acceptance Criteria

1. `B(c)` prend en compte au minimum:
   - maisons principales et secondaires du thème
   - état natal des maîtres utiles
   - angularité
   - occupation par planètes personnelles/rapides
   - aspects natals impliquant les significateurs
2. Le score structurel par thème est borné, centré et explicable.
3. La couche `B(c)` reste indépendante des activations de transit et intrajournalières.
4. Le moteur expose assez d'information debug pour comprendre pourquoi un thème a une susceptibilité forte ou faible.
5. Les tests verrouillent stabilité, bornage et explicabilité minimale.

## Tasks / Subtasks

- [x] Task 1: Reconcevoir le calcul natal structurel (AC: 1, 2)
  - [x] Définir la formule ou la combinaison pondérée des facteurs
  - [x] Introduire les poids paramétrables nécessaires
  - [x] Produire une sortie structurée par thème

- [x] Task 2: Enrichir le contexte et l'explicabilité (AC: 3, 4)
  - [x] Exposer les composantes intermédiaires de `B(c)`
  - [x] Ajouter des artefacts d'explicabilité lisibles
  - [x] Éviter de mélanger natal structurel et signal quotidien

- [x] Task 3: Brancher la nouvelle couche dans le pipeline v3 (AC: 2, 3)
  - [x] Préparer l'appel depuis l'orchestrateur v3
  - [x] Garantir une sortie stable pour les couches suivantes

- [x] Task 4: Tests (AC: 5)
  - [x] Tester bornes et centrage
  - [x] Tester variation contrôlée sur plusieurs profils natals
  - [x] Tester la présence d'explications minimales

## Dev Notes

- La logique actuelle dans `natal_sensitivity.py` peut servir de base, mais la story demande explicitement de passer d'un simple modulateur à une vraie composante structurelle.
- `B(c)` doit rester stable à thème constant. Elle ne dépend ni de l'heure de la journée ni du transit courant.
- Le but n'est pas d'ajouter de l'ésotérisme gratuit, mais de rendre le poids natal par thème plus crédible et plus auditable.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/natal_sensitivity.py`
  - `backend/app/prediction/context_loader.py`
  - `backend/app/prediction/explainability.py`
  - `backend/app/prediction/schemas.py`

### Technical Requirements

- Le score final doit être borné et centré pour rester utilisable dans `S(c,t)`.
- Les poids doivent rester versionnables ou au minimum facilement ajustables.
- L'explicabilité doit survivre au refactor.

### Testing Requirements

- Couvrir thèmes forts/faibles et invariants de stabilité.
- Exécuter `ruff check` et `pytest` dans le venv.

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/natal_sensitivity.py]
- [Source: backend/app/prediction/context_loader.py]
- [Source: backend/app/tests/unit/test_natal_sensitivity.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Refonte de `B(c)` avec contributions signées et bornées pour distinguer thèmes forts et faibles.
- Intégration des maisons principales/secondaires, des significateurs thématiques et des aspects natals contextualisés.
- Pipeline v3 branché sur des aspects natals déterministes dépendants du référentiel de contexte.
- Couverture unitaire étendue pour verrouiller cas faibles, pondération primary/secondary et filtrage des planètes lentes.

### File List

- `_bmad-output/implementation-artifacts/42-2-construire-la-susceptibilite-natale-structurelle.md`
- `backend/app/prediction/natal_sensitivity.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_natal_structural_v3.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/regression/helpers.py`
