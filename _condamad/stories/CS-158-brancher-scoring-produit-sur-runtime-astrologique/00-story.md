# Story CS-158 brancher-scoring-produit-sur-runtime-astrologique: Brancher le scoring produit sur le runtime astrologique

Status: ready-to-dev

## 1. Objective

Faire consommer `HouseRuntimeData` et les resultats d'interpretation
astrologique par les calculateurs produit, notamment `DomainRouter` et
`NatalSensitivityCalculator`. Le scoring transforme alors des faits
astrologiques explicites au lieu de melanger calcul astrologique et decision
produit.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-13 sur le sens autorise `prediction -> astrology`.
- Reason for change: les calculateurs produit doivent lire les faits runtime et appliquer les poids categorie sans devenir proprietaires de l'astrologie.

## 3. Domain Boundary

- Domain: `backend/app/domain/prediction`
- In scope:
  - adapter `DomainRouter` et `NatalSensitivityCalculator` pour lire les faits runtime disponibles;
  - garder `house_category_weights`, `routing_role`, `visibility_weight` et `base_priority` dans prediction/product;
  - conserver les scores publics existants sauf differences explicitement baselinees.
- Out of scope:
  - modification du runtime astrologique;
  - creation de nouvelles categories produit;
  - changement SQL ou seed.
- Explicit non-goals:
  - Ne pas importer prediction depuis astrology.
  - Ne pas deplacer `house_category_weights` vers `domain/astrology`.
  - Ne pas changer les routes API.
  - Ne pas changer les invariants `RG-035` et `RG-094`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: service-boundary-refactor
- Archetype reason: la story reoriente les calculateurs produit vers une source runtime astrologique canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les scores de categorie doivent rester equivalents sur les fixtures existantes sauf difference documentee.
  - Les poids produit restent appliques par prediction.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une categorie produit doit changer de poids ou priorite narrative.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les calculateurs produit doivent lire `HouseRuntimeData`. |
| Baseline Snapshot | yes | les scores produit avant/apres doivent etre compares. |
| Ownership Routing | yes | prediction consomme astrology, jamais l'inverse. |
| Allowlist Exception | yes | une table explicite declare qu'aucune exception n'est ouverte. |
| Contract Shape | yes | l'entree runtime consommee par prediction doit etre explicite. |
| Batch Migration | yes | `DomainRouter` puis `NatalSensitivityCalculator` sont migres par lots bornes. |
| Reintroduction Guard | yes | les anciens recalculs astrologiques produit ne doivent pas revenir. |
| Persistent Evidence | yes | baseline scoring et scans requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard and pytest runtime artifact: `backend/app/domain/astrology/runtime/house_runtime_data.py` consumed by prediction pytest fixtures.
- Secondary evidence:
  - scans for prohibited astrology recalculation sources under `backend/app/domain/prediction`.
- Static scans alone are not sufficient for this story because:
  - product scoring must prove equivalent `DomainRouter` and `NatalSensitivityCalculator` behavior before and after migration.
- Product source: `PredictionContext.house_category_weights` et profils prediction.
- Rule: prediction applique les categories et poids; astrology fournit les faits.

## 4c. Baseline / Before-After Rule

- Baseline required: yes
- Baseline artifact before implementation:
  - `_condamad/stories/CS-158-brancher-scoring-produit-sur-runtime-astrologique/generated/product-scoring-baseline-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-158-brancher-scoring-produit-sur-runtime-astrologique/generated/product-scoring-baseline-after.md`
- Expected invariant:
  - les scores produit restent equivalents sur les fixtures existantes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits maison runtime | `backend/app/domain/astrology/runtime` | `backend/app/domain/prediction` |
| Mapping maison categorie | `backend/app/domain/prediction` | `backend/app/domain/astrology` |
| Priorite narrative produit | `backend/app/domain/prediction` | `backend/app/domain/astrology` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | aucune exception de frontiere n'est acceptee | permanent |

## 4f. Contract Shape

Contract type:
- Calculator input contract.
Fields:
- `HouseRuntimeData.house`, `cusp_sign`, `house_kind`, `ruler`, `occupants`, `strength`.
Required fields:
- `house`, `house_kind`, `ruler`, `occupants`, `strength`.
Optional fields:
- `contained_signs`, `intercepted_signs`, `axis`.
Status codes:
- none.
Serialization names:
- Internal Python contract only.
Frontend type impact:
- none.
Generated contract impact:
- none.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | maison derivee depuis evenement/contexte produit | `HouseRuntimeData` | `DomainRouter` | `test_domain_router.py` | scan recalcul maison produit | score diff non explique |
| 2 | sensibilite sur profils ambigus | runtime + product profile | `NatalSensitivityCalculator` | natal tests | scan anciens champs | decision poids |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `generated/product-scoring-baseline-before.md` | Current scores. |
| Baseline after | `generated/product-scoring-baseline-after.md` | Equivalent scores. |
| Runtime inventory | `generated/prediction-runtime-consumption-after.md` | Runtime facts consumed. |

## 4i. Reintroduction Guard

- Guard type: targeted scan or AST guard.
- Forbidden patterns:
  - recalcul de `ruler` depuis `sign_rulerships` dans `domain/prediction`;
  - nouveaux mappings astrologiques maison -> signe dans prediction;
  - import de `PredictionReferenceRepository` depuis `domain/astrology`.
