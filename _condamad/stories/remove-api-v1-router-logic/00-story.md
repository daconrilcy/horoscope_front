# Story remove-api-v1-router-logic: Supprimer le namespace router_logic API v1

Status: ready-for-review

## 1. Objective

Supprimer completement `backend/app/api/v1/router_logic` en rebasculant ses responsabilites vers
leurs proprietaires canoniques. Les cas d'usage applicatifs vont sous `backend/app/services/**`,
les helpers transverses purs peuvent aller sous `backend/app/core/**`, et les mappers/factories
strictement HTTP restent sous `backend/app/api/v1/**`. La migration ne doit pas dupliquer les
services metier existants, conserver d'alias Python, ni changer les URLs ou contrats HTTP publics.
Les routeurs `backend/app/api/v1/routers/**` restent des adaptateurs HTTP fins.

## 2. Trigger / Source

- Source type: refactor
- Source reference: demande utilisateur du 2026-04-26 dans l'IDE visant a supprimer
  `backend\app\api\v1\router_logic`.
- Reason for change: le namespace `router_logic` a ete cree comme extraction intermediaire de
  helpers de routeurs. Il contient aujourd'hui des services applicatifs admin, query builders,
  serializers, normalizers et helpers transverses qui appartiennent aux packages `services`
  existants ou doivent etre supprimes s'ils sont morts.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend service/API boundary for API v1 route-support logic
- In scope:
  - Auditer tous les fichiers Python sous `backend/app/api/v1/router_logic`.
  - Auditer les proprietaires existants sous `backend/app/services/**`, `backend/app/core/**` et
    `backend/app/api/v1/**` avant tout deplacement.
  - Classer chaque symbole de `router_logic` comme `canonical-active`, `historical-facade`, `dead`,
    `external-active` ou `needs-user-decision`.
  - Reutiliser, fusionner ou etendre les services existants quand ils portent deja la responsabilite cible.
  - Migrer par lots independants: `admin`, `admin/llm`, `ops`, `b2b`, `public`, `internal`.
  - Creer seulement des modules de service dans des sous-dossiers deja existants de
    `backend/app/services/**`, ou dans un sous-dossier de service justifie par l'audit.
  - Adapter les routeurs API v1 pour importer depuis le proprietaire canonique, jamais depuis
    `app.api.v1.router_logic`.
  - Adapter les tests et chemins de monkeypatch vers les proprietaires canoniques.
  - Supprimer physiquement `backend/app/api/v1/router_logic` une fois tous les consommateurs migres ou supprimes.
  - Ajouter ou renforcer les gardes d'architecture qui interdisent la reintroduction du namespace.
- Out of scope:
  - Modifier ou supprimer une URL HTTP active.
  - Repenser les schemas Pydantic API v1 sauf import strictement necessaire.
  - Repenser auth, CORS, migrations DB, entitlements ou clients frontend.
  - Deplacer la logique HTTP pure des routeurs vers `services`.
  - Forcer dans `services` les helpers generiques, les validations transverses, le format CSV HTTP,
    les conversions d'erreur API, `Request`, `Depends`, `APIRouter` ou `StreamingResponse`.
  - Refactoriser les services existants hors du besoin de convergence `router_logic`.
- Explicit non-goals:
  - Ne pas creer `backend/app/services/router_logic`, `backend/app/services/api_v1_router_logic` ou un autre miroir du namespace supprime.
  - Ne pas creer de wrapper, alias, facade, re-export ou fallback pour l'ancien chemin `app.api.v1.router_logic`.
  - Ne pas dupliquer une responsabilite deja presente dans `backend/app/services`, `backend/app/domain` ou `backend/app/infra`.
  - Ne pas forcer dans `services` un helper qui appartient clairement a `core/**` ou a `api/v1/**`.
  - Ne pas conserver du legacy sous pretexte de compatibilite de tests.
  - Ne pas ajouter de dependance.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: legacy-facade-removal
