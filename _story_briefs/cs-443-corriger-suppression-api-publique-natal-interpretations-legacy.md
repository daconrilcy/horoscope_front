# CS-443 - Corriger La Suppression De L'API Publique Natal Interpretations Legacy

<!-- Commentaire global: ce brief cadre le rattrapage CS-438 apres constat que les routes publiques historiques restent montees. -->

## Resume

Rattraper l'echec de suppression de l'API publique historique
`/v1/natal/interpretation(s)`. La review a confirme que l'ancien POST existe encore
en `410 Gone` et que les routes list/get/delete/pdf historiques restent montees.
Cette story doit retirer ces routes de la surface publique nominale et faire passer
la lecture moderne par les slots `theme_natal`.

## Constats De Depart

- `_condamad/stories/story-status.md` marque `CS-438` `ready-to-dev`.
- `backend/app/api/v1/routers/public/natal_interpretation.py` expose encore:
  - `POST /v1/natal/interpretation` en `410`;
  - `GET /v1/natal/interpretations`;
  - `GET /v1/natal/interpretations/{id}`;
  - `DELETE /v1/natal/interpretations/{id}`;
  - `GET /v1/natal/interpretations/{id}/pdf`.
- Le brief CS-438 demande l'absence du POST dans l'OpenAPI/runtime public, sans
  compatibilite publique 410.

## Perimetre Inclus

1. Retirer l'ancien routeur public des interpretations natales du montage public.
2. Supprimer ou rendre non publiques les routes:
   - `POST /v1/natal/interpretation`;
   - `GET /v1/natal/interpretations`;
   - `GET /v1/natal/interpretations/{id}`;
   - `DELETE /v1/natal/interpretations/{id}`;
   - `GET /v1/natal/interpretations/{id}/pdf`.
3. Ajouter ou finaliser les routes modernes de lecture sous `/v1/theme-natal/readings`
   si une action front a encore besoin de list/get/download/delete.
4. Supprimer les mappings publics `natal_long_free -> natal_interpretation_short`.
5. Adapter les tests OpenAPI/routes.
6. Adapter le frontend si une action appelle encore une route historique.
7. Produire un snapshot before/after des routes et OpenAPI.

## Hors Perimetre

- Supprimer le runtime provider legacy: traite par CS-441.
- Supprimer les seeds/catalogues legacy: traite par CS-442.
- Refaire tout le moteur PDF si l'action PDF est retiree temporairement de l'UI.
- Modifier `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/routers/public/theme_natal_readings.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de facade historique publique.
  - `RG-002` - routeurs API v1 a responsabilite claire.
  - `RG-003` - montage canonique des routes.
  - `RG-004` - erreurs HTTP centralisees.
  - `RG-005` - pas de logique metier dans les routes.
  - `RG-006` - frontiere API/service.
  - `RG-150` - rejets non publics.
  - `RG-157` - quota seulement apres acceptation valide.
  - `RG-173` - product+LLM contracts publics.
  - `RG-174` - zero public/runtime hit legacy.
- Required regression evidence:
  - Route inventory before/after.
  - OpenAPI filtered diff.
  - Tests frontend prouvant aucun appel historique.
  - Tests backend accepted-only sur slots modernes.
- Allowed differences:
  - Suppression volontaire de routes publiques legacy.
  - Retrait temporaire d'actions UI sans endpoint moderne, si explicitement teste.

## Criteres D'acceptation

1. `/v1/natal/interpretation` est absent de l'inventaire runtime public.
2. `/v1/natal/interpretations*` est absent de l'inventaire runtime public.
3. L'OpenAPI publique ne publie plus ces chemins.
4. Le frontend nominal n'appelle plus `/v1/natal/interpretation(s)`.
5. La lecture publique moderne passe par `theme_natal_reading_slots` et retourne
   seulement des slots `accepted`.
6. Aucun mapping public ne convertit `natal_long_free` en
   `natal_interpretation_short`.
7. Les boutons PDF/delete/list sont soit rebranches sur endpoints modernes, soit
   retires de l'UI avec tests.
8. CS-440 peut remplacer le test "old route is gone or removed" par un test
   d'absence stricte de route.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_public_reads.py tests/integration/test_contract_bound_llm_gateway_rejections.py --tb=short
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "/v1/natal/interpretation|/v1/natal/interpretations" backend/app/api/v1/routers/public frontend/src
rg -n "natal_long_free|natal_interpretation_short" backend/app/api/v1/routers/public backend/app/services/api_contracts/public frontend/src/api/natal-chart frontend/src/features/natal-chart
```

## Dependances

- Peut etre implementee apres ou en parallele de CS-441.
- Doit etre terminee avant CS-444.

## Risques

Le retrait de list/get/pdf/delete peut casser des actions utilisateur visibles.
La story doit choisir dans le meme diff: endpoint moderne equivalent ou retrait UI
teste; aucune action ne doit rester branchee sur l'ancienne API.
