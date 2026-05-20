# Story CS-199 advanced-sect-scoring-integration: Integrer la condition de secte normalisee dans les scores avances

Status: done

## 1. Objective

Aligner la chaine de scoring astrologique avance sur les contrats livres par
CS-197 et CS-198: `ChartSectResult` reste la source canonique de la secte du
theme, et `PlanetSectCondition` reste la source canonique de la condition de
secte par planete. Les dignites, conditions avancees, profils conditionnels,
dominantes et adaptateur interpretatif doivent consommer ces faits deja
produits, sans recalcul local, sans inference depuis des strings ou breakdowns,
et sans confondre hayz avec `in_sect`.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-20, follow-up CS-197
  `sect-audit-explicit-contract` et CS-198
  `planet-sect-condition-normalization`.
- Reason for change: CS-197 a rendu explicite la secte globale du theme et
  CS-198 a rendu explicite la condition de secte par planete; les couches
  avancees doivent maintenant consommer ces contrats au lieu de conserver des
  logiques paralleles ou implicites.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology`
- In scope:
  - auditer et ajuster la propagation de `ChartSectResult` et
    `PlanetSectCondition` dans `dignities`, `condition`,
    `advanced_conditions`, `dominance` et `interpretation_adapters`;
  - faire consommer `PlanetSectCondition.is_out_of_sect` par
    `AdvancedConditionEngine` pour `out_of_sect`;
  - faire consommer `PlanetSectCondition.is_in_sect` comme precondition de
    secte pour hayz, tout en gardant les autres criteres hayz dans
    `AdvancedConditionEngine`;
  - verifier que `PlanetConditionProfileService`, `PlanetDominanceEngine` et
    `InterpretationAdapterEngine` consomment les faits enrichis sans devenir
    proprietaires de doctrine de secte;
  - ajouter les tests d'integration unitaire cibles, snapshots avant/apres,
    scans anti-recalcul et evidence persistante.
- Out of scope:
  - modifier les regles astrologiques de secte;
  - modifier le calcul de `ChartSectResult`;
  - modifier le calcul de `PlanetSectCondition`;
  - modifier les regles de hayz au-dela de la consommation de la precondition
    canonique de secte;
  - modifier les regles de rejoicing ou triplicite;
  - modifier les poids runtime sauf bug de double-scoring prouve et documente;
  - ajouter des tables DB, migrations, seed changes ou dependances;
  - modifier le frontend React;
  - generer du texte narratif, des prompts, une interpretation LLM, une route,
    une methode HTTP ou un code de statut.
- Explicit non-goals:
  - ne pas creer un second moteur de secte;
  - ne pas recalculer `in_sect`, `out_of_sect`, `hayz` ou `sect_condition`
    dans les couches aval;
  - ne pas ajouter de fallback silencieux, champ legacy ou alias public;
  - ne pas changer la forme publique de `dignities.sect` livree par CS-197;
  - ne pas changer la forme publique de
    `dignities.planets[*].sect_condition` livree par CS-198, sauf correction
    documentee;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`,
    `RG-121`, `RG-122`, `RG-123`, `RG-124`, `RG-125` ou `RG-126`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story securise la consommation de contrats runtime deja
  livres dans les couches de scoring avance, sans changer la doctrine ni la
  source runtime.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `ChartSectResult` reste la seule source de verite pour la secte du theme;
  - `PlanetSectCondition` reste la seule source de verite pour la condition de
    secte par planete;
  - les couches aval peuvent consommer ces contrats mais ne peuvent pas les
    reconstruire;
  - les scores restent stables si l'ancien calcul etait deja equivalent;
  - toute difference de score doit etre expliquee par suppression d'un
    double-scoring, correction d'une incoherence locale ou alignement sur les
    poids runtime existants;
  - aucun comportement frontend, schema DB, route, methode HTTP ou code de
    statut n'est modifie;
  - aucune compatibilite legacy n'est ajoutee.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une condition avancee dependante de la secte ne
  peut pas recevoir `PlanetSectCondition`; dans ce cas, documenter le blocker
  plutot que d'inventer un default, une comparaison locale ou un fallback.

