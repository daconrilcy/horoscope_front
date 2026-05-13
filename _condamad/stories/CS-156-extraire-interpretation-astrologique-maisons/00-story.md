# Story CS-156 extraire-interpretation-astrologique-maisons: Extraire l'interpretation astrologique pure des maisons

Status: ready-to-dev

## 1. Objective

Créer une couche `backend/app/domain/astrology/interpretation` qui enrichit les
faits runtime des maisons sans connaitre les categories produit. Elle porte les
responsabilites comme force de maison, dominance, axes, interceptions et chaines
de maitrise.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-13 sur la couche `astrology/interpretation`.
- Reason for change: les faits runtime et leur interpretation astrologique doivent preceder toute decision de scoring produit.

## 3. Domain Boundary

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - creer les evaluateurs astrologiques purs;
  - deplacer ou encapsuler la logique de force/dominance astrologique si elle existe dans le builder;
  - exposer des raisons astrologiques comme `angular_house`, `ruler_in_cadent_house`, `two_occupants`.
- Out of scope:
  - categories produit et priorites narratives;
  - `DomainRouter`, `CategoryScorer`, `PublicAstroFoundationProjector`;
  - changement de schema SQL ou seed prediction.
- Explicit non-goals:
  - Ne pas modifier les calculs astronomiques.
  - Ne pas changer la projection publique au-dela des faits deja serialises.
  - Ne pas introduire `career`, `love`, `money`, `mood` dans `domain/astrology`.
  - Ne pas changer les invariants `RG-091` a `RG-094`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: service-boundary-refactor
- Archetype reason: la story cree un owner explicite pour l'interpretation astrologique pure.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les scores astrologiques peuvent etre recalcules par une classe dediee si les resultats attendus restent couverts.
  - Aucun score produit ne doit changer dans cette story.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une regle astrologique existante doit changer de semantique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les evaluateurs lisent `HouseRuntimeData` et ne reconstruisent pas le theme. |
| Baseline Snapshot | yes | la force maison avant/apres doit etre comparable. |
| Ownership Routing | yes | l'interpretation astrologique a un owner distinct de runtime et prediction. |
| Allowlist Exception | no | aucune dependance produit n'est autorisee. |
| Contract Shape | yes | les resultats d'interpretation doivent avoir une forme stable. |
| Batch Migration | no | les consommateurs produit ne sont pas migres ici. |
| Reintroduction Guard | yes | l'interpretation ne doit pas importer prediction. |
| Persistent Evidence | yes | les preuves des regles et scans doivent rester dans la story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard and pytest runtime artifact: `backend/app/domain/astrology/runtime/house_runtime_data.py` executed through astrology pytest fixtures.
- Secondary evidence:
  - scans under `backend/app/domain/astrology/interpretation` for product imports and symbols.
- Static scans alone are not sufficient for this story because:
  - `HouseStrengthEvaluator` must prove runtime behavior on angular, succedent, cadent, occupant and ruler-placement cases.
- Interpretation source: evaluateurs sous `backend/app/domain/astrology/interpretation`.
- Rule: l'interpretation enrichit les faits, elle ne les remplace pas.

## 4c. Baseline / Before-After Rule

- Baseline required: yes
- Baseline artifact before implementation:
  - `_condamad/stories/CS-156-extraire-interpretation-astrologique-maisons/generated/house-interpretation-baseline.md`
- Comparison after implementation:
  - `_condamad/stories/CS-156-extraire-interpretation-astrologique-maisons/generated/house-interpretation-after.md`
- Expected invariant:
  - les scores et raisons de force maison restent equivalents sauf correction astrologique documentee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Force astrologique maison | `backend/app/domain/astrology/interpretation` | `backend/app/domain/prediction` |
| Faits source maison | `backend/app/domain/astrology/runtime` | recalcul dans `backend/app/domain/prediction` |
| Poids et categories produit | `backend/app/domain/prediction` | `backend/app/domain/astrology/interpretation` |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: cette couche doit rester astrologique pure; aucune exception produit n'est acceptee.

## 4f. Contract Shape

Contract type:
- Python dataclasses / evaluator return objects.
Fields:
- `score`, `reasons`, `dominant`, `axis`, `interceptions`, `rulership_chain` selon evaluateur implemente.
Required fields:
- `score` et `reasons` pour la force de maison.
Optional fields:
- Champs specifiques aux analyzers non implementes dans la premiere tranche.
Status codes:
- none.
Serialization names:
- Pas d'exposition API directe dans cette story.
Frontend type impact:
- none.
Generated contract impact:
- none.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: aucun lot de consommateurs produit n'est migre dans cette story.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline | `generated/house-interpretation-baseline.md` | Current strength reasons. |
| After | `generated/house-interpretation-after.md` | Evaluator output. |
| Import scan | `generated/astrology-interpretation-import-guard.md` | No product dependency. |

## 4i. Reintroduction Guard

