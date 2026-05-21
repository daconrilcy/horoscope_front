# Story CS-206 benefic-malefic-sect-mitigation-signals: Exposer les signaux de mitigation des benefiques et malefiques par la secte

Status: ready-to-dev

## 1. Objective

Ajouter une couche factuelle, runtime-backed et explicable qui expose comment la
secte du theme module l'expression traditionnelle des planetes benefiques et
malefiques. CS-206 doit produire des contrats techniques
`SectNatureMitigationCondition`, des conditions avancees consommables et une
projection JSON additive, sans modifier les dignites essentielles,
accidentelles, scores existants, routes API, logique frontend ou interpretation
narrative.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-21 pour CS-206, follow-up de
  CS-197, CS-198, CS-199, CS-200, CS-204 et CS-205.
- Reason for change: la secte, la condition de secte par planete, hayz,
  rejoicing et la triplicite sect-aware sont couverts, mais il manque encore un
  fait technique normalise pour la modulation traditionnelle des benefiques et
  malefiques par la secte.
- Brief stakes:
  - le role benefique ou malefique de Mars, Saturne, Jupiter et Venus ne doit
    jamais venir d'un test sur le nom de planete;
  - la nature planetaire doit venir du runtime `astral_planet_natures`;
  - `PlanetSectCondition` et `ChartSectResult` restent les sources canoniques de
    secte;
  - les nouveaux signaux doivent etre consommables par les profils, signaux,
    adaptateurs et UI uniquement depuis des faits calcules et des poids runtime;
  - les scores de dignites doivent rester inchanges.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story couvre le probleme source complet en
  imposant audit runtime, contrat de forme, detection pure, integration
  pipeline, projection serialize-only, tests golden et scans anti-constantes;
  aucune preoccupation du brief n'est deplacee vers une future story.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/advanced_conditions`
- In scope:
  - auditer les natures planetaires runtime et les seeds de conditions
    avancees;
  - ajouter le contrat `SectNatureMitigationCondition`;
  - ajouter un detecteur pur de mitigation/aggravation par nature planetaire et
    `PlanetSectCondition`;
  - integrer les conditions dans `AdvancedConditionEngine` apres disponibilite
    de `PlanetSectCondition` et avant enrichissement des profils;
  - exposer le fait dans `traditional_conditions[planet].sect_nature_mitigation`
    si l'integration CS-204 existante le permet sans cycle;
  - serialiser les faits pre-calcules dans `json_builder.py`;
  - ajouter ou completer les seeds runtime uniquement si l'audit prouve que les
    codes ou poids manquent;
  - ajouter tests unitaires, golden cases, tests JSON et preuves persistantes;
  - mettre a jour le panneau expert frontend seulement si les nouveaux faits ne
    sont pas deja affichables via `advanced_conditions`.
- Out of scope:
  - modifier `SectCalculator`;
  - modifier `PlanetSectConditionCalculator`;
  - modifier hayz, rejoicing, triplicite ou dignites;
  - modifier les scores `essential_score`, `accidental_score`, `total_score`,
    `functional_strength_score`, `expression_quality_score` ou
    `intensity_score`;
  - modifier les routes API, methodes HTTP, status codes, migrations ou domaine
    prediction;
  - ajouter une interpretation narrative, un appel LLM ou une logique
    psychologique frontend.
- Explicit non-goals:
  - ne pas creer de constantes locales `BENEFIC_PLANETS`, `MALEFIC_PLANETS`,
    `MIXED_PLANETS`, `NEUTRAL_PLANETS`, `DIURNAL_MALEFICS`,
    `NOCTURNAL_MALEFICS`, `SECT_MITIGATED_PLANETS`, `MARS_SECT_RULE`,
    `SATURN_SECT_RULE`, `JUPITER_SECT_RULE` ou `VENUS_SECT_RULE`;
  - ne pas deduire une nature depuis `planet_code`;
  - ne pas faire de ces signaux une nouvelle source de dignite essentielle ou
    accidentelle;
  - ne pas rendre `json_builder.py` ou le frontend proprietaires de la logique;
  - ne pas ajouter de champ legacy, alias de compatibilite ou fallback
    silencieux.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story ajoute un nouveau contrat de condition avancee
  runtime-backed avec projection publique additive; aucun archetype supporte ne
  couvre a lui seul la combinaison detection pure, gouvernance seed runtime,
  contrat DTO, snapshots et guard frontend no-calculation.
- Additional validation rules:
  - les preuves runtime et comportementales sont obligatoires; un scan seul ne
    suffit pas;
  - toute seed ajoutee doit etre justifiee dans l'audit before et documentee
    dans la validation;
  - aucun score de dignite ne peut changer;
  - Mars, Saturne, Jupiter et Venus doivent etre verifies via runtime data, pas
    par logique nominale.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `advanced_conditions`, `traditional_conditions`,
    `planet_condition_profiles`, `planet_condition_signals` et
    `interpretation_adapter` peuvent recevoir des deltas additifs;
  - les deltas de profils, signaux et adaptateur doivent venir des seeds runtime
    existants ou ajoutes explicitement;
  - les blocs `dignities`, `dignities.sect`,
    `dignities.planets[*].sect_condition`, `traditional_conditions.hayz` et
    `traditional_conditions.rejoicing` doivent rester stables;
  - les scores de dignites et scores fonctionnels existants doivent rester
    inchanges.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: la nature planetaire runtime est absente ou ne peut
  pas etre consommee sans inventer des classifications locales.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les natures benefique/malefique et les poids doivent venir du runtime. |
