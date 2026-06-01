# CS-426 - Freeze Inventory Legacy Generation Natal Big Bang

<!-- Commentaire global: ce brief cadre l'inventaire destructif controle avant toute implementation du runtime Big Bang theme natal. -->

## Resume

Cartographier et classifier tous les chemins encore capables de generer une lecture natale publique
via l'ancien runtime avant d'ajouter le nouveau modele contractuel. Cette story ne doit coder aucun
nouveau runtime fonctionnel.

Objectif: empecher que le Big Bang devienne une couche supplementaire au-dessus de
`natal_long_free`, `natal_interpretation_short`, `natal_interpretation` ou des fallbacks existants.

## Perimetre Inclus

1. Inventorier les endpoints publics/admin/dev capables de declencher une generation natale.
2. Inventorier les services, gateways, seeds, prompts, schemas, tests, mocks et composants frontend
   lies aux generations natales legacy.
3. Produire une classification persistante par surface:
   - `delete`;
   - `replace`;
   - `readonly`;
   - `keep`;
   - `needs-decision`.
4. Distinguer lecture legacy non generatrice et generation legacy active.
5. Identifier les chemins qui utilisent encore:
   - `natal_interpretation_short`;
   - `natal_long_free`;
   - `natal_interpretation`;
   - `use_case_level`;
   - `variant_code` cote frontend;
   - `forceRefresh` pour generation LLM;
   - fallback public deterministe;
   - cache/persistence sans `chart_id`.
6. Produire les scans initiaux qui deviendront bloquants dans les stories suivantes.
7. Documenter explicitement que `_condamad/run-state.json` est hors perimetre.

## Hors Perimetre

- Implementer `ThemeNatalReadingProductContract`.
- Ajouter des tables ou migrations.
- Brancher un nouveau provider ou fake provider.
- Supprimer physiquement du code legacy.
- Modifier le frontend runtime.
- Traiter la suppression Git de `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - les facades/routes legacy ne doivent pas etre reintroduites comme wrappers.
  - `RG-002` - les routeurs API restent adapteurs, pas owners de logique metier.
  - `RG-005` - pas de logique metier/persistence opportuniste dans les routes.
  - `RG-018` - les familles LLM supportees ne doivent pas redevenir proprietaires de prompt via fallback.
  - `RG-021` - les fallbacks restants doivent etre classes.
  - `RG-149` - la cartographie prompt-generation doit rester explicite.
  - `RG-150` - les rejets restent exclus du public.
  - `RG-152` - les lectures publiques ne doivent pas exposer audit/signaux internes.
  - `RG-157` - quota natal complete transactionnel.
  - `RG-171` - le prompt Basic ne doit pas router par anciennes cles natal.
  - `RG-172` - le cache Basic respecte la version editoriale.
- Required regression evidence:
  - Rapport d'inventaire: `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`
  - Classification: `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md`
  - Scans cibles listes ci-dessous.
- Allowed differences:
  - Documentation et artefacts d'inventaire uniquement.

## Criteres D'acceptation

1. Tous les chemins generatifs natals legacy sont listes avec chemin fichier, symbole, declencheur et classification.
2. Tous les chemins frontend capables d'envoyer un niveau/use case LLM sont listes.
3. Tous les seeds/prompts/use cases natals legacy sont classes.
4. Les chemins readonly sont explicitement non generateurs.
5. Les chemins `needs-decision` ont une decision attendue et un owner.
6. Le rapport distingue generation publique, admin-only, test-only, bootstrap et historique.
7. La suppression de `_condamad/run-state.json` est citee comme hors perimetre et non modifiee.
8. Aucun code fonctionnel nouveau n'est ajoute.

## Commandes De Validation Minimales

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation|basic_natal_prompt_payload" backend frontend _story_briefs _condamad
rg -n "use_case_level|variant_code|forceRefresh|shouldRefreshShortAfterBasicUpgrade" frontend/src backend/app
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|AstroResponse_v3|EXIGENCE PREMIUM" backend/app backend/scripts
rg -n "UserNatalInterpretationModel|chart_id|variant_code|answer_type|was_fallback" backend/app/services/llm_generation/natal backend/app/infra/db/models
git status --short -- _condamad _story_briefs backend frontend
```

## Dependances

- CS-425 est deja utilise par une story existante; ce lot Big Bang commence donc a CS-426.

## Risques

Le risque principal est de commencer par implementer le nouveau modele sans avoir ferme les anciens
chemins generatifs. Cette story force l'inventaire destructif controle avant tout code runtime.