- Archetype reason: le namespace `app.api.v1.router_logic` est devenu une surface de compatibilite
  interne entre routeurs et logique applicative; la story supprime cette facade Python apres
  migration des consommateurs vers les proprietaires canoniques.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une preuve externe explicite apparait hors imports Python internes et
  tests first-party, si une URL active devrait changer, ou si le deplacement exigerait un nouveau
  dossier racine sous `backend/`.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/api/v1/router_logic` - le scan local liste 54 fichiers Python sous ce namespace.
- Evidence 2: `backend/app/api/v1/routers/public/users.py` et les autres routeurs publics/admin/b2b/ops/internal importent directement depuis `app.api.v1.router_logic.*`.
- Evidence 3: `backend/app/tests/unit/test_admin_manual_execute_response.py` importe encore
  `app.api.v1.router_logic.admin.llm.manual_execution`.
- Evidence 4: `backend/app/tests/integration/test_privacy_api.py`, `test_support_api.py`,
  `test_b2b_usage_api.py` et plusieurs tests ops patchent encore `app.api.v1.router_logic.*`.
- Evidence 5: `backend/app/tests/unit/test_api_router_architecture.py` dit encore que la logique
  non HTTP doit rester dans le package `router_logic`; ce contrat doit etre inverse.
- Evidence 6: `backend/app/api/v1/router_logic/admin/llm/consumption.py` normalise, trie, filtre,
  exporte CSV et appelle `LlmCanonicalConsumptionService`.
- Evidence 7: `backend/app/api/v1/router_logic/ops/entitlement_mutation_audits.py` orchestre
  requetes, diff, review state et mapping de reponse avec des services `canonical_entitlement`.
- Evidence 8: `backend/app/services` existe deja avec des sous-domaines cibles: `b2b`, `billing`,
  `canonical_entitlement`, `consultation`, `email`, `entitlement`, `llm_generation`,
  `llm_observability`, `ops`, `prediction`, `privacy_service.py`, `reference_data_service.py`.
- Evidence 9: `_condamad/stories/converge-api-v1-route-architecture/00-story.md` a conserve
  `router_logic` temporairement; cette story remplace cette direction par sa suppression complete.

## 6. Target State

After implementation:

- Le chemin `backend/app/api/v1/router_logic` n'existe plus dans le depot.
- Aucun import, monkeypatch, commentaire de garde, doc de story active ou code applicatif ne reference `app.api.v1.router_logic`.
- Les routeurs API v1 appellent le proprietaire canonique: `app.services.*` pour les cas d'usage,
  `app.core.*` pour les helpers transverses purs, ou `app.api.v1.*` pour les contrats HTTP/API.
- Les responsabilites applicatives migrees vivent dans les sous-domaines de services existants et reutilisent les classes/fonctions deja presentes.
- Chaque lot de migration (`admin`, `admin/llm`, `ops`, `b2b`, `public`, `internal`) a une preuve
  intermediaire avant de passer au lot suivant.
- Les helpers strictement dupliques avec `app.api.v1.errors.api_error_response` ou `app.api.v1.constants` sont supprimes plutot que deplaces.
- Les symboles morts ou legacy sont supprimes avec leurs tests nominaux; les tests restants patchent les services canoniques.
- Les gardes d'architecture echouent si `backend/app/api/v1/router_logic` ou `app.api.v1.router_logic` reapparait.
- Les contrats OpenAPI et les tests d'integration API v1 restent stables.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Inventaire complet de chaque fichier, symbole significatif et consommateur de `router_logic`. | Audit `router-logic-service-audit.md`; `rg -n "router_logic" app tests`. |
| AC2 | Chaque responsabilite migree a un proprietaire canonique. | Audit avec proprietaire inspecte; `rg --files app/services app/core app/api/v1`. |
| AC3 | Aucun code n'est duplique quand une fonction/classe equivalente existe deja. | Tests unitaires des services cibles; audit DRY; `ruff check .`. |
| AC4 | Les routeurs API v1 ne dependent plus de `app.api.v1.router_logic`. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scan routeurs/tests. |
| AC5 | `backend/app/api/v1/router_logic` est supprime sans shim. | `Test-Path app/api/v1/router_logic`; architecture pytest. |
| AC6 | Les tests qui patchaient/importaient `router_logic` ciblent les services canoniques. | `rg -n "app\\.api\\.v1\\.router_logic" app/tests`; tests d'integration concernes. |
| AC7 | Les helpers morts, facades historiques et legacy trouves pendant l'audit sont supprimes. | Audit; `rg -n "app\\.api\\.v1\\.router_logic" app tests`. |
| AC8 | Les contrats HTTP/OpenAPI des routes consommatrices restent inchanges. | Tests d'integration cibles; OpenAPI assertion dans `test_api_router_architecture.py`. |
| AC9 | Les gardes d'architecture interdisent la reintroduction de `router_logic`. | Garde modifie dans `test_api_router_architecture.py`; test d'import negatif. |
| AC10 | Lint, format, tests backend cibles et tests de services migres passent dans le venv. | `ruff format .`; `ruff check .`; targeted pytest commands from Validation Plan. |
| AC11 | La migration est realisee par lots `admin`, `admin/llm`, `ops`, `b2b`, `public`, `internal`. | Audit par lot; architecture pytest; scans par lot. |
| AC12 | Les helpers sont routes vers `services`, `core` ou `api/v1` selon leur responsabilite. | Audit; `rg -n "APIRouter|StreamingResponse" app/services app/core`. |

## 8. Implementation Tasks

- [ ] Task 1 - Produire l'audit prealable de `router_logic` et des services cibles (AC: AC1, AC2, AC7)
  - [ ] Subtask 1.1 - Lister les 54 fichiers Python sous `backend/app/api/v1/router_logic` avec leurs imports, fonctions, classes, dependances DB/FastAPI et consommateurs.
  - [ ] Subtask 1.2 - Pour chaque fichier, inspecter le proprietaire probable sous `services`,
    `core` ou `api/v1` avant de choisir un deplacement ou une suppression.
  - [ ] Subtask 1.3 - Ecrire `_condamad/stories/remove-api-v1-router-logic/router-logic-service-audit.md` avec le format de classification impose.
  - [ ] Subtask 1.4 - Identifier les symboles qui ne sont que des delegations vers `errors`,
    `constants` ou un service existant; les marquer `historical-facade` ou `dead`.

- [ ] Task 2 - Inverser les gardes d'architecture avant migration (AC: AC4, AC5, AC9)
  - [ ] Subtask 2.1 - Modifier `backend/app/tests/unit/test_api_router_architecture.py` pour interdire `API_V1_ROOT / "router_logic"` au lieu de l'exiger.
  - [ ] Subtask 2.2 - Ajouter un test qui verifie que `importlib.import_module("app.api.v1.router_logic")` leve `ModuleNotFoundError`.
  - [ ] Subtask 2.3 - Ajouter un scan AST ou texte qui echoue sur toute occurrence
    `app.api.v1.router_logic` dans `backend/app` et `backend/tests`.
  - [ ] Subtask 2.4 - Executer le test de garde sur l'etat actuel et conserver la preuve de l'echec attendu avant suppression.

- [ ] Task 3 - Migrer les responsabilites par lots independants (AC: AC2, AC3, AC4, AC8, AC11, AC12)
  - [ ] Subtask 3.0 - Traiter les lots dans cet ordre par defaut: `admin`, `admin/llm`, `ops`,
    `b2b`, `public`, `internal`; documenter toute inversion necessaire.
  - [ ] Subtask 3.1 - Migrer les responsabilites admin LLM vers `llm_observability/**`,
    `llm_generation/**` ou un sous-module de service existant justifie par l'audit.
  - [ ] Subtask 3.2 - Migrer les responsabilites ops vers `backend/app/services/ops/**` ou `backend/app/services/canonical_entitlement/**` selon le proprietaire deja present.
  - [ ] Subtask 3.3 - Migrer les responsabilites b2b vers `backend/app/services/b2b/**`, `billing/**` ou `ops/audit_service.py` selon l'audit.
  - [ ] Subtask 3.4 - Migrer les responsabilites publiques vers les services existants:
    `auth_service.py`, `privacy_service.py`, `reference_data_service.py`,
    `geocoding_service.py`, `prediction/**`, `consultation/**`, `billing/**`, `email/**`,
    `entitlement/**`, `llm_generation/**`, `user_profile/**`, `natal/**`.
  - [ ] Subtask 3.5 - Pour chaque lot, produire mapping ancien chemin -> proprietaire canonique,
    imports routeurs modifies, tests ajustes, preuve d'absence de shim et tests cibles du lot.
  - [ ] Subtask 3.6 - Ne pas creer un service generique tant que l'audit ne prouve pas au moins deux consommateurs et l'absence de proprietaire existant.
  - [ ] Subtask 3.7 - Router les helpers transverses purs vers `core/**` et les conversions HTTP
    vers `api/v1/**` quand l'audit montre qu'ils ne sont pas des cas d'usage applicatifs.

- [ ] Task 4 - Adapter routeurs et tests aux proprietaires canoniques (AC: AC4, AC6, AC8)
  - [ ] Subtask 4.1 - Remplacer tous les imports routeurs `from app.api.v1.router_logic`
    par les services ou contrats canoniques.
  - [ ] Subtask 4.2 - Remplacer les monkeypatches de tests qui ciblent `router_logic` par le service canonique appele par le routeur.
  - [ ] Subtask 4.3 - Verifier que les routeurs ne recuperent pas de logique applicative locale pour compenser la suppression.
  - [ ] Subtask 4.4 - Ajouter ou ajuster les tests unitaires de services pour couvrir la logique migree.

- [ ] Task 5 - Supprimer legacy et namespace (AC: AC5, AC7, AC9)
  - [ ] Subtask 5.1 - Supprimer les helpers `router_logic` classes `dead` ou `historical-facade`; ne pas les deplacer.
  - [ ] Subtask 5.2 - Supprimer physiquement `backend/app/api/v1/router_logic` et tous ses `__init__.py`.
  - [ ] Subtask 5.3 - Verifier qu'aucun ancien chemin n'est importable et qu'aucun re-export ne remplace le dossier.
  - [ ] Subtask 5.4 - Nettoyer les references documentaires actives dans `_condamad` seulement si
    elles servent de spec ou evidence de la story courante.

- [ ] Task 6 - Valider comportement, architecture et non-regression (AC: AC3, AC8, AC10)
  - [ ] Subtask 6.1 - Executer lint/format Ruff dans le venv.
  - [ ] Subtask 6.2 - Executer les tests de garde, tests unitaires de services migres et tests d'integration API consommatrices.
  - [ ] Subtask 6.3 - Comparer OpenAPI pour les routes dont les routeurs ont ete modifies.
  - [ ] Subtask 6.4 - Documenter dans le recap dev tout test absent, skippe ou remplace, avec risque residuel.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/llm_observability/consumption_service.py` pour la consommation canonique LLM avant de creer une logique parallele.
  - `backend/app/services/llm_observability/monitoring_service.py` pour monitoring/observability LLM avant nouvelle query.
  - `backend/app/services/llm_generation/**` pour generation, prompts, QA, anonymisation, guidance et natal.
  - `backend/app/services/canonical_entitlement/**` pour audits, diffs, review queue, alert handling et suppression.
  - `backend/app/services/b2b/**` pour billing, credentials, usage, editorial, astrology, reconciliation et repair B2B.
  - `backend/app/services/ops/**` pour audit, monitoring, feature flags et incidents.
  - `backend/app/services/billing/**`, `email/**`, `consultation/**`, `prediction/**`, `entitlement/**`, `user_profile/**`, `natal/**` pour les routeurs publics correspondants.
  - `backend/app/api/v1/errors.py` et `backend/app/api/v1/constants.py` pour les contrats strictement API v1 deja centralises.
  - `backend/app/core/**` pour helpers transverses purs qui ne dependent pas de FastAPI ni d'un
    domaine applicatif.
  - `backend/app/api/v1/**` pour mappers HTTP, factories de reponse, conversions d'erreur API,
    `StreamingResponse`, `Request`, `Depends` et `APIRouter`.
- Do not recreate:
  - Un package `router_logic` ailleurs.
  - Une deuxieme implementation d'un service deja present.
  - Un helper d'erreur qui duplique `api_error_response`.
  - Une constante partagee deja presente dans `app.api.v1.constants`.
  - Un serializer de schema Pydantic equivalent a une methode/service existant.
  - Un query builder DB dans un routeur.
- Shared abstraction allowed only if:
  - L'audit prouve au moins deux consommateurs actifs.
  - Aucun proprietaire existant sous `services`, `core`, `api/v1`, `domain` ou `infra` ne couvre la
    responsabilite.
  - Le nom du module exprime le domaine metier, pas l'origine `router_logic`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when a canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/api/v1/router_logic`
- `app.api.v1.router_logic`
- `backend/app/services/router_logic`
- `backend/app/services/api_v1_router_logic`
- `from app.api.v1.router_logic`
- `import app.api.v1.router_logic`
- `sys.modules["app.api.v1.router_logic"]`
- `__getattr__` compatibility loader for `router_logic`
- Tests that patch `app.api.v1.router_logic.*` as nominal behavior.
- Architecture guard language saying non-HTTP logic "must stay" in `router_logic`.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: allowed only when explicit evidence proves usage outside Python internal
  imports and first-party tests: public docs, generated links, clients, operational scripts, or
  published docs.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old import path or route-support surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `replace-consumer` | Must migrate to a service owner before deletion of the old namespace. |
| `external-active` | `needs-user-decision` | Must stop the story until explicit user decision; no shim may be added. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed `Decision` values:

- `delete`
- `replace-consumer`
- `needs-user-decision`

`keep` is intentionally forbidden in this story. If external evidence requires keeping an item,
implementation must stop and request or update an explicit user decision instead of preserving the
namespace.

Audit output path:

- `_condamad/stories/remove-api-v1-router-logic/router-logic-service-audit.md`

Additional required columns may be added after `Risk`:

- `Services inspected`
- `DRY decision`
- `Tests to update`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| API v1 HTTP routing | `backend/app/api/v1/routers/**` | business/query/serializer logic inside route handlers |
| API v1 schemas | `backend/app/api/v1/schemas/**` | schemas or DTOs hidden in `router_logic` |
| API v1 error payload factory | `backend/app/api/v1/errors.py` | `_error_response` helpers in `router_logic` |
| API v1 shared constants | `backend/app/api/v1/constants.py` or service/domain constants when not HTTP-specific | constants in `router_logic` |
| Cross-cutting pure helpers | `backend/app/core/**` | generic masking, timezone validation, normalization not tied to one service |
| HTTP-only response and error conversion | `backend/app/api/v1/**` | CSV HTTP format, response factories, `Request`, `Depends`, `APIRouter`, `StreamingResponse` |
| Admin LLM consumption/observability | `backend/app/services/llm_observability/**` | `router_logic/admin/llm/consumption.py`, `observability.py` |
| Admin LLM generation and QA support | `backend/app/services/llm_generation/**` | `router_logic/admin/llm/*` generation support modules |
| Ops audit, monitoring and feature flags | `backend/app/services/ops/**` | `router_logic/ops/*.py` and admin modules that record ops audits |
| Canonical entitlement audit and alerts | `backend/app/services/canonical_entitlement/**` | `router_logic/ops/entitlement_mutation_audits.py` |
| B2B application services | `backend/app/services/b2b/**` | `router_logic/b2b/**`, `router_logic/ops/b2b/**` |
| Public route support | Existing matching services under `backend/app/services/**` | `router_logic/public/**` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route-support module active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

This rule applies to Python namespaces and helpers. Active HTTP URLs must not be deleted by this story.

## 15. External Usage Blocker

If explicit external evidence appears, the item must be classified as `external-active`.
It must not be deleted until the dev agent stops or records an explicit user decision with:

- exact external evidence;
- deletion risk;
- canonical service replacement proposed;
- reason a compatibility shim is still forbidden unless the user explicitly changes this story.

First-party tests, first-party production imports and monkeypatch paths are not external blockers.
They must be migrated to canonical owners and cannot justify preserving `router_logic`.

## 16. Reintroduction Guard

The implementation must add or update architecture guards that fail if the removed surface is reintroduced.

The guard must check deterministic source(s):

- filesystem absence of `backend/app/api/v1/router_logic`;
- importable Python modules: `app.api.v1.router_logic` must not be importable;
- no import or monkeypatch string `app.api.v1.router_logic` in `backend/app` and `backend/tests`, except the guard's forbidden-token declaration;
- forbidden symbols: `app.api.v1.router_logic`, `backend/app/api/v1/router_logic`, `backend/app/services/router_logic`;
- generated OpenAPI paths for modified route modules must remain present and unchanged;
- no service package named `router_logic` or `api_v1_router_logic`;
- no route handler containing migrated query-builder or serializer responsibilities that should live in services.

Required forbidden examples:

- `backend/app/api/v1/router_logic`
- `app.api.v1.router_logic.admin.llm.consumption`
- `app.api.v1.router_logic.ops.entitlement_mutation_audits`
- `app.api.v1.router_logic.public.privacy`
- `app.api.v1.router_logic.b2b.usage`

## 17. Generated Contract Check

Required generated-contract evidence:

- FastAPI OpenAPI paths for routes whose imports changed must keep the same path and method.
- Response status codes declared for modified route modules must remain stable unless an existing test proves the previous declaration was wrong.
- No generated frontend/backend contract should reference `app.api.v1.router_logic`.

If no generated client exists for a modified route, record that in the implementation evidence. Use
OpenAPI path/method/status plus targeted integration tests as replacement evidence.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/router_logic`
- `backend/app/api/v1/routers`
- `backend/app/api/v1/errors.py`
- `backend/app/api/v1/constants.py`
- `backend/app/api/v1/schemas`
- `backend/app/services`
- `backend/app/core`
- `backend/app/domain`
- `backend/app/infra`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/tests/unit/test_admin_manual_execute_response.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/integration/test_privacy_api.py`
- `backend/tests/integration/test_support_api.py`
- `backend/tests/integration/test_b2b_usage_api.py`
- `backend/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `backend/tests/integration/test_ops_review_queue_alerts_retry_api.py`
- `_condamad/stories/converge-api-v1-route-architecture/service-boundary-audit.md`
- `_condamad/stories/converge-api-v1-route-architecture/generated/10-final-evidence.md`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/remove-api-v1-router-logic/router-logic-service-audit.md` - audit obligatoire de classification et reuse.
- `backend/app/api/v1/routers/**` - imports remplaces par les services canoniques.
- `backend/app/services/llm_observability/**` - accueil de logique consommation/observability si l'audit confirme le proprietaire.
- `backend/app/services/llm_generation/**` - accueil de logique prompts/manual execution/QA si l'audit confirme le proprietaire.
- `backend/app/services/canonical_entitlement/**` - accueil de logique audit/alert ops si l'audit confirme le proprietaire.
- `backend/app/services/b2b/**` - accueil de logique B2B si l'audit confirme le proprietaire.
- `backend/app/services/ops/**` - accueil de logique audit/monitoring/feature flags si l'audit confirme le proprietaire.
- `backend/app/core/**` - accueil de helpers transverses purs si l'audit confirme le proprietaire.
- `backend/app/api/v1/**` - accueil de mappers/factories strictement HTTP si l'audit confirme le
  proprietaire.
- Services existants publics sous `backend/app/services/**` - accueil de logique route-support publique selon audit.
- `backend/app/tests/unit/test_api_router_architecture.py` - garde inversant l'ancien contrat `router_logic`.
- `backend/app/tests/unit/**` et `backend/app/tests/integration/**` - imports et monkeypatches mis a jour vers services canoniques.
- `backend/app/api/v1/router_logic/**` - suppression complete.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - garde d'absence de namespace et d'import.
- `backend/app/tests/unit/test_llm_canonical_consumption_service.py` - regression de logique consommation si modifiee.
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py` - regression services canonical entitlement si modifiee.
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` - regression review/diff si modifiee.
- `backend/app/tests/unit/test_b2b_audit_service.py` et `test_b2b_entitlement_repair_service.py` - regression B2B si modifiee.
- Tests d'integration admin LLM, B2B, ops, privacy, support, auth, billing, prediction et consultation dont les routeurs importaient `router_logic`.

Files not expected to change:

- `backend/pyproject.toml` - aucune dependance nouvelle.
- `backend/alembic/**` - aucune migration DB attendue.
- `frontend/package.json` - aucun changement frontend attendu.
- `frontend/src/**` - aucun changement attendu sauf scan prouvant une reference first-party `router_logic` a corriger.
- `backend/app/main.py` - aucune URL ou inclusion routeur ne doit changer sauf import indirect devenu necessaire et documente.

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
pytest -q app/tests/unit/test_api_router_architecture.py
pytest -q app/tests/unit/test_llm_canonical_consumption_service.py
pytest -q app/tests/unit/test_canonical_entitlement_mutation_audit.py
pytest -q app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py
pytest -q app/tests/unit/test_b2b_audit_service.py
pytest -q app/tests/unit/test_b2b_entitlement_repair_service.py
pytest -q app/tests/integration/test_admin_llm_canonical_consumption_api.py
pytest -q app/tests/integration/test_admin_llm_catalog.py
pytest -q app/tests/integration/test_admin_llm_config_api.py
pytest -q app/tests/integration/test_admin_ai_api.py
pytest -q app/tests/integration/test_audit_api.py
pytest -q app/tests/integration/test_auth_api.py
pytest -q app/tests/integration/test_b2b_usage_api.py
pytest -q app/tests/integration/test_b2b_billing_api.py
pytest -q app/tests/integration/test_b2b_astrology_api.py
pytest -q app/tests/integration/test_enterprise_credentials_api.py
pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py
pytest -q app/tests/integration/test_ops_monitoring_api.py
pytest -q app/tests/integration/test_ops_persona_api.py
pytest -q app/tests/integration/test_privacy_api.py
pytest -q app/tests/integration/test_support_api.py
pytest -q app/tests/integration/test_daily_prediction_api.py
pytest -q app/tests/integration/test_llm_qa_router.py
Test-Path app/api/v1/router_logic
rg -n "app\.api\.v1\.router_logic|router_logic" app tests
rg -n "services[\\/](router_logic|api_v1_router_logic)|app\.services\.(router_logic|api_v1_router_logic)" app tests
rg -n "from fastapi import .*Request|from fastapi import .*Depends|APIRouter|StreamingResponse" app/services app/core
cd ..
```

Expected validation details:

- `Test-Path app/api/v1/router_logic` must print `False`.
- Import failure for `app.api.v1.router_logic` must be asserted only inside
  `pytest -q app/tests/unit/test_api_router_architecture.py`.
- The `rg` scan for `router_logic` must have no hits in `backend/app` or `backend/tests` except explicit forbidden-token declarations inside architecture tests.
- The FastAPI scan in `app/services` and `app/core` must return no HTTP-only imports or response
  types unless the audit records a deliberate exception outside migrated code.
- If a listed test file does not exist or no longer applies after audit, create the narrowest equivalent test or record the skip and residual risk.
- Every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 22. Regression Risks

- Risk: deplacer une logique HTTP pure dans `services` et coupler les services a FastAPI.
  - Guardrail: les services ne doivent pas dependre de `Request`, `Depends`, `APIRouter` ou `StreamingResponse`; les routeurs gardent la traduction HTTP.
- Risk: executer une migration massive difficile a relire.
  - Guardrail: lotir par sous-arborescence et valider chaque lot avant de passer au suivant.
- Risk: dupliquer un service existant avec un nom different.
  - Guardrail: audit obligatoire des services cibles avant creation; AC2 et AC3 bloquent la duplication.
- Risk: casser les monkeypatches en deplacant les chemins sans adapter le point d'appel reel.
  - Guardrail: tests d'integration consommateurs et scan `app.api.v1.router_logic` dans `backend/tests`.
- Risk: changer un payload ou un status HTTP en deplacant des serializers.
  - Guardrail: tests d'integration cibles et OpenAPI comparison des routes modifiees.
- Risk: supprimer un helper encore consomme par une surface externe.
  - Guardrail: seuls des faits externes explicites declenchent `external-active`; les imports Python
    internes et tests first-party doivent etre migres.
- Risk: recreer un gros service fourre-tout.
  - Guardrail: proprietaire par sous-domaine existant, pas de package miroir, nouvelle abstraction seulement avec preuve DRY.

## 23. Dev Agent Instructions

- Implement only this story.
- Commencer par l'audit et les gardes en echec attendu; ne pas deplacer le code avant d'avoir documente les proprietaires cibles.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Ne pas creer de package ou module dont le nom rappelle `router_logic`.
- Migrer par lots independants: `admin`, `admin/llm`, `ops`, `b2b`, `public`, `internal`.
- Chaque lot doit produire: mapping ancien chemin -> proprietaire canonique, imports routeurs
  modifies, tests ajustes, preuve qu'aucun shim n'a ete cree, tests cibles du lot.
- Ne pas supprimer ou renommer une URL HTTP active.
- Ne pas deplacer `Request`, `Depends`, `APIRouter`, `StreamingResponse` ou la construction de
  reponse HTTP dans `services`; garder ces elements dans les routeurs ou modules API v1 dedies.
- Envoyer les cas d'usage applicatifs vers `services/**`, les helpers transverses purs vers
  `core/**`, et les mappers/factories strictement HTTP vers `api/v1/**`.
- Ne jamais traiter un import Python interne, un monkeypatch ou un test first-party comme bloqueur
  externe; les migrer vers le proprietaire canonique.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas creer de `requirements.txt`; `backend/pyproject.toml` reste la source unique.
- Tout fichier applicatif nouveau ou significativement modifie doit contenir un commentaire global
  en francais et des docstrings en francais pour les fonctions publiques ou non triviales.
- Ne pas ajouter de dossier de base dans `backend/` sans accord explicite de l'utilisateur.

## 24. References

- `backend/app/api/v1/router_logic` - namespace a supprimer.
- `backend/app/api/v1/routers` - consommateurs HTTP a adapter.
- `backend/app/services` - proprietaires canoniques cibles a auditer avant migration.
- `backend/app/api/v1/errors.py` - factory d'erreur API v1 a reutiliser pour les besoins strictement HTTP.
- `backend/app/api/v1/constants.py` - constantes API v1 partagees a reutiliser.
- `backend/app/tests/unit/test_api_router_architecture.py` - garde d'architecture a inverser.
- `_condamad/stories/converge-api-v1-route-architecture/00-story.md` - contexte de refactor precedent ayant conserve `router_logic` temporairement.
- `_condamad/stories/converge-api-v1-route-architecture/service-boundary-audit.md` - audit precedent a reutiliser comme point de depart, pas comme verite finale.
