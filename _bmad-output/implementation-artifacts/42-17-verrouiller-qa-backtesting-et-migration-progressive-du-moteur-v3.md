# Story 42.17: Verrouiller QA, backtesting et migration progressive du moteur v3

Status: completed

## Story

As a QA engineer,
I want sécuriser la coexistence v2/v3 par des fixtures, des métriques et des gates explicites,
so that la bascule vers le moteur daily v3 soit objectivable et réversible.

## Acceptance Criteria

1. Le backend capitalise sur le mode `dual` introduit tôt dans l'epic pour comparer v2 et v3.
2. Des fixtures couvrent journées plates, actives, ambiguës et intensives.
3. Les rapports comparent au minimum:
   - nombre de pivots
   - dispersion des notes
   - fenêtres publiques
   - stabilité inter-runs
4. Des critères go/no-go explicites de migration sont documentés.
5. Les suites ciblées permettent une décision de bascule ou rollback.

## Tasks / Subtasks

- [x] Task 1: Capitaliser sur le mode `dual` introduit plus tôt (AC: 1, 3)
  - [x] Exploiter le mode de double calcul déjà introduit
  - [x] Produire des métriques de comparaison lisibles

- [x] Task 2: Étendre les fixtures et cas QA (AC: 2)
  - [x] Journées plates
  - [x] Journées actives
  - [x] Journées ambiguës
  - [x] Journées intenses mais neutres

- [x] Task 3: Définir les gates produit de migration (AC: 4, 5)
  - [x] Documenter des critères go/no-go
  - [x] Prévoir un rollback propre

- [x] Task 4: Tests et rapport (AC: 3, 5)
  - [x] Générer un rapport comparatif exploitable
  - [x] Vérifier la stabilité inter-runs
  - [x] Vérifier le respect des SLO runtime clés

## Dev Notes

- Cette story clôt l'Epic 42.
- Elle ne sert pas seulement à “avoir des tests”, mais à objectiver la qualité produit du moteur v3 avant bascule.
- Le meilleur résultat attendu est une migration progressive, mesurée, et réversible.
- Le mode `dual` et quelques fixtures canoniques doivent exister avant cette story; ici, on consolide le backtesting complet et les gates de migration.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/tests/integration/test_daily_prediction_qa.py`
  - `_bmad-output/test-artifacts/v3-migration-gates.md`
  - `backend/app/prediction/public_projection.py`
  - `backend/app/services/daily_prediction_service.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/tests/integration/test_daily_prediction_qa.py]
- [Source: backend/app/services/daily_prediction_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour sécuriser la comparaison v2/v3 et la migration progressive du moteur daily.

### File List

- `_bmad-output/implementation-artifacts/42-17-verrouiller-qa-backtesting-et-migration-progressive-du-moteur-v3.md`
- `_bmad-output/test-artifacts/v3-migration-gates.md`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
