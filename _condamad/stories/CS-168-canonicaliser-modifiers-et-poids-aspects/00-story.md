# Story CS-168 canonicaliser-modifiers-et-poids-aspects: Canonicaliser modifiers et poids des aspects

Status: ready-to-dev

## 1. Objective

Introduire `AspectModifierRuntimeData` et clarifier les contrats
`strength`, `importance`, `dominance`, `interpretive_weight` et
`prediction_weight`. La story evite les conditions ad hoc et les confusions de
poids dans le runtime aspect.

## 2. Trigger / Source

- Source type: code-review
- Source reference: revue utilisateur du 2026-05-14 sur les angles morts des
  modifiers et poids aspect.
- Reason for change: angularite, luminaire, phase, retrogradation, chart ruler
  et autres facteurs doivent etre extensibles sans `if` disperses.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/runtime`
- In scope:
  - definir `AspectModifierType`;
  - definir `AspectModifierRuntimeData`;
  - separer les concepts de poids aspect;
  - adapter `AspectRuntimeData` pour porter les modifiers.
- Out of scope:
  - calcul produit prediction;
  - endpoints publics;
  - patterns astrologiques;
  - graph runtime global.
- Explicit non-goals:
  - Ne pas mapper `prediction_weight` dans astrology.
  - Ne pas creer de poids unique universel.
  - Ne pas coder les modifiers comme strings libres.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story durcit le contrat runtime aspect sans changer les
  referentiels SQL.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les modifiers sont typed.
  - Les poids ont des noms distincts et documentes.
  - `prediction_weight` reste possede par prediction.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un modifier demande une source de donnees absente.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `AspectRuntimeData.modifiers` devient la source des modifiers. |
| Baseline Snapshot | yes | Les modifiers et poids before/after doivent etre compares. |
| Ownership Routing | yes | Astrology et prediction possedent des poids distincts. |
| Allowlist Exception | no | Aucune string libre de modifier n'est autorisee. |
| Contract Shape | yes | Les modifiers et poids sont des contrats nouveaux. |
| Batch Migration | no | Aucun consommateur produit n'est migre. |
| Reintroduction Guard | yes | Les poids confondus et modifiers libres doivent etre bloques. |
| Persistent Evidence | yes | Artefacts before/after requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectRuntimeData.modifiers` et AST guard des enums modifiers.
- Secondary evidence:
  - tests `backend/tests/unit/domain/astrology/test_aspect_modifiers.py`.
- Static scans alone are not sufficient for this story because:
  - les modifiers doivent etre produits par le runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-168-canonicaliser-modifiers-et-poids-aspects/generated/aspect-modifiers-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-168-canonicaliser-modifiers-et-poids-aspects/generated/aspect-modifiers-after.md`
- Expected invariant:
  - les poids techniques, structurels, interpretatifs et produit restent distincts.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Force technique | `AspectStrengthEvaluator` | dominance, prediction |
| Modifiers runtime | `AspectModifierRuntimeData` | conditions locales dispersees |
| Dominance structurelle | `DominantAspectEvaluator` | strength |
| Poids prediction | `backend/app/domain/prediction` | `domain/astrology` |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception de modifier libre n'est autorisee.

## 4f. Contract Shape

- Contract type:
  - Python enum and runtime data contracts.
- Fields:
  - `modifier_type`, `source`, `intensity`, `reason`, `applies_to`;
  - `technical_strength`, `structural_dominance`, `interpretive_weight`.
- Required fields:
  - `modifier_type`, `source`, `intensity`.
- Optional fields:
  - `reason`, `applies_to`, `interpretive_weight`.
- Status codes:
  - none.
- Serialization names:
  - snake_case.
- Frontend type impact:
  - none direct.
- Generated contract impact:
  - none.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: cette story definit les contrats avant migration des consommateurs.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Modifiers before | `generated/aspect-modifiers-before.md` | Etat avant contrat modifiers. |
| Modifiers after | `generated/aspect-modifiers-after.md` | Exemple de modifiers typed. |
| Weight taxonomy | `generated/aspect-weight-taxonomy.md` | Separation des poids. |

## 4i. Reintroduction Guard

- Guard type: unit tests plus scans.
- Forbidden patterns:
  - modifier aspect en string libre;
  - champ `weight` ambigu dans runtime aspect;
  - `prediction_weight` dans `domain/astrology`.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_aspect_modifiers.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md` - runtime et force aspect.
