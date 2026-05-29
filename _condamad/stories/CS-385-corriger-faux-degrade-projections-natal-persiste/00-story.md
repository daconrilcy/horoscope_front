# Story CS-385 corriger-faux-degrade-projections-natal-persiste: Corriger le faux degrade des projections natales persistees et stabiliser le parcours /natal Basic

Status: done

## 1. Objective

Corriger le faux etat `degraded` des projections publiques `beginner_summary_v1` et
`client_interpretation_projection_v1` lorsqu'un theme natal persiste contient des
donnees de naissance completes mais plus de `chart_objects` en memoire interne.

Apres correction, un utilisateur `basic` ou `premium` avec heure et lieu connus ne
doit plus voir le bandeau frontend « Lecture partielle : des données de naissance
manquent. » sur les lectures publiques du theme.

Corriger aussi les regressions UX decouvertes lors de la validation sur `/natal` en plan
`basic` pour `daconrilcy@hotmail.com` :

- ne plus regenerer l'interpretation LLM short a chaque retour sur la page ;
- rendre selectionnable l'astrologue dans le modal d'interpretation complete ;
- afficher un message explicite (et non une erreur API) quand le quota Basic complet
  est deja consomme.
## 2. Trigger / Source

- Source type: bug
- Source reference: signalement utilisateur `daconrilcy@hotmail.com` en plan `basic`
- Reason for change: les lectures publiques du theme natal restent en `state=degraded`
  alors que le profil de naissance et le theme calcule sont complets ; validation
  `/natal` a revele trois regressions frontend supplementaires sur le parcours Basic
## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend-domain + frontend natal interpretation (correction couplée au symptôme
  `/natal` observe sur le cas utilisateur Basic)
- In scope:
  - Rehydratation canonique des objets interpretatifs depuis un `NatalResult`
    persiste sans `chart_objects`
  - Correction de la detection `no_time` dans `structured_facts_v1` et les
    builders `beginner_summary_v1` / `client_interpretation_projection_v1`
  - Tests backend deterministes reproduisant le cas theme persiste + plan `basic`
  - Reutilisation de l'interpretation short persistee en plan Basic sur `/natal`
  - Selection d'astrologue fonctionnelle dans le modal d'interpretation complete
  - Message explicite de quota Basic complet (une seule interpretation complete)
- Out of scope:
  - Migration DB, recalcul astronomique, changement de contrat OpenAPI public
  - Refonte LLM, prompts theme astral, expert panel, changement de regles billing
  - Nouvelle route ou endpoint
- Explicit non-goals:
  - No public endpoint addition, OpenAPI schema change, or generated client update
  - No database table, migration, or backfill massif des themes deja stockes
  - No compatibility shim, alias route, fallback UI, or legacy re-export
  - Pas de changement de copy hors messages quota Basic / selection astrologue
## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: corriger un contrat runtime public deja expose sans changer la
  forme HTTP, mais en restaurant la verite metier sur theme persiste
- Behavior change allowed: constrained
- Behavior change constraints:
  - Corriger uniquement la derivation factuelle amont des projections publiques
  - Conserver les champs publics existants (`state`, `missing_data`, `display_messages`)
  - Ne pas reintroduire `chart_objects` dans le JSON persiste de `NatalResult`
  - Ne pas masquer un vrai `no_time` lorsque l'heure de naissance est absente
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: aucun owner existant ne permet de rehydrater
  `chart_objects` sans nouveau moteur parallele

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | le bug se manifeste via `/v1/astrology/projections` |
| Baseline Snapshot | yes | comparer payload degrade vs nominal sur meme theme persiste |
| Ownership Routing | yes | la rehydratation doit rester sur le builder canonique existant |
| Allowlist Exception | no | aucune exception de surface autorisee |
| Contract Shape | yes | conserver la forme publique des payloads projection |
| Batch Migration | no | pas de migration multi-consommateur |
| Reintroduction Guard | yes | empecher le retour du faux degrade sur theme persiste |
| Persistent Evidence | yes | conserver la preuve before/after du cas utilisateur |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `TestClient` sur `POST /v1/astrology/projections`
  - `app.routes` pour confirmer la route `/v1/astrology/projections`
  - builders `StructuredFactsV1Builder`, `BeginnerSummaryV1Builder`,
    `ClientInterpretationProjectionV1Builder`
