# Story CS-169 preparer-pattern-runtime-et-graphe-astrologique: Preparer pattern runtime et graphe astrologique

Status: ready-to-dev

## 1. Objective

Definir le socle `PatternRuntimeData` et les contraintes d'agregation vers un
futur `AstrologicalGraphRuntime`. La story evite que T-square, Grand Trine,
Yod, Kite ou synastrie soient ajoutes plus tard sous forme de hacks disperses.

## 2. Trigger / Source

- Source type: code-review
- Source reference: revue utilisateur du 2026-05-14 sur les futurs piliers
  aspects.
- Reason for change: les patterns astrologiques et le graphe global sont le
  niveau superieur naturel des planètes, signes, maisons, rulers et aspects.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/runtime`
- In scope:
  - definir `PatternRuntimeData`;
  - definir `PatternType`;
  - definir un contrat minimal de graph readiness;
  - ajouter une garde qui interdit les detectors patterns disperses.
- Out of scope:
  - implementer tous les patterns astrologiques;
  - creer embeddings, recherche ou IA;
  - exposer une API de graphe;
  - modifier le frontend.
- Explicit non-goals:
  - Ne pas construire `AstrologicalGraphRuntime` complet.
  - Ne pas coder T-square ou Yod hors contrat pattern.
  - Ne pas dupliquer `AspectRuntimeData`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story cree un contrat runtime preparatoire sans changer
  les comportements publics.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les patterns utilisent des references vers les runtime existants.
  - Le graphe reste un contrat de preparation, pas un moteur complet.
  - Aucun endpoint public n'est ajoute.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un pattern doit etre calcule immediatement.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `PatternRuntimeData` prepare la source runtime pattern. |
| Baseline Snapshot | yes | Les surfaces pattern avant/apres doivent etre inventoriees. |
| Ownership Routing | yes | Patterns et graph restent dans astrology runtime. |
| Allowlist Exception | no | Aucun detector disperse n'est autorise. |
| Contract Shape | yes | `PatternRuntimeData` et graph readiness sont des contrats nouveaux. |
| Batch Migration | no | Aucun consommateur n'est migre. |
| Reintroduction Guard | yes | Les hacks pattern disperses doivent etre bloques. |
| Persistent Evidence | yes | Inventaire before/after requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `PatternRuntimeData` et AST guard des detectors pattern.
- Secondary evidence:
  - tests `backend/tests/unit/domain/astrology/test_pattern_runtime_contract.py`.
- Static scans alone are not sufficient for this story because:
  - le contrat doit prouver l'agregation de runtime existants.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-169-preparer-pattern-runtime-et-graphe-astrologique/generated/pattern-runtime-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-169-preparer-pattern-runtime-et-graphe-astrologique/generated/pattern-runtime-after.md`
- Expected invariant:
  - aucun detector pattern actif ne vit hors owner canonique.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Pattern runtime | `backend/app/domain/astrology/runtime` | prediction, LLM, API |
| Pattern evaluation | `backend/app/domain/astrology/interpretation` ou calculators | services publics |
| Graph readiness | `backend/app/domain/astrology/runtime` | frontend, prediction |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucun detector pattern disperse n'est autorise.

## 4f. Contract Shape

- Contract type:
  - Python runtime data contracts.
- Fields:
  - `pattern_type`, `participants`, `aspects`, `houses`, `signs`,
    `modifiers`, `confidence`, `graph_nodes`, `graph_edges`.
- Required fields:
  - `pattern_type`, `participants`, `aspects`, `confidence`.
- Optional fields:
  - `houses`, `signs`, `modifiers`, `graph_nodes`, `graph_edges`.
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
- Reason: aucun consommateur pattern n'est migre.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Pattern before | `generated/pattern-runtime-before.md` | Inventaire sans contrat pattern. |
| Pattern after | `generated/pattern-runtime-after.md` | Exemple de contrat pattern. |
| Graph readiness | `generated/astrology-graph-readiness.md` | Contraintes d'agregation future. |

