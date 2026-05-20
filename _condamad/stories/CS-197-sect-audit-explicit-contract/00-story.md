# Story CS-197 sect-audit-explicit-contract: Auditer la secte astrologique et exposer un contrat explicite

Status: ready-to-dev

## 1. Objective

Faire de la secte astrologique natale un contrat complet, tracable et testable,
au lieu d'un simple detail interne reduit a `"day"` ou `"night"`. La story doit
auditer `SectCalculator`, formaliser le resultat de secte du theme sous forme
de `ChartSectResult`, puis exposer ce contrat chart-level dans les donnees de
dignites de `NatalResult` et dans le JSON public `dignities.sect`, sans recalcul
dans la couche de projection.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-20, `CS-197 - Sect audit & explicit contract`.
- Reason for change: le runtime actuel determine deja la secte depuis les
  regles d'horizon, mais le resultat public ne documente ni la position du
  Soleil par rapport a l'horizon, ni la base de calcul, ni le systeme de
  reference utilise.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dignities`
- In scope:
  - auditer et renforcer `SectCalculator`;
  - ajouter ou renforcer le contrat chart-level `ChartSectResult`;
  - exposer au minimum `chart_sect`, `sun_horizon_position`,
    `sun_above_horizon`, `calculation_basis` et `reference_system`;
  - propager un seul `ChartSectResult` via le scoring des dignites,
    `NatalResult` et `services/chart/json_builder.py`;
  - couvrir les cas jour, nuit, Soleil absent et regles horizon absentes;
  - ajouter des preuves persistantes dans le dossier de story.
- Out of scope:
  - normaliser la condition de secte par planete, reservee a CS-198;
  - ajouter `PlanetSectCondition`, `planet_sect_condition` ou une exposition
    JSON par planete;
  - changer les regles astrologiques de secte, triplicite, hayz ou
    out_of_sect;
  - modifier les tables de reference si les regles d'horizon existantes
    suffisent;
  - modifier le frontend React;
  - generer du texte narratif, des prompts ou une interpretation LLM;
  - recalculer les dignites dans `json_builder.py`.
- Explicit non-goals:
  - ne pas remplacer la source de verite runtime `above_horizon` /
    `below_horizon` par une constante locale;
  - ne pas ajouter de fallback silencieux si le Soleil ou les regles horizon
    manquent;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`,
    `RG-122` et `RG-123`;
  - ne pas changer les contrats deja livres par CS-191 a CS-196 hors ajout de
    champs de secte explicitement documente.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story transforme une valeur runtime deja calculee en
  contrat explicite tout en preservant les regles de calcul et les contrats
  natals existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `SectCalculator` retourne un objet de contrat au lieu d'une chaine brute;
  - le resultat de dignites conserve un seul `ChartSectResult` calcule une fois
    pour le theme;
  - le JSON public `dignities.sect` doit devenir le contrat chart-level
    `ChartSectResult` serialise, avec les champs minimaux demandes;
  - les scores, breakdowns, profils conditionnels, signaux, conditions
    avancees, dominantes et adaptateur interpretatif ne doivent pas changer hors
    propagation du contrat de secte;
  - aucune route, methode HTTP ou status code n'est ajoute.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le contrat public existant doit rester strictement
  `dignities.sect: string`; dans ce cas, bloquer avant implementation au lieu
  d'ajouter un second champ concurrent comme fallback.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | la secte doit etre prouvee depuis les regles runtime d'horizon, pas depuis une constante locale. |
| Baseline Snapshot | yes | le payload public `dignities.sect` change de forme; un avant/apres est requis. |
| Ownership Routing | no | la story reste dans un domaine et ne deplace pas d'owner. |
| Allowlist Exception | no | aucun fallback, alias ou exception n'est autorise. |
| Contract Shape | yes | `ChartSectResult`, les donnees de dignites de `NatalResult` et le JSON public `dignities.sect` ont une forme chart-level explicite. |
| Batch Migration | no | aucune migration par lots de consommateurs n'est effectuee. |
| Reintroduction Guard | yes | les constantes locales de maisons horizon et les projections qui recalculent la secte doivent etre bloquees. |
| Persistent Evidence | yes | les audits, snapshots et resultats de validation doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.dignity_reference.accidental_rules`
    avec les regles actives `above_horizon` et `below_horizon`, leurs
    `condition_schema_code` et leurs `house_codes`.
- Secondary evidence:
  - tests de `SectCalculator`, tests du service de scoring des dignites, tests
    du contrat `NatalResult`, tests de projection `json_builder.py`, scans
    cibles anti-constantes locales.
- Static scans alone are not sufficient for this story because:
  - la regression critique est un calcul de secte qui semble present dans le
    code mais ne lit plus les regles runtime effectives.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-after.json`
