# Story CS-204 hayz-rejoicing-explicit-condition-contracts: Exposer hayz et rejoicing comme contrats explicites

Status: done

## 1. Objective

Formaliser `hayz` et `rejoicing` comme conditions traditionnelles explicites,
tracables et testables dans le resultat natal et le JSON public. La story doit
normaliser, pour chaque planete evaluable, les faits deja calcules par les
moteurs de dignites, de secte et de conditions avancees: resultat hayz,
composants hayz, maison actuelle, maison de joie, base de calcul et systeme de
reference. Elle ne doit pas changer la doctrine, les scores, les poids runtime,
les routes API ou les modes de calcul existants.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-20 pour CS-204, follow-up de
  CS-197, CS-198, CS-199, CS-200, CS-201, CS-202 et CS-203 si implemente.
- Reason for change: `chart sect` et `planet sect condition` sont explicites,
  mais `hayz` et `rejoicing` restent visibles de facon indirecte ou dispersee
  dans `advanced_conditions`, `accidental_breakdown`,
  `planet_condition_profiles` et `planet_condition_signals`.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/advanced_conditions`
- Consumed domain:
  - `backend/app/domain/astrology/dignities`
- In scope:
  - ajouter les contrats `HayzCondition`, `RejoicingCondition`,
    `TraditionalPlanetCondition` et `TraditionalConditionsResult`;
  - ajouter un normalizer pur dans le domaine `advanced_conditions` qui consomme
    `ChartSectResult`, `PlanetSectCondition`, `PlanetDignityResult`,
    `advanced_conditions`, positions/maisons natales, signes runtime et
    references runtime;
  - exposer `traditional_conditions` sur `NatalResult`;
  - serialiser `NatalResult.traditional_conditions` dans le JSON public sans
    recalcul dans `json_builder.py`;
  - mettre a jour le panneau expert frontend seulement si le bloc public doit
    etre affiche par CS-202;
  - ajouter tests unitaires, integration JSON, golden cases, scans
    anti-recalcul et evidence persistante sous
    `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/`.
- Out of scope:
  - changer la doctrine de hayz, rejoicing, secte ou condition de secte;
  - changer `ChartSectResult`, `PlanetSectCondition`, les scores de dignites,
    les poids runtime, les seeds ou les migrations;
  - ajouter une route API, une methode HTTP, un status code, une table DB ou un
    appel LLM;
  - deplacer le calcul dans `json_builder.py` ou le frontend;
  - generer une interpretation narrative.
- Explicit non-goals:
  - ne pas creer un second moteur de secte;
  - ne pas recalculer la secte du theme ni la condition de secte planetaire;
  - ne pas faire de hayz un alias de `in_sect`;
  - ne pas faire de rejoicing un libelle textuel derive dans la projection;
  - ne pas ajouter de fallback silencieux si les maisons, signes ou regles
    runtime manquent;
  - ne pas exposer de champs legacy;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-122`, `RG-124`,
    `RG-125`, `RG-126`, `RG-127`, `RG-128`, `RG-129`, `RG-130` ou `RG-131`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Brief archetype: explicit-condition-contract
- Archetype reason: la story transforme des faits traditionnels deja calcules
  en contrats explicites, consommables et verifiables, sans correspondre a un
  archetype standard d'API, suppression, migration ou refactor.
- Archetype adaptation: `explicit-condition-contract` est le libelle du brief;
  `custom` est l'archetype CONDAMAD valide avec contrats Runtime Source of
  Truth, Baseline Snapshot, Ownership Routing, Contract Shape, Reintroduction
  Guard et Persistent Evidence actifs.
- Additional validation rules:
  - les tests doivent prouver que hayz explicite est coherent avec
    `advanced_conditions` sans etre equivalent a `in_sect`;
  - les tests doivent prouver que rejoicing explicite est coherent avec
    `accidental_breakdown` et source la maison de joie depuis runtime ou depuis
    un breakdown existant documente;
  - les scans doivent prouver que projection JSON et frontend ne recalculent pas
    hayz ou rejoicing.
- Behavior change allowed: constrained
- Behavior change constraints:
  - un nouveau bloc additif `traditional_conditions` peut apparaitre dans
    `NatalResult` et le JSON public;
  - les blocs existants `dignities`, `advanced_conditions`,
    `planet_condition_profiles`, `planet_condition_signals`,
    `dominant_planets` et `interpretation_adapter` restent disponibles;
  - les scores, breakdowns existants, conditions avancees existantes, routes API
    et status codes ne changent pas;
  - le mode no-time/no-house doit suivre la convention CS-201: ne pas fabriquer
    de conditions house-dependent.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if:
  - les maisons, le genre/polarite de signe ou la maison de joie ne peuvent pas
    etre sources depuis les faits/runtime existants sans constante locale;
  - une migration ou un seed devient necessaire pour representer la maison de
    joie runtime.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Hayz et rejoicing doivent rester gouvernes par les faits calcules et le runtime, pas par projection ou UI. |
