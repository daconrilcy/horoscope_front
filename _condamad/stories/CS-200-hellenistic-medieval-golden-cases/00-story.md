# Story CS-200 hellenistic-medieval-golden-cases: Verrouiller les cas golden hellénistiques et médiévaux

Status: ready-to-dev

## 1. Objective

Créer une batterie de tests golden hellénistiques / médiévaux qui verrouille la
chaîne traditionnelle livrée par CS-197, CS-198 et CS-199 sans modifier la
doctrine astrologique.

La story doit produire des fixtures déterministes, des assertions ciblées et
des snapshots maintenables pour prouver que la secte du thème, la condition de
secte par planète, hayz, hors-secte, rejoicing, dignités essentielles,
dignités accidentelles, profils, signaux, dominantes, adaptateur interprétatif
et projection JSON restent stables.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-20 pour CS-200, follow-up
  de CS-197, CS-198 et CS-199.
- Reason for change: la secte du thème, la condition de secte par planète et
  la consommation avancée des faits de secte sont désormais contractuelles.
  Des cas golden persistants doivent empêcher les régressions.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

This story belongs to one primary domain while validating its documented
projection surfaces:

- Domain: `backend/app/domain/astrology`
- In scope:
  - créer des fixtures golden synthétiques pour les cas G1 à G11;
  - créer au moins un cas intégré G12 pour le payload natal et sa projection JSON;
  - tester `dignities.sect`, `dignities.planets[*].sect_condition`, les
    dignités essentielles, dignités accidentelles, conditions avancées,
    profils, signaux, dominantes, adaptateur interprétatif et
    `json_builder.py`;
  - produire des snapshots compactés et persistants sous
    `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/`;
  - documenter la provenance, l'objectif et les invariants de chaque cas golden;
  - ajouter des scans anti-réintroduction pour les constantes locales,
    recalculs de secte, fallbacks et imports interdits.
- Out of scope:
  - changer `SectCalculator`;
  - changer `PlanetSectConditionCalculator`;
  - changer `AdvancedConditionEngine` sauf bug bloquant documenté avant/après;
  - changer les poids runtime, règles de hayz, rejoicing, triplicité, termes, faces ou décans;
  - modifier les seeds DB, migrations, routes API, frontend React ou logique LLM;
  - générer une interprétation narrative;
  - ajouter une dépendance, un fallback SwissEph caché ou un moteur simplifié masqué;
  - modifier un contrat public sauf bug bloquant prouvé et documenté.
- Explicit non-goals:
  - ne pas créer de doctrine astrologique locale dans les tests;
  - ne pas remplacer le runtime par des constantes applicatives;
  - ne pas snapshotter tout le payload natal sans assertions ciblées;
  - ne pas masquer une instabilité de calcul par une fixture trop permissive;
  - ne pas introduire de fixture dépendante d'une heure DST ambiguë;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`, `RG-121`, `RG-122`, `RG-123`, `RG-124`, `RG-125`, `RG-126` ou `RG-127`.

## 4. Operation Contract

- Operation type: test / validation update
- Primary archetype: regression-contract-preservation
- Archetype reason: la story ne crée pas une nouvelle capacité métier; elle verrouille par tests et snapshots les contrats runtime et doctrinaux déjà livrés par CS-197 à CS-199.
- Behavior change allowed: no
- Behavior change constraints:
  - les résultats de production ne doivent pas changer;
  - toute différence de score ou de forme de contrat découverte doit être traitée comme anomalie à expliquer, pas comme nouveau comportement normal;
  - aucune route, migration, seed, dépendance, surface frontend ou logique LLM ne doit changer;
  - les tests doivent consommer les sources runtime existantes plutôt que recréer la doctrine.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un cas golden requis ne peut pas être produit sans
  changer la doctrine, ajouter une dépendance, utiliser un fallback caché ou
  modifier un contrat public.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les golden cases doivent consommer le runtime et les contrats livrés, pas des constantes locales. |