- Guard command:
  `rg -n "sign_rulerships|get_sign_rulerships|HouseRulerResolver|cusp_sign.*ruler|app\\.infra" app/domain/prediction -g "*.py"`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/prediction/domain_router.py` - `DomainRouter` projette les maisons vers categories via `house_category_weights`.
- Evidence 2: `backend/app/domain/prediction/natal_sensitivity.py` - `NatalSensitivityCalculator` consomme les poids maison categorie.
- Evidence 3: `backend/app/domain/astrology/runtime/house_runtime_data.py` - runtime maison canonique disponible.
- Evidence 4: `docs/tables-maisons-et-roles.md` - le flux cible documente runtime puis prediction.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `DomainRouter` lit les faits maison runtime lorsqu'ils sont disponibles.
- `NatalSensitivityCalculator` separe clairement faits astrologiques et poids produit.
- Les categories produit restent resolues uniquement dans `domain/prediction`.
- Les tests prouvent que les scores restent stables.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-035` - le moteur prediction pur reste sans dependance API, infra, services, settings ou LLM runtime.
  - `RG-094` - `houses[*].ruler` reste la source canonique runtime.
- Non-applicable invariants:
  - `RG-091` - aucune table de reference astrologique n'est modifiee.
- Required regression evidence:
  - tests product scoring;
  - baseline before/after scoring;
  - scans de recalcul astrologique interdit dans prediction.
- Allowed differences:
  - none, sauf decision produit documentee.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `DomainRouter` transforme `HouseRuntimeData` via `house_category_weights`. | `pytest -q app/tests/unit/test_domain_router.py`. |
| AC2 | `NatalSensitivityCalculator` lit les faits runtime. | `pytest -q app/tests/unit/test_natal_sensitivity.py app/tests/unit/test_natal_structural_v3.py`. |
| AC3 | Le moteur prediction conserve ses scores existants. | `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py`. |
| AC4 | `domain/prediction` ne recalcule pas les maitrises astrologiques. | `rg -n "sign_rulerships|get_sign_rulerships|HouseRulerResolver" app/domain/prediction -g "*.py"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Baseline scoring produit (AC: AC3)
  - [ ] Subtask 1.1 - Capturer les fixtures et resultats actuels de routing/sensibilite.
  - [ ] Subtask 1.2 - Enregistrer `product-scoring-baseline-before.md`.

- [ ] Task 2 - Migrer `DomainRouter` vers runtime astrology (AC: AC1, AC4)
  - [ ] Subtask 2.1 - Identifier l'entree runtime disponible.
  - [ ] Subtask 2.2 - Adapter les tests sans introduire de shim.

- [ ] Task 3 - Migrer `NatalSensitivityCalculator` (AC: AC2, AC3)
  - [ ] Subtask 3.1 - Separarer profils produit et faits runtime.
  - [ ] Subtask 3.2 - Verifier les scores avant/apres.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HouseRuntimeData` pour les faits astrologiques.
  - `PredictionContext.house_category_weights` pour le mapping produit.
  - `HousePredictionProfile` issu de CS-157 si cette story est implementee apres.
- Do not recreate:
  - un resolver de maitrise dans prediction;
  - un mapping signe -> maitre dans prediction;
  - une deuxieme categorie router.
- Shared abstraction allowed only if:
  - elle evite une duplication entre calculateurs prediction et reste dans `domain/prediction`.

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

- `backend/app/domain/astrology/** -> backend/app/domain/prediction/**`
- `HouseRulerResolver` dans `backend/app/domain/prediction`
- `sign_rulerships` comme source de calcul dans `backend/app/domain/prediction`
- `house_category_weights` dans `backend/app/domain/astrology`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Faits maison runtime | `backend/app/domain/astrology/runtime` | `backend/app/domain/prediction` |
| Mapping maison -> categorie | `backend/app/domain/prediction` | `backend/app/domain/astrology` |
| Priorite narrative produit | `backend/app/domain/prediction` | astrology runtime/interpretation |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/tests/unit/test_domain_router.py`
- `backend/app/tests/unit/test_natal_sensitivity.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/prediction/domain_router.py` - consommer runtime maison.
- `backend/app/domain/prediction/natal_sensitivity.py` - separer faits runtime et poids produit.

Likely tests:

- `backend/app/tests/unit/test_domain_router.py` - routing depuis runtime.
- `backend/app/tests/unit/test_natal_sensitivity.py` - sensibilite depuis runtime.
- `backend/app/tests/unit/test_engine_orchestrator.py` - non-regression globale.

Files not expected to change:

- `backend/app/domain/astrology/runtime/house_runtime_data.py` - owner traite en CS-155.
- `backend/migrations/**` - aucun changement SQL.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_domain_router.py
pytest -q app/tests/unit/test_natal_sensitivity.py app/tests/unit/test_natal_structural_v3.py
pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py
ruff check .
rg -n "sign_rulerships|get_sign_rulerships|HouseRulerResolver|cusp_sign.*ruler|app\.infra" app/domain/prediction -g "*.py"
```

## 22. Regression Risks

- Risk: score produit modifie sans decision.
  - Guardrail: baseline before/after et tests engine.
- Risk: prediction redevient proprietaire de calcul astrologique.
  - Guardrail: scan anti-recalcul et garde CS-159.

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
  unfinished work, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- Demande utilisateur du 2026-05-13 - cible `Astrology Runtime Data -> Prediction / Product Scoring`.
- `docs/tables-maisons-et-roles.md` - usages actuels de `DomainRouter` et `NatalSensitivityCalculator`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