| Baseline Snapshot | yes | Les deltas sur advanced conditions, profiles, signals, adapter et scores doivent etre compares. |
| Ownership Routing | yes | Chart sect, condition de secte, natures, detection, scoring et projection ont des owners distincts. |
| Allowlist Exception | no | Aucune exception large ou allowlist de doctrine locale n'est autorisee. |
| Contract Shape | yes | `SectNatureMitigationCondition` et la projection publique doivent avoir une forme explicite. |
| Batch Migration | no | Il ne s'agit pas d'une migration par lots. |
| Reintroduction Guard | yes | Les constantes locales benefiques/malefiques et derivations frontend doivent etre bloquees. |
| Persistent Evidence | yes | Audit, snapshots, validation et scans doivent rester attaches a CS-206. |

Brief-level contracts:

- No Dignity Score Change: les scores de dignites et les scores fonctionnels
  existants sont invariants.
- Runtime Weight Governance: tout impact downstream doit etre gouverne par les
  seeds runtime.
- Frontend No-Calculation Guard: le frontend affiche les faits; il ne les
  derive jamais.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AstrologyRuntimeReference`;
  - `AstrologyRuntimeReference.planet_natures`;
  - `AstrologyRuntimeReference.dignity_reference`;
  - `AstrologyRuntimeReference.advanced_condition_reference`;
  - `AstrologyRuntimeReference.condition_signal_profiles`;
  - `AstrologyRuntimeReference.interpretation_adapter_reference`;
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - `TraditionalPlanetCondition` when the CS-204 block is present.
- Runtime seed files to inspect:
  - `docs/db_seeder/astrology/astral_planet_natures.json`;
  - `docs/db_seeder/astrology/astral_advanced_condition_types.json`;
  - `docs/db_seeder/astrology/astral_advanced_condition_score_profiles.json`;
  - `docs/db_seeder/astrology/astral_advanced_condition_weights.json`;
  - `docs/db_seeder/astrology/astral_planet_condition_signal_profiles.json`;
  - `docs/db_seeder/astrology/astral_interpretation_signal_types.json`;
  - `docs/db_seeder/astrology/astral_interpretation_themes.json`;
  - `docs/db_seeder/astrology/astral_interpretation_adapter_rules.json`.
- Runtime artifact: loaded config object `AstrologyRuntimeReference` used by
  backend tests, plus AST guard / `rg` guard for forbidden imports and local
  doctrine constants.
  - loaded `AstrologyRuntimeReference` used by backend tests;
  - targeted detector tests with injected runtime natures;
  - advanced engine integration test;
  - curated before/after JSON snapshots;
  - runtime audit `sect-nature-runtime-audit-before.md`.
- Secondary evidence:
  - `rg` scans anti-constantes and anti-derivation;
  - JSON projection tests;
  - frontend tests if frontend is updated;
  - validation markdown with allowed scan hits.
- Static scans alone are not sufficient because:
  - absence of `BENEFIC_PLANETS` does not prove the detector consumes
    `AstrologyRuntimeReference.planet_natures`;
  - JSON presence does not prove the condition was calculated before
    projection;
  - profile or adapter deltas can only be trusted when tied to runtime weights.
- Forbidden sources:
  - planet name lists;
  - hardcoded benefic/malefic maps;
  - frontend constants;
  - JSON labels;
  - LLM output;
  - prompt hints.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-runtime-audit-before.md`
  - `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-after.json`
  - `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-validation.md`
- Comparison rule:
  - before snapshot must include cases for malefic in sect, malefic out of sect,
    benefic in sect, benefic out of sect and neutral/mixed/unknown when the
    runtime exposes such values;
  - if no prior mitigation fact exists, record that absence as valid JSON;
  - after snapshot must show additive condition codes only when runtime facts
    support them.
- Expected invariant:
  - dignity scores unchanged;
  - `dignities.sect` unchanged;
  - `dignities.planets[*].sect_condition` unchanged;
  - `traditional_conditions.hayz` unchanged;
  - `traditional_conditions.rejoicing` unchanged;
  - new condition codes appear only from runtime nature plus
    `PlanetSectCondition`;
  - downstream profile, signal and adapter deltas are additive and documented.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | CS-206 role | Forbidden destination |
