# Baseline CS-310

Date: 2026-05-26

## Sources relues

- `_story_briefs/cs-310-tests-manuels-profils-naissance-projections-natal.md`: brief source de QA manuelle `/natal`.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json`: exemples backend, dont naissance sans heure en `state=degraded`.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`: preuve du client central et de l'affichage B2C.
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-ledger.json`: baseline navigateur `/natal` desktop/mobile avec les deux projections visibles.
- `frontend/src/pages/NatalChartPage.tsx`: owner de page `/natal`.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`: owner orchestration projection.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: owner affichage projection.
- `frontend/src/api/astrologyProjections.ts`: client HTTP central.
- `backend/app/services/api_contracts/public/projections.py`: contrat public projection.

## Etat avant implementation

- Les tests frontend existants couvrent les bandeaux `degraded_mode`, les donnees de naissance incompletes, les projections B2C, les erreurs de projection, les entitlements et les mentions legales applicatives.
- Les tests backend existants couvrent le endpoint public `/v1/astrology/projections`, dont `birth_input` sans heure et `chart_id` inconnu.
- Aucun changement applicatif n'est requis pour produire la preuve CS-310.

