# Story remove-historical-facade-routes: Supprimer les façades API historiques

Status: ready-for-dev

## 1. Objective

Supprimer les routes, champs, modules et consommations frontend qui existent uniquement pour
maintenir des surfaces historiques. À la fin, les consommateurs first-party doivent utiliser les
endpoints canoniques, les façades supprimées ne doivent plus être enregistrées, importables ou
présentes dans OpenAPI, et les gardes doivent bloquer toute réintroduction.

## 2. Trigger / Source

- Source type: refactor
- Source reference: demande utilisateur du 2026-04-26 et review adversariale du 2026-04-26.
- Reason for change: la surface API expose encore des routes et champs de compatibilité
  historique, notamment autour du moteur LLM public et de l'admin LLM. Ces surfaces maintiennent
  plusieurs chemins pour une même responsabilité et contredisent DRY, No Legacy et mono-domaine.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api/v1` API route surface and first-party API consumers in `frontend/src`
- In scope:
  - Scanner tous les routeurs inclus par `backend/app/main.py`.
  - Scanner tous les modules sous `backend/app/api/v1/routers`.
  - Classer chaque route, champ ou UI route legacy avec les règles déterministes de cette story.
  - Supprimer les items classés `historical-facade` ou `dead` quand aucun blocker externe existe.
  - Adapter les consommateurs frontend first-party vers les propriétaires canoniques existants.
  - Ajouter des gardes backend/frontend/OpenAPI empêchant la réintroduction.
  - Écrire l'audit sous `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md`.
- Out of scope:
  - Repenser le runtime LLM, les modèles DB, les migrations Alembic, billing, auth ou entitlements.
  - Ajouter de nouvelles routes de remplacement.
  - Supprimer une route `external-active` sans décision utilisateur explicite.
  - Nettoyer des compatibilités de données locales frontend non liées à une route API supprimée.
- Explicit non-goals:
  - Ne pas créer de redirection, alias, shim, fallback ou re-export.
  - Ne pas repointer une façade historique vers un service canonique.
  - Ne pas garder deux endpoints actifs pour la même responsabilité canonique.
  - Ne pas faire de refactor cosmétique hors fichiers nécessaires.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire des routes et champs de compatibilité qui préservent des
  surfaces historiques au lieu d'être les propriétaires canoniques du domaine.
- Behavior change allowed: yes
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: un item est classé `external-active` ou `needs-user-decision`.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/main.py` - inclut `ai_engine_router`, donc `/v1/ai/*` est actif.
- Evidence 2: `backend/app/api/v1/routers/public/ai.py` - expose `POST /v1/ai/generate` et
  `POST /v1/ai/chat`; son docstring annonce des endpoints historiques du moteur LLM.
- Evidence 3: `frontend/src/api/chat.ts` - consomme `/v1/chat/*`, pas `/v1/ai/*`.
- Evidence 4: `frontend/src/api/guidance.ts` - consomme `/v1/guidance/*`, pas `/v1/ai/*`.
- Evidence 5: `backend/app/api/v1/router_logic/public/ai.py` - contient des helpers dédiés à la
  façade `/v1/ai`.
- Evidence 6: `backend/app/api/v1/schemas/ai.py` - décrit les contrats `POST /v1/ai/generate` et
  `POST /v1/ai/chat`.
- Evidence 7: `backend/tests/evaluation/__init__.py` - réplique l'inclusion des routeurs de
  `backend/app/main.py`.
- Evidence 8: `backend/app/api/v1/routers/admin/exports.py` - émet encore `use_case_compat` via
  headers de dépréciation et payload d'export.
- Evidence 9: `frontend/src/pages/admin/AdminSettingsPage.tsx` - lit encore `use_case_compat`.
- Evidence 10: `frontend/src/app/routes.tsx` - déclare `/admin/prompts/legacy`.
- Evidence 11: `frontend/src/api/adminPrompts.ts` - expose encore les états `legacy_maintenance`,
  `legacy_alias` et `legacy_registry_only`.

## 6. Target State

After implementation:

- `/v1/ai/*` n'est plus enregistré, importable, présent dans OpenAPI ou consommé.
- Les flux LLM first-party utilisent uniquement `/v1/chat/*` et `/v1/guidance/*`.
- Les champs et états legacy admin ne sont plus produits, typés ou lus comme contrat nominal.
- Les routes frontend purement legacy sont supprimées ou bloquent sur décision documentée.
- L'audit prouve chaque décision avec commandes, chemins et risque.
- Des tests d'architecture empêchent le retour des préfixes, modules, champs et UI routes interdits.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire de suppression est complet et déterministe. | Evidence profile: `route_removed`; audit markdown plus `rg -n "include_router\|APIRouter" backend/app`. |
| AC2 | Les façades supprimables sont supprimées, jamais repointées. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`. |
| AC3 | Aucun item externe n'a `Decision=delete`. | `python scripts/validate_route_removal_audit.py _condamad/stories/remove-historical-facade-routes/route-consumption-audit.md`. |
| AC4 | `/v1/ai/*` est absent de l'application et d'OpenAPI. | Evidence profile: `route_removed`; `pytest -q backend/app/tests/integration/test_api_openapi_contract.py`. |
| AC5 | Les modules Python supprimés ne sont plus importables. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`. |
| AC6 | Les consommateurs LLM first-party ciblent les propriétaires canoniques. | `rg -n "/v1/ai\|ai_engine_router\|app\.api\.v1\.routers\.public\.ai" frontend/src backend/app`. |
| AC7 | `use_case_compat` n'est plus produit ni lu. | `rg -n "use_case_compat" backend/app backend/tests frontend/src`. |
| AC8 | Les états admin legacy ne sont plus typés, produits ou affichés. | `rg -n "legacy_maintenance\|legacy_alias\|legacy_registry_only" backend/app frontend/src`. |
| AC9 | `/admin/prompts/legacy` est absent de `frontend/src`. | Evidence profile: `frontend_route_removed`; `rg -n "/admin/prompts/legacy" frontend/src`. |
| AC10 | Aucun wrapper ou fallback ne remplace la suppression. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`. |
| AC11 | TypeScript, lint, tests backend et tests frontend ciblés passent. | `ruff check .`, pytest ciblés, `npm run lint`, `npm run typecheck`, tests frontend ciblés. |

## 8. Implementation Tasks

- [ ] Task 1 - Écrire l'audit déterministe avant suppression (AC: AC1, AC3)
  - [ ] Subtask 1.1 - Lister les `include_router` de `backend/app/main.py`.
  - [ ] Subtask 1.2 - Lister les routes, champs, fichiers, statuts et UI routes candidats.
  - [ ] Subtask 1.3 - Appliquer la matrice de classification sans catégorie ad hoc.
  - [ ] Subtask 1.4 - Documenter chaque preuve avec commande, chemin ou source d'audit.

- [ ] Task 2 - Supprimer les façades backend LLM prouvées (AC: AC2, AC4, AC5, AC6, AC10)
  - [ ] Subtask 2.1 - Supprimer le montage `ai_engine_router`.
  - [ ] Subtask 2.2 - Supprimer les fichiers dédiés à `/v1/ai/*` si aucun propriétaire canonique ne les utilise.
  - [ ] Subtask 2.3 - Aligner `backend/tests/evaluation/__init__.py`.
  - [ ] Subtask 2.4 - Ajouter les assertions d'absence du préfixe, du module et d'OpenAPI.

- [ ] Task 3 - Fermer les contrats admin legacy (AC: AC7, AC8, AC10, AC11)
  - [ ] Subtask 3.1 - Retirer `use_case_compat` des producteurs backend si l'audit le classe supprimable.
  - [ ] Subtask 3.2 - Retirer les états `legacy_maintenance`, `legacy_alias` et `legacy_registry_only`.
  - [ ] Subtask 3.3 - Adapter les tests admin vers les dimensions canoniques existantes.

- [ ] Task 4 - Retirer les consommations frontend legacy (AC: AC6, AC9, AC11)
  - [ ] Subtask 4.1 - Supprimer ou remplacer les appels API vers les surfaces supprimées.
  - [ ] Subtask 4.2 - Supprimer `/admin/prompts/legacy` si aucun blocker externe n'existe.
  - [ ] Subtask 4.3 - Retirer types, traductions, CSS et tests dédiés uniquement à cette surface.

- [ ] Task 5 - Valider et bloquer la réintroduction (AC: AC4, AC5, AC9, AC10, AC11)
  - [ ] Subtask 5.1 - Ajouter `ForbiddenRouterPrefixes = ["/v1/ai"]` dans le garde d'architecture.
  - [ ] Subtask 5.2 - Vérifier les routes enregistrées, imports, OpenAPI et route table frontend.
  - [ ] Subtask 5.3 - Remplacer tout test positif legacy supprimé par un garde négatif.
  - [ ] Subtask 5.4 - Exécuter lint, format, tests backend, tests frontend et scans négatifs.
  - [ ] Subtask 5.5 - Documenter tout blocker au lieu de continuer silencieusement.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/routers/public/chat.py` for chat LLM HTTP ownership.
  - `backend/app/api/v1/routers/public/guidance.py` for guidance LLM HTTP ownership.
  - `backend/app/services/llm_generation/chat/chat_guidance_service.py` for chat execution.
  - `backend/app/services/llm_generation/guidance/guidance_service.py` for guidance execution.
  - `frontend/src/api/chat.ts` and `frontend/src/api/guidance.ts` for first-party LLM calls.
- Do not recreate:
  - A second public LLM route beside `/v1/chat/*` and `/v1/guidance/*`.
  - Admin legacy fields duplicating canonical feature, subfeature, plan or release snapshot data.
  - A replacement wrapper that keeps the historical URL or import path active.
- Shared abstraction allowed only if:
  - It removes duplication across at least two canonical active endpoints.
  - It lives in an existing canonical service or domain package.
  - It does not expose a legacy route, field, alias or fallback.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/api/v1/routers/public/ai.py`
- `backend/app/api/v1/router_logic/public/ai.py`
- `backend/app/api/v1/schemas/ai.py`
- `app.api.v1.routers.public.ai`
- `ai_engine_router`
- `APIRouter(prefix="/v1/ai")`
- `/v1/ai`
- `/admin/prompts/legacy`
- `use_case_compat`
- `legacy_maintenance`
- `legacy_alias`
- `legacy_registry_only`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is a canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients,
  OpenAPI clients, analytics events, or explicit audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts and known
  external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path:

- `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md`

Rules:

- `Classification` must use only values from `Removal Classification Rules`.
- `Decision` must be `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
- No row classified `external-active` may have `Decision` equal to `delete`.
- `Proof` must include command output, file path evidence, or explicit audit source.
- `Risk` must be filled for every `delete` or `needs-user-decision` item.
- The audit must include docs and generated-surface scans, not only `frontend/src`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public chat LLM HTTP API | `/v1/chat/*` | `/v1/ai/chat` |
| Public guidance LLM HTTP API | `/v1/guidance/*` | `/v1/ai/generate` |
| Admin prompt catalog and release history | `/v1/admin/llm/*` canonical catalog routes | `/admin/prompts/legacy`, legacy prompt states |
| Admin export contract | Canonical feature, subfeature and plan dimensions | `use_case_compat` |

Any non-canonical surface must be deleted, classified `external-active`, or escalated as
`needs-user-decision`.

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted in this story.

The dev agent must stop or record an explicit user decision with:

- the external evidence;
- the deletion risk;
- the proposed next owner;
- the exact item that remains active.

## 16. Reintroduction Guard

The implementation must add or update an architecture guard that fails if a removed surface is
reintroduced.

The guard must check:

- registered FastAPI route paths for `/v1/ai`;
- `APIRouter` prefix values for `/v1/ai`;
- importability of `app.api.v1.routers.public.ai`;
- generated OpenAPI paths for `/v1/ai`;
- frontend route table for `/admin/prompts/legacy`;
- forbidden legacy fields and states.

Required forbidden examples:

- `/v1/ai`
- `app.api.v1.routers.public.ai`
- `/admin/prompts/legacy`
- `use_case_compat`

## 17. Generated Contract Check

Required generated-contract evidence:

- FastAPI OpenAPI paths must not contain `/v1/ai/generate` or `/v1/ai/chat`.
- Generated or typed frontend contracts must not expose `use_case_compat`.
- Route manifests or route tests must not expose `/admin/prompts/legacy`.

If a generated client or route manifest does not exist, the implementation evidence must record the
missing artifact and the replacement validation command used.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/main.py`
- `backend/tests/evaluation/__init__.py`
- `backend/app/api/v1/routers/public/ai.py`
- `backend/app/api/v1/router_logic/public/ai.py`
- `backend/app/api/v1/schemas/ai.py`
- `backend/app/api/v1/routers/public/chat.py`
- `backend/app/api/v1/routers/public/guidance.py`
- `backend/app/api/v1/routers/admin/exports.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `frontend/src/api/chat.ts`
- `frontend/src/api/guidance.ts`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md` - audit structuré.
- `scripts/validate_route_removal_audit.py` - validation stricte de la table d'audit.
- `backend/app/main.py` - retirer les routeurs façade supprimés.
- `backend/tests/evaluation/__init__.py` - aligner le montage de test.
- `backend/app/api/v1/routers/public/ai.py` - delete if `historical-facade` or `dead`; otherwise blocker.
- `backend/app/api/v1/router_logic/public/ai.py` - delete if unused after route removal; otherwise blocker.
- `backend/app/api/v1/schemas/ai.py` - delete if dedicated to removed route; otherwise blocker.
- `backend/app/api/v1/routers/admin/exports.py` - remove compat field if classified removable.
- `frontend/src/api/adminPrompts.ts` - retrait des états legacy.
- `frontend/src/app/routes.tsx` - delete route if `historical-facade` or `dead`; otherwise blocker.
- `frontend/src/pages/admin/AdminPromptsPage.tsx` - remove legacy surface if classified removable.
- `frontend/src/pages/admin/AdminSettingsPage.tsx` - remove `use_case_compat` if classified removable.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - gardes route, module, champ et préfixe.
- `backend/app/tests/integration/test_api_openapi_contract.py` - absence OpenAPI de `/v1/ai`.
- `backend/app/tests/integration/test_chat_api.py` - chemin chat canonique.
- `frontend/src/tests/AdminPromptsRouting.test.tsx` - absence route legacy.
- `frontend/src/tests/AdminSettingsPage.test.tsx` - retrait `use_case_compat`.
- `frontend/src/tests/adminPromptsApi.test.ts` - types et payloads canoniques.

Files not expected to change:

- `backend/pyproject.toml` - aucune dépendance nouvelle.
- `frontend/package.json` - aucune dépendance nouvelle.
- `backend/migrations` - aucune migration DB attendue.
- `backend/app/infra/db/models` - aucun modèle DB attendu.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/app/tests/unit/test_api_router_architecture.py
pytest -q backend/app/tests/integration/test_api_openapi_contract.py
pytest -q backend/app/tests/integration/test_chat_api.py
@'
import importlib
try:
    importlib.import_module("app.api.v1.routers.public.ai")
except ModuleNotFoundError:
    raise SystemExit(0)
raise SystemExit("Forbidden module is still importable")
'@ | python -
rg -n "/v1/ai|ai_engine_router|use_case_compat|legacy_maintenance|legacy_alias|legacy_registry_only" app tests
cd ..
cd frontend
npm run lint
npm run typecheck
npm run test -- --run src/tests/AdminPromptsRouting.test.tsx src/tests/AdminSettingsPage.test.tsx src/tests/adminPromptsApi.test.ts
rg -n "/v1/ai|/admin/prompts/legacy|use_case_compat|legacy_maintenance|legacy_alias|legacy_registry_only" src
cd ..
rg -n "/v1/ai|/admin/prompts/legacy|use_case_compat" . `
  --glob "!node_modules" `
  --glob "!.git" `
  --glob "!_condamad/stories/remove-historical-facade-routes/00-story.md" `
  --glob "!_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md"
```

The import check must succeed only when the forbidden module cannot be imported. OpenAPI validation
must be generated from the real FastAPI app exported by `backend/app/main.py`. If a command or script
does not exist, record the exact skipped command and residual risk in the implementation evidence.
Negative `rg` commands must return no result. The final repository-wide scan excludes this story and
the audit because they preserve historical proof. If `/admin/prompts/legacy` remains in
`frontend/src`, the item must be classified `needs-user-decision` and the story must not be marked
done.

## 22. Regression Risks

- Risk: supprimer une route non appelée par le frontend mais utilisée par email, docs ou intégration.
  - Guardrail: classer `external-active`; ne pas supprimer sans décision utilisateur.
- Risk: un agent repointe une façade au lieu de la supprimer.
  - Guardrail: `Delete-Only Rule`; les tests doivent échouer si l'ancien préfixe reste enregistré.
- Risk: l'admin LLM perd une surface encore nécessaire à l'investigation hors catalogue.
  - Guardrail: classifier en `needs-user-decision` si le remplacement canonique n'est pas prouvé.
- Risk: des types frontend orphelins restent après suppression de route.
  - Guardrail: `npm run typecheck`, `npm run lint` et scans négatifs.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not delete any `external-active` item without explicit user decision.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas créer de `requirements.txt`; `backend/pyproject.toml` reste la source unique.
- Tout fichier applicatif nouveau ou significativement modifié doit contenir un commentaire global
  en français et des docstrings françaises pour les fonctions publiques ou non triviales.

## 24. References

- `backend/app/main.py` - source des routeurs FastAPI actifs.
- `backend/app/api/v1/routers/public/ai.py` - façade historique LLM ciblée.
- `backend/app/api/v1/routers/public/chat.py` - propriétaire canonique chat.
- `backend/app/api/v1/routers/public/guidance.py` - propriétaire canonique guidance.
- `frontend/src/api` - clients first-party à vérifier et adapter.
- `frontend/src/app/routes.tsx` - routing frontend contenant une surface legacy admin.
- `references/removal-story-contract.md` - contrat de suppression appliqué par le skill.
