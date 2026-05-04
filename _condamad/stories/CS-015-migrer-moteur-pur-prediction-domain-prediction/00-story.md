# Story CS-015 migrer-moteur-pur-prediction-domain-prediction: Migrer le moteur pur prediction sous domain/prediction

Status: done

## 1. Objective

Deplacer le calcul pur, les schemas metier et les policies deterministes depuis `app.prediction` vers `app.domain.prediction`, sans dependance API, infra, settings ou LLM runtime.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` indique que le moteur pur est appele par les services mais reste physiquement dans le namespace legacy.

## 3. Domain Boundary

- Domain: `backend/app/domain/prediction`
- In scope:
  - Creation du package domaine prediction.
  - Migration des modules de calcul pur et schemas metier necessaires.
  - Mise a jour des imports internes et des tests moteur.
  - Garde zero import inverse depuis `domain` vers API, services, infra, settings ou LLM runtime.
- Out of scope:
  - Suppression finale de `backend/app/prediction`.
  - Migration des DTO persisted et read models DB.
  - Decouplage des routeurs API.
  - Changement de comportement de calcul.
- Explicit non-goals:
  - Ne pas affaiblir `RG-027`, `RG-029`, `RG-030` ou `RG-033`.
  - Ne pas ajouter de dossier de base sous `backend/`.
  - Ne pas creer de facade `app.prediction` vers `app.domain.prediction`.

## 4. Operation Contract

- Operation type: move
- Primary archetype: module-move
- Archetype reason: la story deplace des modules Python vers un owner canonique domaine.
- Behavior change allowed: no
- Behavior change constraints:
  - Les imports changent, pas les resultats du moteur.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un module migre a besoin d'une dependance infra ou API pour conserver son comportement.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde AST et les tests moteur sont la source executable du contrat domaine. |
| Baseline Snapshot | yes | Les imports et tests moteur doivent etre compares avant/apres. |
| Ownership Routing | yes | Le domaine pur doit exclure les dependances applicatives. |
| Allowlist Exception | no | Aucune exception de dependance inverse n'est autorisee. |
| Contract Shape | no | Aucun contrat API ou DTO public ne change. |
| Batch Migration | no | La story est limitee au moteur pur. |
| Reintroduction Guard | yes | Les imports inverses et `app.prediction` doivent etre bloques. |
| Persistent Evidence | yes | Les inventaires de migration doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
  - Tests moteur sous `backend/app/tests/unit`.
- Secondary evidence:
  - Scans `rg` des imports interdits sous `app/domain/prediction`.
- Static scans alone are not sufficient for this story because:
  - Les imports peuvent etre conformes alors qu'un comportement moteur regresse.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-after.md`
- Expected invariant:
  - `backend/app/domain/prediction` contient le moteur pur sans import interdit.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Calcul pur prediction | `backend/app/domain/prediction` | `backend/app/services/prediction` |
| Orchestration de use case | `backend/app/services/prediction` | `backend/app/domain/prediction` |
| Persistance | `backend/app/infra` | `backend/app/domain/prediction` |
| Adaptateur HTTP | `backend/app/api` | `backend/app/domain/prediction` |
| Runtime LLM | `backend/app/services/llm_generation` | `backend/app/domain/prediction` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: aucune exception de dependance inverse n'est autorisee dans le domaine pur.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: la migration est bornee au moteur pur et ne couvre pas tous les consommateurs `app.prediction`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventaire avant | `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-before.md` | Capturer modules moteur et imports initiaux. |
| Inventaire apres | `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-after.md` | Prouver le nouvel owner et les scans zero hit. |

## 4i. Reintroduction Guard

- Guard target:
  - Aucun import `fastapi`, `sqlalchemy`, `Session`, `settings`, `AIEngineAdapter`, `from app.infra` ou `from app.api` sous `backend/app/domain/prediction`.
  - Les services prediction importent le moteur via `app.domain.prediction`.