- Expected invariant:
  - les champs de dignites par planete et leurs scores restent stables; seul le
    contrat chart-level de secte devient explicite et explique la base de calcul.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no file, route or package ownership is moved by this story.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload public `dignities.sect`.
- Required domain contracts:
  - `ChartSectResult`
- `ChartSectResult` required fields:
  - `chart_sect: str` - allowed values exactly `day` or `night`;
  - `sun_horizon_position: str` - allowed values exactly `above_horizon` or
    `below_horizon`;
  - `sun_above_horizon: bool`;
  - `calculation_basis: str` - explicit non-empty basis such as
    `sun_house_horizon_rule`;
  - `reference_system: str` - explicit non-empty runtime reference identifier,
    for example `traditional` when sourced from the dignity rule system.
- Fields:
  - `ChartSectResult.chart_sect`;
  - `ChartSectResult.sun_horizon_position`;
  - `ChartSectResult.sun_above_horizon`;
  - `ChartSectResult.calculation_basis`;
  - `ChartSectResult.reference_system`.
- Required fields:
  - all fields listed above are required when `ChartSectResult` is emitted.
- Optional fields:
  - none for `ChartSectResult`.
- Status codes:
  - no HTTP endpoint or API status code is changed by this story.
- Frontend type impact:
  - none in this story; frontend TypeScript contracts are out of scope.
- Generated contract impact:
  - conditional; if the chart JSON response shape is modeled by OpenAPI or a
    generated client, the before/after evidence must document only the
    `dignities.sect` shape change.
  - no route path, HTTP method or status code is changed.
- Serialization names:
  - public JSON keeps the top-level path `dignities.sect`;
  - `dignities.sect` becomes the serialized `ChartSectResult` object;
  - no per-planet sect condition is added in this story.
- Compatibility decision:
  - do not add `sect_legacy`, `sect_code`, `chart_sect_code` or duplicate
    compatibility aliases unless the user explicitly changes this story.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no multi-batch migration is authorized.

## 4h. Persistent Evidence Artifacts

- Required evidence directory:
  - `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/`
- Required artifacts:
  - `sect-contract-before.json` - minimal pre-change snapshot of
    `dignities.sect`, one day case and one night case.
  - `sect-contract-after.json` - matching post-change snapshot with the new
    fields.
  - `sect-contract-validation.md` - commands run, result summary, and any
    bounded skipped command with reason.

| Artifact | Path | Purpose |
|---|---|---|
| before snapshot | `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-before.json` | Capture the current `dignities.sect` shape before implementation. |
| after snapshot | `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-after.json` | Prove the new explicit sect object and allowed JSON delta. |
| validation summary | `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-validation.md` | Persist commands, scan results and allowed hits. |

## 4i. Reintroduction Guard

- Guard target:
  - prevent local horizon mappings, silent fallback sect values and projection
    layer recalculation.
- Required guard evidence:
  - tests fail when `above_horizon` or `below_horizon` runtime rules are missing;
  - scan proves no new local tuple/list/set such as `(7, 8, 9, 10, 11, 12)` is
    introduced under `backend/app/domain/astrology/dignities` or
    `backend/app/services/chart`;
  - scan proves `json_builder.py` serializes a precomputed sect contract and
    does not instantiate `SectCalculator`.
- Executable evidence:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/domain/astrology/test_sect_calculator.py
cd ..
rg -n "SectCalculator" backend/app/services/chart/json_builder.py
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"
```

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/dignities/sect_calculator.py` -
  `SectCalculator.calculate()` returns only `"day"` or `"night"` from
  `above_horizon` / `below_horizon` runtime rules.
- Evidence 2: `backend/app/domain/astrology/dignities/contracts.py` -
  `PlanetDignityResult` exposes `sect: str` but no structured chart sect
  contract.
