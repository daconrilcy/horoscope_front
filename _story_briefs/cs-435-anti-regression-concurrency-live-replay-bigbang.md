# CS-435 - Anti Regression Concurrency And Live Replay Big Bang

<!-- Commentaire global: ce brief cadre la cloture Big Bang par scans, tests de concurrence et replay live du parcours theme natal. -->

## Resume

Cloturer le Big Bang par une validation transversale: scans anti-retour, tests de concurrence,
tests entitlement frais, replay du parcours Free -> Basic -> lecture complete, et preuve que le
legacy n'est plus generateur public.

## Perimetre Inclus

1. Ajouter une suite de scans anti-regression bloquants.
2. Ajouter tests de concurrence:
   - deux clics simultanes;
   - un seul slot generating;
   - une seule lecture accepted;
   - pas de double quota.
3. Ajouter tests entitlement frais apres checkout Basic ou simulation equivalente.
4. Ajouter replay live/local avec utilisateur test ou fixture:
   - Free preview;
   - upgrade Basic;
   - generate_full Basic;
   - aucune lecture short supplementaire;
   - GET/list accepted-only.
5. Produire evidence avant/apres.
6. Produire des preuves SQL/API concretes:
   - count des readings publics par `chart_id` et `output_variant`;
   - count des runs rejetes et preuve qu'ils ne sortent pas en GET/list;
   - preuve que l'ancien endpoint ne peut pas generer;
   - preuve que les logs ne contiennent pas `plan=free` pour une action Basic payante;
   - preuve que le quota est debite une seule fois apres `accepted`.
7. Mettre a jour guardrails si un nouvel invariant durable est cree.

## Hors Perimetre

- Nouvelles features produit.
- Redesign UI.
- Optimisation provider.
- Nettoyage de `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`
- `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de retour legacy facade.
  - `RG-018` - pas de fallback prompt canonique.
  - `RG-021` - fallbacks classifies.
  - `RG-149` - cartographie prompt-generation explicite.
  - `RG-150` - rejets exclus public.
  - `RG-152` - pas de fuite technique.
  - `RG-154` - denylist DOM publique.
  - `RG-155` - invalides rejetes hors public.
  - `RG-157` - quota transactionnel.
  - `RG-164` a `RG-172` - invariants Basic natal existants.
- Required regression evidence:
  - Suite backend.
- Suite frontend ciblee.
- Scans anti-retour.
- Replay evidence.
- Artefacts:
  - `evidence/replay-free-basic-generate-full.md`;
  - `evidence/concurrency-proof.md`;
  - `evidence/entitlement-freshness-proof.md`;
  - `evidence/public-get-list-accepted-only.md`;
  - `evidence/legacy-scan-results.md`.
- Registry enrichment expected:
  - Ajouter un guardrail durable: toute generation LLM publique theme natal passe par
    `ThemeNatalReadingProductContract` et `LLMGenerationContract`; aucun endpoint public ne peut
    appeler un prompt natal par ancien `use_case` brut.
- Allowed differences:
  - Anciennes donnees dev peuvent etre purgees ou marquees `legacy_readonly`.

## Criteres D'acceptation

1. Le parcours Free -> Basic -> generate_full produit au maximum une Free preview et une Basic full reading.
2. Aucune lecture `natal_interpretation_short` n'est creee apres upgrade Basic.
3. Basic full reading contient contract key/version/hash/schema/data hash.
4. Les routes publiques GET/list retournent uniquement accepted.
5. Deux generations simultanees ne creent ni double accepted ni double quota.
6. Apres checkout Basic, une action payante ne se resout jamais `plan=free`.
7. Les scans legacy sont zero-hit ou hits historiques explicitement allowlistes.
8. Le DOM public ne montre pas de fuites techniques ni de fallback legacy.
9. Le registre guardrails contient le nouvel invariant Big Bang si cree.
10. Les preuves SQL/API listent les counts publics par `chart_id/output_variant`.
11. Les preuves SQL/API montrent que les runs rejetes ne sortent pas en GET/list public.
12. Les preuves SQL/API montrent que l'ancien endpoint ne peut pas generer.
13. Les preuves SQL/API montrent qu'une action Basic payante ne produit pas de log `plan=free`.
14. Les preuves SQL/API montrent un seul debit quota apres `accepted`.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration tests/llm_orchestration -k "theme_natal or basic_full_reading or concurrency or entitlement" --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation" backend/app frontend/src
rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src backend/app
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|EXIGENCE PREMIUM|AstroResponse_v3" backend/app backend/tests
rg -n "ThemeNatalReadingProductContract|LLMGenerationContract|basic_full_reading|generation_contract_hash" backend/app backend/tests frontend/src
Test-Path _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/replay-free-basic-generate-full.md
Test-Path _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/concurrency-proof.md
Test-Path _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/entitlement-freshness-proof.md
Test-Path _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/public-get-list-accepted-only.md
Test-Path _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md
git status --short -- _condamad _story_briefs backend frontend
```

## Dependances

- CS-426 a CS-434.

## Risques

Le risque est une cloture documentaire sans preuve runtime. Cette story exige replay, concurrence,
entitlement et scans anti-retour comme preuves de fin de Big Bang.