- Guard evidence:
  - Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.
  - Evidence profile: `targeted_forbidden_symbol_scan`; scan `rg` des imports interdits.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-007` montre les imports moteur depuis `app.prediction`.
- Evidence 2: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-010` indique que `backend/app/domain/prediction` est absent.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `backend/app/domain/prediction` existe et porte les modules de calcul pur.
- `backend/app/services/prediction/engine_orchestrator.py` consomme le domaine canonique.
- Les tests moteur conservent les resultats existants.
- Les scans de dependances interdites dans le domaine sont zero-hit.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-027` - le domaine prediction pur ne doit pas importer infra ou SQLAlchemy.
  - `RG-030` - les evenements `astro_foundation` doivent rester resolus.
  - `RG-035` - invariant cree par cette story pour l'owner `app.domain.prediction`.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Tests moteur, scans imports interdits, inventaire avant/apres.
- Allowed differences:
  - Changement des chemins d'import vers `app.domain.prediction`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `app/domain/prediction` existe comme owner moteur. | Evidence profile: `namespace_converged`; `rg --files app/domain/prediction`. |
| AC2 | Les services consomment `app.domain.prediction`. | Evidence profile: `python_import_absence`; `rg -n "from app\\.prediction" app/services/prediction -g "*.py"`. |
| AC3 | Le domaine n'importe aucune couche interdite. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "fastapi|sqlalchemy" app/domain/prediction`. |
| AC4 | Les tests moteur restent passants. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_engine_orchestrator.py`. |
| AC5 | Les preuves avant/apres sont persistantes. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_engine_orchestrator.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'inventaire moteur avant migration (AC: AC5)
- [x] Task 2 - Creer `backend/app/domain/prediction` et migrer les modules purs (AC: AC1)
- [x] Task 3 - Mettre a jour les imports services et tests moteur (AC: AC2, AC4)
- [x] Task 4 - Ajouter ou adapter les guards de dependances domaine (AC: AC3)
- [x] Task 5 - Persister l'inventaire apres migration (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Les implementations existantes de `backend/app/prediction` pour le moteur.
  - Les tests unitaires prediction existants pour verifier l'equivalence.
- Do not recreate:
  - Une seconde implementation du calcul.
  - Des schemas metier dupliques sous plusieurs owners.
- Shared abstraction allowed only if:
  - Elle supprime une duplication constatee pendant la migration.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `from app.prediction` dans `backend/app/services/prediction`.
- `from app.infra` dans `backend/app/domain/prediction`.
- `from app.api` dans `backend/app/domain/prediction`.
- `AIEngineAdapter` dans `backend/app/domain/prediction`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Moteur pur prediction | `backend/app/domain/prediction` | `backend/app/prediction` |
| Orchestration use case | `backend/app/services/prediction` | `backend/app/domain/prediction` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/astro_calculator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/prediction/__init__.py` - nouveau package domaine.
- `backend/app/services/prediction/engine_orchestrator.py` - imports canoniques.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde dependances domaine.

Likely tests:

- `backend/app/tests/unit/test_engine_orchestrator.py` - imports et comportement moteur.
- `backend/app/tests/unit/test_transit_signal_v3.py` - comportement signaux.
- `backend/tests/unit/prediction/test_public_astro_foundation.py` - non-regression astro.

Files not expected to change:

- `backend/app/api/v1/routers/public/predictions.py` - decouplage API traite par CS-017.
- `frontend/src` - aucun impact frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py
pytest -q tests/unit/prediction/test_public_astro_foundation.py
rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api|from app\.services" app/domain/prediction -g "*.py"
rg -n "from app\.prediction" app/services/prediction -g "*.py"
ruff check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py
```

## 22. Regression Risks

- Risk: le domaine pur recupere une dependance de service.
  - Guardrail: `AC3` impose un scan d'import interdit.
- Risk: un schema est duplique sous deux owners actifs.
  - Guardrail: `AC2` et `AC5` imposent migration et inventaire.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md#F-002` - finding source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