## 4i. Reintroduction Guard

- Guard type: unit tests plus scans.
- Forbidden patterns:
  - `t_square`, `grand_trine`, `yod`, `kite` hors owner canonique;
  - graph nodes sous prediction;
  - duplication de `AspectRuntimeData`.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md` - runtime aspect.
- Evidence 2: `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/00-story.md` - inter-chart et dominance.
- Evidence 3: `backend/app/domain/astrology/runtime/house_runtime_data.py` - runtime maisons agregeable.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `PatternRuntimeData` existe comme contrat d'agregation.
- `PatternType` nomme les patterns supportables.
- La preparation graph indique nodes, edges, modifiers et weights.
- Les detectors pattern disperses sont interdits par garde.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-094` - les maisons runtime restent source maison.
  - `RG-098` - les aspects runtime restent source aspect.
  - `RG-101` - inter-chart reutilise les referentiels aspects.
  - `RG-103` - modifiers et poids restent typed.
- Non-applicable invariants:
  - `RG-100` - pas de renderer editorial.
- Required regression evidence:
  - test contrat pattern;
  - scan anti-detectors disperses;
  - artefact graph readiness.
- Allowed differences:
  - ajout de contrats preparatoires.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `PatternRuntimeData` reference les runtimes existants. | `pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py`. |
| AC2 | `PatternType` enumere les patterns sans les calculer tous. | `pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py`. |
| AC3 | Le graph readiness nomme les node types. | `pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py` + artefact graph readiness. |
| AC4 | Les detectors pattern disperses sont absents. | `rg -n "t_square|grand_trine|yod|kite|mystic_rectangle" app -g "*.py"` avec classification. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir les contrats pattern (AC: AC1, AC2)
  - [ ] Ajouter `PatternType`.
  - [ ] Ajouter `PatternRuntimeData`.

- [ ] Task 2 - Documenter la readiness graph (AC: AC3)
  - [ ] Definir nodes, edges, modifiers et poids attendus.
  - [ ] Relier maisons, signes, planetes, aspects et rulers.

- [ ] Task 3 - Ajouter guards (AC: AC4)
  - [ ] Ajouter test contrat.
  - [ ] Capturer scans pattern.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData`.
  - `HouseRuntimeData`.
  - `AspectModifierRuntimeData`.
- Do not recreate:
  - participants aspect sous un autre format;
  - detectors pattern dans prediction ou LLM;
  - graph runtime complet.
- Shared abstraction allowed only if:
  - elle reference les contrats runtime existants sans les copier.

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

- `t_square` hors owner pattern
- `grand_trine` hors owner pattern
- graph nodes dans `backend/app/domain/prediction`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Runtime pattern | `backend/app/domain/astrology/runtime` | prediction, API |
| Evaluation pattern | `backend/app/domain/astrology` | LLM |
| Graph global futur | `backend/app/domain/astrology/runtime` | frontend |

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
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/aspect_modifiers.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/pattern_runtime_data.py` - contrat pattern.
- `backend/app/domain/astrology/runtime/__init__.py` - export.
- `backend/app/domain/astrology/runtime/astrological_graph_contracts.py` - readiness graph.

Likely tests:

- `backend/tests/unit/domain/astrology/test_pattern_runtime_contract.py` - pattern et graph readiness.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - aucune UI.
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
pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py
rg -n "t_square|grand_trine|yod|kite|mystic_rectangle" app -g "*.py"
rg -n "graph_nodes|graph_edges" app/domain/prediction -g "*.py"
```

## 22. Regression Risks

- Risk: les patterns sont codes dans LLM ou prediction.
  - Guardrail: scan owner pattern.
- Risk: le graphe copie les runtime au lieu de les referencer.
  - Guardrail: tests contractuels.
- Risk: scope trop large.
  - Guardrail: aucun moteur graph complet dans cette story.

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

- Revue utilisateur du 2026-05-14 - patterns et graphe astrologique global.
- `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md`.
- `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/00-story.md`.
