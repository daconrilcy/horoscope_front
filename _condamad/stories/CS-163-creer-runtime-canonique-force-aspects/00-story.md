# Story CS-163 creer-runtime-canonique-force-aspects: Creer le runtime canonique et la force des aspects

Status: ready-to-dev

## 1. Objective

Creer le contrat `AspectRuntimeData` et le service `AspectStrengthEvaluator`.
Ils transforment les aspects calcules plats en faits enrichis pour LLM,
frontend, scoring et projections publiques.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-14 sur le `Canonical Aspect Runtime`.
- Reason for change: `AspectResult` expose surtout `aspect_code`, participants et orbes.
  Les maisons disposent deja d'un runtime riche via `HouseRuntimeData`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology`
- In scope:
  - definir `AspectRuntimeData` sous le runtime astrologique;
  - definir `AspectStrengthEvaluator` et `AspectStrengthReason`;
  - calculer `ratio`, `level`, `normalized_score`, `is_exact`, `is_tight` et `reasons`;
  - brancher le builder runtime depuis les resultats d'aspects natals existants.
- Out of scope:
  - modifier les tables SQL des aspects;
  - modifier le scoring produit dans `backend/app/domain/prediction`;
  - generer les textes editoriaux LLM;
  - changer les endpoints publics frontend/API.
- Explicit non-goals:
  - Ne pas deplacer les categories produit vers astrology.
  - Ne pas recreer un resolver d'orbes concurrent.
  - Ne pas modifier les invariants `RG-091` a `RG-097`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story ajoute une source runtime canonique sans casser les calculs existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les aspects detectes restent les memes pour les fixtures existantes.
  - Le nouveau runtime enrichit les donnees sans supprimer les champs actuels.
  - Les raisons de force doivent etre enumerees, jamais des strings libres.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un seuil de force doit diverger des profils de reference existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `AspectRuntimeData` devient la source canonique des faits runtime aspect. |
| Baseline Snapshot | yes | Les aspects detectes et leurs orbes doivent etre compares avant/apres. |
| Ownership Routing | yes | `domain/astrology` possede le runtime, `domain/prediction` ne le definit pas. |
| Allowlist Exception | no | Aucune exception de raison libre n'est autorisee. |
| Contract Shape | yes | La forme du runtime et de la force est le coeur de la story. |
| Batch Migration | no | Aucun lot de migration de consommateurs n'est requis dans cette story. |
| Reintroduction Guard | yes | Les raisons libres et dicts runtime concurrents doivent etre bloques. |
| Persistent Evidence | yes | Les snapshots runtime avant/apres doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/aspect_runtime_data.py`;
  - AST guard et tests `backend/tests/unit/domain/astrology/test_aspect_strength.py` et `test_aspect_runtime_builder.py`.
- Secondary evidence:
  - scan des strings libres dans `backend/app/domain/astrology`.
- Static scans alone are not sufficient for this story because:
  - les fixtures doivent prouver que le runtime enrichi est produit depuis les aspects calcules.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/generated/aspect-runtime-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/generated/aspect-runtime-after.md`
- Expected invariant:
  - les couples aspect/participants/orbes restent identiques; seuls les champs runtime enrichis sont ajoutes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Donnees runtime aspect | `backend/app/domain/astrology/runtime` | `backend/app/domain/prediction` |
| Evaluation de force aspect | `backend/app/domain/astrology/interpretation` | services API, frontend, scoring produit |
| Resolution des orbes | `backend/app/domain/astrology/calculators/aspects.py` | nouveau resolver concurrent |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune raison libre ni exception wildcard n'est autorisee.

## 4f. Contract Shape

- Contract type:
  - Python runtime data classes / Pydantic-compatible models.
- Fields:
  - `aspect.code`, `aspect.family`, `aspect.angle`;
  - `participants.planet_a`, `participants.planet_b`;
  - `orb.exact`, `orb.max`, `orb.ratio`, `orb.strength_level`;
  - `phase.type`;
  - `interpretation.default_valence`, `interpretation.interpretive_valence`, `interpretation.energy_type`;
  - `metadata.is_major`, `metadata.is_exact`, `metadata.is_tight`;
  - `strength.normalized_score`, `strength.level`, `strength.reasons`.
- Required fields:
  - `aspect`, `participants`, `orb`, `metadata`, `strength`.
- Optional fields:
  - `phase`, `interpretation`.
- Status codes:
  - none.
- Serialization names:
  - snake_case stable.
- Frontend type impact:
  - none direct in this story.
- Generated contract impact:
  - none unless an existing chart schema auto-exposes the runtime.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: les consommateurs sont enrichis dans des stories suivantes.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Runtime before | `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/generated/aspect-runtime-before.md` | Montrer la forme plate actuelle. |
| Runtime after | `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/generated/aspect-runtime-after.md` | Montrer le runtime enrichi. |
| Reason scan | `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/generated/aspect-strength-reason-scan.md` | Prouver l'absence de raisons libres. |

## 4i. Reintroduction Guard

