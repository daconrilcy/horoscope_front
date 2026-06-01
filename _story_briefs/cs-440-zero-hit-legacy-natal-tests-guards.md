# CS-440 - Verrou Zero Hit Legacy Natal Et Nettoyage Des Tests

<!-- Commentaire global: ce brief cadre la derniere passe anti-retour apres suppression du legacy natal. -->

## Resume

Transformer les allowlists temporaires CS-434/CS-435 en gardes zero-hit ou en
allowlists minimales limitees aux preuves `_condamad`. Cette story ferme la serie
de suppression en supprimant les tests, fixtures et exemptions qui maintiennent les
anciens symboles comme vocabulaire nominal.

## Perimetre Inclus

1. Relire les allowlists:
   - CS-434 `legacy-allowlist.md`;
   - CS-435 `legacy-scan-results.md`;
   - tout inventaire CS-426 encore actif.
2. Supprimer les tests nominaux qui creent ou attendent:
   - `natal_interpretation_short`;
   - `natal_long_free`;
   - `natal_interpretation` pour Basic/Free;
   - `use_case_level` en contrat public moderne;
   - `variant_code` comme commande de generation.
3. Conserver uniquement des tests d'extinction, avec noms explicites:
   - `test_legacy_natal_*_is_absent`;
   - `test_old_public_route_is_removed_or_gone`;
   - `test_theme_natal_contract_is_only_public_generation_path`.
4. Ajouter ou mettre a jour un guard d'architecture qui echoue sur tout nouveau hit
   legacy hors chemins autorises.
5. Mettre a jour le registre de guardrails avec un nouvel invariant durable si la
   suppression est complete.
6. Produire un rapport final de scan zero-hit.

## Hors Perimetre

- Implementer les suppressions fonctionnelles des CS-436 a CS-439.
- Supprimer les documents historiques `_condamad/reports` ou briefs deja livres.
- Supprimer `basic_natal_prompt_payload` si CS-437 l'a conserve comme payload moderne
  `theme_astral`; dans ce cas il doit etre allowliste par owner moderne.
- Toucher `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md`
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - aucune facade legacy.
  - `RG-010` - tests sous topologie collectee.
  - `RG-012` - pas de nouveaux tests story-numbered non classes.
  - `RG-014` - pas de tests noop.
  - `RG-018` - pas de fallback prompt supporte.
  - `RG-021` - fallbacks restants classifies ou supprimes.
  - `RG-149` - cartographie prompt-generation exacte.
  - `RG-153`, `RG-154`, `RG-170` - DOM natal moderne conserve.
  - `RG-173` - aucune generation publique par old raw use case.
- Required regression evidence:
  - Scans zero-hit ou allowlist minimale.
  - Tests backend architecture et llm orchestration.
  - Tests front DOM/API.
  - Mise a jour du registre si nouvel invariant.
- Allowed differences:
  - Suppression d'anciens tests et fixtures.
  - Changement de noms de tests pour clarifier leur role anti-retour.

## Criteres D'acceptation

1. Les allowlists CS-434/CS-435 sont fermees: elles ne peuvent plus autoriser de
   code runtime legacy sous `backend/app` ou `frontend/src`; les seuls residus
   acceptes sont des preuves `_condamad` ou des tests d'extinction nommes.
2. Aucun test nominal n'utilise `natal_interpretation_short` comme prompt actif.
3. Aucun test nominal n'utilise `natal_long_free` comme prompt actif.
4. Aucun test nominal ne mocke l'ancien `generate_natal_interpretation` comme runtime
   positif.
5. Les scans legacy sur `backend/app` et `frontend/src` sont zero-hit pour:
   - `natal_interpretation_short`;
   - `natal_long_free`;
   - `use_case_level` dans les contrats publics theme natal;
   - `shouldRefreshShortAfterBasicUpgrade`;
   - `forceRefresh`.
6. Les hits `variant_code` restants sont limites aux entitlements, prediction/daily,
   calculs astrologiques ou donnees historiques explicitement non generatives.
   Aucun hit ne doit construire une commande theme natal ou choisir un prompt.
7. Le registre `regression-guardrails.md` contient un invariant durable de type
   "Legacy natal deleted: zero public/runtime hit".
8. Un rapport final sous `_condamad/reports` documente les suppressions, scans et
   risques residuels.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short
python -B -m pytest -q tests/unit/domain/theme_natal tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_public_reads.py --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src backend/tests frontend/src/tests
rg -n "use_case_level" backend/app/services/api_contracts/public backend/app/api/v1/routers/public frontend/src/api/natal-chart frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation|patch\.object\(AIEngineAdapter, \"generate_natal_interpretation\"" backend/app backend/tests
```

## Dependances

- CS-436.
- CS-437.
- CS-438.
- CS-439.

## Risques

Cette story ne doit pas devenir une passe cosmetique de scans. Si un hit legacy
reste necessaire au runtime, il faut rouvrir la story fonctionnelle correspondante
au lieu d'ajouter une nouvelle exception permanente.
