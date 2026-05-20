# Story CS-198 planet-sect-condition-normalization: Normaliser la condition de secte par planete

Status: done

## 1. Objective

Transformer la condition de secte par planete en contrat explicite, stable et
testable, derive une seule fois depuis le `ChartSectResult` livre par CS-197 et
depuis les donnees runtime de secte planetaire. La story expose cette condition
sous chaque entree `dignities.planets[planet_code].sect_condition` sans changer
les regles astrologiques, sans recalculer la secte globale du theme et sans
introduire de logique de hayz, rejoicing ou conditions avancees.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: demande utilisateur du 2026-05-20, follow-up CS-197
  `sect-audit-explicit-contract`.
- Reason for change: apres exposition du contrat chart-level
  `dignities.sect`, les couches aval doivent disposer d'un fait normalise par
  planete au lieu d'inferer `in_sect`, `out_of_sect` ou des statuts variables
  depuis les breakdowns accidentels, les conditions avancees ou des regles
  locales.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dignities`
- In scope:
  - ajouter le contrat `PlanetSectCondition` dans le module canonique des
    contrats de dignites;
  - ajouter un evaluateur pur de condition de secte planetaire sous
    `backend/app/domain/astrology/dignities`;
  - deriver une condition par planete depuis un seul `ChartSectResult`, les
    donnees runtime disponibles et les profils ou regles runtime de secte
    planetaire;
  - attacher la condition au `PlanetDignityResult`;
  - projeter `sect_condition` sous chaque planete dans le JSON public;
  - couvrir les cas theme diurne, theme nocturne, planete diurne, planete
    nocturne, Mercure ou planete commune/variable, et planete sans profil
    runtime;
  - produire les snapshots et preuves persistantes de validation.
- Out of scope:
  - modifier le calcul chart-level `ChartSectResult` livre par CS-197;
  - modifier les regles astrologiques de secte;
  - recalculer hayz, rejoicing, heliacal, conditions avancees ou dominantes;
  - modifier les tables DB si les informations runtime existent deja;
  - modifier le frontend React;
  - generer une interpretation narrative, des prompts ou du LLM;
  - changer une route, methode HTTP ou status code.
- Explicit non-goals:
  - ne pas creer un second moteur de secte dans `advanced_conditions`,
    `condition`, `dominance`, `interpretation_adapters` ou `json_builder.py`;
  - ne pas ajouter de fallback silencieux quand la secte intrinseque d'une
    planete manque;
  - ne pas hardcoder de listes locales de planetes diurnes, nocturnes,
    communes ou neutres;
  - ne pas dupliquer le `ChartSectResult` complet dans chaque planete;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`,
    `RG-122`, `RG-123`, `RG-124` et `RG-125`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story expose un fait derive du runtime et d'un contrat
  existant, sans changer la doctrine de calcul ni les proprietaires de regles
  astrologiques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `ChartSectResult` reste la seule source de verite pour la secte globale du
    theme;
  - `PlanetDignityResult` peut recevoir un `PlanetSectCondition` explicite;
  - le JSON public ajoute uniquement `sect_condition` sous chaque entree
    `dignities.planets[planet_code]`;
  - les scores, breakdowns, conditions avancees, dominantes et signaux
    existants doivent rester stables sauf bug de double calcul documente dans
    l'evidence;
  - aucune route, methode HTTP ou status code n'est modifie.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le runtime ne contient aucune source explicite et
  testable permettant d'identifier la secte intrinseque des planetes; dans ce
  cas, documenter le blocker au lieu de coder un mapping local.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | la condition de secte planetaire doit venir du runtime et du `ChartSectResult`, pas de constantes locales. |