- Secondary evidence:
  - `pytest -q backend/tests/api/test_projection_real_conditions.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
  - `npm run test -- --run frontend/src/tests/natalInterpretation.test.tsx`
  - `npm run test -- --run frontend/src/tests/NatalChartPage.test.tsx`
  - `npm run test -- --run frontend/src/tests/AstrologersPage.test.tsx`
  - navigateur `/natal` connecte (`daconrilcy@hotmail.com`)- Static scans alone are not sufficient for this story because:
  - le bug depend du runtime apres deserialisation d'un theme persiste sans
    `chart_objects`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-385-corriger-faux-degrade-projections-natal-persiste/evidence/before-persisted-chart-projection.json`
- Comparison after implementation:
  - `_condamad/stories/CS-385-corriger-faux-degrade-projections-natal-persiste/evidence/after-persisted-chart-projection.json`
- Expected invariant:
  - meme `chart_id`, meme profil de naissance complet, `payload.state` passe de
    `degraded` a `normal`
  - un vrai theme sans heure conserve `state=degraded`

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection des objets runtime du theme | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | nouveau builder parallele dans services ou frontend |
| Input interpretatif amont | `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` | relecture directe de `planet_positions` dans les builders B2C |
| Faits structures hashables | `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | duplication dans `projection_endpoint_service.py` |
| Orchestration HTTP projections | `backend/app/services/projections/projection_endpoint_service.py` | logique metier de rehydratation locale ad hoc |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist is required for this story.

## 4f. Contract Shape

- Contract type:
  - payload public `beginner_summary_v1` et `client_interpretation_projection_v1`
- Fields:
  - `state`: `normal` quand heure et collections factuelles sont disponibles
  - `missing_data`: ne doit plus contenir `no_time` sur theme persiste complet
  - `display_messages`: conserve les codes stables existants
- Required fields:
  - `state`, `projection_id`, `source_projection_id`
- Optional fields:
  - `degraded_reason`, `missing_data`, `display_messages`
- Status codes:
  - HTTP 200 inchange pour projection valide
- Serialization names:
  - aucun renommage autorise
- Frontend type impact:
  - aucun changement de type frontend requis si le backend cesse d'emettre `degraded`
- Generated contract impact:
  - none

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Evidence directory:
`_condamad/stories/CS-385-corriger-faux-degrade-projections-natal-persiste/evidence/`

| Artifact | Path | Purpose |
|---|---|---|
| Baseline projection degradee | `before-persisted-chart-projection.json` | prouver l'etat bug actuel |
| Projection corrigee | `after-persisted-chart-projection.json` | prouver la correction runtime |
| Note de reproduction | `reproduction-notes.md` | tracer le cas utilisateur initial |
| Notes de clôture | `closure-notes.md` | synthese backend + correctifs frontend associes |
## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- `pytest -q backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `pytest -q backend/tests/api/test_projection_real_conditions.py`
- `rg -n "build_chart_object_runtime_data" backend/app/domain/astrology/interpretation`

Required forbidden examples:

- inferring `no_time` only from `empty_collections=["houses"]` when birth time is known
- building `structured_facts_v1` from an empty `chart_objects` tuple on persisted charts
- duplicating chart-object projection logic outside `chart_object_runtime_builder.py`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py -k persisted` checks persisted-chart rehydration.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: signalement utilisateur projection natale basic toujours degradee
- Closure proof required: tests backend + frontend + snapshots before/after +
  verification manuelle bornee sur `/natal` (login `daconrilcy@hotmail.com`)
- Known residual in-domain work: none
- Deferred non-domain concerns: none

### Correctifs frontend associes (meme livraison)

| ID | Symptome | Cause | Correction | Preuve |
|---|---|---|---|---|
| FE-1 | Interpretation regeneree a chaque visite `/natal` | effet Basic remettait `selectedInterpretationId=null` et relançait `POST /natal/interpretation` | reutiliser `latestShortInterpretation` via `useNatalInterpretationById` ; bloquer `mainQuery` si historique persisté | test `reutilise l'interpretation short persistee en Basic` |
| FE-2 | Clic astrologue sans effet dans le modal | `AstrologerCard` sans handler cliquable hors `showProfileCta` | `selectionMode` + CTA « Demander l'interprétation complète » | tests AstrologersPage + natalInterpretation |
| FE-3 | 2e interpretation complete Basic → erreur 429 generique | pas de garde client avant `POST` ; CTA en-tete redirigeait | `isBasicCompleteLimitReached` + bandeau `basicCompleteLimitMessage` | tests natalInterpretation + NatalChartPage |
## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
  affiche `copy.degraded` quand `payload.state === "degraded"`.
- Evidence 2: `frontend/src/i18n/natalChart.ts` mappe ce texte a
  « Lecture partielle : des données de naissance manquent. ».