| Baseline Snapshot | yes | Un nouveau bloc public additif exige une comparaison avant/apres et une confirmation no-score-change. |
| Ownership Routing | yes | Les owners de secte, dignites, conditions avancees, projection JSON et frontend doivent rester separes. |
| Allowlist Exception | no | Aucune exception large, alias legacy, compatibilite ou fallback doctrinal n'est autorise. |
| Contract Shape | yes | La forme de `traditional_conditions`, `HayzCondition` et `RejoicingCondition` doit etre stable et testee. |
| Batch Migration | no | La story n'est pas une migration par lots et ne remplace pas des surfaces concurrentes. |
| Reintroduction Guard | yes | Les calculateurs et constantes doctrinales ne doivent pas revenir dans projection/frontend. |
| Persistent Evidence | yes | Snapshots, audit, validation et hits de scans doivent etre conserves. |

Brief-level contract requirements not represented as CONDAMAD contract names:

- No Score Change: required; covered by AC11, snapshots and golden cases.
- Frontend Consumption Guard: required when frontend is updated; covered by
  AC10 and scans.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - `AdvancedConditionEngine` output for hayz;
  - `PlanetDignityResult.accidental_breakdown` for rejoicing;
  - `AstrologyRuntimeReference.dignity_reference`;
  - `AstrologyRuntimeReference.advanced_condition_reference`;
  - planet positions, houses and signs already present in `NatalResult`.
- Runtime artifact:
  - AST guard/static scan over `backend/app/services/chart` and `frontend` for
    forbidden calculator imports and doctrine constants;
  - `TraditionalConditionsResult` attached to `NatalResult`;
  - public JSON `traditional_conditions` produced only from
    `NatalResult.traditional_conditions`;
  - golden cases G7/G8/G9 prove complete hayz, in-sect-not-hayz and planetary
    rejoicing; G13/G14 prove the sect-aware triplicity no-score-change guard.
- Secondary evidence:
  - contract/unit tests for the normalizer;
  - JSON builder tests with preconstructed `traditional_conditions`;
  - frontend component tests if the panel is updated;
  - static scans for forbidden constants, calculators and frontend derivation
    patterns.
- Forbidden sources:
  - frontend constants;
  - projection logic;
  - local hardcoded planet lists;
  - local hardcoded joy houses;
  - local hardcoded horizon houses;
  - local sign-gender maps;
  - LLM outputs, prompts or prompt hints.