|---|---|---|---|
| Chart sect | CS-197 `ChartSectResult` owner | consume | local chart sect recalculation |
| Per-planet sect condition | CS-198 `PlanetSectCondition` owner | consume | detector/frontend/json builder recalculation |
| Planet nature | `AstrologyRuntimeReference.planet_natures` / `astral_planet_natures` | consume | local planet lists |
| Sect nature mitigation detection | CS-206 detector in `advanced_conditions` | own | dignity calculators or frontend |
| Advanced condition weighting | `AdvancedConditionEngine` via runtime weights | consume emitted conditions | local score constants |
| Condition profiles/signals | existing condition profile and signal builders | consume runtime-weighted facts | detector-local signal thresholds |
| Interpretation adapter | existing adapter runtime rules | consume facts | narrative code or LLM |
| Public JSON | `backend/app/services/chart/json_builder.py` | serialize only | calculation or import of detectors |
| Frontend expert panel | CS-202 panel | display only when generic facts are insufficient | doctrine derivation |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: CS-206 forbids broad exceptions. Any scan hit must be documented in
  `sect-nature-mitigation-validation.md` as an exact, justified hit and cannot
  authorize production doctrine constants, frontend derivation or fallback
  behavior.

## 4f. Contract Shape

- Contract type:
  - new immutable domain DTO `SectNatureMitigationCondition`;
  - no aggregate is required; a `SectNatureMitigationResult` aggregate is
    allowed only if it removes duplicated conversion or grouping code without
    creating a second doctrine source;
  - public JSON serialization of precomputed values only.
- Fields:
  - `planet_code: str`
  - `planet_nature: str`
  - `chart_sect: str`
  - `intrinsic_sect: str`
  - `planet_sect_condition: str`
  - `is_in_sect: bool`
  - `is_out_of_sect: bool`
  - `mitigation_state: str`
  - `condition_code: str`
  - `condition_family: str`
  - `calculation_basis: str`
  - `reference_system: str`
  - `evidence: tuple of str`
- Required fields:
  - all fields listed above are required on the domain contract.
- Optional fields:
  - no optional field is allowed on `SectNatureMitigationCondition` unless the
    implementation documents a blocker and updates contract tests first.
- Allowed values:
  - `planet_nature`: `benefic`, `malefic`, `mixed`, `neutral`, `luminary`,
    `unknown`;
  - `chart_sect`: `day`, `night`;
  - `intrinsic_sect`: `diurnal`, `nocturnal`, `common`, `neutral`, `unknown`;
  - `planet_sect_condition`: `in_sect`, `out_of_sect`, `neutral_to_sect`,
    `variable_by_condition`, `unknown`;
  - `mitigation_state`: `mitigated`, `aggravated`, `supported`, `weakened`,
    `neutral`, `unknown`;
  - `condition_family`: `sect_nature_mitigation`;
  - `condition_code`: `malefic_mitigated_by_sect`,
    `malefic_aggravated_out_of_sect`, `benefic_supported_by_sect`,
    `benefic_weakened_out_of_sect`, `sect_nature_neutral`,
    `sect_nature_unknown`.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - public JSON uses snake_case names identical to contract fields;
  - forbidden public fields: `sect_mitigation_legacy`,
    `legacy_sect_mitigation`, `benefic_code`, `malefic_code`,
    `planet_nature_code_legacy`.
- Frontend type impact:
  - if the frontend type layer models `traditional_conditions` or
    `advanced_conditions`, add the new fields as consumed facts only;
  - no frontend inference from planet name, sign, house or sect is allowed.
- Generated contract impact:
  - no OpenAPI route or status code change is expected;
  - JSON contract tests must prove additivity and serialize-only behavior.

### 4f.1 Detection Semantics

| Runtime facts | condition_code | mitigation_state |
|---|---|---|
| `planet_nature == "malefic"` and `is_in_sect == true` | `malefic_mitigated_by_sect` | `mitigated` |
| `planet_nature == "malefic"` and `is_out_of_sect == true` | `malefic_aggravated_out_of_sect` | `aggravated` |
| `planet_nature == "benefic"` and `is_in_sect == true` | `benefic_supported_by_sect` | `supported` |
| `planet_nature == "benefic"` and `is_out_of_sect == true` | `benefic_weakened_out_of_sect` | `weakened` |
| `planet_nature in ("mixed", "neutral", "luminary")` | `sect_nature_neutral` | `neutral` |
| missing runtime nature | `sect_nature_unknown` | `unknown` |

The domain contract must expose the explicit neutral or unknown fact when a
planet is evaluated. Omitting an `AdvancedPlanetaryCondition` record is allowed
only when the runtime lacks the corresponding condition type or weight; that
omission must be recorded in validation evidence and must not suppress the
domain `SectNatureMitigationCondition` fact.

The detector must never branch on Mars, Saturn, Jupiter or Venus by name in
production code.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-206 adds one bounded runtime-backed condition family; there is no
  namespace, route, field or multi-batch migration.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime audit before | `evidence/sect-nature-runtime-audit-before.md` | Documenter natures, codes, poids, profils, signaux, adapter rules et besoins de seeds. |
