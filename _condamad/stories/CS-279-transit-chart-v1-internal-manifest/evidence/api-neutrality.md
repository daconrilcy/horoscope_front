# API Neutrality Evidence - CS-279

- `backend/tests/architecture/test_api_contract_neutrality.py` ajoute `test_transit_chart_manifest_is_not_public_api_contract`.
- Le test inspecte `app.routes`, `app.openapi()` et `TestClient(app)`.
- Resultat cible: `TransitChartManifest`, `TransitManifestClassification`, `transit_chart_manifest` et `transit_chart_v1` restent absents des schemas/routes/OpenAPI publics.
- Aucun fichier `frontend/src/**`, router public, schema public, migration ou modele DB n'est modifie par CS-279.