| Baseline Snapshot | yes | Les sorties actuelles doivent être capturées avant/après pour prouver l'absence de drift. |
| Ownership Routing | yes | Chaque responsabilité traditionnelle doit rester chez son owner canonique. |
| Allowlist Exception | no | Aucune exception d'implémentation large n'est autorisée; seuls les hits de scan enregistrés comme preuves peuvent être documentés. |
| Contract Shape | yes | Les formes CS-197, CS-198 et CS-199 doivent rester explicites et stables. |
| Batch Migration | no | La story n'autorise pas de migration par lots ni de surfaces parallèles. |
| Reintroduction Guard | yes | Les recalculs locaux de secte, hayz, horizon, joie ou scoring doivent être bloqués. |
| Persistent Evidence | yes | Index, snapshots, validations et scans doivent rester dans le dossier de story. |
| Golden Snapshot Stability | yes | Les snapshots doivent rester comparables, compactés et maintenables. |
| Test Fixture Provenance | yes | Chaque cas golden doit expliciter ce qu'il teste, pourquoi il existe et quelle source runtime il verrouille. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config/runtime object `AstrologyRuntimeReference`;
  - `dignity_reference`;
  - `advanced_condition_reference`;
  - `condition_signal_profiles`;
  - `dominance_reference`;
  - `interpretation_adapter_reference`;
  - `ChartSectResult` livré par CS-197;
  - `PlanetSectCondition` livré par CS-198;
  - intégration avancée livrée par CS-199.
- Runtime artifact:
  - `AstrologyRuntimeReference` loaded config/runtime object assembled by existing test builders or runtime fixtures;
  - AST guard/static import scan over canonical modules for ownership boundaries;
  - JSON artifact produced from runtime test execution for
    `golden-cases-before.json` and `golden-cases-after.json`, or a valid
    baseline marker when no prior golden suite exists.
- Secondary evidence:
  - tests unitaires ciblés;
  - cas intégré natal;
  - snapshots golden compactés;
  - scans anti-constantes, anti-recalcul et anti-imports interdits;
  - validation markdown persistante.