- Static scans alone are not sufficient because:
  - absence of constants does not prove consistency with
    `advanced_conditions`/`accidental_breakdown`;
  - no-score-change and no-time behavior must be proven by tests and
    before/after snapshots.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-before.json`
  - `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-audit-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-after.json`
  - `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-validation.md`
- Required baseline questions:
  - where hayz is currently detected;
  - where rejoicing is currently detected;
  - where hayz/rejoicing are exposed in JSON today;
  - which facts are available to explain hayz;
  - which facts are available to explain rejoicing;
  - whether rejoicing house can be sourced from runtime;
  - whether planet horizon position can be sourced without local constants.
- Expected invariant:
  - scores unchanged;
  - existing `advanced_conditions` unchanged;
  - existing dignity breakdowns unchanged;
  - public JSON receives only documented additive fields;
  - frontend displays the new fields without calculation when updated.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | CS-204 role | Forbidden destination |
|---|---|---|---|
| Chart sect | `ChartSectResult` from CS-197 owner | consume | `json_builder.py` or frontend recalculation |
| Planet sect condition | `PlanetSectCondition` from CS-198 owner | consume | local planet doctrine maps |
| Hayz detection | `backend/app/domain/astrology/advanced_conditions/HayzCalculator` and `AdvancedConditionEngine` | normalize/explain | second sect or hayz engine |
| Rejoicing detection | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | normalize/explain | local joy-house constants |
| Traditional condition contract | CS-204 normalizer | own normalized public shape | scoring engines as public DTO owners |
| Natal orchestration | `backend/app/domain/astrology/natal_calculation.py` | attach result after advanced facts exist | API route or persistence layer |
| Public projection | `backend/app/services/chart/json_builder.py` | serialize only | calculation or inference |
| Frontend expert panel | CS-202 frontend owner | display only if changed | doctrine derivation |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason:
  - no broad allowlist, compatibility path, alias legacy or doctrinal fallback
    is allowed;
  - any retained scan hit must be exact, pre-existing and documented in
    `hayz-rejoicing-validation.md`.

## 4f. Contract Shape

- Contract type:
  - domain dataclass contracts plus additive public JSON block
    `traditional_conditions`.
- Fields:
  - `HayzCondition`;
  - `RejoicingCondition`;
  - `TraditionalPlanetCondition`;
  - `TraditionalConditionsResult`;
  - public JSON `traditional_conditions.planets` map keyed by `planet_code`.
- Required fields:
  - `HayzCondition.is_hayz: bool`;
  - `HayzCondition.sect_match: bool`;
  - `HayzCondition.hemisphere_match: bool | None`;
  - `HayzCondition.sign_gender_match: bool | None`;
  - `HayzCondition.calculation_basis: str`;
  - `HayzCondition.reference_system: str`;
  - `HayzCondition.evidence: tuple of str`;
  - `RejoicingCondition.is_rejoicing: bool`;
  - `RejoicingCondition.current_house: int | None`;
  - `RejoicingCondition.rejoicing_house: int | None`;
  - `RejoicingCondition.calculation_basis: str`;
  - `RejoicingCondition.reference_system: str`;
  - `RejoicingCondition.evidence: tuple of str`;
  - `TraditionalPlanetCondition.planet_code: str`;
  - `TraditionalPlanetCondition.hayz: HayzCondition`;
  - `TraditionalPlanetCondition.rejoicing: RejoicingCondition`;
  - `TraditionalConditionsResult.planets: tuple of TraditionalPlanetCondition`.
- Optional fields:
  - `NatalResult.traditional_conditions` may be `None` in no-time/no-house
    contexts per CS-201 convention;
  - `HayzCondition.hemisphere_match` may be `None` when the canonical hayz
    facts do not expose the hemisphere component;
  - `HayzCondition.sign_gender_match` may be `None` when the canonical hayz
    facts do not expose the sign-gender component;
  - `RejoicingCondition.current_house` may be `None` when a planet lacks a
    current house and the behavior is tested;
  - `RejoicingCondition.rejoicing_house` may be `None` only when runtime lacks a
    source and the blocker/behavior is documented and tested.
- Allowed values:
  - booleans stay booleans and unknown component facts stay `null`;
  - `calculation_basis`: stable technical string, expected
    `sect_hemisphere_sign_gender` for hayz and `planetary_joy_house` for
    rejoicing;
  - `reference_system`: stable runtime/tradition string, expected
    `traditional` for the current implementation.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - public JSON field: `traditional_conditions`;
  - nested names use snake_case exactly as the contract field names;
  - forbidden aliases: `hayz_legacy`, `rejoicing_legacy`, `legacy_hayz`,
    `legacy_rejoicing`, `joy_code`, `sect_code`, `chart_sect_code`,
    `planet_sect_code`.
- Frontend type impact:
  - if frontend is updated, extend existing natal payload types to consume
    `traditional_conditions` only as explicit backend data.
- Generated contract impact:
  - no route/OpenAPI path change is expected; inspect generated frontend/API
    contract ownership and document if no generated chart type exists.

### 4f.1 Contract Semantics

`HayzCondition` semantics:

- `is_hayz`: resultat final normalise.
- `sect_match`: recopie controlee de `PlanetSectCondition.is_in_sect`.
- `hemisphere_match`: indique si la planete est dans l'hemisphere attendu pour
  hayz selon les faits/runtime existants.
- `sign_gender_match`: indique si le genre ou la polarite du signe correspond a
  la regle runtime hayz.
- `calculation_basis`: valeur technique stable, par exemple
  `sect_hemisphere_sign_gender`.
- `reference_system`: systeme runtime utilise.
- `evidence`: faits courts non narratifs expliquant le resultat.

`RejoicingCondition` semantics:

- `is_rejoicing`: resultat final normalise.
- `current_house`: maison natale de la planete depuis le resultat deja calcule.
- `rejoicing_house`: maison de joie issue du runtime ou d'un breakdown existant
  documente.
- `calculation_basis`: valeur technique stable, par exemple
  `planetary_joy_house`.
- `reference_system`: systeme runtime utilise.
- `evidence`: faits courts non narratifs expliquant le resultat.

Public JSON target:

```json
{
  "traditional_conditions": {
    "planets": {
      "mars": {
        "hayz": {
          "is_hayz": true,
          "sect_match": true,
          "hemisphere_match": true,
          "sign_gender_match": true,
          "calculation_basis": "sect_hemisphere_sign_gender",
          "reference_system": "traditional",
          "evidence": []
        },
        "rejoicing": {
          "is_rejoicing": false,
          "current_house": 4,
          "rejoicing_house": 6,
          "calculation_basis": "planetary_joy_house",
          "reference_system": "traditional",
          "evidence": []
        }
      },
      "moon": {
        "hayz": {
          "is_hayz": true,
          "sect_match": true,
          "hemisphere_match": null,
          "sign_gender_match": null,
          "calculation_basis": "sect_hemisphere_sign_gender",
          "reference_system": "traditional",
          "evidence": []
        },
        "rejoicing": {
          "is_rejoicing": true,
          "current_house": 3,
          "rejoicing_house": 3,
          "calculation_basis": "planetary_joy_house",
          "reference_system": "traditional",
          "evidence": []
        }
      }
    }
  }
}
```

### 4f.2 Relationship With Existing Blocks

This story must not remove or replace existing blocks.

Existing blocks remain:

- `dignities`;
- `dignities.sect`;
- `dignities.planets[*].sect_condition`;
- `dignities.planets[*].accidental_breakdown`;
- `advanced_conditions`;
- `planet_condition_profiles`;
- `planet_condition_signals`.

New block:

- `traditional_conditions`.

Rules:

- `traditional_conditions.planets[*].hayz` must be consistent with
  `advanced_conditions` hayz.
- `traditional_conditions.planets[*].rejoicing` must be consistent with
  accidental dignity rejoicing.
- If `advanced_conditions` has hayz for a planet,
  `traditional_conditions.planets[planet].hayz.is_hayz` must be `true`.
- If `accidental_breakdown` has rejoicing for a planet,
  `traditional_conditions.planets[planet].rejoicing.is_rejoicing` must be
  `true`.
- The new block is a normalized contract, not a new scoring source.

### 4f.3 Missing / No-Time Behavior

If birth time or houses are unavailable:

- `traditional_conditions` must not fabricate hayz or rejoicing.
- If the application's existing no-time mode neutralizes house-dependent facts,
  `traditional_conditions` should be `null` or omitted according to the CS-201
  convention.
- If a planet lacks `current_house`, `rejoicing.current_house` should be `null`.
- If runtime lacks `rejoicing_house`, implementation must fail explicitly or
  mark `rejoicing_house: null` only when this is tested and documented.
- If hayz cannot be evaluated because hemisphere or sign gender is unavailable,
  `is_hayz` must not default to `false` silently unless the reason appears in
  `evidence`.

Preferred behavior for no-time/no-house contexts:

```text
traditional_conditions: null
```

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la story ajoute un contrat additif et ne migre pas plusieurs surfaces
  concurrentes ni des donnees historiques.

## 4h. Persistent Evidence Artifacts

Required artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `evidence/hayz-rejoicing-before.json` | Montrer hayz, in-sect-not-hayz, rejoicing et absence de `traditional_conditions`. |
| Before audit | `evidence/hayz-rejoicing-audit-before.md` | Documenter detection, exposition et sources runtime disponibles. |
| After snapshot | `evidence/hayz-rejoicing-after.json` | Montrer `traditional_conditions`, cas vrais/faux et comparaison scores. |
| Validation record | `evidence/hayz-rejoicing-validation.md` | Enregistrer commandes, tests, scans, score comparison et limites. |

The validation artifact must include:

- commands run;
- test results;
- snapshot comparison;
- score-change confirmation;
- frontend validation if applicable;
- allowed scan hits;
- no recalculation confirmation;
- no migration/seed confirmation or documented blocker.

## 4i. Reintroduction Guard

- Guard type:
  - contract tests for dataclass allowed values and required fields;
  - normalizer tests proving consistency with existing calculated facts;
  - JSON builder test using preconstructed `NatalResult.traditional_conditions`;
  - frontend render tests and scans if frontend is updated;
  - golden cases G7/G8/G9 cover the traditional condition cases and G13/G14
    cover the sect-aware triplicity no-score-change guard.
- Forbidden production doctrine constants:
  - `DIURNAL_PLANETS`;
  - `NOCTURNAL_PLANETS`;
  - `ABOVE_HORIZON_HOUSES`;
  - `BELOW_HORIZON_HOUSES`;
  - `JOY_HOUSES`;
  - `PLANETARY_JOYS`;
  - `HAYZ_RULES`;
  - `SIGN_GENDERS`.
- Forbidden calculator imports in projection/frontend:
  - `SectCalculator`;
  - `PlanetSectConditionCalculator`;
  - `AdvancedConditionEngine`;
  - `AccidentalDignityCalculator`.
- Forbidden frontend logic patterns:
  - `is_hayz =`;
  - `is_rejoicing =`;
  - `planet.house`;
  - `planet_code in`;
  - `sign_gender ===`;
  - `chart_sect ===`.
- Conditional allowed hits:
  - domain implementation may reference `HayzCalculator` or
    `AccidentalDignityCalculator` only in existing canonical owners, not in the
    new normalizer unless the implementation documents why reuse is pure and
    does not duplicate scoring;
  - tests may contain expected values and fixture constants when scoped to
    cases and documented.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` -
  `HayzCalculator` emits `hayz` only when `PlanetSectCondition.is_in_sect` and
  non-sect hayz factors match runtime horizon/sign-gender rules.