- Guard type: deterministic scan, then AST test when CS-159 is implemented.
- Forbidden patterns:
  - `app.domain.prediction`
  - `app.services.prediction`
  - `prediction_categories`
  - `house_category_weights`
  - `category_weight`
- Guard command:
  `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|category_weight" app/domain/astrology/interpretation -g "*.py"`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/runtime/house_runtime_data.py` - `HouseStrengthRuntimeData` est deja rattache au runtime maisons.
- Evidence 2: `backend/app/domain/astrology/builders/house_runtime_builder.py` - la construction de force maison peut etre extraite vers un evaluator.
- Evidence 3: `docs/tables-maisons-et-roles.md` - la documentation distingue deja faits runtime et consommation produit.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `HouseStrengthEvaluator` existe et ne depend que du runtime astrologique.
- Les futures classes `HouseDominanceEvaluator`, `RulershipChainResolver`, `InterceptionAnalyzer` et `AxisAnalyzer` ont un emplacement canonique documente.
- Le builder runtime orchestre l'evaluation sans porter toute la logique d'interpretation.
- Aucun symbole produit n'est present dans `domain/astrology/interpretation`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - pas de retour a une reference astrologique generique.
  - `RG-093` - les maitrises restent issues de la source canonique.
  - `RG-094` - la projection des maitres reste issue de `HouseRuntimeData.ruler`.
- Non-applicable invariants:
  - `RG-035` - le moteur prediction pur n'est pas modifie.
- Required regression evidence:
  - tests unitaires `HouseStrengthEvaluator`;
  - scan imports interdits;
  - comparaison before/after des raisons de force.
- Allowed differences:
  - none, sauf correction astrologique explicitement documentee.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `HouseStrengthEvaluator` produit les raisons astrologiques. | `pytest -q tests/unit/domain/astrology/test_house_strength.py`. |
| AC2 | Le builder runtime appelle l'interpretation sans dupliquer le calcul. | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py`. |
| AC3 | `domain/astrology/interpretation` ne depend pas de prediction. | `rg -n "app\\.domain\\.prediction" app/domain/astrology/interpretation -g "*.py"` zero-hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Creer l'owner interpretation maison (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Ajouter le package `backend/app/domain/astrology/interpretation`.
  - [ ] Subtask 1.2 - Extraire `HouseStrengthEvaluator` depuis la logique existante ou l'implementer par reutilisation.

- [ ] Task 2 - Couvrir les cas astrologiques (AC: AC1, AC3)
  - [ ] Subtask 2.1 - Tester angularite, occupants et placement du maitre.
  - [ ] Subtask 2.2 - Ajouter la preuve de scan anti-produit.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HouseRuntimeData` et ses sous-structures.
  - les constantes ou helpers existants de signes, maisons et maitrises.
- Do not recreate:
  - une table de poids maison;
  - un mapping categorie produit;
  - un second builder de theme natal.
- Shared abstraction allowed only if:
  - elle est limitee a l'interpretation astrologique et reutilisee par au moins deux evaluateurs.

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

- `backend/app/domain/astrology/interpretation/** -> app.domain.prediction`
- `backend/app/domain/astrology/interpretation/** -> app.services.prediction`
- `DomainRouter`
- `PublicAstroFoundationProjector`
- `house_category_weights`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Force astrologique maison | `backend/app/domain/astrology/interpretation/house_strength.py` | builders runtime, prediction calculators |
| Analyse interceptions/axes | `backend/app/domain/astrology/interpretation` | product scoring |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/tests/unit/domain/astrology`
- `backend/app/tests/unit/test_chart_json_builder.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/house_strength.py` - nouvel evaluator astrologique.
- `backend/app/domain/astrology/interpretation/__init__.py` - exports limites.
- `backend/app/domain/astrology/builders/house_runtime_builder.py` - delegation vers l'evaluator.

Likely tests:

- `backend/tests/unit/domain/astrology/test_house_strength_evaluator.py` - cas d'interpretation.
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py` - integration builder.

Files not expected to change:

- `backend/app/domain/prediction/domain_router.py` - hors scope.
- `backend/app/infra/db/models/prediction_reference.py` - hors scope SQL.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/domain/astrology -k "house_strength or house_runtime"
pytest -q app/tests/unit/test_chart_json_builder.py
ruff check .
rg -n "app\.domain\.prediction|app\.services\.prediction|prediction_categories|house_category_weights|category_weight" app/domain/astrology/interpretation -g "*.py"
```

## 22. Regression Risks

- Risk: divergence entre builder runtime et evaluator.
  - Guardrail: tests builder + evaluator sur les memes fixtures.
- Risk: l'interpretation devient implicitement produit.
  - Guardrail: scan et future garde AST `CS-159`.

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

- Demande utilisateur du 2026-05-13 - couche `astrology/interpretation`.
- `docs/tables-maisons-et-roles.md` - documentation runtime maisons et scoring.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