## 4a. Required Contracts

La story doit conserver les contrats selectionnes depuis l'archetype et son
perimetre.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les faits de secte viennent de CS-197/CS-198 et les poids des references runtime. |
| Baseline Snapshot | yes | les scores et sorties avancees doivent etre compares avant/apres. |
| Ownership Routing | yes | chaque responsabilite de secte doit rester chez son owner canonique. |
| Allowlist Exception | yes | les seuls hits de scan toleres doivent etre exacts, documentes et limites a l'evidence; aucune exception d'implementation large n'est autorisee. |
| Contract Shape | yes | les formes CS-197/CS-198 doivent etre preservees et consommees sans champ legacy. |
| Batch Migration | no | la story n'autorise pas une migration par lots ni des surfaces paralleles. |
| Reintroduction Guard | yes | les recalculs locaux et imports interdits doivent etre bloques. |
| Persistent Evidence | yes | snapshots, audits, commandes et scans doivent rester dans le dossier de story. |
| Score Stability | yes | l'integration ne doit pas modifier les scores sauf correction prouvee et documentee. |
| Downstream Ownership Guard | yes | condition, dominance, signaux et adapter ne doivent pas devenir proprietaires de la secte. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - configuration runtime chargee `AstrologyRuntimeReference` utilisee par les
    tests de scoring et les guards AST/imports pour les frontieres de domaine;
  - `ChartSectResult` produit par CS-197;
  - `PlanetSectCondition` produit par CS-198;
  - `AstrologyRuntimeReference.dignity_reference`;
  - `AstrologyRuntimeReference.advanced_condition_reference`;
  - `AstrologyRuntimeReference.dominance_reference`;
  - `AstrologyRuntimeReference.interpretation_adapter_reference`.
- Runtime scoring sources:
  - `astral_advanced_condition_types`;
  - `astral_advanced_condition_score_profiles`;
  - `astral_advanced_condition_weights`;
  - `astral_dominance_factor_types`;
  - `astral_dominance_score_profiles`;
  - `astral_dominance_score_weights`;
  - `astral_interpretation_signal_types`;
  - `astral_interpretation_themes`;
  - `astral_interpretation_adapter_rules`.
- Secondary evidence:
  - tests unitaires cibles;
  - tests d'integration du pipeline natal;
  - snapshots avant/apres;
  - scans anti-recalcul, anti-constantes locales et anti-imports interdits;
  - validation que `json_builder.py` ne fait que projeter.