- Evidence 3: `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
  lit uniquement `natal_result.chart_objects`.
- Evidence 4: `backend/app/domain/astrology/natal_calculation.py` exclut
  `chart_objects` du schema public/persiste (`SkipJsonSchema`, `exclude=True`).
- Evidence 5: `backend/app/services/projections/projection_endpoint_service.py`
  deserialise un theme persiste via `NatalResult.model_validate(model.result_payload)`
  sans rehydratation.
- Evidence 6: reproduction locale sur `daconrilcy@hotmail.com` —
  `birth_time='11:00'`, `detect_degraded_natal_mode=None`, `chart_objects=0`,
  `planet_positions=10`, `houses=12`, `structured_facts.houses=0`,
  `beginner_summary.state=degraded`, `client_interpretation.state=degraded`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registre consulte via
  resolver scope backend interpretation/projections.
- Source-alignment evidence: PASS; la story corrige la cause racine backend et les
  regressions UX `/natal` observees lors de la validation utilisateur Basic.
- Evidence 8: validation navigateur — login OK, bandeau degrade absent, retour
  dashboard → `/natal` sans regeneration LLM visible.
- Evidence 9: `evidence/closure-notes.md` — synthese des quatre correctifs livres.
## 6. Target State

After implementation:

- Un `NatalResult` persiste sans `chart_objects` mais avec collections historiques
  disponibles produit des `structured_facts_v1` non vides pour positions et maisons.
- Les projections publiques retournent `state=normal` pour un theme complet avec
  heure connue, y compris via source `chart_id`.
- `_has_missing_birth_time` s'appuie sur une precision explicite de naissance
  quand elle est disponible, au lieu d'inférer `no_time` depuis des collections
  vides causees par la deserialisation.
- Le cas utilisateur `basic` ne declenche plus le bandeau « Lecture partielle »
  sur les lectures publiques du theme.
- Les vrais themes sans heure conservent `state=degraded` et `missing_data=["no_time"]`.
- L'interpretation short Basic persistee est relue depuis l'historique sans nouveau
  `POST /v1/natal/interpretation` a chaque visite `/natal`.
- Le modal astrologue permet de confirmer une interpretation complete via un CTA
  cliquable.
- Une seconde demande d'interpretation complete Basic affiche un message explicite
  de quota (une seule interpretation complete incluse) au lieu d'une erreur generique.
## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - Operation: update
  - Domain: backend-domain interpretation/projections
  - Touched surfaces:
    - `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
    - `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
    - `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`
    - `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
    - `backend/app/services/projections/projection_endpoint_service.py`
    - `frontend/src/features/natal-chart/NatalInterpretation.tsx`
    - `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx`
    - `frontend/src/features/astrologers/components/AstrologerCard.tsx`
    - `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
    - `frontend/src/pages/NatalChartPage.tsx`
    - `frontend/src/i18n/natalChart.ts`
  - Out-of-scope surfaces: billing backend, LLM prompts, DB migrations- Selection rule:
  - Applied only guardrails matching exact path, file surface, operation,
    contract, domain, or universal local guardrails.
- Applicable invariants:
  - `RG-144` - rehydrater via `chart_object_runtime_builder`, sans remplacer
    `planet_positions`, `houses`, `astral_points` ni autres collections historiques
  - `RG-002` - conserver la surface API `/v1/astrology/projections` sans route parallele
  - `RG-073` - parcours `/natal` et interpretation natale ; corrections UX sans
    masquer un `payload.state=degraded` legitime
- Needs-investigation invariants:
  - none
- Non-applicable examples:
  - `RG-150` - rejets narratifs LLM ; hors surface projection publique factuelle
- Required regression evidence:
  - tests unitaires structured facts + builders projection
  - test API projection sur theme persiste
  - tests frontend natalInterpretation + NatalChartPage + AstrologerGrid selectionMode
  - snapshots before/after dans evidence story- Allowed differences:
  - `payload.state` passe de `degraded` a `normal` uniquement pour themes complets
    deserialises sans `chart_objects`

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Rehydrater chart_objects sur theme persiste. | Evidence profile: `runtime_openapi_contract`; `pytest -q test_structured_facts_v1_builder.py -k persisted` |
| AC2 | structured_facts expose des positions non vides. | Evidence profile: `json_contract_shape`; `pytest -q test_structured_facts_v1_builder.py -k persisted_complete` |
| AC3 | beginner_summary_v1 retourne state=normal theme complet. | Evidence profile: `json_contract_shape`; `pytest -q test_beginner_summary_v1_builder.py -k persisted_complete` |
| AC4 | client_interpretation state=normal plan basic. | Evidence profile: `json_contract_shape`; `pytest -q test_client_interpretation_projection_v1_builder.py -k basic` |
| AC5 | API projections chart_id sans state=degraded. | Evidence profile: `runtime_openapi_contract`; `pytest -q test_projection_real_conditions.py -k persisted_chart` |
| AC6 | Theme sans heure conserve state=degraded. | Evidence profile: `json_contract_shape`; `pytest -q test_projection_real_conditions.py -k no_time` |
| AC7 | Pas de projection chart-object parallele. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n build_chart_object_runtime_data backend/app/domain/astrology` |
| AC8 | Manual check sans bandeau degrade. | Evidence profile: `repo_wide_negative_scan`; navigateur `/natal` sans « Lecture partielle » |
| AC9 | Basic reutilise l'interpretation short persistee sans POST LLM. | Evidence profile: `json_contract_shape`; `npm run test -- natalInterpretation.test.tsx -t persisted` |
| AC10 | Modal astrologue selectionnable pour interpretation complete. | Evidence profile: `json_contract_shape`; tests AstrologersPage + natalInterpretation selectionMode |
| AC11 | 2e complete Basic → message quota explicite, pas erreur generique. | Evidence profile: `json_contract_shape`; tests natalInterpretation + NatalChartPage quota Basic |
| AC12 | Documentation de clôture complete. | Evidence profile: `persistent_evidence`; `evidence/closure-notes.md` |
## 8. Implementation Tasks

- [x] Task 1: Cartographier le point unique de rehydratation amont. (AC: AC1, AC7)
  - [x] Subtask 1.1: Confirmer l'owner canonique (`ChartInterpretationInputBuilder` ou helper domaine adjacent).
  - [x] Subtask 1.2: Reutiliser `build_chart_object_runtime_data` et les enrichissements deja disponibles sur `NatalResult`.