| Before snapshot | `evidence/sect-nature-mitigation-before.json` | Capturer l'etat initial et les invariants avant detection. |
| After snapshot | `evidence/sect-nature-mitigation-after.json` | Capturer les nouveaux faits, deltas additifs et comparaison scores. |
| Validation summary | `evidence/sect-nature-mitigation-validation.md` | Enregistrer commandes, resultats, scans, seeds et limitations exactes. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher le retour de listes locales benefiques/malefiques, de logique
    Mars/Saturne/Jupiter/Venus par nom, de recalcul dans la projection et de
    derivation frontend.
- Forbidden production constants:
  - `BENEFIC_PLANETS`;
  - `MALEFIC_PLANETS`;
  - `MIXED_PLANETS`;
  - `NEUTRAL_PLANETS`;
  - `DIURNAL_MALEFICS`;
  - `NOCTURNAL_MALEFICS`;
  - `SECT_MITIGATED_PLANETS`;
  - `MARS_SECT_RULE`;
  - `SATURN_SECT_RULE`;
  - `JUPITER_SECT_RULE`;
  - `VENUS_SECT_RULE`.
- Forbidden production logic:
  - `if planet_code == "mars"`;
  - `if planet_code == "saturn"`;
  - `if planet_code == "jupiter"`;
  - `if planet_code == "venus"`;
  - `if planet_code in local collection`;
  - `if chart_sect == "day" and planet_code == local rule target`.
- Forbidden projection/frontend imports:
  - `SectCalculator`;
  - `PlanetSectConditionCalculator`;
  - `SectNatureMitigationDetector`;
  - `AdvancedConditionEngine`.
- Required guard evidence:
  - architecture guard or exact static guard command that fails when forbidden
    constants, local planet-name branches, projection imports or frontend
    derivations reappear;
  - targeted pytest for detector and engine;
  - JSON projection tests;
  - frontend tests if frontend changes;
  - negative `rg` scans listed in the validation plan;
  - validation artifact classifying any allowed hits.

## 4j. Missing / No-Time Behavior

- If birth time, chart sect or per-planet sect condition is unavailable or
  neutralized by the existing no-time calculation mode, CS-206 must not
  fabricate `sect_nature_mitigation`.
- If `PlanetSectCondition` is missing in the full calculation path, the
  implementation must either raise the existing explicit contract error or emit
  `sect_nature_unknown` only when the behavior is documented and tested.
- If runtime planet nature is missing, the implementation must emit
  `sect_nature_unknown` for an evaluated planet or document why no advanced
  condition record can be emitted; it must not coerce the planet to benefic,
  malefic or neutral.
- If no-time mode removes sect-dependent outputs, mitigation signals must be
  absent from domain facts, public JSON and frontend display.
- If a public field is absent or null because mitigation is not evaluable, the
  frontend must display only the existing unavailable/empty state and must not
  infer a replacement label.

## 4k. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - CS-197 through CS-205 are
  registered, and `CS-206` is the next sequential `CS-###` number.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared invariants
  consulted before story scope was finalized; this story adds `RG-133`.
- Evidence 3: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  `PlanetNatureReferenceSet.nature_for_planet()` exposes runtime-backed planet
  nature lookup.
- Evidence 4: `docs/db_seeder/astrology/astral_planet_natures.json` - current
  seed data includes `benefic` for Venus/Jupiter and `malefic` for
  Mars/Saturn; neutral, mixed, luminary and unknown behavior must be tested with
  injected runtime data or documented if absent from seeds.
- Evidence 5: `backend/app/domain/astrology/dignities/contracts.py` -
  `ChartSectResult` and `PlanetSectCondition` contracts exist and are attached
  to `PlanetDignityResult`.
- Evidence 6: `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py` -
  the engine already consumes runtime weights and enriches condition profiles
  from emitted advanced conditions.
- Evidence 7: `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` -
  CS-204 normalizes `hayz` and `rejoicing` from calculated facts, giving a
  possible integration point for `sect_nature_mitigation`.
- Evidence 8: `backend/app/services/chart/json_builder.py` - public JSON
  already serializes `advanced_conditions`, `traditional_conditions`,
  `planet_condition_signals` and `interpretation_adapter`.
- Evidence 9: drafting scan for the four mitigation codes and `sect_nature`
  over `docs/db_seeder/astrology`, `backend/app`, `backend/tests` and
  `frontend`
  returned no current hit during story drafting, so seed additions are likely
  required but must still be confirmed by the implementation audit.

## 6. Target State

After implementation:

- each evaluable planet can expose `sect_nature_mitigation`;
- malefics in sect produce `malefic_mitigated_by_sect`;
- malefics out of sect produce `malefic_aggravated_out_of_sect`;
- benefics in sect produce `benefic_supported_by_sect`;
- benefics out of sect produce `benefic_weakened_out_of_sect`;
- neutral, mixed, luminary and missing natures are handled explicitly;
- `advanced_conditions` contains the corresponding condition records when the
  runtime reference supports the condition type and weight;
- condition profiles, condition signals and interpretation adapter consume the
  facts only through runtime rules;