| Baseline Snapshot | yes | la forme publique de chaque entree `dignities.planets[planet_code]` change. |
| Ownership Routing | yes | la story doit figer les proprietaires canoniques pour eviter le recalcul dans les couches aval. |
| Allowlist Exception | yes | les seuls resultats de scan toleres doivent etre exacts, documentes et lies au runtime; aucun fallback, alias ou shim n'est autorise. |
| Contract Shape | yes | `PlanetSectCondition` a une forme obligatoire et des valeurs autorisees. |
| Batch Migration | no | aucune migration par lots de consommateurs n'est autorisee. |
| Reintroduction Guard | yes | les recalculs locaux, aliases legacy et imports interdits doivent etre bloques. |
| Persistent Evidence | yes | snapshots, scans et validations doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config/runtime object: `AstrologyRuntimeReference` charge pendant les
    tests, en particulier `AstrologyRuntimeReference.dignity_reference` et la
    source runtime typée qui porte la secte intrinseque planetaire;
  - `ChartSectResult` deja produit par CS-197;
  - `AstrologyRuntimeReference.dignity_reference`;
  - toute donnee runtime existante permettant de classifier la secte
    intrinseque d'une planete, par exemple profils, regles accidentelles ou
    conditions runtime explicites liees a `in_sect`, `out_of_sect`,
    `diurnal`, `nocturnal`, `common`, `neutral` ou equivalent.
- Secondary evidence:
  - tests unitaires du contrat `PlanetSectCondition`;
  - tests du service de scoring des dignites;
  - tests de projection JSON;
  - scans anti-recalcul dans `json_builder.py`, `condition`,
    `advanced_conditions`, `dominance` et `interpretation_adapters`.
- Static scans alone are not sufficient for this story because:
  - une regression peut conserver des noms corrects tout en appliquant une
    logique locale incorrecte pour comparer secte du theme et secte de la
    planete.
- Blocker rule:
  - si l'inspection runtime ne trouve pas de source explicite de secte
    intrinseque planetaire, l'implementation doit s'arreter et documenter le
    blocker dans `planet-sect-validation.md`; aucun mapping local ne peut etre
    ajoute pour debloquer la story.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-after.json`
- Expected invariant:
  - `dignities.sect` reste conforme au contrat CS-197;
  - les scores et breakdowns des dignites restent stables;
  - chaque planete recoit une condition de secte explicite;
  - aucun consommateur aval ne recalcule la condition.
- Allowed differences:
  - ajout de `sect_condition` sous chaque entree de
    `dignities.planets[planet_code]`;
  - aucune suppression ou renommage de champ existant.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | `json_builder.py`, condition, advanced conditions, dominance, adapters |
| Planet sect condition calculation | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | downstream projection or adapter layers |
| Planet sect DTO | `backend/app/domain/astrology/dignities/contracts.py` | API routes, frontend, tests-only helper modules |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculators |
| Runtime planet sect source | `AstrologyRuntimeReference.dignity_reference` or typed runtime reference | local constants, fixtures-only maps, frontend |

- Validation evidence:
  - tests prove `PlanetDignityScoringService` computes the condition once per
    planet;
  - scans prove downstream layers do not import the new calculator or
    `SectCalculator`.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/tests/factories/astrology_runtime_reference_factory.py` | existing fixture keys | Mirrors runtime vocabulary. | Permanent for fixture data only. |
| `planet-sect-validation.md` | recorded allowed scan hits | Each hit must prove no local sect engine or public alias. | Permanent as story evidence. |

## 4f. Contract Shape

- Contract type:
  - immutable domain DTO and public JSON object under
    `dignities.planets[planet_code].sect_condition`.
- Required domain contracts:
  - `PlanetSectCondition`
- Fields:
  - `planet_code: str`
  - `chart_sect: str`
  - `intrinsic_sect: str`
  - `planet_sect_condition: str`
  - `is_in_sect: bool`
  - `is_out_of_sect: bool`
  - `calculation_basis: str`
  - `reference_system: str`
- Required fields:
  - all fields are required.
- Optional fields:
  - none.
- Allowed `chart_sect` values:
  - `day`
  - `night`
- Allowed `intrinsic_sect` values:
  - `diurnal`
  - `nocturnal`
  - `common`
  - `neutral`
  - `unknown`
- Allowed `planet_sect_condition` values:
  - `in_sect`
  - `out_of_sect`
  - `neutral_to_sect`
  - `variable_by_condition`
  - `unknown`
- Status codes:
  - no HTTP endpoint or API status code is changed.
- Serialization names:
  - public JSON field name is exactly `sect_condition`;
  - no parallel `sect_code`, `planet_sect_code`, `sect_legacy` or
    `legacy_sect` field is allowed.
- Public JSON example:

```json
{
  "sect_condition": {
    "planet_code": "mars",
    "chart_sect": "night",
    "intrinsic_sect": "nocturnal",
    "planet_sect_condition": "in_sect",
    "is_in_sect": true,
    "is_out_of_sect": false,
    "calculation_basis": "chart_sect_vs_planet_intrinsic_sect",
    "reference_system": "traditional"
  }
}
```

- Frontend type impact:
  - no frontend code change in this story; any generated or hand-written
    frontend type update requires a separate story.
- Generated contract impact:
  - conditional; if chart JSON is represented in OpenAPI or generated clients,
    evidence must show only the additive `sect_condition` delta.
- Compatibility decision:
  - no compatibility alias, fallback field or legacy projection is allowed.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no multi-batch migration is authorized.

## 4h. Persistent Evidence Artifacts

- Required evidence directory:
  - `_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/`
- Required artifacts:
  - `planet-sect-before.json` - pre-change chart JSON excerpt covering
    `dignities.sect` and `dignities.planets`.
  - `planet-sect-after.json` - matching post-change excerpt proving
    `sect_condition` per planet and stable existing scores.
  - `planet-sect-validation.md` - commands run, scan results, allowed hits,
    runtime source found for planet sect metadata, and any explicit blocker.

| Artifact | Path | Purpose |
|---|---|---|
| before snapshot | `evidence/planet-sect-before.json` | Capture the current planet dignity payload before adding `sect_condition`. |
| after snapshot | `evidence/planet-sect-after.json` | Prove the additive JSON delta and stable CS-197 `dignities.sect`. |
| validation summary | `evidence/planet-sect-validation.md` | Persist tests, scans, runtime source assessment and blocker notes. |

## 4i. Reintroduction Guard

- Guard target:
  - prevent local planet sect mappings, chart sect recalculation, hayz logic,
    legacy aliases and downstream ownership drift.
- Required guard evidence:
  - `json_builder.py` does not import `SectCalculator`,
    `PlanetSectConditionCalculator` or `planet_sect_condition_calculator`;
  - downstream domains do not import the calculator or create local sect
    condition engines;
  - forbidden legacy field names are absent;
  - dignity domain remains free of DB/API/services/prediction/LLM imports;
  - scans for horizon house lists and local diurnal/nocturnal planet maps are
    recorded with allowed hits.
- Executable evidence:

```powershell
.\.venv\Scripts\Activate.ps1
rg -n "SectCalculator" backend/app/services/chart/json_builder.py
rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" `
  backend/app/services/chart backend/app/domain/astrology/condition `
  backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|COMMON_PLANETS|NEUTRAL_PLANETS|planet.*diurnal|planet.*nocturnal" `
  backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy" backend/app backend/tests -g "*.py"
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"
```

Allowed scan results must be recorded in
`_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-validation.md`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/dignities/contracts.py` -
  `ChartSectResult` and `PlanetDignityResult.chart_sect` already exist from
  CS-197, but `PlanetSectCondition` does not exist.
- Evidence 2: `backend/app/domain/astrology/dignities/sect_calculator.py` -
  `SectCalculator.calculate()` returns the chart-level `ChartSectResult` from
  runtime horizon rules; CS-198 must consume it and must not change its
  doctrine.
