# Story CS-160 canonicaliser-contrats-interpretation-astrologique: Canonicaliser les contrats d'interpretation astrologique

Status: done

## 1. Objective

Formaliser les contrats de sortie de l'interpretation astrologique des maisons
avant que les calculateurs produit ne les consomment. La story introduit des
types canoniques pour les raisons, niveaux et echelles de force afin d'eviter
les strings libres, les scores ambigus et les protocoles implicites.

## 2. Trigger / Source

- Source type: code-review
- Source reference: revue utilisateur du 2026-05-13 sur les stories CS-155 a
  CS-159.
- Reason for change: `HouseStrengthRuntimeData.reasons` est une liste de
  strings libres et `strength.score` expose un float sans contrat d'echelle
  assez strict pour proteger la frontiere astrology/product.

## 3. Domain Boundary

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - definir les contrats d'interpretation de force maison;
  - canonicaliser les raisons via enum;
  - definir une echelle normalisee et un niveau qualitatif;
  - faire produire ces contrats par le calcul de force maison.
- Out of scope:
  - mapping produit vers `career`, `love`, `money`, `mood`;
  - changement de poids prediction;
  - modification SQL ou seed;
  - refonte globale des autres patterns astrologiques.
- Explicit non-goals:
  - Ne pas deplacer les categories produit dans astrology.
  - Ne pas faire de fallback astrologique dans prediction.
  - Ne pas changer les invariants `RG-091` a `RG-095`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story stabilise un contrat runtime astrologique expose
  par `HouseRuntimeData.strength`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les raisons existantes doivent etre migrees vers des enums canoniques.
  - Le score numerique doit conserver l'ordre relatif des fixtures existantes.
  - Les serializers publics gardent des valeurs JSON stables ou documentent un
    ajout compatible.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une raison existante doit changer de sens
  astrologique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le contrat est execute via `HouseRuntimeData.strength`. |
| Baseline Snapshot | yes | Les raisons et scores avant/apres doivent etre compares. |
| Ownership Routing | yes | Interpretation astrology possede le contrat, prediction le consomme. |
| Allowlist Exception | no | Aucune string libre nouvelle n'est autorisee. |
| Contract Shape | yes | La forme enum/niveau/score est le coeur de la story. |
| Batch Migration | no | Les consommateurs produit ne sont pas migres ici. |
| Reintroduction Guard | yes | Les strings libres ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires before/after sont requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard and pytest runtime artifact:
    `backend/tests/unit/domain/astrology/test_house_strength.py`.
- Secondary evidence:
  - scans des raisons libres dans `backend/app/domain/astrology`.
- Static scans alone are not sufficient for this story because:
  - les fixtures doivent prouver que le contrat typed est produit par le
    calcul runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/generated/house-strength-contract-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/generated/house-strength-contract-after.md`
- Expected invariant:
  - Les maisons fortes restent plus fortes que les maisons cadentes vides, et
    les raisons existantes restent representables par enum.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat force maison | `backend/app/domain/astrology/interpretation` | `backend/app/domain/prediction` |
| Faits runtime maison | `backend/app/domain/astrology/runtime` | scoring produit |
| Mapping categorie produit | `backend/app/domain/prediction` | astrology interpretation |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception de string libre n'est autorisee pour les nouvelles
  raisons de force maison.

## 4f. Contract Shape

Contract type:
- Python enums and frozen dataclasses.
Fields:
- `normalized_score`, `level`, `reasons`, `modifiers`.
Required fields:
- `normalized_score`, `level`, `reasons`.
Optional fields:
- `angularity_modifier`, `occupancy_modifier`, `ruler_condition_modifier`.
Status codes:
- none.
Serialization names:
- `strength.score`, `strength.level`, `strength.reasons`.
Frontend type impact:
- none in this story unless chart payload typing exists.
Generated contract impact:
- OpenAPI diff only if public schema is generated for chart payloads.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: cette story definit le contrat avant migration des consommateurs
  produit.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Contract before | `generated/house-strength-contract-before.md` | Current free-string state. |
| Contract after | `generated/house-strength-contract-after.md` | Typed contract state. |
| Reason scan | `generated/house-strength-reason-scan.md` | No ad hoc reasons. |

## 4i. Reintroduction Guard

- Guard type: unit test plus targeted scan.
- Forbidden patterns:
  - appending raw string literals to strength reasons outside the enum owner;
  - assigning raw string literal lists to `reasons`;
  - passing raw string literal lists to `HouseStrengthRuntimeData.reasons`;
  - comparing `strength.score` directly in prediction without level/profile;
  - introducing `dict` payloads as interpretation contracts.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_house_strength.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/runtime/house_runtime_data.py` -
  `HouseStrengthRuntimeData` expose `score`, `dominant`, `reasons`.
- Evidence 2: `backend/app/domain/astrology/calculators/house_strength.py` -
  les raisons sont ajoutees comme strings libres.
- Evidence 3: `backend/tests/unit/domain/astrology/test_house_strength.py` -
  les tests assertent directement les strings et scores.
- Evidence 4: `docs/tables-maisons-et-roles.md` - documente un score
  deterministe entre `0.0` et `1.0`.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage.

## 6. Target State

After implementation:

- `HouseStrengthReason` enumere toutes les raisons supportees.
- `HouseStrengthLevel` qualifie la force sans obliger le produit a lire un
  seuil numerique brut.
- Le score est nomme `normalized_score` dans le contrat interne ou documente
  comme tel si `score` reste le nom JSON public.
- Les modifiers astrologiques sont structures ou explicitement absents.
- Les tests interdisent l'ajout de raisons ad hoc.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-094` - `HouseRuntimeData` reste la source de verite runtime maison.
  - `RG-095` - astrology ne depend pas de prediction.
- Non-applicable invariants:
  - `RG-035` - aucun changement du moteur prediction pur n'est requis.
- Required regression evidence:
  - tests unitaires de force maison;
  - scan des raisons libres;
  - snapshot before/after du contrat strength.
- Allowed differences:
  - ajout de `level` et de modifiers astrologiques structures.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les raisons de force maison passent par `HouseStrengthReason`. | `pytest -q tests/unit/domain/astrology/test_house_strength.py`. |
| AC2 | Le contrat expose un niveau qualitatif stable. | `pytest -q tests/unit/domain/astrology/test_house_strength.py`. |
| AC3 | L'echelle numerique est documentee comme normalisee. | `rg -n "normalized_score|score.*normalisee" app/domain/astrology docs -g "*.py" -g "*.md"`. |
| AC4 | Aucune raison ad hoc n'est ajoutee dans le calcul. | `rg -n "reasons\\s*=\\s*\\[|reasons\\.append" app/domain/astrology -g "*.py"` avec hits classes. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir les contrats canoniques (AC: AC1, AC2, AC3)
  - [ ] Subtask 1.1 - Ajouter `HouseStrengthReason`.
  - [ ] Subtask 1.2 - Ajouter `HouseStrengthLevel`.
  - [ ] Subtask 1.3 - Definir le contrat de score normalise.

- [ ] Task 2 - Migrer le calcul de force maison (AC: AC1, AC2, AC4)
  - [ ] Subtask 2.1 - Remplacer les strings libres par enum.
  - [ ] Subtask 2.2 - Conserver une serialization JSON stable si exposee.

- [ ] Task 3 - Ajouter preuves et guards (AC: AC3, AC4)
  - [ ] Subtask 3.1 - Capturer les snapshots before/after.
  - [ ] Subtask 3.2 - Ajouter un test ou scan anti-raison ad hoc.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HouseStrengthRuntimeData` ou son remplacement typed.
  - `calculate_house_strength` comme point de production existant.
  - tests `backend/tests/unit/domain/astrology/test_house_strength.py`.
- Do not recreate:
  - un second score de force maison;
  - des dicts d'interpretation non types;
  - des strings de raison hors enum.
- Shared abstraction allowed only if:
  - elle sert plusieurs contrats d'interpretation astrologique.

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

- `reasons.append("raw_reason")` hors owner canonique.
- `strength.score >` dans `backend/app/domain/prediction`.
- `dict[str, Any]` comme contrat d'interpretation astrologique.
- `backend/app/domain/astrology/** -> app.domain.prediction`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Raisons de force maison | `backend/app/domain/astrology/interpretation` | strings locales |
| Niveau de force maison | `backend/app/domain/astrology/interpretation` | seuils produit |
| Score produit categorie | `backend/app/domain/prediction` | astrology interpretation |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: constrained
- Reason: si `strength.level` est expose via JSON public, capturer le diff du
  payload chart et confirmer la compatibilite.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/calculators/house_strength.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_house_strength.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/house_strength_contracts.py` -
  nouveaux enums et dataclass typed.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - brancher le
  contrat typed si l'owner runtime reste ici.
- `backend/app/domain/astrology/calculators/house_strength.py` - produire les
  raisons enum et le niveau.

Likely tests:

- `backend/tests/unit/domain/astrology/test_house_strength.py` - contrat typed.
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py` -
  integration runtime.
- `backend/app/tests/unit/test_chart_json_builder.py` - serialization publique.

Files not expected to change:

- `backend/app/domain/prediction/**` - seulement scans anti-consommation brute.
- `backend/migrations/**` - aucun changement SQL.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/domain/astrology/test_house_strength.py
pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py
pytest -q app/tests/unit/test_chart_json_builder.py
ruff check .
rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"
rg -n "reasons\\s*=\\s*\\[|HouseStrengthRuntimeData\\(" app/domain/astrology -g "*.py"
rg -n "strength\\.score\\s*[<>]=?" app/domain/prediction -g "*.py"
```

## 22. Regression Risks

- Risk: le payload public change brutalement pour `strength.reasons`.
  - Guardrail: test chart JSON et snapshot after.
- Risk: les enums deviennent un protocole produit cache.
  - Guardrail: `RG-095` et interdiction des imports prediction.
- Risk: les seuils numeriques sont reutilises directement en scoring.
  - Guardrail: scan `strength.score` dans `domain/prediction`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias,
  fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unfinished work, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- Revue utilisateur du 2026-05-13 - angles morts sur contracts, enums,
  reasons et score normalise.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - contrat
  runtime actuel.
- `backend/app/domain/astrology/calculators/house_strength.py` - raisons libres
  actuelles.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