- public JSON serializes the new facts without calculation;
- frontend expert panel displays the facts without deriving doctrine if an
  update is required;
- no dignity score, sect fact, hayz fact, rejoicing fact, route, migration,
  dependency or LLM behavior changes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return.
  - `RG-118` - dignity calculators remain pure and runtime-backed.
  - `RG-122` - advanced conditions remain factual and runtime-weighted.
  - `RG-123` - interpretation adapter consumes runtime rules and no narrative
    code.
  - `RG-124` - chart-level sect contract remains canonical.
  - `RG-125` - per-planet sect condition remains canonical.
  - `RG-126` - advanced sect scoring consumes canonical facts.
  - `RG-127` - traditional golden cases remain stable.
  - `RG-128` - public JSON projection does not calculate astrology.
  - `RG-129` - frontend does not calculate astrology.
  - `RG-131` - hayz/rejoicing contracts do not become scoring sources.
  - `RG-132` - triplicity consumes runtime assignments and active chart sect.
  - `RG-133` - benefic/malefic sect mitigation consumes runtime planet nature
    and `PlanetSectCondition`, never local planet lists.
- Non-applicable invariants:
  - Stripe, billing, route-removal, frontend design-system-only and
    prediction-only guardrails are not touched.
- Required regression evidence:
  - runtime nature audit;
  - detector and engine unit tests;
  - traditional golden cases;
  - JSON projection tests;
  - frontend tests when frontend files change;
  - before/after snapshots;
  - scans for local doctrine constants, legacy fields and forbidden imports.
- Allowed differences:
  - additive `advanced_conditions` codes;
  - additive `traditional_conditions[*].sect_nature_mitigation` when integrated;
  - additive condition profile, signal and adapter effects if runtime-weighted;
  - seed additions for the new condition family if audit proves they are
    missing;
  - no dignity score differences expected.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime natures are audited. | Runtime evidence: loaded config object + `rg` audit command in section 20. |