- Evidence 2: `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` -
  accidental dignities include house-based rules and can emit
  `planetary_joy` from runtime `house_code`/`house_codes` conditions.
- Evidence 3: `backend/app/domain/astrology/dignities/contracts.py` -
  `PlanetDignityResult` already contains `accidental_breakdown`,
  `chart_sect` and optional `sect_condition`.
- Evidence 4: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` currently exposes `dignities`, `condition_profiles`,
  `condition_signals`, `advanced_conditions`, `dominant_planets` and
  `interpretation_adapter`, but no `traditional_conditions` field.
- Evidence 5: `backend/app/services/chart/json_builder.py` - public JSON
  serializes `dignities`, `dignities.planets[*].sect_condition`,
  `accidental_breakdown` and `advanced_conditions`, but has no
  `traditional_conditions` serializer.
- Evidence 6: `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` -
  G7/G8 already prove complete hayz versus in-sect-only, and G9 proves
  `planetary_joy` in accidental breakdown/profile contribution.
- Evidence 7: `backend/app/tests/unit/test_chart_json_builder.py` - existing
  tests assert JSON projection of hayz via `advanced_conditions` and sect
  contracts via `dignities`.
- Evidence N: `_condamad/stories/regression-guardrails.md` - shared regression
  invariants consulted before story scope was finalized, and `RG-131` is added
  for CS-204.

Assumptions to verify during implementation:

- runtime reference data contains enough structured information to source
  rejoicing house without a local `JOY_HOUSES` map;
- sign polarity can be converted to `masculine | feminine | neutral | unknown`
  from existing runtime sign data without a local `SIGN_GENDERS` map;
- no-time/no-house mode follows CS-201 conventions by omitting or nulling
  house-dependent blocks.

## 6. Target State

After implementation:

- `NatalResult.traditional_conditions` exists and is `None` only when the facts
  are not evaluable by existing no-time/no-house conventions;
- each evaluable planet has `hayz` and `rejoicing` contracts with required
  fields and evidence;
- `hayz.is_hayz` is consistent with `advanced_conditions` hayz and remains
  false for in-sect-only incomplete cases;
- `rejoicing.is_rejoicing` is consistent with
  `PlanetDignityResult.accidental_breakdown` `planetary_joy`;
- public JSON exposes an additive `traditional_conditions` block;
- `json_builder.py` serializes only the precomputed contract;
- frontend expert panel displays the block without deriving doctrine if it is
  updated;
- no scores, weights, existing breakdowns, routes, migrations or seeds change.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return.
  - `RG-118` - dignity calculators remain pure and runtime-backed.
  - `RG-122` - `AdvancedConditionEngine` remains the owner of advanced
    conditions and runtime weights.
  - `RG-124` - chart-level sect contract remains canonical.
  - `RG-125` - per-planet sect condition remains canonical.
  - `RG-126` - advanced sect scoring consumes canonical facts and hayz is not
    merely in-sect.
  - `RG-127` - golden traditional cases remain stable.
  - `RG-128` - public JSON projection does not calculate astrology.
  - `RG-129` - frontend does not calculate astrology.
  - `RG-130` - dignity audit persistence must not become a calculator or public
    source.
  - `RG-131` - hayz and rejoicing explicit contracts normalize existing facts
    without becoming new scoring sources.
- Non-applicable invariants:
  - API route guardrails outside natal payload projection - no route is added,
    removed or renamed.
  - DB migration guardrails - no schema or seed change is expected unless a
    documented blocker requires user decision.
- Required regression evidence:
  - unit tests for contracts and normalizer;
  - public JSON tests proving serialization only;
  - golden cases;
  - before/after snapshots;
  - frontend tests/scans if frontend updated;
  - static scans for local doctrine constants and forbidden calculators.
- Allowed differences:
  - additive `NatalResult.traditional_conditions`;
  - additive public JSON block `traditional_conditions`;
  - additive frontend section if implemented;
  - new tests and evidence files;
  - no score, route, migration or seed difference expected.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `HayzCondition` exposes hayz fields without duplicated doctrine. | `test_traditional_condition_normalizer.py` plus `test_chart_json_builder.py`. |
| AC2 | `RejoicingCondition` preserves the nullable house contract. | `test_traditional_condition_normalizer.py` plus `test_chart_json_builder.py`. |
| AC3 | `traditional_conditions` is attached to `NatalResult`. | `test_traditional_golden_cases.py` plus `test_chart_json_builder.py`. |
| AC4 | Hayz exposes `sect_match`, `hemisphere_match`, `sign_gender_match`. | Pytest: `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`. |
| AC5 | Hayz is not equivalent to `in_sect` alone. | Pytest: `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. |
| AC6 | Rejoicing exposes explicit house fields. | Pytest: `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`. |
| AC7 | Hayz matches `advanced_conditions`. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`. |
| AC8 | Rejoicing matches `accidental_breakdown`. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`. |
| AC9 | Public JSON exposes `traditional_conditions` without recalculation. | Pytest: `backend/app/tests/unit/test_chart_json_builder.py` plus forbidden scan. |
| AC10 | Frontend displays the block without deriving it when changed. | `npm --prefix frontend test -- NatalExpertPanel`; frontend scans. |
| AC11 | Scores are unchanged. | Before/after snapshots plus `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. |
| AC12 | Persistent evidence files are complete. | `Test-Path` checks and `rg` evidence scan. |

## 8. Implementation Tasks

- [x] Task 1 - Audit current hayz/rejoicing flow and capture baseline (AC: AC7, AC8, AC11, AC12)
  - [x] Subtask 1.1 - Inspecter `backend/app/domain/astrology/advanced_conditions/**`,
    `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`,
    `contracts.py`, `natal_calculation.py`, `json_builder.py` and `frontend/**`.
  - [x] Subtask 1.2 - Creer `hayz-rejoicing-audit-before.md` repondant aux
    questions baseline de la section 4c.
  - [x] Subtask 1.3 - Creer `hayz-rejoicing-before.json` avec au moins un cas
    hayz, un cas in-sect non hayz, un cas rejoicing et l'absence actuelle de
    `traditional_conditions`.

- [x] Task 2 - Ajouter les contrats typés (AC: AC1, AC2, AC3)
  - [x] Subtask 2.1 - Ajouter les dataclasses dans le module canonique choisi,
    preferentiellement `backend/app/domain/astrology/advanced_conditions/contracts.py`
    si l'audit confirme l'ownership.
  - [x] Subtask 2.2 - Valider la forme publique, les champs obligatoires,
    la nullabilite et l'evidence non narrative via les tests du normalizer et
    de projection JSON.
  - [x] Subtask 2.3 - Etendre `NatalResult` avec
    `traditional_conditions: TraditionalConditionsResult | None`.

- [x] Task 3 - Construire le normalizer domaine (AC: AC4, AC5, AC6, AC7, AC8)
  - [x] Subtask 3.1 - Ajouter un service pur, par exemple
    `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`.
  - [x] Subtask 3.2 - Consommer les dignites, conditions avancees, positions,
    signes, maisons et runtime reference deja disponibles.
  - [x] Subtask 3.3 - Sourcing hayz: reprendre `PlanetSectCondition`, presence
    de `advanced_conditions.hayz`, horizon runtime et polarite runtime sans
    recalculer la secte.
  - [x] Subtask 3.4 - Sourcing rejoicing: reprendre `accidental_breakdown`
    `planetary_joy`, maison courante et maison de joie issue du runtime ou
    documenter explicitement le blocker.
  - [x] Subtask 3.5 - Gerer no-time/no-house par `traditional_conditions: None`
    ou omission selon la convention CS-201, sans faux `false` silencieux.

- [x] Task 4 - Integrer dans le calcul natal (AC: AC3, AC7, AC8, AC11)
  - [x] Subtask 4.1 - Calculer `traditional_conditions` apres
    `advanced_conditions` et avant le retour `NatalResult`.
  - [x] Subtask 4.2 - Ne pas alimenter scoring, dominance, profils ou signaux
    depuis le nouveau bloc, sauf si l'audit prouve un besoin et conserve les
    scores inchanges.
  - [x] Subtask 4.3 - Ajouter tests `NatalResult` et integration.

- [x] Task 5 - Ajouter la projection JSON publique (AC: AC9, AC11)
  - [x] Subtask 5.1 - Ajouter un serializer strict de
    `NatalResult.traditional_conditions`.
  - [x] Subtask 5.2 - Tester que `json_builder.py` ne lit pas maisons/signes
    pour inferer hayz ou rejoicing.
  - [x] Subtask 5.3 - Tester les payloads no-time/anciens payloads selon la
    convention CS-201.

- [x] Task 6 - Mettre a jour le frontend lorsque le bloc public est consomme (AC: AC10)
  - [x] Subtask 6.1 - Inspecter `NatalExpertPanel` et types natals existants.
  - [x] Subtask 6.2 - Afficher `traditional_conditions` dans une section
    `Conditions traditionnelles` depuis les booleens/champs fournis.
  - [x] Subtask 6.3 - Ajouter ou adapter tests/CSS sans styles inline et sans
    derivation frontend.

- [x] Task 7 - Ajouter tests et golden cases (AC: AC1, AC2, AC4, AC5, AC6, AC7, AC8, AC9, AC11)
  - [x] Subtask 7.1 - Ajouter `test_traditional_condition_normalizer.py`.
  - [x] Subtask 7.2 - Mettre a jour `test_chart_json_builder.py` et
    `test_traditional_golden_cases.py`.
  - [x] Subtask 7.3 - Couvrir hayz complet, in-sect non hayz, out-of-sect non
    hayz, rejoicing vrai/faux, no-time, coherence `advanced_conditions` et
    coherence `accidental_breakdown`.

- [x] Task 8 - Capturer evidence apres implementation et valider (AC: AC10, AC11, AC12)
  - [x] Subtask 8.1 - Creer `hayz-rejoicing-after.json` avec contrats et
    comparaison score/breakdown.
  - [x] Subtask 8.2 - Creer `hayz-rejoicing-validation.md` avec commandes,
    resultats, scans, hits autorises et no migration/seed confirmation.
  - [x] Subtask 8.3 - Executer tests, lint, scans et checks d'evidence.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult` for chart-level sect;
  - `PlanetSectCondition` for per-planet sect state;
  - existing `AdvancedConditionEngine` output for hayz truth;
  - existing `PlanetDignityResult.accidental_breakdown` for rejoicing truth;
  - existing runtime references for sign polarity, horizon/house rules and
    planetary joy rule metadata;
  - existing house assignment and planet positions from `NatalResult`;
  - existing JSON projection helper style;
  - existing CS-202 expert panel if frontend is updated.
- Do not recreate:
  - chart sect calculation;
  - planet sect calculation;
  - local joy-house mapping;
  - local horizon house mapping;
  - local sign gender mapping;
  - scoring weights;
  - LLM or narrative interpretation.
- Shared abstraction allowed only if:
  - it is a pure normalizer from calculated facts to the new contract and
    prevents duplication between tests and domain orchestration.
- Allowed:
  - expected values in tests;
  - display labels in frontend;
  - pure mapping of already computed facts into contract field names.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- local astrology constants in production;
- projection/frontend doctrine derivation;
- DB migration or seed update without documented blocker and user decision.

Specific forbidden public fields:

- `hayz_legacy`
- `rejoicing_legacy`
- `sect_code`
- `chart_sect_code`
- `planet_sect_code`
- `joy_code`
- `legacy_hayz`
- `legacy_rejoicing`

Specific forbidden doctrine constants in production:

- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `ABOVE_HORIZON_HOUSES`
- `BELOW_HORIZON_HOUSES`
- `JOY_HOUSES`
- `PLANETARY_JOYS`
- `HAYZ_RULES`
- `SIGN_GENDERS`

Specific forbidden calculator imports in projection/frontend:

- `SectCalculator`
- `PlanetSectConditionCalculator`
- `AdvancedConditionEngine`
- `AccidentalDignityCalculator`

Specific forbidden frontend logic:

- `is_hayz =`
- `is_rejoicing =`
- `planet.house ===`
- `planet_code in`
- `sign_gender ===`
- `chart_sect ===`

Allowed frontend use of backend booleans:

- `condition.hayz.is_hayz`
- `condition.rejoicing.is_rejoicing`
- `condition.hayz.sect_match`
- `condition.hayz.hemisphere_match`
- `condition.hayz.sign_gender_match`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect | CS-197 `ChartSectResult` owner | CS-204 normalizer, JSON builder, frontend |
| Planet sect condition | CS-198 `PlanetSectCondition` owner | local planet code constants |
| Hayz detection | `backend/app/domain/astrology/advanced_conditions/**` | JSON builder/frontend reconstruction |
| Rejoicing detection | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | local joy-house constants |
| Traditional condition contract | CS-204 normalizer | scoring engines as public DTO owners |
| Public projection | `backend/app/services/chart/json_builder.py` | domain calculation |
| Frontend expert panel | CS-202 frontend | doctrine calculation |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: applicable because public JSON shape is extended.
- Required generated-contract evidence:
  - inspect whether generated frontend/OpenAPI contracts exist before editing;
  - if generated contracts exist, regenerate or update them according to project
    convention and record the command/result;
  - if no generated chart contract exists, record manual type ownership in
    `hayz-rejoicing-audit-before.md`.

## 17. Files to Inspect First

Codex doit inspecter avant edition:

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `frontend/**`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/advanced_conditions/contracts.py` - add
  traditional condition contracts if ownership is confirmed.
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` -
  add pure normalizer.
- `backend/app/domain/astrology/natal_calculation.py` - attach
  `traditional_conditions` to `NatalResult`.
- `backend/app/services/chart/json_builder.py` - serialize precomputed
  `traditional_conditions`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/app/tests/unit/test_chart_json_builder.py`

Possible frontend files:

- `frontend/**/NatalExpertPanel.*` - display block when frontend consumption is implemented.
- `frontend/**/NatalExpertPanel.test.*` - rendering/no-derivation tests if
  frontend is changed.
- `frontend/**/natal-chart*.ts` - public payload types if manual types exist.

Evidence files:

- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-before.json`
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-audit-before.md`
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-after.json`
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-validation.md`

Files not expected to change:

- `backend/app/api/**` - no route or HTTP behavior change.
- `backend/app/infra/**` - no DB/repository change expected.
- `backend/app/domain/prediction/**` - prediction out of scope.
- `backend/migrations/**` - no migration expected.
- `docs/db_seeder/**` - no seed update expected.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only when explicitly listed here with
  justification.
- Justification: existing dataclasses/Pydantic contracts, runtime references,
  pytest, Vitest/Testing Library and CSS are sufficient.

## 20. Validation Plan

All Python commands must be run after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Backend targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py
```

Quality checks:

```powershell
ruff format .
ruff check .
```

Frontend checks if frontend is updated:

```powershell
npm --prefix frontend test -- NatalExpertPanel
npm --prefix frontend run lint
npm --prefix frontend run build
```

No-recalculation scans:

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES|SIGN_GENDERS" backend/app frontend -g "*.{py,ts,tsx,js,jsx}"
rg -n "hayz_legacy|rejoicing_legacy|legacy_hayz|legacy_rejoicing|joy_code|sect_code|chart_sect_code|planet_sect_code" backend/app backend/tests frontend -g "*.{py,ts,tsx,js,jsx}"
rg -n "SectCalculator|PlanetSectConditionCalculator|AdvancedConditionEngine|AccidentalDignityCalculator" backend/app/services/chart frontend -g "*.{py,ts,tsx,js,jsx}"
rg -n "is_hayz\s*=|is_rejoicing\s*=|planet\.house|planet_code\s+in|sign_gender\s*===|chart_sect\s*===" frontend -g "*.{ts,tsx,js,jsx}"
```

Forbidden path diff checks:

```powershell
git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder
```

Evidence checks:

```powershell
Test-Path _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-before.json
Test-Path _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-audit-before.md
Test-Path _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-after.json
Test-Path _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/hayz-rejoicing-validation.md
rg -n "hayz|rejoicing|traditional_conditions|sect_match|hemisphere_match" `
  _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence
rg -n "sign_gender_match|no score change|no recalculation" `
  _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence
```

Story validation commands:

```powershell
$story = "_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 21. Regression Risks

- Risk: hayz becomes equal to `in_sect`.
  - Guardrail: G8/unit test with `is_in_sect=true` and `is_hayz=false`.
- Risk: rejoicing is recalculated with a local constant.
  - Guardrail: no `JOY_HOUSES`/`PLANETARY_JOYS` in production and test proving
    runtime/breakdown source.
- Risk: JSON builder recalculates conditions.
  - Guardrail: test with preconstructed `NatalResult.traditional_conditions`
    and forbidden calculator scans.
- Risk: frontend recreates doctrine.
  - Guardrail: scans and tests based only on explicit payload fields.
- Risk: scores change.
  - Guardrail: before/after snapshots and golden cases.
- Risk: no-time mode fabricates false states.
  - Guardrail: missing-house/no-time test and documented null/omitted behavior.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-204.
- Do not broaden the domain.
- Treat CS-197 through CS-203 as canonical if present.
- Do not change doctrine, scoring, runtime weights, routes, migrations or seeds.
- Do not recalculate chart sect or planet sect condition.
- Do not make hayz equal to `in_sect`.
- Do not create joy-house, horizon-house, planet-sect or sign-gender constants
  in production.
- Do not add LLM behavior or narrative interpretation.
- Do not move calculation to `json_builder.py` or frontend.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in the validation
  evidence.
- If runtime facts required by the contract are missing, document the blocker
  instead of inventing a fallback.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 23. References

- `CS-197 sect-audit-explicit-contract` - chart-level sect contract.
- `CS-198 planet-sect-condition-normalization` - per-planet sect condition.
- `CS-199 advanced-sect-scoring-integration` - hayz/out-of-sect integration
  against canonical sect facts.
- `CS-200 hellenistic-medieval-golden-cases` - G7/G8/G9 traditional cases.
- `CS-201 natal-public-json-projection-cleanup` - public JSON projection and
  no-time convention.
- `CS-202 natal-expert-panel` - frontend display-only consumption.
- `CS-203 natal-dignity-audit-persistence` - audit persistence remains
  non-calculating if implemented.
- `_condamad/stories/regression-guardrails.md` - applicable invariants and
  new `RG-131`.

## 24. Closure Notes

- Implementation date: 2026-05-20.
- `TraditionalConditionNormalizer` is the domain owner for the public
  `traditional_conditions` contract.
- `HayzCalculator` keeps hayz detection ownership and now emits
  `calculation_facts` used by the normalizer.
- `json_builder.py` serializes `NatalResult.traditional_conditions` only; it no
  longer reconstructs hayz or rejoicing from raw houses/signs.
- `NatalExpertPanel` displays `traditional_conditions` as backend facts without
  frontend doctrine.
- G13/G14 extend CS-200 golden cases to lock sect-aware triplicity day/night
  rulers for the same fire element.
- Final validation and review evidence are recorded in `generated/`.
