# CS-302 — Test Astrology Projections Endpoint In Real Conditions

## Résumé

Valider `POST /v1/astrology/projections` en conditions proches réel avec données utilisateur, entitlement, persistance optionnelle, erreurs et smoke OpenAPI.

## Contexte

Le backend projections est livré et validé localement. Avant de brancher le frontend B2C, il faut prouver que l'endpoint générique fonctionne avec des scénarios représentatifs, pas seulement avec des tests unitaires isolés.

## Objectif

Produire une preuve runtime consommable pour les projections B2C :

- `structured_facts_v1`;
- `beginner_summary_v1`;
- `client_interpretation_projection_v1`;
- plans `free`, `basic`, `premium`;
- mode dégradé quand certaines données, comme l'heure de naissance, sont absentes.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `backend/app/api/v1/routers/public/projections.py`
- `backend/app/services/projections/projection_endpoint_service.py`
- `backend/app/services/api_contracts/public/projections.py`
- les tests CS-291 existants.

## Périmètre inclus

1. Construire des scénarios HTTP réalistes avec `TestClient` ou serveur local.
2. Tester `POST /v1/astrology/projections` pour chaque projection B2C supportée.
3. Tester les plans et refus d'entitlement.
4. Tester les erreurs de payload et les réponses sans chart disponible.
5. Tester la persistance optionnelle si le contrat le permet.
6. Capturer une preuve OpenAPI et une preuve de réponse JSON.
7. Documenter les limites restantes avant branchement frontend.

## Hors périmètre

- Ajouter une UI frontend.
- Modifier les builders.
- Modifier le modèle d'entitlement.
- Ajouter replay ou audit admin.

## Critères d'acceptation

1. Les trois projections B2C répondent avec le contrat attendu.
2. Les refus d'autorisation/entitlement sont stables.
3. Les erreurs de payload sont explicites.
4. Le mode dégradé est visible dans le payload quand applicable.
5. OpenAPI expose toujours uniquement le endpoint public attendu.
6. Les preuves sont stockées dans la story.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests\api\test_projection_endpoint.py tests\api\test_projection_authorization.py tests\api\test_projection_persistence_endpoint.py tests\api\test_projection_openapi.py --tb=short
python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"
```

## Dépendances

- CS-291.
- CS-284.
- CS-285 à CS-287.

## Risques

Le risque principal est de brancher le frontend sur un endpoint qui fonctionne seulement dans des fixtures faibles. Cette story doit produire des cas représentatifs et des preuves exploitables par le frontend.