- [x] Task 2: Rehydrater les objets interpretatifs depuis collections historiques persistees. (AC: AC1, AC2)
  - [x] Subtask 2.1: Detecter `chart_objects` vide avec `planet_positions`/`houses` disponibles.
  - [x] Subtask 2.2: Reconstruire l'input interpretatif sans persister `chart_objects` en DB.

- [x] Task 3: Durcir la detection `no_time` dans les faits structures et builders B2C. (AC: AC3, AC4, AC6)
  - [x] Subtask 3.1: Exposer la precision explicite de naissance dans `missing_data`.
  - [x] Subtask 3.2: Faire preferer cette precision au proxy `empty_collections=["houses"]`.

- [x] Task 4: Ajouter tests de non-regression theme persiste + plan basic. (AC: AC5, AC6, AC7)
  - [x] Subtask 4.1: Test unitaire structured facts sur payload deserialise sans `chart_objects`.
  - [x] Subtask 4.2: Test API projection `chart_id` nominal vs vrai `no_time`.

- [x] Task 5: Produire evidence before/after et valider le cas utilisateur. (AC: AC8)
  - [x] Subtask 5.1: Ecrire les snapshots JSON dans le dossier evidence story.
  - [x] Subtask 5.2: Verifier manuellement `/natal` pour `daconrilcy@hotmail.com`.

- [x] Task 6: Reutiliser l'interpretation short persistee en plan Basic. (AC: AC9)
  - [x] Subtask 6.1: Selectionner `latestShortInterpretation` depuis l'historique au mount.
  - [x] Subtask 6.2: Desarmer `mainQuery` quand un candidat persisté existe.

- [x] Task 7: Corriger la selection d'astrologue dans le modal complete. (AC: AC10)
  - [x] Subtask 7.1: Ajouter `selectionMode` sur `AstrologerCard` / `AstrologerGrid`.
  - [x] Subtask 7.2: Activer le mode selection dans `NatalInterpretationPersonaSelector`.

- [x] Task 8: Afficher un message quota Basic explicite. (AC: AC11)
  - [x] Subtask 8.1: Detecter `isBasicCompleteLimitReached` cote client.
  - [x] Subtask 8.2: Bandeau `basicCompleteLimitMessage` + mapping erreur 429.

- [x] Task 9: Documenter la clôture etendue. (AC: AC12)
  - [x] Subtask 9.1: Rediger `evidence/closure-notes.md`.
  - [x] Subtask 9.2: Mettre a jour la story et les AC de non-regression frontend.
## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `build_chart_object_runtime_data` pour reconstruire les objets runtime
  - `ChartInterpretationInputBuilder` comme owner unique de l'input interpretatif
  - `StructuredFactsV1Builder` comme owner unique de `structured_facts_v1`
- Do not recreate:
  - un second builder chart-object
  - une heuristique frontend ou service HTTP locale de detection `no_time`
- Shared abstraction allowed only if:
  - un helper domaine unique est necessaire et reste confine a
    `backend/app/domain/astrology/interpretation/`

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

