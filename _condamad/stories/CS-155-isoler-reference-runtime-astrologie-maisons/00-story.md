# Story CS-155 isoler-reference-runtime-astrologie-maisons: Isoler les faits runtime astrologiques des maisons

Status: ready-to-dev

## 1. Objective

Faire de `backend/app/domain/astrology` le proprietaire strict des faits
astrologiques de maison: cuspide, signe, signes contenus, maitre, placement du
maitre, occupants, angularite et force astrologique. Cette story ne doit
introduire aucune categorie produit, aucun poids de scoring et aucune dependance
vers `prediction`.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-13 sur la separation entre astrologie runtime et scoring produit.
- Reason for change: `HouseRuntimeData` existe deja apres la priorite 3, mais
  la frontiere doit etre explicite avant la consommation par prediction.

## 3. Domain Boundary

- Domain: `backend/app/domain/astrology`
- In scope:
  - stabiliser le contrat runtime des maisons dans `runtime/house_runtime_data.py`;
  - documenter ou ajouter les dataclasses astrologiques pures utiles aux maisons;
  - garantir que les donnees runtime ne portent que des faits astrologiques.
- Out of scope:
  - scoring `career`, `love`, `money`, `mood` ou autre categorie produit;
  - migration SQL ou changement de seed;
  - modification de `DomainRouter` ou `NatalSensitivityCalculator`.
- Explicit non-goals:
  - Ne pas modifier SwissEph ou les calculs astronomiques.
  - Ne pas ajouter de table SQL de runtime maisons.
  - Ne pas changer le payload public hors ajout strictement derive de `HouseRuntimeData`.
  - Ne pas changer les invariants `RG-091`, `RG-092`, `RG-093` et `RG-094`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story clarifie et verrouille un contrat runtime deja expose par la priorite 3.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les champs astrologiques peuvent etre normalises ou enrichis s'ils restent derives du theme natal.
  - Les valeurs publiques existantes doivent rester equivalentes pour les consommateurs actuels.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un champ public existant doit etre retire ou renomme.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `HouseRuntimeData` doit rester la source canonique des faits de maison. |
| Baseline Snapshot | yes | le payload maison avant/apres doit prouver l'absence de regression publique. |
| Ownership Routing | yes | les faits astrologiques doivent rester sous `domain/astrology`. |
| Allowlist Exception | no | aucune exception de dependance produit n'est autorisee. |
| Contract Shape | yes | la forme runtime des maisons doit etre explicite. |
| Batch Migration | no | aucun lot de migration de consommateurs n'est execute ici. |
| Reintroduction Guard | yes | les concepts produit ne doivent pas entrer dans `domain/astrology`. |
| Persistent Evidence | yes | les preuves avant/apres doivent etre conservees dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard and pytest runtime artifact: `backend/app/domain/astrology/runtime/house_runtime_data.py` loaded by pytest runtime tests.
- Secondary evidence:
  - `rg` scans for forbidden product symbols under `backend/app/domain/astrology`.
- Static scans alone are not sufficient for this story because:
  - the runtime builder and chart serializer must prove the dataclass is actually produced and consumed.
- Source rule: les faits de maison sont calcules une fois dans le runtime astrologique puis projetes par les couches aval.
- Forbidden alternate sources:
  - recalcul de maitrise dans `backend/app/services/chart`;
  - lecture de poids produit dans `backend/app/domain/astrology`;
  - duplication de structures maison dans `backend/app/domain/prediction`.
- Validation: tests unitaires de `build_house_runtime_data` et scan des imports interdits.

## 4c. Baseline / Before-After Rule

- Baseline required: yes
- Baseline artifact before implementation:
  - `_condamad/stories/CS-155-isoler-reference-runtime-astrologie-maisons/generated/house-runtime-contract-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-155-isoler-reference-runtime-astrologie-maisons/generated/house-runtime-contract-after.md`
- Expected invariant:
  - `chart_results.result_payload.houses[]` reste derive de `HouseRuntimeData` et ne contient aucun champ produit.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits runtime maisons | `backend/app/domain/astrology/runtime` | `backend/app/domain/prediction` |
| Construction runtime maisons | `backend/app/domain/astrology/builders` | `backend/app/services/prediction` |
| Projection publique chart | `backend/app/services/chart` | recalcul astrologique depuis prediction |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception n'est acceptable pour importer `prediction` depuis `domain/astrology`.

## 4f. Contract Shape

Contract type:
- Python dataclass runtime.
Fields:
- `house`, `cusp_sign`, `sign`, `contained_signs`, `intercepted_signs`, `ruler`, `occupants`, `axis`, `strength`.
Required fields:
- `house`, `cusp_sign`, `house_kind` ou equivalent astrologique, `ruler`, `occupants`, `strength`.
Optional fields:
- Champs de compatibilite publique deja presents comme `sign`.
Status codes:
- none.
Serialization names:
- `houses[]` dans `chart_results.result_payload`.
Frontend type impact:
- Aucun changement attendu dans cette story.
Generated contract impact:
- OpenAPI seulement si les schemas exposes changent; sinon capturer un snapshot sans difference.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: cette story stabilise l'owner runtime sans migrer les calculateurs produit.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Runtime before | `generated/house-runtime-contract-before.md` | Initial runtime shape. |
| Runtime after | `generated/house-runtime-contract-after.md` | Final runtime shape. |
| Import scan | `generated/astrology-no-product-imports-after.md` | No product dependency. |