- Static scans alone are not sufficient for this story because:
  - un test peut éviter les imports interdits tout en reconstituant localement une liste de planètes, de maisons d'horizon, de joies ou de poids;
  - les invariants de forme doivent être prouvés par des sorties runtime et des assertions ciblées.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/`
- Baseline documentation and artifact before implementation:
  - `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md`
  - `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json`
  - `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md`
- Comparison rule:
  - before and after runtime snapshots must match unless the story uncovers a
    pre-existing bug;
  - if no prior golden fixture suite exists, `golden-cases-index.md` must state
    that no prior suite existed and the first deterministic output establishes
    the baseline;
  - in that case, `golden-cases-before.json` must remain valid JSON and record
    the absence of a prior suite instead of pretending to be a real previous
    snapshot;
  - no fake before snapshot is allowed.
- Expected invariant:
  - no production contract changes;
  - no public JSON shape changes;
  - no score delta unless documented as a bug correction;
  - no frontend, API route, migration, seed or dependency change.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | tests helpers, downstream layers, `json_builder.py` |
| Planet sect condition | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | tests helpers, advanced conditions, dominance, adapters, JSON builder |
| Essential dignity | `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` | golden snapshot helper |
| Accidental dignity and rejoicing | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | condition/adapters/snapshot helper |
| Hayz and out-of-sect facts | `backend/app/domain/astrology/advanced_conditions/**` | dignity calculators, JSON builder, test-local doctrine engines |
| Condition profiles and signals | `backend/app/domain/astrology/condition/**` | sect calculators, dominance, adapters |
| Dominance | `backend/app/domain/astrology/dominance/**` | sect calculators, condition profile builders |
| Interpretation adapter | `backend/app/domain/astrology/interpretation_adapters/**` | sect calculators, prompts, LLM, narration |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculation or doctrine ownership |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: no broad allowlist or implementation exception is allowed. Exact scan
  hits may be recorded only as validation evidence in
  `golden-cases-validation.md`.

## 4f. Contract Shape

- Contract type:
  - existing domain DTO and public JSON contracts from CS-197, CS-198 and CS-199.
- Fields:
  - `dignities.sect.chart_sect`
  - `dignities.sect.sun_horizon_position`
  - `dignities.sect.sun_above_horizon`
  - `dignities.sect.calculation_basis`
  - `dignities.sect.reference_system`
  - `dignities.planets[*].sect_condition.planet_code`
  - `dignities.planets[*].sect_condition.chart_sect`
  - `dignities.planets[*].sect_condition.intrinsic_sect`
  - `dignities.planets[*].sect_condition.planet_sect_condition`
  - `dignities.planets[*].sect_condition.is_in_sect`
  - `dignities.planets[*].sect_condition.is_out_of_sect`
  - `dignities.planets[*].sect_condition.calculation_basis`
  - `dignities.planets[*].sect_condition.reference_system`
  - `advanced_conditions[*].condition_code`
  - `planet_condition_profiles`
  - `planet_condition_signals`
  - `dominant_planets`
  - `interpretation_adapter`
- Required fields:
  - all listed sect and sect_condition fields are required when dignity results are present;
  - G12 must prove downstream surfaces are present or explicitly `None` only according to existing runtime behavior.
- Optional fields:
  - none introduced by this story.
- Status codes:
  - no HTTP endpoint or status code is modified.
- Serialization names:
  - existing public names remain unchanged;
  - forbidden new names include `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`.
- Frontend type impact:
  - no frontend change in this story.
- Generated contract impact:
  - no generated route or OpenAPI change expected; if chart JSON is represented in generated contracts, document no delta in validation evidence.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: golden cases must be introduced in one coherent validation suite and must not create parallel migrated surfaces.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Golden cases index | `evidence/golden-cases-index.md` | Documenter G1-G12, provenance, fixture, invariants et contrats. |
| Before snapshot | `evidence/golden-cases-before.json` | Capturer l'état initial ou l'absence de suite golden préalable. |
| After snapshot | `evidence/golden-cases-after.json` | Capturer les sorties finales compactées et comparables. |
| Validation summary | `evidence/golden-cases-validation.md` | Enregistrer commandes, résultats, deltas, scans et surfaces non touchées. |

## 4i. Reintroduction Guard

- Guard target:
  - prevent local doctrine, local constants, hidden fallbacks and downstream sect recalculation from returning.
- Forbidden examples:
  - local `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`, `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`;
  - local `ABOVE_HORIZON_HOUSES`, `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`, `PLANETARY_JOYS` in production code;
  - local horizon tuples equivalent to `7, 8, 9, 10, 11, 12` or `1, 2, 3, 4, 5, 6` in production astrology/chart code;
  - downstream imports of `SectCalculator` or `PlanetSectConditionCalculator`;
  - hayz implemented as `is_in_sect` only;
  - out-of-sect recalculated from chart sect and planet lists;
  - SwissEph-labeled golden case backed by a hidden simplified fallback.
- Architecture guard against reintroduction:
  - targeted pytest proves the runtime facts;
  - `rg` scans listed in the validation plan must be recorded in `golden-cases-validation.md`;
  - hits in test fixtures are acceptable only when classified as explicit
    per-case input data, not as reusable local doctrine tables or recalculation
    helpers;
  - curated snapshots must fail review if a protected field disappears or a score changes beyond documented tolerance.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 4k. Golden Case Strategy

Two fixture levels are required:

1. Level 1 - synthetic domain fixtures:
   - preferred for G1-G11;
   - fixtures specify exact factual inputs such as planet code, sign, house, motion state, chart sect result and per-planet sect condition;
   - missing or malformed condition inputs may be covered only through explicit
     negative fixtures, when existing project contracts make the expected
     behavior unambiguous;
   - helpers must make tested facts explicit and must not hide doctrine behind names such as `make_valid_astrology_case`.
2. Level 2 - integrated natal fixtures:
   - required for G12;
   - must use stable `BirthInput` values, unambiguous timezone, fixed coordinates, fixed house system and fixed zodiac/frame;
   - if SwissEph ephemerides are unstable in CI, the test must use existing deterministic project conventions or be explicitly marked according to project convention.

Snapshot policy:

- snapshots must be compact and curated;
- each case entry must include `case_id`, `fixture_type`, `targeted_contracts`, `expected_summary`, `observed_summary` and `assertions`;
- float policy must be documented when floats are included: scores, longitudes and orb ratios rounded to 6 decimals;
- exclude timestamps, database ids, unstable hashes, ordering noise, full ephemeris traces and unrelated localized labels.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - CS-197, CS-198 and CS-199 are registered as `done`; CS-200 is the next sequential `CS-###` number.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared
  invariants consulted before story scope was finalized; `RG-127` is added by
  this story.
- Evidence 3: `backend/app/domain/astrology/dignities/contracts.py` -
  `ChartSectResult`, `PlanetSectCondition` and
  `PlanetDignityResult.sect_condition` exist.
- Evidence 4: `backend/app/domain/astrology/dignities/sect_calculator.py` - chart-level sect calculation is the canonical owner for day/night and Sun horizon facts.
- Evidence 5: `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` - per-planet sect condition is derived from `ChartSectResult` and runtime sect rules.
- Evidence 6:
  `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  computes `chart_sect` once and attaches `sect_condition`.
- Evidence 7:
  `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` -
  consumes canonical sect facts and evaluates non-sect hayz factors.
- Evidence 8: `backend/app/domain/astrology/natal_calculation.py` - the natal
  pipeline builds signals, dominance and adapter after dignity calculation.
- Evidence 9: `backend/app/services/chart/json_builder.py` - projection
  serializes the targeted downstream fields.
- Evidence 10: all `Files to Inspect First` paths were checked for existence
  before drafting; the new golden test and fixture helpers do not yet exist.

## 6. Target State

After implementation:

- `golden-cases-index.md` documents G1-G12 with fixture type, doctrine target, contracts, assertions and reason;
- `golden-cases-before.json` and `golden-cases-after.json` exist; when both
  contain runtime outputs, they use the same curated stable shape, and when no
  prior suite exists, the before file is a valid absence marker;
- synthetic fixtures cover exact doctrinal edge cases for day/night sect,
  in-sect/out-of-sect, hayz complete/incomplete, rejoicing, Mercury, essential
  dignity and accidental dignity stability;
- an integrated natal fixture proves downstream propagation through dignity, profiles, signals, dominance, interpretation adapter and JSON projection;
- tests fail if `dignities.sect`, `sect_condition`, hayz, out_of_sect, rejoicing, essential dignity, dominance or adapter facts drift unexpectedly;
- no production code changes are required unless a pre-existing bug is uncovered and documented with before/after evidence;
- no frontend, API route, migration, seed, DB model, dependency or LLM change is made.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return in backend astrology.
  - `RG-118` - dignity calculators must remain pure, runtime-backed and free of DB/API/services/prediction/LLM dependencies.
  - `RG-119` - condition profiles must remain derived from dignity results and advanced facts.
  - `RG-120` - condition signals must not encode local sect thresholds or prompts.
  - `RG-121` - dominance must consume approved factors and not own doctrine.
  - `RG-122` - advanced conditions must consume factual dignity outputs without local sect recalculation.
  - `RG-123` - interpretation adapter must consume facts and not become a sect calculator.
  - `RG-124` - chart-level sect contract remains canonical.
  - `RG-125` - per-planet sect condition remains canonical.
  - `RG-126` - advanced sect scoring consumes canonical sect contracts and runtime weights.
  - `RG-127` - traditional golden cases must remain stable unless an approved doctrine/runtime change updates expected snapshots.
- Non-applicable invariants:
  - API, Stripe, frontend design-system and prediction-only guardrails are not touched because this story is limited to backend astrology tests and evidence.
- Required regression evidence:
  - targeted pytest;
  - curated snapshots;
  - `rg` scans;
  - `Test-Path` evidence checks;
  - validation markdown.
- Allowed differences:
  - none expected by default;
  - any production bug correction must document exact before/after delta and affected case IDs.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | G1/G2 prove day/night chart sect plus Sun horizon fields. | Test + snapshot: `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. |
| AC2 | G3-G6 prove in-sect/out-of-sect for diurnal/nocturnal planets. | Test + snapshot: targeted pytest; G3-G6 snapshot includes explicit `PlanetSectCondition` fields. |
| AC3 | G7/G8 prove hayz complete versus in-sect-only incomplete. | Test + snapshot: targeted pytest asserts hayz appears only in G7, not G8. |
| AC4 | G9 proves planetary rejoicing remains stable. | Test + snapshot: targeted pytest asserts canonical joy code, score contribution and profile impact. |
| AC5 | G10 proves explicit runtime-backed Mercury handling. | Runtime test: pytest reads Mercury from loaded config `AstrologyRuntimeReference`; index documents it. |
| AC6 | G11 proves at least one essential dignity remains stable. | Test: targeted pytest asserts a canonical dignity and stable score fields. |
| AC7 | G12 proves full pipeline propagation to downstream JSON outputs. | Integration test: targeted pytest covers golden case, `NatalResult`, chart JSON and result service. |
| AC8 | Snapshots stay curated compact without volatile fields. | Evidence review: `python -m json.tool`; validation markdown documents rounding and exclusions. |
| AC9 | No local production doctrine constants, test-local doctrine engines or recalculations are introduced. | Static scans: required `rg` scans for symbols, tuples, calculators and forbidden imports across production and test helper surfaces. |
| AC10 | No forbidden path or dependency change is made. | Diff + AST guard: forbidden-path diff; chart JSON pytest; validation records zero forbidden-path, dependency, migration, API, frontend or seed changes. |
| AC11 | Public JSON remains aligned with CS-197/CS-198. | Chart JSON test: `pytest -q backend/app/tests/unit/test_chart_json_builder.py`; G12 includes projection fields. |
| AC12 | Persistent evidence artifacts cover all case IDs G1-G12. | Evidence checks: `Test-Path` for artifacts; `rg -n "G1|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Create story evidence directory and index (AC: AC8, AC12)
  - [ ] Subtask 1.1 - Create `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/`.
  - [ ] Subtask 1.2 - Create `golden-cases-index.md`.
  - [ ] Subtask 1.3 - For every case G1-G12, document `case_id`, title, fixture type, targeted doctrine, targeted contracts, key assertions and reason the case exists.
  - [ ] Subtask 1.4 - Add the no-prior-suite baseline note if no earlier golden fixture suite exists.

- [ ] Task 2 - Capture baseline snapshot (AC: AC8, AC12)
  - [ ] Subtask 2.1 - Create `golden-cases-before.json` from the first deterministic output generation, or write a valid JSON marker documenting that no prior golden suite exists.
  - [ ] Subtask 2.2 - Do not fake a before snapshot.
  - [ ] Subtask 2.3 - Keep the baseline shape curated and comparable to `golden-cases-after.json`.

- [ ] Task 3 - Build synthetic fixture helpers (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC8)
  - [ ] Subtask 3.1 - Create or extend helpers under `backend/tests/unit/domain/astrology/fixtures/`.
  - [ ] Subtask 3.2 - Provide explicit builders for day/night chart sect,
    in/out-of-sect planets, hayz complete/incomplete and rejoicing.
  - [ ] Subtask 3.3 - Ensure helpers construct only the contracts needed for
    each test: dignity input/result, sect contracts, profiles, dominance or
    adapter inputs.
  - [ ] Subtask 3.4 - Do not add hidden doctrine helpers such as `make_valid_astrology_case`, `make_default_planet` or `make_magic_payload`.

- [ ] Task 4 - Add chart sect golden tests (AC: AC1)
  - [ ] Subtask 4.1 - Add `G1_day_chart`.
  - [ ] Subtask 4.2 - Add `G2_night_chart`.
  - [ ] Subtask 4.3 - Assert `chart_sect`, `sun_horizon_position`, `sun_above_horizon`, `calculation_basis` and `reference_system`.

- [ ] Task 5 - Add planet sect condition golden tests (AC: AC2, AC5)
  - [ ] Subtask 5.1 - Add G3 for a diurnal planet in a day chart.
  - [ ] Subtask 5.2 - Add G4 for a nocturnal planet in a night chart.
  - [ ] Subtask 5.3 - Add G5 for a diurnal planet out of sect in a night chart and assert advanced `out_of_sect`.
  - [ ] Subtask 5.4 - Add G6 for a nocturnal planet out of sect in a day chart and assert advanced `out_of_sect`.
  - [ ] Subtask 5.5 - Add G10 for Mercury and document the exact runtime classification in `golden-cases-index.md`.

- [ ] Task 6 - Add hayz golden tests (AC: AC3)
  - [ ] Subtask 6.1 - Add G7 where the planet is in sect, hemisphere condition passes and sign gender/polarity condition passes.
  - [ ] Subtask 6.2 - Add G8 where the planet is in sect but at least one non-sect hayz factor fails.
  - [ ] Subtask 6.3 - Assert hayz appears only in G7 and `out_of_sect` does not appear in G7.
  - [ ] Subtask 6.4 - Assert G8 has `sect_condition.is_in_sect == true` and no `hayz` advanced condition.

- [ ] Task 7 - Add rejoicing and essential dignity golden tests (AC: AC4, AC6)
  - [ ] Subtask 7.1 - Add G9 using a stable house-of-joy case, preferring an existing project-supported mapping.
  - [ ] Subtask 7.2 - Assert accidental breakdown contains the canonical rejoicing / joy condition and stable score contribution.
  - [ ] Subtask 7.3 - Add G11 using at least one stable essential dignity fact.
  - [ ] Subtask 7.4 - Assert `essential_breakdown`, `essential_score`, functional, expression and intensity scores within documented tolerance.

- [ ] Task 8 - Add full pipeline golden test (AC: AC7, AC11)
  - [ ] Subtask 8.1 - Add G12 with a stable integrated natal fixture.
  - [ ] Subtask 8.2 - Exercise `build_natal_result`, `NatalResult` and JSON projection where existing project conventions allow it.
  - [ ] Subtask 8.3 - Assert curated fields across dignity, advanced
    conditions, profiles, signals, dominance, adapter and `json_builder`.
  - [ ] Subtask 8.4 - Do not assert volatile ephemeris traces or full payload fields unrelated to the contracts.

- [ ] Task 9 - Add curated snapshot helper and after snapshot (AC: AC8, AC12)
  - [ ] Subtask 9.1 - Reuse existing snapshot tooling if present.
  - [ ] Subtask 9.2 - If no tooling exists, add a test-local helper under `backend/tests/unit/domain/astrology/fixtures/golden_snapshot.py`.
  - [ ] Subtask 9.3 - Normalize outputs into stable JSON with 6-decimal rounding for included floats.
  - [ ] Subtask 9.4 - Write `golden-cases-after.json` with all implemented case IDs.

- [ ] Task 10 - Validate and record evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [ ] Subtask 10.1 - Run all targeted tests, lint/format and scans from the validation plan after venv activation.
  - [ ] Subtask 10.2 - Record commands, outputs summary, scan hits, skipped commands and any score deltas in `golden-cases-validation.md`.
  - [ ] Subtask 10.3 - Confirm no production files changed unless a documented bug correction occurred.
  - [ ] Subtask 10.4 - Confirm no frontend, DB migration, seed, API route or dependency change occurred.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - `PlanetDignityInput`;
  - `PlanetDignityResult`;
  - `AdvancedConditionEngine`;
  - `PlanetConditionProfileService`;
  - `PlanetConditionSignalBuilder`;
  - `PlanetDominanceEngine`;
  - `InterpretationAdapterEngine`;
  - `json_builder.py`;
  - existing runtime reference fixtures and builders when available.
- Do not recreate:
  - production runtime lookup logic;
  - planet sect classification logic;
  - horizon house mapping logic;
  - hayz calculation logic;
  - dominance scoring logic;
  - interpretation adapter rule matching logic;
  - local planet sect constants, horizon constants or joy tables in production code.
- Shared abstraction allowed only if:
  - it lives in test helper scope;
  - it reduces duplicated fixture construction;
  - it makes tested facts explicit;
  - it cannot become a second production doctrine engine.

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
- `chart_sect_code`
- `planet_sect_code`
- `planet_sect_legacy`
- `sect_score_legacy`
- `legacy_planet_sect`
- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `SECT_PLANETS`
- `DAY_SECT_PLANETS`
- `NIGHT_SECT_PLANETS`
- `ABOVE_HORIZON_HOUSES`
- `BELOW_HORIZON_HOUSES`
- `JOY_HOUSES`
- `PLANETARY_JOYS`
- local horizon tuples/lists equivalent to `7, 8, 9, 10, 11, 12` or `1, 2, 3, 4, 5, 6` in production astrology/chart code
- `SectCalculator` imports in `condition`, `advanced_conditions`, `dominance`, `interpretation_adapters` or `json_builder.py`
- `PlanetSectConditionCalculator` imports in `condition`, `advanced_conditions`, `dominance`, `interpretation_adapters` or `json_builder.py`
- imports from `app.infra`, `app.api`, `app.services`, `app.domain.prediction`, OpenAI clients, `AIEngineAdapter`, `chat.completions` or `prompt` inside pure astrology domains.

Forbidden changes:

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/app/domain/prediction/**`
- `migrations/**`
- `docs/db_seeder/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | fixture helpers, downstream layers, JSON builder |
| Planet sect condition | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | fixture helpers, advanced conditions, dominance, adapters, JSON builder |
| Hayz / out-of-sect advanced condition | `backend/app/domain/astrology/advanced_conditions/**` | dignity calculators, JSON builder, test snapshot helper |
| Rejoicing accidental dignity | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | condition, dominance, adapters |
| Essential dignity | `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` | snapshot helper |
| Condition profile enrichment | `backend/app/domain/astrology/condition/**` | dominance and adapters |
| Condition signals | `backend/app/domain/astrology/condition/**` | prompts, frontend, adapters |
| Dominance | `backend/app/domain/astrology/dominance/**` | sect calculators, adapters |
| Interpretation adapter | `backend/app/domain/astrology/interpretation_adapters/**` | sect calculators, LLM, narration |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculation |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: conditional
- Reason: no API route is changed, but chart JSON must remain aligned with CS-197/CS-198 and any generated schema must not drift.
- Required generated-contract evidence:
  - `backend/app/tests/unit/test_chart_json_builder.py` passes;
  - `golden-cases-validation.md` states whether OpenAPI/generated clients were unaffected or, if inspected, records no relevant delta.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`

## 18. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md` - case provenance and invariants.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json` - baseline artifact.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json` - final curated snapshot.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md` - commands, results and deltas.
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` - G1-G12 targeted assertions.
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` - explicit deterministic fixture builders.
- `backend/tests/unit/domain/astrology/fixtures/golden_snapshot.py` - curated snapshot normalization if existing tooling is absent.

Likely tests:

- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` - primary golden suite.
- `backend/tests/unit/domain/astrology/test_sect_calculator.py` - existing chart-level sect guard.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` - existing dignity scoring and sect condition guard.
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` - hayz/out-of-sect guard.
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py` - canonical hayz projection guard.
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` - profile propagation guard.
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` - dominance propagation guard.
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` - adapter factual consumption guard.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - full pipeline contract guard.
- `backend/app/tests/unit/test_chart_json_builder.py` - public projection guard.
- `backend/app/tests/unit/test_chart_result_service.py` - chart result service stability if relevant.

Files not expected to change:

- `backend/app/domain/astrology/dignities/**` - production doctrine is out of scope unless a documented bug is found.
- `backend/app/domain/astrology/advanced_conditions/**` - production behavior is out of scope unless a documented bug is found.
- `backend/app/domain/astrology/condition/**` - production behavior is out of scope unless a documented bug is found.
- `backend/app/domain/astrology/dominance/**` - production behavior is out of scope unless a documented bug is found.
- `backend/app/domain/astrology/interpretation_adapters/**` - production behavior is out of scope unless a documented bug is found.
- `backend/app/services/chart/json_builder.py` - projection should already be stable; change only for documented bug correction.
- `frontend/**` - frontend is out of scope.
- `backend/app/api/**` - no route change.
- `backend/app/infra/**` - no persistence or repository change.
- `backend/app/domain/prediction/**` - prediction and LLM are out of scope.
- `migrations/**` - migrations are forbidden.
- `docs/db_seeder/**` - seed changes are forbidden.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes are not allowed in this story.

## 20. Validation Plan

Run from repository root after activating the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1

pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py

ruff format .
ruff check .

rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS" backend/app backend/tests/unit/domain/astrology -g "*.py"
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart backend/tests/unit/domain/astrology -g "*.py"
rg -n "SectCalculator" backend/app/domain/astrology/condition `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters `
  backend/app/services/chart -g "*.py"
rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" `
  backend/app/domain/astrology/condition `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters `
  backend/app/services/chart -g "*.py"

$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/condition `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"

Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md
Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json
Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json
Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md

rg -n "G1|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12" _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md
rg -n "hayz|out_of_sect|rejoicing|sect_condition|ChartSectResult|PlanetSectCondition|dominant_planets|interpretation_adapter" `
  _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence

python -m json.tool _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json
python -m json.tool _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json
```

Allowed scan results must be recorded in:

```text
_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md
```

## 21. Regression Risks

- Risk: snapshots trop larges et instables.
  - Guardrail: curated snapshot shape, targeted assertions and volatile fields excluded.
- Risk: tests qui dupliquent la logique métier.
  - Guardrail: helpers explicites, runtime source of truth, no local doctrine algorithms.
- Risk: confusion hayz / in_sect.
  - Guardrail: G8 asserts `is_in_sect=true` and no hayz.
- Risk: out-of-sect recalculé ailleurs.
  - Guardrail: G5/G6 assertions plus calculator-import and constant scans.
- Risk: Mercury hardcodé.
  - Guardrail: G10 documents exact runtime classification and rejects silent fallback.
- Risk: rejoicing déplacé hors dignity owner.
  - Guardrail: G9 asserts accidental dignity / condition impact through canonical owner.
- Risk: integrated fixture unstable due to ephemeris availability.
  - Guardrail: synthetic cases for doctrine; integrated case follows existing project deterministic or marked conventions.
- Risk: production behavior changes during a test-only story.
  - Guardrail: before/after evidence, production diff review and validation note.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-200.
- Treat CS-197, CS-198 and CS-199 as completed and canonical.
- Prefer tests, fixtures and evidence over production changes.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not change chart-level sect calculation.
- Do not change per-planet sect condition calculation.
- Do not change advanced sect scoring unless a bug is found and documented.
- Do not add local planet sect constants.
- Do not add local horizon constants.
- Do not add frontend changes.
- Do not add DB migrations or seed updates.
- Do not add narrative interpretation, prompts or LLM logic.
- Do not mark a task complete without validation evidence.
- Do not mark the story complete without all evidence files.
- If a required golden case cannot be produced, document the blocker and implement the remaining cases.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 23. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` - chart-level sect contract.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` - per-planet sect condition contract.
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` - advanced sect scoring integration.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` - dignity scoring context.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - condition profile context.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` - condition signal context.
- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - dominance context.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` - advanced conditions and hayz context.
- `_condamad/stories/CS-196-interpretation-adapter-layer/00-story.md` - interpretation adapter context.
- `_condamad/stories/regression-guardrails.md` - shared invariants consulted and extended with `RG-127`.
- `backend/app/domain/astrology/dignities/contracts.py` - canonical sect and dignity contracts.
- `backend/app/services/chart/json_builder.py` - public chart projection.