- Evidence 3: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult.dignities` is a list of `PlanetDignityResult`, so no chart-level
  sect object is currently attached to the dignity aggregate.
- Evidence 4: `backend/app/services/chart/json_builder.py` -
  `_serialize_dignities()` emits `dignities.sect` as a string copied from the
  latest planet dignity result.
- Evidence 5: `backend/tests/unit/domain/astrology/test_sect_calculator.py` -
  tests cover day, night and missing Sun, but do not assert an explainable
  contract.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants
  consulted before story scope was finalized.

## 6. Target State

After implementation:

- `SectCalculator` exposes a deterministic, typed chart sect result sourced
  from runtime horizon rules.
- `ChartSectResult` carries the chart-level sect, Sun horizon position,
  boolean horizon state, calculation basis and reference system.
- `NatalResult` and `build_chart_json()` expose `dignities.sect` as the
  serialized chart-level `ChartSectResult` object.
- CS-197 prepares the chart-level contract that CS-198 can consume later for
  per-planet sect condition normalization.
- Missing Sun or missing horizon runtime rules remain hard failures, not
  fallbacks.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - DB-backed/runtime reference data must not be recreated as local
    constants.
  - `RG-112` - astrology constants and fallbacks must not return in backend
    astrology.
  - `RG-118` - dignity calculators must remain pure, runtime-backed and free of
    DB/API/services/prediction/LLM dependencies.
  - `RG-119` - condition profiles must remain derived from dignity results, not
    a second sect engine.
  - `RG-120` - condition signals must not encode sect thresholds or prompts
    locally.
  - `RG-122` - advanced conditions must continue to consume factual dignity
    outputs without local sect recalculation.
  - `RG-123` - interpretation adapter must consume facts and must not become a
    sect calculator.
  - `RG-124` - new invariant from this story protecting explicit sect
    contract.
- Non-applicable invariants:
  - `RG-121` - dominance engine is not modified by this story.
- Required regression evidence:
  - targeted pytest commands listed in the validation plan;
  - before/after JSON snapshots;
  - scans for local horizon constants, forbidden imports and projection
    recalculation.
- Allowed differences:
  - `dignities.sect` changes from string to explicit object;
  - no per-planet sect condition field is added by this story.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `SectCalculator` returns chart sect fields. | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` |
| AC2 | Missing Sun or horizon rules raise explicit errors. | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` |
| AC3 | Dignity results consume one shared chart-level `ChartSectResult`; no planet recalculates chart sect. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` |
| AC4 | `NatalResult` exposes explicit sect without removing fields. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` |
| AC5 | `build_chart_json()` serializes the precomputed `dignities.sect` object. | Evidence profile: projection test; `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC6 | Chart result persistence stores the explicit sect contract. | Evidence profile: service test; `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC7 | No local horizon constants, per-planet sect condition contract or legacy sect alias is introduced. | Horizon constant scan plus `rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"` plus `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"` |
| AC8 | Before/after evidence documents the allowed JSON delta. | `rg -n "chart_sect|sun_horizon_position" _condamad/stories/CS-197-sect-audit-explicit-contract/evidence` |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline and audit current sect flow (AC: AC1, AC5, AC8)
  - [ ] Subtask 1.1 - Create `evidence/sect-contract-before.json` with current
    `dignities.sect` shape for one day case and one night case.
  - [ ] Subtask 1.2 - Record which runtime rules currently feed
    `SectCalculator`.

- [ ] Task 2 - Define explicit chart-level sect contract (AC: AC1, AC3, AC4)
  - [ ] Subtask 2.1 - Add `ChartSectResult` in the canonical dignity contracts
    module or a narrowly scoped sibling module.
  - [ ] Subtask 2.2 - Ensure fields are typed, immutable where consistent with
    existing dataclass contracts, and documented in French docstrings.

- [ ] Task 3 - Update calculation and orchestration (AC: AC1, AC2, AC3)
  - [ ] Subtask 3.1 - Make `SectCalculator` return or expose the full chart
    sect result from runtime rules.
  - [ ] Subtask 3.2 - Pass the same chart sect result through
    `PlanetDignityScoringService` without duplicate calculation or per-planet
    sect recomputation.
  - [ ] Subtask 3.3 - Preserve explicit errors for missing Sun and missing
    runtime horizon rules.

- [ ] Task 4 - Expose the contract through natal and JSON outputs (AC: AC4, AC5, AC6)
  - [ ] Subtask 4.1 - Attach the sect contract to the dignity result path in
    `NatalResult`.
  - [ ] Subtask 4.2 - Update `_serialize_dignities()` to project the existing
    sect result without importing or instantiating `SectCalculator`.
  - [ ] Subtask 4.3 - Update chart result service tests for the new persisted
    payload shape.

- [ ] Task 5 - Add guards, tests and persistent evidence (AC: AC1, AC2, AC5, AC7, AC8)
  - [ ] Subtask 5.1 - Extend day/night/negative sect tests.
  - [ ] Subtask 5.2 - Extend contract and projection tests for the new shape.
  - [ ] Subtask 5.3 - Save `sect-contract-after.json` and
    `sect-contract-validation.md`.
  - [ ] Subtask 5.4 - Run validation commands after activating `.venv`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetDignityReferenceSet.accidental_rules` for horizon rules.
  - `DignityConditionValue` / `AccidentalDignityRuleReferenceData` as the
    runtime condition source.
  - Existing `PlanetDignityInput.house_number` for Sun house lookup.
  - Existing `PlanetDignityScoringService` orchestration for one sect
    calculation per chart.
- Do not recreate:
  - local mappings of horizon houses;
  - a second sect calculator in condition, advanced condition, dominance,
    interpretation adapter or JSON builder;
  - per-planet sect condition normalization before CS-198;
  - a parallel public `sect_code` field as compatibility surface.