## 4i. Reintroduction Guard

- Guard type: AST import guard or deterministic scan
- Forbidden patterns:
  - `from app.domain.prediction`
  - `from app.services.prediction`
  - `prediction_categories`
  - `house_category_weights`
  - `visibility_weight`
  - `base_priority`
  - `routing_role`
- Guard command:
  `rg -n "prediction_categories|house_category_weights|visibility_weight|base_priority" app/domain/astrology -g "*.py"`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/runtime/house_runtime_data.py` - `HouseRuntimeData` existe deja pour porter les maisons runtime.
- Evidence 2: `backend/app/domain/astrology/builders/house_runtime_builder.py` - `build_house_runtime_data` construit les maisons runtime.
- Evidence 3: `backend/app/domain/astrology/natal_calculation.py` - `build_natal_result` assemble les maisons dans le resultat natal.
- Evidence 4: `_condamad/stories/priorite-3-runtime-maisons-riches/00-story.md` - la priorite 3 a etabli le runtime maisons enrichi.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `HouseRuntimeData` repond aux questions astrologiques pures demandees par le produit.
- Aucun champ ou import produit n'apparait dans `backend/app/domain/astrology`.
- Les serializers chart lisent le runtime sans recalculer les maitres.
- Les preuves persistent le contrat runtime avant/apres.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - les donnees astrologiques de reference ne doivent pas revenir vers une table generique.
  - `RG-092` - les tables structurelles astrologiques restent non versionnees.
  - `RG-093` - les maitrises de signes restent canoniques.
  - `RG-094` - `houses[*].ruler` reste la source runtime canonique.
- Non-applicable invariants:
  - `RG-035` - le moteur prediction pur n'est pas modifie dans cette story.
- Required regression evidence:
  - tests unitaires astrology runtime;
  - scan anti-import produit dans `app/domain/astrology`;
  - snapshot de contrat maison runtime.
- Allowed differences:
  - ajout de champs astrologiques purs.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `HouseRuntimeData` expose les faits astrologiques sans champ produit. | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py`. |
| AC2 | `domain/astrology` ne contient aucun symbole produit. | `rg -n "prediction_categories|house_category_weights" app/domain/astrology -g "*.py"` zero-hit. |
| AC3 | `houses[*].ruler` reste serialise depuis `HouseRuntimeData`. | `pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter et verrouiller le contrat runtime maison (AC: AC1, AC3)
  - [ ] Subtask 1.1 - Lire `house_runtime_data.py`, `house_runtime_builder.py` et `natal_calculation.py`.
  - [ ] Subtask 1.2 - Ajouter ou ajuster les dataclasses astrologiques pures necessaires sans champ produit.

- [ ] Task 2 - Ajouter les preuves et tests de non-regression (AC: AC1, AC2, AC3)
  - [ ] Subtask 2.1 - Completer les tests unitaires runtime et chart.
  - [ ] Subtask 2.2 - Persister les inventaires before/after dans `generated/`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HouseRuntimeData` pour tout fait maison runtime.
  - `build_house_runtime_data` pour assembler les maisons.
  - `HouseRulerRuntimeData` ou structure existante pour les maitres.
- Do not recreate:
  - un second resolver de maitrise dans les serializers;
  - un mapping maison -> categorie dans `domain/astrology`.
- Shared abstraction allowed only if:
  - elle remplace une duplication observee dans `domain/astrology` et reste astrologique pure.

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

- `backend/app/domain/astrology/** -> app.domain.prediction`
- `backend/app/domain/astrology/** -> app.services.prediction`
- `prediction_categories`
- `house_category_weights`
- `visibility_weight`
- `base_priority`
- `routing_role`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Faits runtime maisons | `backend/app/domain/astrology/runtime` | `backend/app/domain/prediction`, `backend/app/services/prediction` |
| Construction runtime maisons | `backend/app/domain/astrology/builders` | serializers chart et calculateurs produit |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: constrained
- Reason: verifier l'absence de changement OpenAPI si aucun schema public ne change; sinon capturer le diff des champs maisons.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `_condamad/stories/priorite-3-runtime-maisons-riches/generated/10-final-evidence.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/house_runtime_data.py` - clarifier le contrat runtime astrologique.
- `backend/app/domain/astrology/builders/house_runtime_builder.py` - alimenter tout champ astrologique manquant.

Likely tests:

- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py` - couverture runtime maison.
- `backend/app/tests/unit/test_chart_json_builder.py` - couverture projection publique.

Files not expected to change:

- `backend/app/domain/prediction/domain_router.py` - migration produit reservee a une story ulterieure.
- `backend/app/infra/db/models/prediction_reference.py` - pas de changement SQL.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/domain/astrology app/tests/unit -k "house_runtime or chart_json"
pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py
ruff check .
rg -n "app\.domain\.prediction|app\.services\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: le serializer chart recalcule un maitre au lieu de lire le runtime.
  - Guardrail: `RG-094` et tests chart.
- Risk: un poids produit entre dans le runtime astrologique.
  - Guardrail: scan anti-symboles et future garde AST.

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

- Demande utilisateur du 2026-05-13 - separation cible des couches astrology/runtime et prediction/product.
- `_condamad/stories/priorite-3-runtime-maisons-riches/00-story.md` - runtime maisons deja livre.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