- Evidence 2: `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/00-story.md` - dominance aspect.
- Evidence 3: `backend/app/domain/prediction/natal_sensitivity.py` - poids produit existants hors astrology.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `AspectModifierType` enumere les modifiers supportes.
- `AspectModifierRuntimeData` porte type, source et intensite.
- `AspectRuntimeData` expose une collection de modifiers.
- Les poids strength, dominance, interpretive et prediction sont nommes et separes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne depend pas de prediction.
  - `RG-098` - le runtime aspect reste canonique.
  - `RG-101` - dominance et synastrie reutilisent le runtime.
- Non-applicable invariants:
  - `RG-100` - pas de generation editoriale.
- Required regression evidence:
  - tests modifiers;
  - scan poids ambigus;
  - artefact taxonomie des poids.
- Allowed differences:
  - ajout de modifiers typed.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `AspectModifierType` enumere les modifiers supportes. | `pytest -q tests/unit/domain/astrology/test_aspect_modifiers.py`. |
| AC2 | `AspectRuntimeData` expose des modifiers typed. | `pytest -q tests/unit/domain/astrology/test_aspect_modifiers.py`. |
| AC3 | Les poids aspect sont nommes sans champ `weight` ambigu. | `rg -n "\\bweight\\b|prediction_weight" app/domain/astrology -g "*.py"` avec classification. |
| AC4 | `prediction_weight` reste hors `domain/astrology`. | `rg -n "prediction_weight" app/domain/astrology -g "*.py"` attendu zero hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir les modifiers (AC: AC1, AC2)
  - [ ] Ajouter `AspectModifierType`.
  - [ ] Ajouter `AspectModifierRuntimeData`.

- [ ] Task 2 - Clarifier les poids (AC: AC3, AC4)
  - [ ] Nommer les poids dans des contrats distincts.
  - [ ] Documenter `prediction_weight` comme owner prediction.

- [ ] Task 3 - Ajouter preuves et guards (AC: AC1, AC2, AC3, AC4)
  - [ ] Ajouter tests.
  - [ ] Capturer `aspect-weight-taxonomy.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData`.
  - `AspectStrengthEvaluator`.
  - `DominantAspectEvaluator`.
- Do not recreate:
  - conditions modifiers dispersees;
  - poids unique universel;
  - logique prediction dans astrology.
- Shared abstraction allowed only if:
  - elle sert les aspects natals et inter-chart.

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

- `modifier = "angular"`
- champ runtime generique `weight`
- `prediction_weight` dans `backend/app/domain/astrology`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Modifiers aspect | `AspectModifierRuntimeData` | conditions locales |
| Force technique | `AspectStrengthEvaluator` | dominance |
| Poids produit | `domain/prediction` | astrology |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/domain/astrology/interpretation/aspect_strength.py`
- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/tests/unit/test_astrology_prediction_boundary.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/aspect_modifiers.py` - enums et data.
- `backend/app/domain/astrology/runtime/aspect_runtime_data.py` - collection modifiers.
- `backend/app/domain/astrology/interpretation/aspect_strength_contracts.py` - clarifier strength.
- `backend/app/domain/astrology/interpretation/dominant_aspects.py` - clarifier dominance.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_modifiers.py` - modifiers et poids.
- `backend/app/tests/unit/test_astrology_prediction_boundary.py` - frontiere prediction.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - aucun impact UI.
- `backend/app/api/**` - aucun endpoint.

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
pytest -q tests/unit/domain/astrology/test_aspect_modifiers.py
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
rg -n "\\bweight\\b|prediction_weight" app/domain/astrology -g "*.py"
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: `weight` devient un concept fourre-tout.
  - Guardrail: taxonomie et scan.
- Risk: modifiers sous forme de strings.
  - Guardrail: enum et tests.
- Risk: prediction infiltre astrology.
  - Guardrail: `RG-095`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'AGENTS.md: toute commande Python doit etre executee apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- Revue utilisateur du 2026-05-14 - modifiers et distinction des poids.
- `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md`.
- `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/00-story.md`.