- Evidence 3:
  `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  `PlanetDignityScoringService` computes one chart-level sect result and passes
  it into each `PlanetDignityResult`.
- Evidence 4: `backend/app/services/chart/json_builder.py` -
  `_serialize_dignities()` serializes `dignities.sect` from precomputed data
  and currently emits planet dignity entries without `sect_condition`.
- Evidence 5:
  `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` -
  accidental rules can already read `chart_sect_code` and horizon conditions,
  which must not become the owner of the new normalized per-planet contract.
- Evidence 6: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  `AstrologyRuntimeReference` exposes typed runtime references including
  `dignity_reference` and `planet_natures`; a dedicated planet sect source must
  be verified during implementation before coding the evaluator.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants
  consulted before story scope was finalized; `RG-124` protects the CS-197
  chart-level sect contract.

## 6. Target State

After implementation:

- `PlanetSectCondition` is an immutable typed contract with the exact fields and
  allowed values listed in this story.
- A pure calculator under `backend/app/domain/astrology/dignities` derives one
  condition per planet from `ChartSectResult` and runtime planet sect data.
- `PlanetDignityResult` carries the calculated condition without duplicating
  the whole `ChartSectResult`.
- `json_builder.py` projects `sect_condition` from the precomputed
  `PlanetDignityResult` only.
- Condition profiles, advanced conditions, dominance and interpretation
  adapters receive a stable fact for later consumption without becoming sect
  engines.
- Mercure or any common/variable runtime profile is handled explicitly.
- Missing runtime data produces either an explicit tested `unknown` condition
  or a documented blocker; no silent fallback is allowed.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return in backend
    astrology.
  - `RG-118` - dignity calculators remain pure and runtime-backed.
  - `RG-119` - condition profiles consume dignity results, not a second sect
    engine.
  - `RG-120` - condition signals must not encode sect logic.
  - `RG-122` - advanced conditions must not recalculate sect.
  - `RG-123` - interpretation adapter consumes facts only.
  - `RG-124` - chart-level sect contract from CS-197 remains canonical.
  - `RG-125` - per-planet sect condition must be derived once from
    `ChartSectResult` and runtime planetary sect data.
- Non-applicable invariants:
  - `RG-121` - dominance scoring is not modified by this story except through
    forbidden scans proving it does not become a sect owner.
- Required regression evidence:
  - targeted pytest commands in the validation plan;
  - before/after JSON snapshots;
  - scans for local planet sect constants, forbidden imports, forbidden legacy
    aliases and projection-layer recalculation.
- Allowed differences:
  - additive `sect_condition` object per planet under `dignities.planets`;
  - no score, route, status code, hayz, rejoicing, dominance or interpretation
    behavior change.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `PlanetSectCondition` is a typed immutable dignity contract. | Deterministic test: `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py`. |
| AC2 | Planet sect condition derives from one `ChartSectResult`. | Deterministic test: `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`. |
| AC3 | Diurnal planets are `in_sect` in day charts. | Runtime evidence: loaded config `AstrologyRuntimeReference`; scoring pytest plus validation note. |
| AC4 | Nocturnal planets are `in_sect` in night charts. | Runtime evidence: loaded config `AstrologyRuntimeReference`; scoring pytest plus validation note. |
| AC5 | Diurnal planets are `out_of_sect` in night charts unless runtime says otherwise. | Runtime evidence: loaded config; scoring pytest plus validation note. |
| AC6 | Nocturnal planets are `out_of_sect` in day charts unless runtime says otherwise. | Runtime evidence: loaded config; scoring pytest plus validation note. |
| AC7 | Mercure maps to the runtime-defined common or variable condition. | Runtime evidence: loaded config; scoring pytest plus scan of validation notes. |
| AC8 | Public JSON exposes `sect_condition` per planet. | Projection test: `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC9 | Downstream layers do not import the planet sect calculator. | Static guard: run the calculator-import `rg` command listed in `4i`. |
| AC10 | Before/after evidence documents only the additive JSON delta. | Snapshot evidence: `rg -n "allowed delta|sect_condition" evidence/planet-sect-validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline and runtime source assessment (AC: AC2, AC9, AC10)
  - [ ] Subtask 1.1 - Create
    `_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/`.
  - [ ] Subtask 1.2 - Capture `planet-sect-before.json` from a representative
    chart payload covering `dignities.sect` and `dignities.planets`.
  - [ ] Subtask 1.3 - Document current sect-like data in dignity breakdowns,
    advanced conditions, condition profiles and JSON projection.
  - [ ] Subtask 1.4 - Identify the runtime source for intrinsic planet sect;
    if absent, record the blocker and stop without local constants.

- [ ] Task 2 - Add `PlanetSectCondition` contract (AC: AC1, AC7)
  - [ ] Subtask 2.1 - Add an immutable dataclass in
    `backend/app/domain/astrology/dignities/contracts.py`.
  - [ ] Subtask 2.2 - Add French module/class/function docstrings or comments
    consistent with repository rules.
  - [ ] Subtask 2.3 - Validate required fields and allowed values without
    optional fields or legacy aliases.

- [ ] Task 3 - Implement pure planet sect evaluation (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC9)
  - [ ] Subtask 3.1 - Add
    `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
    or an equally narrow dignity-domain module.
  - [ ] Subtask 3.2 - Consume `PlanetDignityInput`, `ChartSectResult` and the
    runtime reference data only.
  - [ ] Subtask 3.3 - Compare `chart_sect` with intrinsic planet sect; do not
    inspect horizon houses, sign gender, hayz, rejoicing or advanced
    conditions.
  - [ ] Subtask 3.4 - Implement explicit behavior for `common`, `neutral`,
    `unknown` and missing runtime data as tested by AC7.

