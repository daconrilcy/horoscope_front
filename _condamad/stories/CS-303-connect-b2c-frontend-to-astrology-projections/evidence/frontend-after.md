# Frontend After

- `frontend/src/api/astrologyProjections.ts` expose un wrapper authentifie centralise pour `POST /v1/astrology/projections`.
- `NatalInterpretationSection` charge les deux projections B2C a partir du `chartId` existant et transmet un etat de rendu presentational.
- `InterpretationContent` affiche `beginner_summary_v1` et `client_interpretation_projection_v1` avec loading, empty, error, entitlement et degraded states.
- Le rendu des disclaimers reste app-owned via `legalNoticeLines`; aucun texte de disclaimer n'est lu depuis les payloads de projection.