| AC2 | `SectNatureMitigationCondition` exists. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC3 | Malefic in sect gives `mitigated`. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC4 | Malefic out of sect gives `aggravated`. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC5 | Benefic in sect gives `supported`. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC6 | Benefic out of sect gives `weakened`. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC7 | Non-evaluable natures are explicit. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC8 | Missing or no-time sect conditions do not fabricate mitigation signals. | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`. |
| AC9 | `AdvancedConditionEngine` consumes runtime-supported codes. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` + snapshot. |
| AC10 | Public JSON serializes precomputed facts only. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` + `rg` scan. |
| AC11 | Traditional conditions integrate or document non-integration. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. |
| AC12 | Downstream effects are runtime-governed. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. |
| AC13 | Listed score fields remain unchanged. | Before/after snapshot + `test_natal_result_contract.py` score invariants. |
| AC14 | Frontend displays facts without deriving them if frontend changes. | `npm run test -- NatalExpertPanel`; `npm run lint`; section 20 frontend `rg` scans. |
| AC15 | Local doctrine constants are absent. | `rg` anti-constant, anti-branch and compatibility scans in section 20. |
| AC16 | Evidence references runtime. | Runtime evidence: loaded config object; `Test-Path` and `rg` checks in section 20. |

## 8. Implementation Tasks

- [ ] Task 1 - Audit runtime planet natures and existing condition support (AC: AC1, AC12, AC16)
  - [ ] Subtask 1.1 - Inspect `advanced_conditions/**`, `dignities/contracts.py`,
    `planet_sect_condition_calculator.py`, `condition/**`,
    `interpretation_adapters/**`, `natal_calculation.py` and
    `json_builder.py`.
  - [ ] Subtask 1.2 - Inspect all seed files listed in section 4b.
  - [ ] Subtask 1.3 - Create `sect-nature-runtime-audit-before.md` answering:
    load path, available nature values, Mars/Saturn/Jupiter/Venus runtime
    representation, existing condition codes, weights, signal profiles, adapter
    rules and seed additions required.

- [ ] Task 2 - Capture before snapshot (AC: AC9, AC11, AC12, AC13, AC16)
  - [ ] Subtask 2.1 - Create `sect-nature-mitigation-before.json` with malefic
    in sect, malefic out of sect, benefic in sect, benefic out of sect and
    neutral/mixed/unknown where available.
  - [ ] Subtask 2.2 - Include `dignities.sect`,
    `dignities.planets[*].sect_condition`, `traditional_conditions`,
    `advanced_conditions`, `planet_condition_profiles`,
    `planet_condition_signals` and `interpretation_adapter`.
  - [ ] Subtask 2.3 - Record no existing mitigation facts if that is the current
    state; do not fake a prior payload.

- [ ] Task 3 - Add runtime seed data when audit proves it is missing (AC: AC9, AC12, AC16)
  - [ ] Subtask 3.1 - Add `sect_nature_mitigation` and the six condition codes
    to `astral_advanced_condition_types.json` when absent.
  - [ ] Subtask 3.2 - Add `astral_advanced_condition_weights.json` records only
    if downstream profile effects are required.
  - [ ] Subtask 3.3 - Add condition signal and interpretation adapter seed
    records when the existing runtime flow cannot consume the new facts.
  - [ ] Subtask 3.4 - Document exact seed file changes, codes and downstream
    impact in validation evidence.

- [ ] Task 4 - Add condition contracts (AC: AC2, AC7, AC11)
  - [ ] Subtask 4.1 - Add `SectNatureMitigationCondition` to
    `advanced_conditions/contracts.py` or an adjacent canonical module.
  - [ ] Subtask 4.2 - Extend `TraditionalPlanetCondition` with
    `sect_nature_mitigation` if CS-204 integration is viable without circular
    dependency.
  - [ ] Subtask 4.3 - Add contract tests for required fields, immutability and
    allowed values.

- [ ] Task 5 - Add pure detector / normalizer (AC: AC3, AC4, AC5, AC6, AC7, AC8, AC15)
  - [ ] Subtask 5.1 - Add
    `backend/app/domain/astrology/advanced_conditions/sect_nature_mitigation_detector.py`.
  - [ ] Subtask 5.2 - Consume `PlanetDignityResult.sect_condition`,
    `PlanetSectCondition`, runtime planet nature and runtime condition support.
  - [ ] Subtask 5.3 - Emit `SectNatureMitigationCondition` and advanced
    condition records through the existing emitter.
  - [ ] Subtask 5.4 - Raise or document explicit unknown behavior when
    `PlanetSectCondition` or runtime nature is missing; no silent coercion.
  - [ ] Subtask 5.5 - Add detector tests with injected runtime natures so the
    behavior is not tied to planet names.

- [ ] Task 6 - Integrate with `AdvancedConditionEngine` (AC: AC9, AC12, AC13, AC15)
  - [ ] Subtask 6.1 - Invoke the detector after `PlanetSectCondition` is
    available and before profile enrichment.
  - [ ] Subtask 6.2 - Ensure emitted condition weights come from
    `advanced_condition_reference.weights_for_profile`.
  - [ ] Subtask 6.3 - Assert no dignity score fields are mutated.

- [ ] Task 7 - Integrate traditional conditions and public JSON (AC: AC10, AC11, AC15)
  - [ ] Subtask 7.1 - Update `traditional_condition_normalizer.py` to attach
    `sect_nature_mitigation` from precomputed advanced facts after cycle checks
    pass.
  - [ ] Subtask 7.2 - Update `json_builder.py` to serialize precomputed facts
    only.
  - [ ] Subtask 7.3 - Add JSON tests proving no calculation imports appear in
    the projection.

- [ ] Task 8 - Update frontend expert panel only when existing display is insufficient (AC: AC14, AC15)
  - [ ] Subtask 8.1 - Inspect existing CS-202 panel display of
    `advanced_conditions`.
  - [ ] Subtask 8.2 - When the generic display is insufficient, add display
    labels for the four active mitigation codes using `condition_code`,
    `mitigation_state` and `planet_nature`.
  - [ ] Subtask 8.3 - Keep all styles in CSS/SCSS and reuse existing variables;
    no inline style or frontend doctrine constants.

- [ ] Task 9 - Add tests, snapshots and validation evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)
  - [ ] Subtask 9.1 - Add or update targeted backend tests listed in section 20.
  - [ ] Subtask 9.2 - Create `sect-nature-mitigation-after.json`.
  - [ ] Subtask 9.3 - Create `sect-nature-mitigation-validation.md` with
    commands, results, seed changes, snapshot comparison, dignity score
    invariants, downstream deltas, frontend validation and scan hits.
  - [ ] Subtask 9.4 - Run backend lint/tests after venv activation and frontend
    commands if frontend changed.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - `PlanetDignityResult`;
  - `AstrologyRuntimeReference.planet_natures`;
  - existing `AdvancedPlanetaryCondition` emitter and runtime weights;
  - existing condition profile enrichment flow;
  - existing condition signal builder;
  - existing interpretation adapter runtime rules;
  - existing `TraditionalConditionNormalizer`;
  - existing `json_builder.py` serializer patterns;
  - existing frontend expert panel when it already displays
    `advanced_conditions`.
- Do not recreate:
  - planet nature classification;
  - sect calculation;
  - planet sect condition calculation;
  - hayz;
  - rejoicing;
  - triplicity;
  - dignity scoring;
  - signal threshold logic;
  - interpretation adapter matching.
- Shared abstraction allowed only when:
  - it removes duplicated serialization or contract conversion in the existing
    advanced/traditional condition modules;
  - it does not introduce a second source of doctrine.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- local astrology constants in production;
- frontend or JSON builder doctrine derivation;
- seed additions without audit proof;
- DB migrations;
- LLM calls or prompt-based logic.

Specific forbidden production constants:

- `BENEFIC_PLANETS`
- `MALEFIC_PLANETS`
- `MIXED_PLANETS`
- `NEUTRAL_PLANETS`
- `DIURNAL_MALEFICS`
- `NOCTURNAL_MALEFICS`
- `SECT_MITIGATED_PLANETS`
- `MARS_SECT_RULE`
- `SATURN_SECT_RULE`
- `JUPITER_SECT_RULE`
- `VENUS_SECT_RULE`

Specific forbidden public fields:

- `sect_mitigation_legacy`
- `legacy_sect_mitigation`
- `benefic_code`
- `malefic_code`
- `planet_nature_code_legacy`

Specific forbidden paths unless blocker approved:

- `backend/app/api/**`
- `backend/app/domain/prediction/**`
- `migrations/**`

Specific forbidden imports in projection/frontend:

- `SectCalculator`
- `PlanetSectConditionCalculator`
- `SectNatureMitigationDetector`
- `AdvancedConditionEngine`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect | CS-197 `ChartSectResult` owner | detector-local sect calculation, frontend sect calculation |
| Planet sect condition | CS-198 `PlanetSectCondition` owner | JSON builder or frontend derivation |
| Planet nature | `AstrologyRuntimeReference.planet_natures` | local planet lists or name checks |
| Sect nature mitigation | CS-206 detector in `advanced_conditions` | dignity calculators, frontend, JSON builder |
| Profile impact | advanced condition runtime weights and profile enrichment | local detector weights |
| Condition signals | `PlanetConditionSignalBuilder` runtime profiles | frontend thresholds |
| Interpretation adapter | `InterpretationAdapterEngine` runtime rules | narrative logic or LLM |
| Public JSON | CS-201 `json_builder.py` projection | calculation imports |
| Frontend expert panel | CS-202 panel | doctrine rules |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API route, method, status code or generated client change
  is expected.
- Required generated-contract evidence:
  - JSON projection test proves additive fields;
  - validation markdown states no route/status-code change;
  - OpenAPI regeneration is not required unless the project treats natal JSON
    DTOs as generated contracts.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `docs/db_seeder/astrology/astral_planet_natures.json`
- `docs/db_seeder/astrology/astral_advanced_condition_types.json`
- `docs/db_seeder/astrology/astral_advanced_condition_weights.json`
- `docs/db_seeder/astrology/astral_planet_condition_signal_profiles.json`
- `docs/db_seeder/astrology/astral_interpretation_signal_types.json`
- `docs/db_seeder/astrology/astral_interpretation_themes.json`
- `docs/db_seeder/astrology/astral_interpretation_adapter_rules.json`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `frontend/**`

Also inspect any runtime fixture builders discovered by:

```powershell
rg -n "AstrologyRuntimeReference|planet_natures|nature_for_planet|PlanetSectCondition" backend/tests backend/app -g "*.py"
```

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/advanced_conditions/contracts.py` - add
  `SectNatureMitigationCondition` and extend
  `TraditionalPlanetCondition`.
- `backend/app/domain/astrology/advanced_conditions/sect_nature_mitigation_detector.py` -
  pure detector.
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py` -
  pipeline integration.
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` -
  traditional block integration after cycle checks pass.
- `backend/app/domain/astrology/natal_calculation.py` - wire new precomputed
  facts only after result-shape audit requires it.
- `backend/app/services/chart/json_builder.py` - serialize precomputed facts.
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-runtime-audit-before.md` -
  runtime audit.
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-before.json` -
  baseline snapshot.
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-after.json` -
  after snapshot.
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-validation.md` -
  validation summary.

Possible seed files:

- `docs/db_seeder/astrology/astral_advanced_condition_types.json` - condition
  family/code support if missing.
- `docs/db_seeder/astrology/astral_advanced_condition_weights.json` - runtime
  weights if profile deltas are required.
- `docs/db_seeder/astrology/astral_planet_condition_signal_profiles.json` -
  signal profiles when the audit proves the profiles are missing.
- `docs/db_seeder/astrology/astral_interpretation_signal_types.json` - signal
  types if adapter rules require new signal codes.
- `docs/db_seeder/astrology/astral_interpretation_themes.json` - themes if no
  existing theme is appropriate.
- `docs/db_seeder/astrology/astral_interpretation_adapter_rules.json` - adapter
  rules if interpretation adapter must consume new facts.

Likely tests:

- `backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/tests/unit/domain/astrology/test_runtime_reference_loading.py` if
  runtime seeds changed.
- `frontend/**/NatalExpertPanel.test.*` if frontend changed.

Files not expected to change:

- `backend/app/api/**` - no route/API change.
- `backend/app/domain/prediction/**` - prediction and LLM are out of scope.
- `migrations/**` - no DB schema migration expected.
- `backend/app/domain/astrology/dignities/sect_calculator.py` - chart sect is
  consumed only.
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` -
  per-planet sect condition is consumed only.
- dignity calculators - no essential/accidental dignity recalculation change.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only when explicitly listed here with
  justification.
- Dependency changes are not allowed for CS-206.

## 20. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted backend tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
```

If runtime seeds changed:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_runtime_reference_loading.py
```

Frontend when frontend files change:

```powershell
cd frontend
npm test -- NatalExpertPanel
npm run typecheck
npm run lint
npm run build
cd ..
```

Quality:

```powershell
ruff format .
ruff check .
```

Anti-constant scans:

```powershell
$natureConstants = @(
  "BENEFIC_PLANETS",
  "MALEFIC_PLANETS",
  "MIXED_PLANETS",
  "NEUTRAL_PLANETS",
  "DIURNAL_MALEFICS",
  "NOCTURNAL_MALEFICS",
  "SECT_MITIGATED_PLANETS",
  "MARS_SECT_RULE",
  "SATURN_SECT_RULE",
  "JUPITER_SECT_RULE",
  "VENUS_SECT_RULE"
) -join "|"
rg -n $natureConstants backend/app frontend -g "*.{py,ts,tsx,js,jsx}"
$natureBranches = @(
  "if .*planet_code.*mars",
  "if .*planet_code.*saturn",
  "if .*planet_code.*jupiter",
  "if .*planet_code.*venus",
  "planet_code\s+in"
) -join "|"
rg -n $natureBranches backend/app/domain/astrology frontend -g "*.{py,ts,tsx,js,jsx}"
```

Legacy scans:

```powershell
rg -n "sect_mitigation_legacy|legacy_sect_mitigation|benefic_code|malefic_code|planet_nature_code_legacy" backend/app backend/tests frontend -g "*.{py,ts,tsx,js,jsx}"
```

Projection/frontend no-calculation scans:

```powershell
rg -n "SectCalculator|PlanetSectConditionCalculator|SectNatureMitigationDetector|AdvancedConditionEngine" backend/app/services/chart frontend -g "*.{py,ts,tsx,js,jsx}"
```

Forbidden imports in pure astrology domains:

```powershell
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition backend/app/domain/astrology/interpretation_adapters -g "*.py"
```

Evidence checks:

```powershell
Test-Path _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-runtime-audit-before.md
Test-Path _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-before.json
Test-Path _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-after.json
Test-Path _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-validation.md
$evidenceTerms = @(
  "malefic_mitigated_by_sect",
  "malefic_aggravated_out_of_sect",
  "benefic_supported_by_sect",
  "benefic_weakened_out_of_sect",
  "planet_nature",
  "no dignity score change",
  "runtime"
) -join "|"
rg -n $evidenceTerms _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence
python -m json.tool _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-before.json
python -m json.tool _condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/evidence/sect-nature-mitigation-after.json
```

Story validation commands:

```powershell
$story = "_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 21. Regression Risks

- Risk: local benefic/malefic planet lists are introduced for convenience.
  - Guardrail: runtime nature audit, injected runtime nature tests and
    anti-constant scans.
- Risk: nature and intrinsic sect are confused.
  - Guardrail: contract exposes both `planet_nature` and `intrinsic_sect`;
    tests separate nature from `PlanetSectCondition`.
- Risk: dignity scores change accidentally.
  - Guardrail: before/after snapshots and explicit score invariants.
- Risk: downstream profile or adapter effects are hardcoded.
  - Guardrail: runtime seed documentation and tests through existing builders.
- Risk: frontend derives mitigation from planet names.
  - Guardrail: frontend scans and `NatalExpertPanel` tests when frontend files
    change.
- Risk: unknown nature is silently coerced.
  - Guardrail: missing nature test and documented `sect_nature_unknown` or skip
    behavior.
- Risk: public JSON diverges from domain facts.
  - Guardrail: JSON projection tests and no-calculation scans.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-206.
- Treat CS-197 through CS-205 as canonical.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not change sect calculation.
- Do not change planet sect condition calculation.
- Do not change hayz, rejoicing, triplicity, essential dignity or accidental
  dignity logic.
- Do not change dignity scores.
- Do not hardcode benefic/malefic planet lists.
- Do not branch on Mars, Saturn, Jupiter or Venus by name in production.
- Use runtime planet nature as source of truth.
- Add seed records when audit proves they are missing.
- Do not add DB migrations unless a blocker is documented and approved.
- Do not add narrative interpretation.
- Do not add LLM calls.
- Do not let frontend derive mitigation.
- Do not mark a task complete without validation evidence.
- Do not mark the story complete without all evidence files.
- If runtime planet nature is unavailable, document the blocker instead of
  inventing doctrine.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 23. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` - chart
  sect contract.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` -
  per-planet sect condition contract.
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` -
  advanced sect scoring integration.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md` -
  traditional golden case baseline.
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md` -
  hayz/rejoicing traditional condition contracts.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` -
  sect-aware triplicity guardrail context.
- `_condamad/stories/regression-guardrails.md` - applicable invariants and
  `RG-133`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - runtime planet
  nature contracts.
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py` -
  advanced condition pipeline.
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` -
  traditional facts normalization.
- `backend/app/services/chart/json_builder.py` - public JSON projection.
- `docs/db_seeder/astrology/astral_planet_natures.json` - runtime planet nature
  seed reference.
