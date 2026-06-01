# CS-438 - Remplacer L'API Historique Des Interpretations Par Les Slots Theme Natal

<!-- Commentaire global: ce brief cadre la suppression de la facade publique historique des interpretations natales. -->

## Resume

Supprimer la dependance publique a `/v1/natal/interpretations` pour les lectures
natales modernes et remplacer GET/LIST/PDF/delete par des routes ou projections
fondees sur les slots `theme_natal`. L'ancien POST `/v1/natal/interpretation`
est deja non generatif; cette story retire le reste de la facade publique
historique comme API nominale.

## Perimetre Inclus

1. Inventorier les consommateurs frontend et backend de:
   - `GET /v1/natal/interpretations`;
   - `GET /v1/natal/interpretations/{id}`;
   - `DELETE /v1/natal/interpretations/{id}`;
   - `GET /v1/natal/interpretations/{id}/pdf`;
   - `GET /v1/natal/pdf-templates`.
2. Ajouter ou finaliser les endpoints modernes equivalents sous
   `/v1/theme-natal/readings`.
3. Faire lire uniquement les slots publics `accepted` pour les lectures modernes.
4. Decider explicitement du sort des anciennes lignes `user_natal_interpretations`:
   - dev purge;
   - admin/debug only hors surface publique;
   - migration one-shot vers slots modernes si elle est plus simple que la purge.
5. Supprimer l'ancien routeur public des interpretations natales de la surface
   montee publiquement. Ne pas conserver de facade publique 410 comme contrat
   nominal; le retrait doit etre visible dans l'inventaire de routes et l'OpenAPI.
6. Adapter OpenAPI et tests pour que la surface publique nominale soit `theme-natal`.
7. Supprimer les mappings publics qui transforment `natal_long_free` en
   `natal_interpretation_short`.

## Hors Perimetre

- Refaire le moteur PDF complet si le PDF moderne n'existe pas encore; dans ce cas,
  cadrer un endpoint `theme-natal` minimal et documenter la limite.
- Migrer les donnees production: l'application n'est pas encore en prod selon la
  decision Big Bang.
- Modifier les calculs astrologiques.
- Toucher les routes admin LLM.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/routers/public/theme_natal_readings.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `backend/app/infra/db/models/llm_generation_run.py`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de facade legacy reintroduite.
  - `RG-002` - les routeurs gardent une responsabilite claire.
  - `RG-003` - routes API v1 montees via le mecanisme canonique.
  - `RG-004` - erreurs HTTP centralisees.
  - `RG-005` - pas de logique metier dans les routeurs.
  - `RG-006` - frontiere API/service respectee.
  - `RG-150` - les rejets LLM ne sont pas publics.
  - `RG-157` - quota debite uniquement apres lecture complete valide.
  - `RG-173` - routes publiques fondees sur product+LLM contracts.
- Required regression evidence:
  - OpenAPI before/after filtre sur `/v1/natal` et `/v1/theme-natal`.
  - Inventaire runtime `app.routes`.
  - Tests GET/LIST accepted-only sur slots modernes.
- Allowed differences:
  - Suppression de routes publiques historiques.
  - Changement volontaire des URLs frontend vers `/v1/theme-natal/readings`.

## Criteres D'acceptation

1. Le frontend nominal n'appelle plus `/v1/natal/interpretations`.
2. Les routes publiques modernes permettent de lire une lecture acceptee depuis
   `theme_natal_reading_slots`.
3. Les runs rejetes ou techniques restent invisibles publiquement.
4. L'ancien POST `/v1/natal/interpretation` est absent de l'OpenAPI publique et
   de l'inventaire runtime public; aucune compatibilite 410 publique ne reste.
5. Aucun mapping public ne retourne `use_case=natal_interpretation_short` pour une
   ligne `natal_long_free`.
6. Les delete/PDF/list historiques sont soit remplaces, soit explicitement retires
   avec tests front de non-appel.
7. Les routes admin/debug eventuelles ne sont pas montees sous public et ne
   re-exportent pas les handlers publics supprimes.
8. Les tests d'architecture routes et OpenAPI prouvent l'absence de facade legacy
   nominale.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_theme_natal_public_reads.py tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_contract_bound_llm_gateway_rejections.py --tb=short
python -B -m pytest -q app/tests/unit/test_backend_test_topology.py tests/architecture --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx
```

Scans:

```powershell
rg -n "/v1/natal/interpretations|/v1/natal/interpretation|natal_long_free|natal_interpretation_short" frontend/src backend/app/api/v1/routers/public backend/app/services/api_contracts/public
rg -n "theme-natal/readings" frontend/src backend/app/api/v1/routers/public
```

## Dependances

- CS-436 avant suppression complete du routeur si celui-ci depend encore de
  `NatalInterpretationService`.
- CS-439 pour retirer les adaptateurs front restants.

## Risques

La suppression de PDF/delete/list peut casser des boutons front encore visibles.
La story doit trancher dans le meme diff: soit fournir l'equivalent moderne, soit
retirer l'action UI. Elle ne doit pas garder une action visible branchee sur une
route historique.
