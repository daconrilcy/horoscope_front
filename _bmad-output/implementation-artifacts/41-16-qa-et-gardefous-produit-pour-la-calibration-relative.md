# Story 41.16: QA et garde-fous produit pour la calibration relative

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA engineer,
I want valider que la calibration relative enrichit les journées plates sans créer de faux signaux forts,
so that le daily reste honnête, lisible et conforme au budget de bruit Epic 41.

## Acceptance Criteria

1. Une suite QA distingue explicitement:
   - journée plate sans micro-tendance
   - journée plate avec micro-tendances relatives
   - journée active avec fenêtres/pivots absolus inchangés

2. Des garde-fous automatiques empêchent les faux reliefs:
   - pas de `best_window` sur journée plate
   - pas de `turning_points` publics induits par les micro-tendances
   - pas de vocabulaire éditorial trompeur ou trop actionnable

3. Le budget de bruit intraday Epic 41.5 reste respecté après ajout de la calibration relative.

4. Les tests couvrent les cas de baseline manquante ou obsolète sans dégrader le comportement public nominal.

5. Un rapport QA ou jeu de fixtures permet de vérifier la cohérence produit sur plusieurs journées et plusieurs profils utilisateur.

## Tasks / Subtasks

- [x] Task 1: Étendre les fixtures QA de daily prediction (AC: 1, 5)
  - [x] Ajouter des cas "flat day no relative signal"
  - [x] Ajouter des cas "flat day with relative micro trends"
  - [x] Ajouter des cas "active day unchanged"

- [x] Task 2: Formaliser les garde-fous produit (AC: 2, 3)
  - [x] Ajouter des assertions sur l’absence de faux windows/pivots
  - [x] Vérifier le wording et la hiérarchie des messages
  - [x] Rejouer le budget de bruit intraday existant

- [x] Task 3: Couvrir les fallbacks baseline (AC: 4)
  - [x] Tester baseline absente
  - [x] Tester baseline obsolète
  - [x] Vérifier la continuité du daily

- [x] Task 4: Produire une validation QA exploitable par l’équipe (AC: 5)
  - [x] Ajouter rapport/fixtures lisibles
  - [x] Permettre une décision go/no-go claire

## Dev Notes

- Cette story verrouille la qualité produit de la calibration relative.
- Le principal risque est le faux relief: rendre excitante une journée objectivement neutre.
- La QA doit donc juger à la fois:
  - la véracité du signal
  - la budget de bruit
  - la cohérence éditoriale
- Les nouvelles assertions doivent compléter Epic 41.5, pas le remplacer.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/tests/integration/test_daily_prediction_qa.py`
  - `backend/app/tests/fixtures/intraday_qa_fixtures.py`
  - `backend/app/tests/helpers/intraday_qa_report.py`

### Technical Requirements

- Les nouvelles suites doivent être déterministes.
- Les fixtures doivent rendre visibles les différences entre absolu et relatif.
- Les tests doivent détecter les régressions de contrat public et de budget de bruit.
- Les rapports QA doivent rester lisibles pour une décision produit rapide.

### Architecture Compliance

- La QA doit couvrir l’ensemble de la chaîne:
  - baseline
  - scoring relatif
  - projection publique
- Le frontend pourra être couvert plus tard, mais la vérité métier doit être verrouillée côté backend d’abord.

### Library / Framework Requirements

- Réutiliser Pytest et la stack de tests existante uniquement.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- Étendre les suites QA existantes Epic 41 au lieu de créer un second système parallèle de validation.

### Testing Requirements

- Couvrir:
  - journée plate sans micro-tendance
  - journée plate avec micro-tendance
  - journée active inchangée
  - baseline absente / obsolète
  - budget de bruit intraday inchangé
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 41.5 a déjà posé un budget de bruit intraday objectif; cette story doit l’étendre à la calibration relative sans l’affaiblir. [Source: _bmad-output/implementation-artifacts/41-5-qa-actionability-et-budget-de-bruit-intraday.md]
- 38.3 a renforcé la QA produit sur cas réels; la calibration relative doit suivre la même exigence de validation qualitative. [Source: _bmad-output/implementation-artifacts/38-3-qa-produit-cas-reels.md]

### Git Intelligence Summary

- Les derniers ajustements sur les journées plates ont montré que des changements apparemment mineurs de projection publique peuvent casser la cohérence produit; cette story est le garde-fou final contre ces régressions.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md`, de `epics.md` et de la spec `_bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]
- [Source: _bmad-output/implementation-artifacts/41-5-qa-actionability-et-budget-de-bruit-intraday.md]
- [Source: backend/app/tests/integration/test_daily_prediction_qa.py]
- [Source: backend/app/tests/unit/test_public_projection.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story implémentée le 2026-03-10.
- Extension des fixtures dans `intraday_qa_fixtures.py` avec support des baselines et mock engine.
- Mise à jour du report QA dans `intraday_qa_report.py` (ajout `total_micro_trends`).
- Passe de vérification globale du 2026-03-11: fallback sûr sur snapshot complet dans le routeur uniquement si nécessaire.
- Passe de vérification globale du 2026-03-11: projection publique durcie pour ne pas synthétiser de fenêtres sur snapshot low-signal et pour fusionner les blocs timeline neutres identiques.
- Vérifications ciblées repassées avec succès sur baseline, scoring relatif, projection publique et QA produit.

### Completion Notes List

- QA de la calibration relative verrouillé : les scénarios de journées plates et actives sont correctement discriminés et protégés.
- Les micro-tendances sont limitées à 3 et n'apparaissent que si les conditions produit sont réunies.
- Le budget de bruit public reste sous contrôle après filtrage des pivots reconstruits et consolidation de la timeline.
- La matrice de validation 41.12–41.16 repasse verte après corrections.
- Passe de stabilisation 2026-03-11: isolation automatique des `dependency_overrides` FastAPI entre suites unitaires et d’intégration pour supprimer les fuites de mocks inter-tests.
- Passe de stabilisation 2026-03-11: durcissement de `AuditService` et des suites daily/geocoding/guidance pour éviter les faux négatifs liés à des objets ORM ou rôles mockés non sérialisables.

### File List

- `backend/app/prediction/public_projection.py`
- `backend/app/services/audit_service.py`
- `backend/app/tests/fixtures/intraday_qa_fixtures.py`
- `backend/app/tests/helpers/intraday_qa_report.py`
- `backend/app/tests/integration/conftest.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `backend/app/tests/integration/test_geocoding_api.py`
- `backend/app/tests/integration/test_enterprise_credentials_api.py`
- `backend/app/tests/integration/test_natal_calculate_api.py`
- `backend/app/tests/unit/conftest.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/api/v1/routers/predictions.py`
- `_bmad-output/implementation-artifacts/41-16-qa-et-gardefous-produit-pour-la-calibration-relative.md`