- Static scans alone are not sufficient for this story because:
  - un downstream peut ne pas importer `SectCalculator` mais reconstruire
    fonctionnellement une condition de secte depuis des strings, breakdowns ou
    listes locales.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-before.json`
  - `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-pipeline-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-after.json`
  - `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-validation.md`
- Required snapshot content:
  - `dignities.sect`;
  - `dignities.planets[*].sect_condition`;
  - `advanced_conditions`;
  - `planet_condition_profiles`;
  - `planet_condition_signals`;
  - `dominant_planets`;
  - `interpretation_adapter`.
- Required cases:
  - theme diurne avec planete diurne `in_sect`;
  - theme diurne avec planete nocturne `out_of_sect`;
  - theme nocturne avec planete nocturne `in_sect`;
  - theme nocturne avec planete diurne `out_of_sect`;
  - hayz complet;
  - hayz incomplet car condition de secte non conforme;
  - Mercure ou planete variable/commune si le runtime la definit.
- Expected invariants:
  - `dignities.sect` reste conforme a CS-197;
  - `dignities.planets[*].sect_condition` reste conforme a CS-198;
  - `advanced_conditions` utilise les faits de secte normalises;
  - profils, signaux, dominantes et adaptateur interpretatif restent
    coherents;
  - les scores restent identiques sauf correction documentee;
  - aucun champ legacy ou alias n'est ajoute.
- Allowed differences:
  - aucune difference publique attendue par defaut;
  - score delta autorise seulement s'il est documente comme correction de
    double-scoring ou d'incoherence entre logique locale et contrat canonique;
  - toute difference dans `advanced_conditions`, `planet_condition_profiles`,
    `planet_condition_signals`, `dominant_planets` ou
    `interpretation_adapter` doit etre expliquee dans
    `advanced-sect-validation.md`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | downstream layers and `json_builder.py` |
| Planet sect condition calculation | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | downstream layers and `json_builder.py` |
| Out-of-sect advanced condition detection | `backend/app/domain/astrology/advanced_conditions/**` consuming `is_out_of_sect` | dignity calculators, JSON builder, profiles |
| Hayz advanced condition detection | `backend/app/domain/astrology/advanced_conditions/**` consuming `is_in_sect` as prerequisite only | dignity calculators, JSON builder |
| Condition profile enrichment | `backend/app/domain/astrology/condition/**` | sect calculators, dominance, adapters |
| Dominance scoring | `backend/app/domain/astrology/dominance/**` | sect calculators, adapters |
| Interpretation adaptation | `backend/app/domain/astrology/interpretation_adapters/**` | sect calculators, prompt or LLM layers |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculators |

- Validation evidence:
  - targeted tests prove consumption paths;
  - scans prove forbidden imports and constants are absent;
  - pipeline audit documents any allowed scan hit.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `evidence/advanced-sect-validation.md` | resultats exacts des scans enregistres | Hits limites a l'evidence prouvant l'absence de moteur local de secte. | Evidence permanente uniquement; aucune exception d'implementation. |

## 4f. Contract Shape

- Contract type:
  - existing domain DTO and public JSON contracts from CS-197/CS-198.
- Fields:
  - `ChartSectResult.chart_sect: str`
  - `ChartSectResult.sun_horizon_position: str`
  - `ChartSectResult.sun_above_horizon: bool`
  - `ChartSectResult.calculation_basis: str`
  - `ChartSectResult.reference_system: str`
  - `PlanetSectCondition.planet_code: str`
  - `PlanetSectCondition.chart_sect: str`
  - `PlanetSectCondition.intrinsic_sect: str`
  - `PlanetSectCondition.planet_sect_condition: str`
  - `PlanetSectCondition.is_in_sect: bool`
  - `PlanetSectCondition.is_out_of_sect: bool`
  - `PlanetSectCondition.calculation_basis: str`
  - `PlanetSectCondition.reference_system: str`
- Required fields:
  - all listed fields are required for canonical runtime results.
- Optional fields:
  - none for new public contracts in this story.
- Status codes:
  - aucun endpoint HTTP ni code de statut n'est modifie.
- Serialization names:
  - `dignities.sect`;
  - `dignities.planets[*].sect_condition`;
  - forbidden new public fields: `sect_code`, `chart_sect_code`,
    `planet_sect_code`, `sect_legacy`, `legacy_sect`,
    `sect_score_legacy`, `sect_scoring_legacy`.
- Frontend type impact:
  - no frontend change in this story.
- Generated contract impact:
  - conditional; if chart JSON is represented in OpenAPI or generated clients,
    evidence must show no shape drift except documented correction.
- Compatibility decision:
  - no compatibility alias, fallback field or legacy projection is allowed.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: the story updates one backend astrology pipeline and must not create
  parallel migrated surfaces.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| snapshot scoring avant | `evidence/advanced-sect-scoring-before.json` | Capturer les sorties de theme selectionnees avant implementation. |
| audit pipeline avant | `evidence/advanced-sect-pipeline-before.md` | Auditer la detection actuelle de `out_of_sect` et de hayz. |
| snapshot scoring apres | `evidence/advanced-sect-scoring-after.json` | Prouver la stabilite des scores et de la forme du contrat apres implementation. |
| synthese de validation | `evidence/advanced-sect-validation.md` | Conserver commandes, scans, comparaison et deltas de score. |

## 4i. Reintroduction Guard

- Guard target:
  - prevent local sect recalculation in advanced conditions, condition
    profiles, dominance, interpretation adapters and JSON projection.
- Forbidden examples:
  - `out_of_sect = chart_sect == "day" and planet in nocturnal_planets`;
  - `hayz = chart_sect == planet_sect and planet_above_horizon and sign_gender_match`;
  - local `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`,
    `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`, `ABOVE_HORIZON_HOUSES` or
    `BELOW_HORIZON_HOUSES`;
  - downstream imports of `SectCalculator` or `PlanetSectConditionCalculator`;
  - legacy public fields listed in `4f`.
- Architecture guard against reintroduction:
  - the validation plan must run deterministic forbidden symbols scans and
    targeted tests so reintroduced sect calculators, local constants or legacy
    aliases fail review.
- Deterministic sources:
  - forbidden symbols;
  - importable Python modules through targeted pytest files;
  - AST guard or static import scans recorded in evidence.
- Required guard evidence:
  - targeted unit tests for `out_of_sect`, hayz and missing
    `PlanetSectCondition`;
  - scans listed in the validation plan;
  - `advanced-sect-validation.md` records zero-hit expectations and exact
    tolerated evidence hits.
- Executable guard commands:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py
rg -n "SectCalculator|PlanetSectConditionCalculator|planet_sect_condition_calculator" `
  backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters `
  backend/app/services/chart -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS" `
  backend/app backend/tests -g "*.py"
rg -n "ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|sect_legacy|legacy_sect|sect_code|planet_sect_code" `
  backend/app backend/tests -g "*.py"
```

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 4k. Score Integration Contract

The functional integration path after implementation must remain:

```text
ChartSectResult
  -> PlanetSectCondition
    -> PlanetDignityResult
      -> AdvancedConditionEngine
        -> PlanetConditionProfileService
          -> PlanetConditionSignalBuilder
            -> PlanetDominanceEngine
              -> InterpretationAdapterEngine
```

Rules:

1. `ChartSectResult` is computed once per chart.
2. `PlanetSectCondition` is computed once per planet.
3. `AdvancedConditionEngine` may consume `PlanetSectCondition`.
4. `AdvancedConditionEngine` must not recompute chart sect.
5. `AdvancedConditionEngine` must not recompute intrinsic planet sect.
6. Hayz may depend on `PlanetSectCondition.is_in_sect`, but only as the sect
   prerequisite.
7. Hayz must still require the non-sect hayz factors: hemisphere condition,
   sign gender or polarity condition, and any other runtime-defined hayz
   factor.
8. `out_of_sect` must be derived from
   `PlanetSectCondition.is_out_of_sect`, not from a second comparison.
9. `PlanetConditionProfileService` consumes enriched conditions and runtime
   weights.
10. `PlanetConditionSignalBuilder` consumes condition facts without encoding
    local sect thresholds or prompts.
11. `PlanetDominanceEngine` consumes condition profiles, advanced conditions
    and runtime dominance weights.
12. `InterpretationAdapterEngine` consumes semantic facts and must not contain
    sect doctrine.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/dignities/contracts.py` -
  `ChartSectResult`, `PlanetSectCondition` and
  `PlanetDignityResult.sect_condition` exist after CS-197/CS-198.
- Evidence 2:
  `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
  - per-planet sect is derived in the dignity domain from chart sect and
  runtime accidental sect rules.
- Evidence 3:
  `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` -
  current hayz/out-of-sect projection reads accidental dignity breakdown codes
  `hayz` and `out_of_sect`; this is the main surface to audit against
  canonical `PlanetSectCondition`.
- Evidence 4:
  `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
  - conditions are emitted via runtime `advanced_condition_reference` weights
  and then enrich condition profiles.
- Evidence 5:
  `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
  - condition profiles are derived from `PlanetDignityResult` and runtime
  weights, with no direct sect calculator import observed.
- Evidence 6:
  `backend/app/domain/astrology/dominance/planet_dominance_engine.py` -
  dominance consumes condition profiles and advanced conditions for scoring.
- Evidence 7:
  `backend/app/domain/astrology/interpretation_adapters/interpretation_adapter_engine.py`
  - the adapter consumes profiles, signals, advanced conditions and dominant
  planets without owning sect doctrine.
- Evidence 8: `backend/app/services/chart/json_builder.py` - projection
  serializes `dignities.sect` and per-planet `sect_condition` from precomputed
  data and must remain a projection layer only.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - shared invariants
  consulted before story scope was finalized; `RG-124`, `RG-125` and `RG-126`
  directly protect the contracts consumed by this story.

## 6. Target State

After implementation:

- the full advanced scoring pipeline consumes canonical sect facts;
- `AdvancedConditionEngine` derives `out_of_sect` from
  `PlanetSectCondition.is_out_of_sect`;
- hayz uses `PlanetSectCondition.is_in_sect` only as the sect prerequisite and
  still requires the non-sect hayz factors;
- condition profiles receive sect impact through dignity breakdowns, advanced
  conditions and runtime weights only;
- dominance receives sect impact only through approved advanced
  condition/profile inputs and runtime dominance weights;
- interpretation adapter receives semantic facts only and contains no sect
  doctrine;
- JSON projection preserves the CS-197/CS-198 public shapes;
- tests and evidence prove day/night, in-sect, out-of-sect and hayz stability.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return in backend
    astrology.
  - `RG-118` - dignity calculators remain pure, runtime-backed and free of
    DB/API/services/prediction/LLM dependencies.
  - `RG-119` - condition profiles remain derived from dignity results and
    advanced facts, not a second sect engine.
  - `RG-120` - condition signals must not encode sect thresholds or prompts
    locally.
  - `RG-121` - dominance engine consumes approved factors and does not own
    astrology doctrine.
  - `RG-122` - advanced conditions consume factual dignity outputs without
    local sect recalculation.
  - `RG-123` - interpretation adapter consumes facts and does not become a sect
    calculator.
  - `RG-124` - chart-level sect contract from CS-197 remains canonical.
  - `RG-125` - per-planet sect condition from CS-198 remains canonical.
  - `RG-126` - advanced sect scoring may only consume canonical sect contracts
    and runtime weights.
- Non-applicable invariants:
  - frontend design-system invariants are not applicable because no frontend
    files are in scope.
  - API route invariants are not applicable because no route, method or status
    code changes.
- Required regression evidence:
  - targeted pytest commands;
  - before/after JSON snapshots;
  - pipeline audit markdown;
  - scans for local sect constants, forbidden imports and downstream
    recalculation;
  - validation that public JSON remains aligned with CS-197/CS-198.
- Allowed differences:
  - no public shape change expected by default;
  - score differences only when documented as correction of duplicate or
    inconsistent sect scoring.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `out_of_sect` uses `PlanetSectCondition.is_out_of_sect`. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. |
| AC2 | Hayz sect prerequisite uses `PlanetSectCondition.is_in_sect`. | `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py`. |
| AC3 | Hayz still requires non-sect hayz factors and is not reduced to `in_sect`. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. |
| AC4 | Missing `PlanetSectCondition` fails explicitly. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. |
| AC5 | Profiles consume runtime-weighted advanced facts only and do not recalculate sect. | Loaded runtime config; `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`; forbidden scans. |
| AC6 | Dominance consumes condition/profile factors without sect recomputation. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`; forbidden scans. |
| AC7 | Interpretation adapter consumes facts only. | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`; forbidden scans. |
| AC8 | Day/night score outputs stay stable where prior logic was equivalent. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`; `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-before.json`; `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-after.json`. |
| AC9 | Score deltas are documented. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`; `rg -n "score delta" _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-validation.md`. |
| AC10 | Forbidden sect patterns remain absent. | `rg` scans in validation plan; hits recorded in `advanced-sect-validation.md`. |
| AC11 | Public JSON shape remains CS-197/CS-198-compatible. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`; snapshot comparison. |
| AC12 | Persistent evidence files are complete. | `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-before.json`; `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-after.json`; evidence `rg`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline and audit pipeline (AC: AC8, AC9, AC10, AC12)
  - [ ] Subtask 1.1 - Create
    `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/`.
  - [ ] Subtask 1.2 - Capture
    `advanced-sect-scoring-before.json` with the required snapshot content and
    seven required cases.
  - [ ] Subtask 1.3 - Write `advanced-sect-pipeline-before.md` answering:
    where `out_of_sect` is detected, where hayz is detected, whether any
    downstream layer compares chart/planet sect, inspects Sun horizon, contains
    local diurnal/nocturnal planet lists, or inspects horizon house constants.

- [ ] Task 2 - Audit and adjust `AdvancedConditionEngine` (AC: AC1, AC2, AC3, AC4, AC10)
  - [ ] Subtask 2.1 - Inspect
    `backend/app/domain/astrology/advanced_conditions/**`.
  - [ ] Subtask 2.2 - Replace local or breakdown-based sect comparisons for
    `out_of_sect` with `planet_dignity_result.sect_condition.is_out_of_sect`.
  - [ ] Subtask 2.3 - Replace the sect prerequisite of hayz with
    `planet_dignity_result.sect_condition.is_in_sect`.
  - [ ] Subtask 2.4 - Keep non-sect hayz factors in the advanced condition
    owner: hemisphere condition, sign gender/polarity condition and any other
    runtime-defined hayz factor.
  - [ ] Subtask 2.5 - Raise an explicit error when `PlanetSectCondition` is
    missing for sect-dependent advanced conditions.

- [ ] Task 3 - Verify condition profile enrichment (AC: AC5, AC8, AC10)
  - [ ] Subtask 3.1 - Inspect `backend/app/domain/astrology/condition/**`.
  - [ ] Subtask 3.2 - Ensure profiles receive sect impact only through dignity
    result breakdowns, advanced conditions and runtime weights.
  - [ ] Subtask 3.3 - Add or update tests proving `out_of_sect` and hayz
    profile impacts come from advanced conditions, not direct sect logic.

- [ ] Task 4 - Verify dominance integration (AC: AC6, AC8, AC10)
  - [ ] Subtask 4.1 - Inspect `backend/app/domain/astrology/dominance/**`.
  - [ ] Subtask 4.2 - Ensure dominance uses condition profile scores, advanced
    condition factors and runtime dominance weights.
  - [ ] Subtask 4.3 - Add a test proving dominance changes, if any, are caused
    by existing advanced condition/profile inputs, not direct sect
    recomputation.

- [ ] Task 5 - Verify interpretation adapter integration (AC: AC7, AC10)
  - [ ] Subtask 5.1 - Inspect
    `backend/app/domain/astrology/interpretation_adapters/**`.
  - [ ] Subtask 5.2 - Ensure the adapter consumes condition signals, advanced
    conditions, dominant planets and dignity facts.
  - [ ] Subtask 5.3 - Add a test or scan proving no adapter-level sect
    calculation exists.

- [ ] Task 6 - Preserve public projection (AC: AC10, AC11)
  - [ ] Subtask 6.1 - Inspect `backend/app/services/chart/json_builder.py`.
  - [ ] Subtask 6.2 - Ensure it serializes CS-197 `dignities.sect`, CS-198
    `dignities.planets[*].sect_condition`, and downstream outputs already
    present.
  - [ ] Subtask 6.3 - Do not import `SectCalculator`,
    `PlanetSectConditionCalculator` or `AdvancedConditionEngine`.
  - [ ] Subtask 6.4 - Do not infer sect condition from strings, labels,
    breakdowns or planet names.

- [ ] Task 7 - Tests, after snapshot and validation evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [ ] Subtask 7.1 - Add or update all targeted test files listed in
    `Expected Files to Modify`.
  - [ ] Subtask 7.2 - Capture `advanced-sect-scoring-after.json`.
  - [ ] Subtask 7.3 - Write `advanced-sect-validation.md` with commands run,
    test results, snapshot comparison, score deltas, allowed scan hits,
    skipped commands and public shape confirmation.
  - [ ] Subtask 7.4 - Run lint, tests, scans and evidence checks from the
    validation plan after venv activation.

Required test scenarios:

1. Day chart, diurnal planet, `is_in_sect=true`.
2. Day chart, nocturnal planet, `is_out_of_sect=true`.
3. Night chart, nocturnal planet, `is_in_sect=true`.
4. Night chart, diurnal planet, `is_out_of_sect=true`.
5. Hayz is true only when `is_in_sect=true`, hemisphere condition passes, and
   sign gender or polarity condition passes.
6. Hayz is false when `is_in_sect=true` but another hayz factor fails.
7. `out_of_sect` advanced condition is sourced from
   `PlanetSectCondition.is_out_of_sect`.
8. Missing `PlanetSectCondition` fails explicitly for sect-dependent advanced
   conditions.
9. Dominance does not directly calculate sect.
10. Interpretation adapter does not directly calculate sect.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - existing `PlanetDignityResult`;
  - existing `AdvancedConditionEngine`;
  - existing `PlanetConditionProfileService`;
  - existing `PlanetDominanceEngine`;
  - existing `InterpretationAdapterEngine`;
  - existing runtime references and weights.
- Do not recreate:
  - diurnal planet lists;
  - nocturnal planet lists;
  - Mercury special-case constants;
  - horizon house lists;
  - sect scoring weights outside runtime;
  - duplicate hayz ownership;
  - duplicate out-of-sect ownership;
  - fallback condition labels.
- Shared abstraction allowed only if:
  - it removes duplicate consumption logic;
  - it remains within the relevant astrology domain;
  - it does not become a new sect calculator;
  - it does not bypass CS-197 or CS-198.

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
- `sect_score_legacy`
- `legacy_planet_sect`
- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `SECT_PLANETS`
- `DAY_SECT_PLANETS`
- `NIGHT_SECT_PLANETS`
- `ABOVE_HORIZON_HOUSES`
- `BELOW_HORIZON_HOUSES`
- local horizon tuples/lists equivalent to `7, 8, 9, 10, 11, 12` or
  `1, 2, 3, 4, 5, 6` in downstream application code
- `SectCalculator` imports in `condition`, `advanced_conditions`, `dominance`,
  `interpretation_adapters` or `json_builder.py`
- `PlanetSectConditionCalculator` imports in `condition`, `advanced_conditions`,
  `dominance`, `interpretation_adapters` or `json_builder.py`
- imports from `app.infra`, `app.api`, `app.services`,
  `app.domain.prediction`, OpenAI clients, `AIEngineAdapter`,
  `chat.completions` or `prompt` inside pure astrology domains.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect calculation | `backend/app/domain/astrology/dignities/sect_calculator.py` | advanced conditions, condition profiles, dominance, adapters, JSON builder |
| Planet sect condition calculation | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | advanced conditions, dominance, adapters, JSON builder |
| Out-of-sect advanced condition detection | `backend/app/domain/astrology/advanced_conditions/**` consuming `PlanetSectCondition` | dignity calculators, JSON builder |
| Hayz advanced condition detection | `backend/app/domain/astrology/advanced_conditions/**` consuming `PlanetSectCondition` | dignity calculators, JSON builder |
| Condition profile enrichment | `backend/app/domain/astrology/condition/**` | advanced condition owner |
| Dominance scoring | `backend/app/domain/astrology/dominance/**` | sect calculators |
| Interpretation adaptation | `backend/app/domain/astrology/interpretation_adapters/**` | sect calculators |
| Public serialization | `backend/app/services/chart/json_builder.py` | domain calculators |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: conditional
- Reason: the story preserves chart JSON shapes delivered by CS-197/CS-198 and
  must not change routes, HTTP methods or status codes.
- Required generated-contract evidence:
  - chart JSON test proves `dignities.sect` and
    `dignities.planets[*].sect_condition` remain aligned;
  - if OpenAPI or generated clients model the chart result, document that no
    generated contract delta occurred, or list exact allowed delta.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
  - consume canonical sect facts for advanced sect-dependent conditions.
- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` -
  source `out_of_sect` and hayz sect prerequisite from
  `PlanetSectCondition` while retaining non-sect hayz factors.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
  - add or preserve proof that enrichment consumes advanced conditions and
  runtime weights only.
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py` - add or
  preserve proof that dominance consumes profiles/advanced conditions only.
- `backend/app/domain/astrology/interpretation_adapters/interpretation_adapter_engine.py`
  - add or preserve proof that the adapter consumes facts only.
- `backend/app/services/chart/json_builder.py` - preserve projection-only
  behavior if tests expose drift.

Likely tests:

- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` -
  canonical sect consumption, hayz true/false and missing sect condition cases.
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py` - hayz and
  out-of-sect source-of-truth cases if the helper remains separate.
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
  - profile impact sourced from advanced conditions.
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` -
  dominance consumes profiles and advanced conditions only.
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` -
  adapter contains no sect calculation.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
  - preserve CS-198 sect condition behavior.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - pipeline
  contract stability.
- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON shape.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted payload
  stability if chart result serialization is touched.

Files not expected to change:

- `frontend/**` - frontend is out of scope.
- `backend/app/api/**` - no route or HTTP behavior changes.
- `backend/app/infra/**` - no DB, repository or persistence change.
- `backend/app/domain/prediction/**` - prediction and LLM behavior are out of
  scope.
- `backend/app/infra/db/**` - no migration or model change.
- `docs/db_seeder/**` - no seed change.
- `migrations/**` - migrations are forbidden without explicit approval.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes are not allowed in this story.

## 20. Validation Plan

Run from repository root after activating the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1

pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py

pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py

ruff format .
ruff check .

rg -n "SectCalculator" backend/app/domain/astrology/condition `
  backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"
rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" `
  backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters `
  backend/app/services/chart -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES" backend/app -g "*.py"
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart -g "*.py"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition `
  backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters `
  -g "*.py"

Test-Path _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-before.json
Test-Path _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-pipeline-before.md
Test-Path _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-after.json
Test-Path _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-validation.md
rg -n "hayz|out_of_sect|PlanetSectCondition|ChartSectResult|score delta|public shape" _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence
```

Allowed scan results must be recorded in:

```text
_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-validation.md
```

## 21. Regression Risks

- Risk: double-scoring gives a planet both an accidental dignity penalty and an
  advanced condition penalty for the same sect fact without runtime intent.
  - Guardrail: before/after score comparison, advanced condition weight check
    and tests for one in-sect and one out-of-sect planet.
- Risk: hayz becomes too broad and is treated as equivalent to `in_sect`.
  - Guardrail: negative hayz test where `is_in_sect=true` but another hayz
    factor fails.
- Risk: hayz becomes a duplicate sect calculator.
  - Guardrail: hayz must use `PlanetSectCondition.is_in_sect` and scans must
    reject local planet sect constants.
- Risk: downstream layers become sect owners.
  - Guardrail: scans for calculator imports and tests proving consumption of
    profiles, advanced conditions and facts.
- Risk: public payload drifts.
  - Guardrail: chart JSON test and before/after snapshot listing exact JSON
    delta.
- Risk: missing facts silently default.
  - Guardrail: negative test requiring explicit failure for sect-dependent
    advanced conditions.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-199.
- Treat CS-197 and CS-198 contracts as canonical and delivered.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not change chart-level sect calculation.
- Do not change per-planet sect condition calculation unless a blocker is
  found and documented before code changes.
- Do not add local diurnal/nocturnal planet constants.
- Do not add local above/below horizon house constants.
- Do not add frontend changes.
- Do not add DB migrations or seed updates unless explicitly approved.
- Do not introduce legacy aliases or fallback fields.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not mark the story complete without evidence artifacts.
- If score deltas occur, document them precisely before claiming success.
- If a required sect fact is unavailable, fail explicitly and document the
  blocker instead of inventing a default.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 23. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` -
  chart-level sect contract consumed by this story.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` -
  per-planet sect condition contract consumed by this story.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` -
  dignity scoring owner.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` -
  condition profile context.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` -
  condition signal context.
- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - dominance
  context.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` -
  advanced condition and hayz context.
- `_condamad/stories/CS-196-interpretation-adapter-layer/00-story.md` -
  adapter context.
- `_condamad/stories/regression-guardrails.md` - shared invariants consulted
  and extended with `RG-126`.
- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` -
  current sect-dependent advanced condition surface.
- `backend/app/domain/astrology/dignities/contracts.py` - canonical sect
  contracts.