- [ ] Task 4 - Propagate through dignity scoring (AC: AC2, AC3, AC4, AC5, AC6)
  - [ ] Subtask 4.1 - Update `PlanetDignityScoringService` to compute the
    chart-level `ChartSectResult` once, as today.
  - [ ] Subtask 4.2 - Compute one `PlanetSectCondition` per planet and attach
    it to `PlanetDignityResult`.
  - [ ] Subtask 4.3 - Preserve existing essential and accidental scoring
    outputs unless a double-calculation bug is documented in evidence.

- [ ] Task 5 - Public projection (AC: AC8, AC9, AC10)
  - [ ] Subtask 5.1 - Update `_serialize_dignities()` in
    `backend/app/services/chart/json_builder.py` to serialize
    `result.sect_condition`.
  - [ ] Subtask 5.2 - Do not import `SectCalculator`,
    `PlanetSectConditionCalculator` or any dignity calculator into
    `json_builder.py`.
  - [ ] Subtask 5.3 - Reject incomplete precomputed sect-condition payloads in
    projection tests using the current JSON builder validation style.

- [ ] Task 6 - Tests, scans and persistent evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 6.1 - Extend contract, scoring and JSON builder tests.
  - [ ] Subtask 6.2 - Extend natal result or chart result service tests if the
    serialized persisted payload shape changes.
  - [ ] Subtask 6.3 - Save `planet-sect-after.json`.
  - [ ] Subtask 6.4 - Save `planet-sect-validation.md` with commands, scan
    results, allowed hits and skipped-command justifications.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult` from CS-197 for chart-level sect.
  - Existing `PlanetDignityScoringService` orchestration for per-planet
    dignity results.
  - Existing runtime references, especially
    `AstrologyRuntimeReference.dignity_reference` and any typed runtime planet
    metadata that encodes intrinsic sect.
  - Existing JSON serialization style in `backend/app/services/chart/json_builder.py`.
- Do not recreate:
  - local mappings of diurnal, nocturnal, common or neutral planets;
  - local mappings of above/below horizon houses;
  - duplicate sect logic in advanced conditions, condition profiles, dominance
    or interpretation adapters;
  - duplicate `ChartSectResult` copies inside each planet;
  - compatibility aliases or legacy public fields.
- Shared abstraction allowed only if:
  - it remains inside `backend/app/domain/astrology/dignities`;
  - it consumes typed runtime references;
  - it removes actual duplication without changing calculation ownership.

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

- `sect_legacy`
- `legacy_sect`
- `sect_code`
- `chart_sect_code` as a new public field or DTO alias
- `planet_sect_code`
- `planet_sect_legacy`
- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `COMMON_PLANETS`
- `NEUTRAL_PLANETS`
- local horizon house lists equivalent to `[7, 8, 9, 10, 11, 12]` or
  `[1, 2, 3, 4, 5, 6]`
- `SectCalculator` import in `backend/app/services/chart/json_builder.py`
- `PlanetSectConditionCalculator` import in `backend/app/services/chart/**`,
  `backend/app/domain/astrology/condition/**`,
  `backend/app/domain/astrology/advanced_conditions/**`,
  `backend/app/domain/astrology/dominance/**` or
  `backend/app/domain/astrology/interpretation_adapters/**`
- imports from `app.infra`, `app.api`, `app.services`,
  `app.domain.prediction`, OpenAI clients or LLM prompt builders inside
  `backend/app/domain/astrology/dignities/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | JSON builder, advanced conditions, condition profiles, adapters |
| Planet sect condition calculation | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | condition profiles, dominance, adapters, JSON builder |
| Planet sect DTO | `backend/app/domain/astrology/dignities/contracts.py` | API routes, frontend, fixtures-only helpers |
| Runtime planet sect data | `AstrologyRuntimeReference` typed runtime references | local constants, test-only maps, frontend |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculators |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: conditional
- Reason: the story changes the public chart JSON shape under
  `dignities.planets[planet_code]`, but does not add or modify any route,
  method or status code.
- Required generated-contract evidence:
  - if OpenAPI or a generated client models chart JSON, capture and document
    that only `sect_condition` is added under planet dignities;
  - if chart JSON remains dynamically shaped and not represented by generated
    schemas, record that fact in `planet-sect-validation.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/dignities/contracts.py` - add
  `PlanetSectCondition` and attach it to `PlanetDignityResult`.
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
  - add pure evaluator if runtime source exists.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  compute and attach one condition per planet.
- `backend/app/domain/astrology/natal_calculation.py` - propagate the updated
  dignity result shape if contract serialization or persistence requires it.
- `backend/app/services/chart/json_builder.py` - serialize precomputed
  `sect_condition` without recalculation.

Likely tests:

- `backend/tests/unit/domain/astrology/test_dignity_contracts.py` - contract
  shape and invalid-value cases.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
  - day/night/in/out/common or variable condition cases.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - natal
  contract exposure when the result contract changes.
- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON
  `sect_condition` projection.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted payload if
  chart result serialization changes.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` -
  runtime loading coverage for planet sect metadata without schema changes.

Files not expected to change:

- `frontend/**` - frontend changes are out of scope.
- `backend/app/domain/astrology/condition/**` - future fact consumption is
  outside this story; sect calculation is forbidden here.
- `backend/app/domain/astrology/advanced_conditions/**` - hayz and advanced
  conditions remain separate.
- `backend/app/domain/astrology/dominance/**` - dominance remains fact consumer
  only.
- `backend/app/domain/astrology/interpretation_adapters/**` - adapters consume
  facts only.
- `backend/migrations/**` - no migration unless runtime data is proven missing
  and the blocker receives explicit user approval.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes are not allowed in this story.

## 20. Validation Plan

Run from repository root or `backend` as indicated, always after activating the
venv:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
ruff format .
ruff check .
rg -n "SectCalculator" backend/app/services/chart/json_builder.py
rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" `
  backend/app/services/chart backend/app/domain/astrology/condition `
  backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|COMMON_PLANETS|NEUTRAL_PLANETS|planet.*diurnal|planet.*nocturnal" `
  backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy" backend/app backend/tests -g "*.py"
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"
Test-Path _condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-before.json
Test-Path _condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-after.json
Test-Path _condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-validation.md
```

Allowed scan results must be recorded in:

```text
_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/planet-sect-validation.md
```

## 21. Regression Risks

- Risk: a downstream layer recalculates `in_sect` or `out_of_sect`.
  - Guardrail: scans anti-import calculator and tests proving JSON projection
    consumes precomputed facts.
- Risk: implementation adds local planet sect constants.
  - Guardrail: runtime source blocker, code review and scans for local
    diurnal/nocturnal/common maps.
- Risk: Mercure is silently treated as diurnal or nocturnal.
  - Guardrail: explicit common/variable test and validation note naming the
    runtime source.
- Risk: implementation confuses this story with hayz.
  - Guardrail: task and scan constraints forbid horizon/sign-gender/hayz logic
    in the planet sect condition calculator.
- Risk: public JSON destabilizes existing consumers.
  - Guardrail: additive change only under each planet and before/after
    snapshot proving no field removal.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-198.
- Treat CS-197 `ChartSectResult` as completed and canonical.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not modify chart-level sect calculation unless a blocker is found and
  documented before code changes.
- Do not add frontend changes.
- Do not add DB migrations unless runtime planet sect metadata is absent and
  the user explicitly approves a separate persistence change.
- Do not implement hayz, rejoicing or advanced conditions in this story.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, TODO or hidden residual work.

## 23. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` -
  chart-level sect contract consumed by this story.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` -
  dignity scoring and runtime-backed calculator context.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` -
  hayz and advanced conditions context that must remain out of scope.
- `_condamad/stories/regression-guardrails.md` - shared invariants consulted
  and extended with `RG-125`.
- `backend/app/domain/astrology/dignities/contracts.py` - canonical dignity
  DTO module.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  scoring orchestration owner.
- `backend/app/services/chart/json_builder.py` - public JSON projection owner.
