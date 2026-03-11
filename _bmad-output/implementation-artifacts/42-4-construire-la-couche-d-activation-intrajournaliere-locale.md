# Story 42.4: Construire la couche d'activation intrajournalière locale

Status: review

## Story

As a product owner du daily,
I want une activation locale continue à l'intérieur de la journée,
so that la composante `A(c,t)` donne du relief horaire sans traiter chaque modulateur comme un pivot.

## Acceptance Criteria

1. `A(c,t)` intègre les activations locales pertinentes:
   - passages de la Lune
   - aspects lunaires utiles
   - activations d'angles et de maisons locales
   - modulateurs horaires jugés pertinents
2. Les signaux comme `asc_sign_change` et `planetary_hour_change` sont traités comme modulateurs secondaires.
3. La sortie est une série continue par thème, compatible avec le signal composite v3.
4. La logique reste distincte de la couche impulsionnelle `E(c,t)`.
5. Des tests montrent que l'activation locale donne du relief sans créer artificiellement des pivots.
6. Un budget de performance explicite borne le coût de calcul de la couche `A(c,t)` sur une journée standard.

## Tasks / Subtasks

- [x] Task 1: Définir les sources d'activation locale (AC: 1, 2)
  - [x] Lister les modulateurs conservés
  - [x] Définir leur poids relatif
  - [x] Distinguer clairement ce qui relève de `A` et de `E`

- [x] Task 2: Introduire un builder d'activation intrajournalière (AC: 3, 4)
  - [x] Créer un module dédié si nécessaire
  - [x] Réutiliser `temporal_sampler.py` comme source de grille temporelle
  - [x] Produire une série continue par thème

- [x] Task 3: Brancher le calcul dans le pipeline v3 (AC: 3)
  - [x] Appeler la couche depuis l'orchestrateur
  - [x] Permettre l'inspection debug par thème

- [x] Task 4: Tests (AC: 5)
  - [x] Tester la contribution de la Lune et des angles
  - [x] Tester que les modulateurs secondaires ne créent pas seuls du faux relief

- [x] Task 5: Mesurer et verrouiller le coût de la couche `A` (AC: 6)
  - [x] Définir un SLO de temps de calcul
  - [x] Ajouter une instrumentation ou un benchmark ciblé


## Dev Notes

- Aujourd'hui, certains signaux horaires ressemblent trop à des “faits” alors qu'ils devraient enrichir un régime local.
- Cette story est l'endroit où repositionner `asc_sign_change` et `planetary_hour_change` comme signaux secondaires de texture.
- Le produit attendu est un relief intrajournalier continu, pas un catalogue d'événements.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/temporal_sampler.py`
  - `backend/app/prediction/engine_orchestrator.py`
  - nouveau fichier recommandé: `backend/app/prediction/intraday_activation_builder.py`

### Technical Requirements

- Garder une granularité compatible avec le pas de 15 minutes existant.
- Le coût de calcul doit rester raisonnable.
- Les sorties doivent être directement combinables avec `B/T/E`.
- La performance doit être explicitement mesurée; cette couche ne doit pas devenir le principal goulet d'étranglement du daily v3.

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/temporal_sampler.py]
- [Source: backend/app/prediction/engine_orchestrator.py]
- [Source: backend/app/prediction/event_detector.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- `A(c,t)` réutilise désormais les règles d'orbe, de phase et de pondération du moteur événementiel pour les aspects lunaires, et route les ingresses ASC/MC via les pondérations thématiques v3.
- Les heures planétaires sont branchées dans le runtime v3 réel, avec diagnostics dédiés et budget de performance explicite.
- Les tests couvrent le routage des modulateurs secondaires, l'absence de faux relief hors thème, l'intégration orchestrateur et l'exposition des diagnostics.

### File List

- `_bmad-output/implementation-artifacts/42-4-construire-la-couche-d-activation-intrajournaliere-locale.md`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_intraday_activation_v3.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/unit/test_transit_performance.py`