- Shared abstraction allowed only if:
  - it removes duplicate sect result construction and remains inside
    `backend/app/domain/astrology/dignities`.

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

- local constants equivalent to above-horizon houses `[7, 8, 9, 10, 11, 12]`
  or below-horizon houses `[1, 2, 3, 4, 5, 6]` in application code;
- `PlanetSectCondition`, `planet_sect_condition` or equivalent per-planet sect
  condition contracts in this story;
- `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code` public aliases;
- `SectCalculator` import in `backend/app/services/chart/json_builder.py`;
- imports from `app.infra`, `app.api`, `app.services`, `app.domain.prediction`
  or LLM providers inside `backend/app/domain/astrology/dignities/**`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Sect calculation from Sun horizon | `backend/app/domain/astrology/dignities/sect_calculator.py` | `json_builder.py`, condition, dominance, advanced conditions |
| Chart-level sect DTO contract | `backend/app/domain/astrology/dignities/contracts.py` or dedicated dignity contract module | API routes, services, frontend |
| Runtime horizon rule source | `AstrologyRuntimeReference.dignity_reference.accidental_rules` | hardcoded local mappings |
| Public JSON projection | `backend/app/services/chart/json_builder.py` | any domain calculator |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: conditional
- Reason: the story changes the public chart JSON shape at `dignities.sect`,
  but does not add or modify any route, method or status code.
- Required generated-contract evidence:
  - if OpenAPI or a generated client models `dignities.sect`, capture the
    before/after change and document that only this field shape changed;
  - if the chart JSON remains dynamically shaped and not represented by a
    generated schema, record that fact in
    `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-validation.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/dignities/contracts.py` - add the chart-level
  sect contract.
- `backend/app/domain/astrology/dignities/sect_calculator.py` - produce the
  explicit chart sect result.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  propagate one chart sect result through dignity scoring.
- `backend/app/domain/astrology/natal_calculation.py` - expose the sect
  contract through natal dignity data.
- `backend/app/services/chart/json_builder.py` - serialize the contract without
  recalculation.

Likely tests:

- `backend/tests/unit/domain/astrology/test_sect_calculator.py` - day/night and
  negative contract cases.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
  - propagation into dignity results.
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py` - DTO shape.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - natal
  contract exposure.
- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON shape.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted payload.

Files not expected to change:

- `frontend/**` - no UI change in this story.
- per-planet sect condition contracts or JSON fields - reserved for CS-198.
- `backend/app/domain/astrology/condition/**` - condition profiles consume
  dignity results and must not recalculate sect.
- `backend/app/domain/astrology/advanced_conditions/**` - advanced conditions
  must not become sect owner.
- `backend/app/domain/astrology/interpretation_adapters/**` - adapter consumes
  facts only.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes are not allowed in this story.

## 20. Validation Plan

Run from repository root or `backend` as indicated, always after activating the
venv:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py `
  backend/tests/unit/domain/astrology/test_dignity_contracts.py `
  backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py `
  backend/app/tests/unit/test_chart_result_service.py
ruff format .
ruff check .
rg -n "SectCalculator" backend/app/services/chart/json_builder.py
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"
Test-Path _condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-before.json
Test-Path _condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-after.json
Test-Path _condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-validation.md
```

Allowed scan results must be recorded in
`_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/sect-contract-validation.md`.

## 21. Regression Risks

- Risk: `dignities.sect` changes shape and an existing consumer expects a
  string.
  - Guardrail: chart JSON test and before/after snapshot must make the change
    explicit; string compatibility requires a new user decision before code changes.
- Risk: local horizon constants replace runtime rules.
  - Guardrail: `SectCalculator` negative tests and scans for local house lists.
- Risk: JSON builder recalculates sect during projection.
  - Guardrail: scan for `SectCalculator` in `json_builder.py` and projection
    tests using precomputed data.
- Risk: CS-197 expands into per-planet sect condition normalization.
  - Guardrail: `PlanetSectCondition` and `planet_sect_condition` remain
    forbidden in this story and are reserved for CS-198.
- Risk: condition or interpretation layers become a second sect owner.
  - Guardrail: forbidden import/recalculation scans and non-goals tied to
    `RG-119`, `RG-122` and `RG-123`.

## 22. Dev Agent Instructions

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
  TODO, or hidden residual in-domain work.

## 23. References

- `backend/app/domain/astrology/dignities/sect_calculator.py` - current sect
  calculation owner.
- `backend/app/domain/astrology/dignities/contracts.py` - current dignity DTO
  contracts.
- `backend/app/services/chart/json_builder.py` - current public projection of
  `dignities.sect`.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` -
  dignity engine context.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` -
  hayz/out_of_sect downstream context.
- `_condamad/stories/regression-guardrails.md` - shared invariants consulted.