- `backend/app/services/chart/json_builder.py` comme source de rehydratation interpretative
- toute relecture directe de `planet_positions` dans `beginner_summary_v1_builder.py`
- toute relecture directe de `houses` dans `client_interpretation_projection_v1_builder.py`
- masquage frontend du bandeau sans corriger `payload.state`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Objets runtime du theme | `chart_object_runtime_builder.py` | services projections, frontend |
| Input interpretatif | `chart_interpretation_input_builder.py` | endpoint HTTP |
| Faits structures | `structured_facts_v1_builder.py` | persistence chart |
| Projections B2C publiques | builders `*_v1_builder.py` | i18n frontend |
| Parcours interpretation /natal | `NatalInterpretation.tsx` | page chart, modal persona |
| Grille astrologues selection | `AstrologerGrid.tsx` / `AstrologerCard.tsx` | pages catalogue sans selectionMode |
## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/projections/projection_endpoint_service.py`
- `backend/tests/api/test_projection_real_conditions.py`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/pages/NatalChartPage.tsx`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - rehydratation amont
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - precision explicite de naissance
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` - detection degrade corrigee
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - detection degrade corrigee
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py` - cas persiste complet
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py` - cas persiste complet
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py` - cas basic persiste
- `backend/tests/api/test_projection_real_conditions.py` - cas `chart_id` persiste

Frontend (correctifs associes validation `/natal`):

- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - cache short Basic, quota notice
- `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` - selectionMode
- `frontend/src/features/natal-chart/NatalInterpretation.css` - styles `ni-quota-notice`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - selectionMode
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx` - propagation selectionMode
- `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx` - erreur quota
- `frontend/src/pages/NatalChartPage.tsx` - signal quota Basic a l'en-tete
- `frontend/src/i18n/natalChart.ts` - `basicCompleteLimitMessage`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/AstrologersPage.test.tsx`

Likely tests:
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `backend/tests/api/test_projection_real_conditions.py`

Files not expected to change:

- `backend/app/infra/db/models/*` - pas de migration
- `backend/app/services/llm_generation/natal/*` - hors scope sauf effet indirect via structured facts corrige
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - bandeau degrade corrige via backend `payload.state`
## 20. Dependency Policy

- New dependencies: none
- Justification: no dependency changes are authorized.

## 21. Validation Plan

Run or justify why skipped:

```bash
cd backend
pytest -q tests/unit/domain/astrology/test_structured_facts_v1_builder.py -k persisted
pytest -q tests/unit/domain/astrology/test_beginner_summary_v1_builder.py -k persisted
pytest -q tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py -k persisted
pytest -q tests/api/test_projection_real_conditions.py -k "persisted_chart or no_time"
rg -n "build_chart_object_runtime_data" app/domain/astrology/interpretation app/services/projections
ruff format .
ruff check .

cd frontend
npm run test -- --run src/tests/natalInterpretation.test.tsx src/tests/NatalChartPage.test.tsx src/tests/AstrologersPage.test.tsx
```

Manual check:

- Ouvrir `/natal` avec `daconrilcy@hotmail.com` / `admin123` en plan `basic`
- Verifier l'absence du texte « Lecture partielle : des données de naissance manquent. »
- Aller au dashboard puis revenir sur `/natal` : pas de regeneration LLM visible
- Demander une interpretation complete : modal astrologue cliquable, generation OK une fois
- Redemander une complete : message « Le plan Basic inclut une seule interprétation complète… »
## 22. Regression Risks

- Risk: masquer un vrai theme sans heure
  - Guardrail: conserver AC6 et test `no_time` existant
- Risk: dupliquer la projection chart-object hors builder canonique
  - Guardrail: AC7 + `RG-144`
- Risk: persister `chart_objects` en DB par effet de bord
  - Guardrail: conserver exclusion schema `NatalResult.chart_objects`
- Risk: relancer un POST LLM short Basic alors qu'un historique existe
  - Guardrail: AC9 + test `reutilise l'interpretation short persistee`
- Risk: modal astrologue non actionnable
  - Guardrail: AC10 + `selectionMode` sur AstrologerGrid
- Risk: erreur 429 affichee comme panne generique sur quota Basic
  - Guardrail: AC11 + `basicCompleteLimitMessage`
## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `frontend/src/i18n/natalChart.ts` - texte utilisateur observe
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - rendu du bandeau degrade
- `backend/app/domain/astrology/natal_calculation.py` - exclusion de `chart_objects` du payload persiste
- `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md` - owner structured facts
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md` - owner chart objects
- `_condamad/stories/CS-385-corriger-faux-degrade-projections-natal-persiste/evidence/closure-notes.md` - synthese livraison