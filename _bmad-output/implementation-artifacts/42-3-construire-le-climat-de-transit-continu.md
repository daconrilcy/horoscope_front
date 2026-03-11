# Story 42.3: Construire le climat de transit continu

Status: review

## Story

As a prediction engine designer,
I want remplacer la logique de transit purement événementielle par une couche continue,
so that la composante `T(c,t)` exprime un fond de journée cohérent qui monte, culmine puis redescend.

## Acceptance Criteria

1. Les transits pertinents sont évalués à chaque pas de temps avec une fonction continue d'orbe.
2. `T(c,t)` prend en compte:
   - nature de la planète transitante
   - nature de la cible natale
   - type d'aspect
   - applying vs separating
   - polarité contextuelle
   - routage vers les thèmes
3. Le signal de transit n'est plus réduit aux seuls événements `exact`, `enter_orb` et `exit_orb`.
4. La couche produite est déterministe, lissable et testable.
5. Les tests montrent une montée/pic/retombée sur un transit significatif.
6. Un budget de performance explicite borne le coût de calcul de la couche `T(c,t)` sur une journée standard.

## Tasks / Subtasks

- [x] Task 1: Définir la formule continue de transit (AC: 1, 2)
  - [x] Choisir la fonction d'orbite continue
  - [x] Définir les composantes de poids
  - [x] Définir la sortie par thème et par pas

- [x] Task 2: Introduire un builder dédié de signal de transit (AC: 3, 4)
  - [x] Créer un module dédié si nécessaire
  - [x] Éviter d'enfler `event_detector.py` au-delà du raisonnable
  - [x] Garder la taxonomie événementielle comme couche séparée

- [x] Task 3: Brancher `T(c,t)` dans l'orchestrateur v3 (AC: 4)
  - [x] Construire la série complète sur la journée
  - [x] Conserver la possibilité de debug et d'inspection

- [x] Task 4: Tests (AC: 5)
  - [x] Tester une courbe simple de transit
  - [x] Tester le comportement applying/separating
  - [x] Tester qu'un signal continu existe même sans exact event exact au pas observé

- [x] Task 5: Mesurer et verrouiller le coût de la couche `T` (AC: 6)
  - [x] Définir un SLO de temps de calcul
  - [x] Ajouter une instrumentation ou un benchmark ciblé

## Dev Notes

- Cette story ne remplace pas encore la détection d'événements; elle introduit une couche de fond de journée.
- Le bon design est probablement un module de type `transit_signal_builder.py`, appelé par l'orchestrateur v3.
- Il faut éviter de rendre `event_detector.py` responsable à la fois:
  - de la détection discrète
  - et de la construction du fond continu

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/event_detector.py`
  - `backend/app/prediction/contribution_calculator.py`
  - `backend/app/prediction/engine_orchestrator.py`
  - nouveau fichier recommandé: `backend/app/prediction/transit_signal_builder.py`

### Technical Requirements

- La fonction continue doit rester bornée et stable.
- Le coût runtime doit rester compatible avec un calcul quotidien en backend.
- La sortie doit s'intégrer naturellement à `S(c,t)`.
- La story doit poser un budget runtime explicite, pas seulement une intention d'optimisation.

### Testing Requirements

- Tester des transits représentatifs.
- Vérifier la forme de la courbe.
- Exécuter `ruff check` et les tests dans le venv.

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/event_detector.py]
- [Source: backend/app/prediction/contribution_calculator.py]
- [Source: backend/app/prediction/engine_orchestrator.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- La couche `T(c,t)` réutilise désormais les primitives du moteur événementiel pour l'orbe, la polarité, les poids d'aspect et la phase.
- Le routage v3 tient compte des pondérations `primary/secondary` côté planètes et maisons.
- L'orchestrateur v3 expose des diagnostics de transit stables et inspectables dans `run_metadata`.
- Les tests verrouillent la courbe continue, l'absence d'exact observé au pas, le routage pondéré et le budget de calcul.

### File List

- `_bmad-output/implementation-artifacts/42-3-construire-le-climat-de-transit-continu.md`
- `backend/app/prediction/transit_signal_builder.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_transit_signal_v3.py`
- `backend/app/tests/unit/test_transit_performance.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