- Guard type: unit tests plus scans cibles.
- Forbidden patterns:
  - `reasons.append("raw_reason")` pour la force aspect;
  - dict runtime aspect concurrent hors `runtime/aspect_runtime_data.py`;
  - import `app.domain.prediction` depuis `app.domain.astrology`.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/natal_calculation.py` - `AspectResult` expose un contrat plat avec `aspect_code`, participants et orbes.
- Evidence 2: `backend/app/domain/astrology/runtime/house_runtime_data.py` - `HouseRuntimeData` fournit le precedent de runtime riche.
- Evidence 3: `backend/app/domain/astrology/interpretation/house_strength.py` - `HouseStrengthEvaluator` fournit le precedent d'evaluateur typed.
- Evidence 4: `backend/app/domain/astrology/calculators/aspects.py` - `resolve_orb` et `calculate_major_aspects` produisent deja `orb_max`.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `AspectRuntimeData` existe et porte les dimensions aspect, participants, orbe, phase, interpretation et metadata.
- `AspectStrengthEvaluator` produit `normalized_score`, `level`, `is_exact`, `is_tight` et `reasons`.
- `AspectStrengthReason` enumere les raisons major/minor/advanced, orbe,
  luminaire, angle, paire transpersonnelle et phase.
- Les tests prouvent que les raisons ne sont pas des strings libres.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne doit pas importer prediction.
  - `RG-096` - les contrats de force astrologique doivent rester enumérés et normalisés.
  - `RG-097` - les orbes resolus par systeme restent la base du calcul `orb.max`.
- Non-applicable invariants:
  - `RG-091` a `RG-094` - referentiels et runtime maisons non modifies.
- Required regression evidence:
  - tests unitaires strength/runtime aspect;
  - scans anti-import prediction;
  - snapshots before/after.
- Allowed differences:
  - ajout de champs runtime enrichis.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `AspectRuntimeData` expose le contrat canonique aspect/participants/orb/metadata/strength. | `pytest -q tests/unit/domain/astrology/test_aspect_runtime_builder.py`. |
| AC2 | `AspectStrengthEvaluator` calcule `normalized_score`. | `pytest -q tests/unit/domain/astrology/test_aspect_strength.py`. |
| AC3 | `AspectStrengthReason` couvre les raisons enumerees sans strings libres. | `pytest -q tests/unit/domain/astrology/test_aspect_strength.py` + scan des `reasons`. |
| AC4 | Les aspects detectes avant/apres restent identiques. | `pytest -q tests/unit/domain/astrology/test_aspect_runtime_builder.py` + artefacts before/after. |
| AC5 | `domain/astrology` ne depend pas de `domain/prediction`. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir les contrats runtime aspect (AC: AC1, AC3)
  - [ ] Ajouter `backend/app/domain/astrology/runtime/aspect_runtime_data.py`.
  - [ ] Ajouter les enums et contrats strength sous `backend/app/domain/astrology/interpretation`.

- [ ] Task 2 - Implementer l'evaluateur de force (AC: AC2, AC3)
  - [ ] Reutiliser les seuils `exact_orb_deg`, `strong_ratio`, `moderate_ratio` issus des profils.
  - [ ] Calculer `normalized_score` et `level` sans seuil produit.

- [ ] Task 3 - Brancher un builder runtime aspect (AC: AC1, AC4)
  - [ ] Construire le runtime depuis `AspectResult` et les donnees de reference disponibles.
  - [ ] Garder la detection d'aspects existante intacte.

- [ ] Task 4 - Ajouter preuves et guards (AC: AC3, AC4, AC5)
  - [ ] Capturer les artefacts before/after.
  - [ ] Ajouter les tests et scans anti-regression.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/domain/astrology/calculators/aspects.py` pour les orbes resolus.
  - `HouseStrengthEvaluator` comme precedent de structure, pas par heritage artificiel.
  - `HouseRuntimeData` comme precedent de shape, pas comme classe parente.
- Do not recreate:
  - un resolver d'orbes;
  - un second score produit;
  - des raisons sous forme de strings libres.
- Shared abstraction allowed only if:
  - elle sert explicitement les contrats astrologiques house et aspect sans dependance prediction.

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
- `reasons.append("raw_reason")` pour les aspects
- `dict[str, Any]` comme contrat runtime aspect canonique

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Runtime aspect | `backend/app/domain/astrology/runtime` | DTO plats ad hoc |
| Force aspect | `backend/app/domain/astrology/interpretation` | scoring prediction |
| Orbes | `backend/app/domain/astrology/calculators/aspects.py` | nouveau resolver |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/interpretation/house_strength_contracts.py`
- `backend/tests/unit/domain/astrology/test_house_strength.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py` - nouveau contrat runtime.
- `backend/app/domain/astrology/runtime/__init__.py` - export canonique.
- `backend/app/domain/astrology/interpretation/aspect_strength.py` - evaluateur.
- `backend/app/domain/astrology/interpretation/aspect_strength_contracts.py` - enums et contrats.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py` - assemblage runtime.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_strength.py` - evaluation force.
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py` - integration runtime.
- `backend/app/tests/unit/test_astrology_prediction_boundary.py` - frontiere astrology/prediction.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - aucun impact UI dans cette story.
- `backend/app/domain/prediction/**` - aucun changement produit.

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
pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
rg -n "reasons\\.append\\(\"|AspectStrengthRuntimeData\\(.*reasons=\\[" app/domain/astrology -g "*.py"
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: le runtime aspect diverge des aspects detectes.
  - Guardrail: snapshot before/after des aspects.
- Risk: les raisons libres reviennent.
  - Guardrail: enum + scan cible.
- Risk: le domaine astrology importe prediction.
  - Guardrail: `RG-095` et test de frontiere.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, compatibility, legacy, migration-only, shim, alias, TODO, or hidden residual work.
- Respecter l'AGENTS.md: toute commande Python doit etre executee apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- Demande utilisateur du 2026-05-14 - priorites `Canonical Aspect Runtime`, `Aspect Strength Evaluator`, `AspectRuntimeReason enum`.
- `backend/app/domain/astrology/natal_calculation.py` - contrat `AspectResult` actuel.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - precedent runtime maison.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
