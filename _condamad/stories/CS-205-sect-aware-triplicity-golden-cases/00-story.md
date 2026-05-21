# Story CS-205 sect-aware-triplicity-golden-cases: Verrouiller les cas golden de triplicité dépendante de la secte

Status: ready-to-dev

## 1. Objective

Créer une story de verrouillage doctrinal par tests et preuves persistantes pour prouver
que la triplicité essentielle traditionnelle reste dépendante de la secte du
thème et des attributions runtime. CS-205 doit ajouter des cas golden dédiés
diurne/nocturne, des snapshots curés et des scans anti-constantes locales sans
modifier la doctrine, les scores, les seeds, les migrations, le JSON public ou
le frontend.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-21 pour CS-205, follow-up de
  CS-197, CS-198, CS-199, CS-200 et CS-204.
- Reason for change: CS-200 et CS-204 verrouillent des cas traditionnels
  globaux, et le repository contient déjà des tests de triplicité sect-aware,
  mais aucune story dédiée ne force une preuve persistante complète sur le
  runtime, les snapshots before/after, le participant et les scans
  anti-constantes locales.
- Brief stakes:
  - le besoin initial vise un niveau hellénistique, médiéval et traditional
    avancé;
  - la triplicité est une dignité essentielle structurante dans ces traditions;
  - les maîtres de triplicité peuvent dépendre de la secte du thème;
  - CS-205 doit empêcher une régression qui rendrait la triplicité indépendante
    de la secte ou d'une constante locale.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dignities`
- In scope:
  - auditer les assignments de triplicité chargés dans le runtime;
  - créer ou compléter une suite golden dédiée à la triplicité dépendante de la
    secte;
  - tester un même élément en thème diurne et nocturne lorsque le runtime définit
    des maîtres distincts pour cet élément;
  - vérifier le maître participant si le runtime et le profil de scoring le
    supportent, sinon documenter explicitement son statut;
  - vérifier qu'une planète non maîtresse de triplicité active ne reçoit pas la
    dignité;
  - couvrir l'intégration via `PlanetDignityScoringService`, pas seulement
    `EssentialDignityCalculator`;
  - produire les preuves persistantes sous
    `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/`;
  - enregistrer les scans anti-constantes locales et imports interdits.
- Out of scope:
  - changer les règles de triplicité;
  - changer `ChartSectResult`, `SectCalculator` ou
    `PlanetSectConditionCalculator`;
  - changer les règles, poids ou scores de dignités essentielles;
  - modifier les seeds, migrations, routes API, projection JSON publique,
    frontend React ou logique LLM;
  - élargir la story aux termes, faces, décans ou autres dignités essentielles;
  - générer une interprétation narrative.
- Explicit non-goals:
  - ne pas hardcoder les maîtres de triplicité dans le calcul ou les helpers;
  - ne pas créer une deuxième table logique de triplicité dans les tests;
  - ne pas remplacer le runtime `triplicity_ruler_assignments`;
  - ne pas introduire de constante locale de type `FIRE_DAY_RULER`;
  - ne pas masquer une absence de participant par un faux cas de test;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-124`, `RG-125`,
    `RG-127`, `RG-131` ou `RG-132`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: runtime-contract-preservation
- Brief archetype: regression-contract-preservation
- Archetype reason: la story ne crée pas une fonctionnalité; elle préserve un
  contrat runtime doctrinal déjà présent en ajoutant tests, snapshots et
  preuves persistantes.
- Archetype adaptation: `regression-contract-preservation` est le libellé du
  brief; `runtime-contract-preservation` est l'archetype CONDAMAD supporté le
  plus proche.
- Behavior change allowed: no
- Behavior change constraints:
  - aucun score ne doit changer;
  - aucun payload public ne doit changer;
  - aucun fichier de production ne doit changer sauf bugfix explicitement
    documenté avec before/after;
  - les tests doivent échouer si la triplicité cesse de consommer
    `ChartSectResult`;
  - les tests doivent échouer si une constante locale remplace le runtime.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un cas golden requis ne peut pas être produit sans
  changer doctrine, scoring, seed, migration, contrat public ou dépendance.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les maîtres de triplicité viennent du runtime, pas d'une table locale. |
| Baseline Snapshot | yes | La story exige des preuves before/after pour démontrer l'absence de changement de score et de payload public. |
| Ownership Routing | yes | Chart sect, runtime triplicity, calcul essentiel et scoring service doivent rester chez leurs owners canoniques. |
| Allowlist Exception | yes | Les seuls hits de scans autorisés doivent être exacts, préexistants et documentés dans les preuves; aucune exception large n'est autorisée. |
| Contract Shape | yes | `PlanetDignityResult.essential_breakdown` doit exposer `triplicity` de manière stable et factuelle. |
| Batch Migration | no | La story n'est pas une migration par lots. |
| Reintroduction Guard | yes | Les constantes locales et tables de triplicité parallèles doivent être bloquées. |
| Persistent Evidence | yes | Audit, snapshots, validation et scans doivent rester dans le dossier de story. |

Brief-level contract constraints:

- Golden snapshot stability: les cas G1 à G6 doivent verrouiller des snapshots
  curés et non volatils.
- No score change: CS-205 est une story de tests et preuves; aucun changement
  de scoring n'est attendu.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - le champ canonique runtime de
    `AstrologyRuntimeReference.dignity_reference` qui expose les maîtres de
    triplicité; son nom exact doit être identifié dans l'audit before;
  - seed source attendue:
    `docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json`;
  - tables ou seeds runtime à vérifier si disponibles:
    `astral_triplicity_ruler_assignments`,
    `astral_essential_dignity_rules`,
    `astral_essential_dignity_score_weights`,
    `astral_dignity_score_profiles` ou nom existant équivalent,
    `astral_sect`;
  - `ChartSectResult.chart_sect` pour sélectionner la règle `day` ou `night`;
  - `EssentialDignityCalculator` pour produire le match essentiel;
  - `PlanetDignityScoringService` pour l'intégration complète.
- Runtime artifact:
  - loaded config object `AstrologyRuntimeReference` construit ou consommé par
    les fixtures/tests runtime;
  - AST guard ou scan statique du code pur de dignités pour les imports
    interdits et les constantes locales de triplicité;
  - test unitaire ciblé qui construit ou consomme la référence runtime et
    vérifie les assignments chargés;
  - snapshot curé `triplicity-golden-after.json`;
  - audit `triplicity-runtime-audit-before.md`.
- Secondary evidence:
  - scans `rg` anti-constantes;
  - tests de contrat `PlanetDignityResult` et service scoring;
  - validation markdown avec commandes et hits autorisés.
- Static scans alone are not sufficient because:
  - l'absence de constantes ne prouve pas que `ChartSectResult.chart_sect`
    influence le calcul;
  - un test isolé du calculateur ne prouve pas l'intégration par
    `PlanetDignityScoringService`;
  - le participant peut exister dans le runtime sans être actif dans le scoring.
- Forbidden sources:
  - dictionnaires hardcodés par élément;
  - constantes `DAY_TRIPLICITY_RULERS` ou équivalentes;
  - texte d'interprétation;
  - frontend payload;
  - calcul de secte local au test.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json`
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-runtime-audit-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json`
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-validation.md`
- Comparison rule:
  - if no dedicated CS-205 suite existed before implementation,
    `triplicity-golden-before.json` must be valid JSON and state that no
    dedicated sect-aware triplicity golden case existed before CS-205;
  - do not fake a before snapshot;
  - when before and after both contain runtime outputs, scores and curated
    fields must match unless a pre-existing bug is documented.
- Expected invariant:
  - un même élément peut activer des maîtres de triplicité différents selon la
    secte quand le runtime définit des maîtres distincts;
  - `ChartSectResult.chart_sect` influences the active triplicity match;
  - `essential_breakdown` contains a factual `triplicity` reason for active
    rulers;
  - scores remain stable;
  - public JSON remains unchanged.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | CS-205 role | Forbidden destination |
|---|---|---|---|
| Chart sect | `ChartSectResult` from CS-197 owner | consume in tests | local sect flag or recalculation helper |
| Runtime triplicity data | `AstrologyRuntimeReference.dignity_reference` | audit and assert | test-local triplicity table |
| Essential dignity calculation | `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` | test only | fixture algorithm |
| Dignity scoring orchestration | `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` | integration test | calculator-only proof |
| Contract shape | `PlanetDignityResult.essential_breakdown` | snapshot/assert | public JSON change |
| Public JSON | CS-201 projection owner | unchanged | CS-205 modifications |

## 4e. Allowlist / Exception Register

- Allowlist scope:
  - only exact pre-existing scan hits may be recorded.
- Allowed exception records:
  - path;
  - matched pattern;
  - owner;
  - reason the hit is not a local triplicity doctrine table;
  - command that produced the hit.
- Forbidden exception records:
  - wildcard paths;
  - broad "tests are allowed" classifications;
  - production constants;
  - compatibility aliases;
  - fallback doctrinal code.
- Exception register artifact:
  - `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-validation.md`
- Required exception register format:

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | `triplicity` | `fixture explicite` | `permanent fixture-only` |

## 4f. Contract Shape

- Contract type:
  - existing domain DTOs and curated snapshot shape for
    `PlanetDignityResult.essential_breakdown`.
- Fields:
  - `case_id`;
  - `chart_sect`;
  - `element`;
  - `sign`;
  - `planet_code`;
  - `expected_triplicity_role`;
  - `observed.essential_score`;
  - `observed.essential_breakdown[].type_code`;
  - `observed.essential_breakdown[].score`;
  - `observed.essential_breakdown[].source`;
  - `observed.essential_breakdown[].reason`.
- Required fields:
  - every snapshot case must include `case_id`, `chart_sect`, `element`,
    `sign`, `planet_code`, `expected_triplicity_role` and `observed`;
  - every active triplicity case must include one `essential_breakdown` item
    with `type_code` or equivalent code `triplicity`;
  - non-ruler case must explicitly show no active `triplicity` item.
- Optional fields:
  - participant case may include `participant_supported`,
    `participant_applied` and `participant_note`;
  - integration summary may include `service_path` and `chart_sect_source`.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - snapshot names use snake_case;
  - forbidden aliases: `triplicity_legacy`, `triplicity_code_legacy`,
    `day_ruler_constant`, `night_ruler_constant`.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - no OpenAPI, route manifest or generated client change is expected; validation
    evidence must record no public payload change.

### 4f.1 Snapshot Shape

Curated snapshots should use this shape and exclude volatile fields:

```json
{
  "case_id": "G1_day_triplicity",
  "chart_sect": "day",
  "element": "fire",
  "sign": "aries",
  "planet_code": "sun",
  "expected_triplicity_role": "day",
  "observed": {
    "essential_score": 3,
    "essential_breakdown": [
      {
        "type_code": "triplicity",
        "score": 3,
        "source": "runtime",
        "reason": "sun rules fire triplicity for day sect"
      }
    ]
  }
}
```

Exclude:

- timestamps;
- database IDs;
- hashes;
- localized labels;
- raw ephemeris traces;
- full natal payload unrelated to triplicity.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: aucune migration par lots, convergence de namespace ou migration
  multi-surface n'est autorisée par cette story de tests et de preuves.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime audit before | `evidence/triplicity-runtime-audit-before.md` | Documenter chargement, rôles, scoring et fixtures. |
| Before snapshot | `evidence/triplicity-golden-before.json` | Capturer l'absence de suite dédiée ou l'état initial réel. |
| After snapshot | `evidence/triplicity-golden-after.json` | Capturer G1 à G6 dans une forme curée. |
| Validation summary | `evidence/triplicity-golden-validation.md` | Enregistrer commandes, résultats, scans et confirmations. |

## 4i. Reintroduction Guard

- Guard target:
  - empêcher le retour d'une doctrine locale de triplicité, de constantes et de
    mappings de maîtres hors runtime.
- Forbidden production constants:
  - `TRIPLICITY_RULERS`;
  - `DAY_TRIPLICITY_RULERS`;
  - `NIGHT_TRIPLICITY_RULERS`;
  - `PARTICIPATING_TRIPLICITY_RULERS`;
  - `FIRE_TRIPLICITY`;
  - `EARTH_TRIPLICITY`;
  - `AIR_TRIPLICITY`;
  - `WATER_TRIPLICITY`.
- Forbidden production doctrine patterns:
  - branch conditionnelle locale combinant `chart_sect == "day"` et un element;
  - branch conditionnelle locale combinant `chart_sect == "night"` et un element;
  - test d'appartenance `planet_code in` pour sélectionner la triplicité;
  - local element-to-ruler dictionaries.
- Required guard evidence:
  - targeted pytest for G1-G6;
  - `rg` scans listed in the validation plan;
  - forbidden import scan over pure dignity code;
  - validation artifact classifying any allowed hits.
- Les scans statiques doivent être associés à des tests comportementaux parce
  que:
  - les scans détectent des symboles, mais ne prouvent pas l'alternance des
    maîtres diurne/nocturne;
  - les tests comportementaux détectent une indépendance à la secte, mais ne
    prouvent pas à eux seuls que le runtime reste la source de vérité.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 4k. Required Golden Case Intent

- G1 day triplicity:
  - prouver qu'un thème diurne active le maître de triplicité diurne issu du
    runtime;
  - assert minimum: `chart_sect == "day"`, item `triplicity` présent,
    rôle runtime diurne et contribution de score stable.
- G2 night triplicity:
  - prouver qu'un thème nocturne active le maître de triplicité nocturne issu du
    runtime;
  - assert minimum: `chart_sect == "night"`, item `triplicity` présent,
    rôle runtime nocturne et contribution de score stable.
- G3 same element, different sect:
  - prouver que la secte modifie réellement le maître activé quand le runtime
    définit des maîtres distincts;
  - si le runtime définit le même maître pour l'élément retenu, documenter cette
    règle runtime au lieu de forcer un résultat artificiel.
- G4 participating ruler:
  - vérifier que l'assignation participante est chargée;
  - appliquer la dignité si le profil de scoring actif la supporte, sinon
    documenter explicitement la raison runtime/profil.
- G5 non-ruler:
  - prouver qu'une planète non maîtresse de triplicité pour la secte active ne
    reçoit pas d'item `triplicity`.
- G6 full scoring service integration:
  - prouver le comportement via `PlanetDignityScoringService`, pas seulement via
    `EssentialDignityCalculator`;
  - vérifier que `ChartSectResult` est consommé, que les sorties day/night
    diffèrent si le runtime l'attend et que les scores restent déterministes.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - CS-197 through CS-204 are
  registered, and `CS-205` is the next sequential `CS-###` number.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared invariants
  consulted before story scope was finalized; this story adds `RG-132`.
- Evidence 3: `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` -
  current triplicity matching iterates over runtime triplicity rulers and uses a
  `sect` input.
- Evidence 4: `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  computes `ChartSectResult` once and passes `chart_sect.chart_sect` into
  essential dignity calculation.
- Evidence 5: `backend/app/domain/astrology/dignities/contracts.py` -
  `ChartSectResult`, `PlanetDignityResult` and `essential_breakdown` contracts
  exist.
- Evidence 6: `docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json` -
  runtime seed data includes day, night and participating triplicity roles.
- Evidence 7: `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py` -
  existing unit tests already exercise day/night triplicity on a synthetic
  reference, but they do not create CS-205 evidence artifacts.
- Evidence 8: `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` -
  existing broad golden cases include G13/G14 triplicity assertions from CS-204,
  but CS-205 requires a dedicated suite and evidence.

## 6. Target State

After implementation:

- dedicated CS-205 golden tests cover sect-aware triplicity;
- G1 day and G2 night cases prove `ChartSectResult.chart_sect` changes the
  active triplicity ruler where runtime assigns different rulers;
- G3 documents same-element day/night behavior and asserts different rulers or
  documents the runtime rule if identical;
- G4 tests participating ruler behavior when supported or documents why the
  active scoring profile does not apply it;
- G5 proves a non-ruler does not receive triplicity for the active sect;
- G6 proves `PlanetDignityScoringService` uses chart sect in full integration;
- before/after snapshots and validation evidence are persisted;
- no production, seed, migration, API, public JSON, frontend or dependency
  change is expected.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - runtime reference data must not be recreated as local constants.
  - `RG-112` - astrology constants and fallbacks must not return.
  - `RG-118` - dignity calculators must remain pure, runtime-backed and free of
    DB/API/services/prediction/LLM dependencies.
  - `RG-124` - chart-level sect contract remains canonical.
  - `RG-125` - per-planet sect condition remains canonical and must not be
    confused with triplicity selection.
  - `RG-127` - traditional golden cases remain stable.
  - `RG-131` - hayz/rejoicing explicit contracts must not become scoring
    sources or triplicity substitutes.
  - `RG-132` - triplicity dignity must consume runtime triplicity assignments
    and active chart sect.
- Non-applicable invariants:
  - API, Stripe, frontend design-system and prediction-only guardrails are not
    touched because this story is limited to backend astrology dignity tests and
    evidence.
- Required regression evidence:
  - targeted pytest;
  - scoring service integration test;
  - curated before/after snapshots;
  - runtime audit;
  - `rg` scans anti-constantes and forbidden imports;
  - evidence file existence checks.
- Allowed differences:
  - new tests and evidence files only;
  - no score, public JSON, production, seed, migration, frontend or dependency
    difference expected.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime assignments are audited with day/night/participating roles. | Audit: loaded config object, exact field name, `rg -n "triplicity" backend/app backend/tests`. |
| AC2 | G1 day chart activates the day triplicity ruler from runtime. | Test: `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`. |
| AC3 | G2 night chart activates the night triplicity ruler from runtime. | Test: `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`. |
| AC4 | Same-element day/night behavior is tested or documented from runtime. | Runtime evidence + snapshot: loaded config, targeted pytest and `triplicity-golden-after.json`. |
| AC5 | Participating triplicity ruler behavior is tested or documented. | `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`; validation note. |
| AC6 | A non-ruler does not receive active triplicity for the active sect. | Evidence profile: deterministic negative test; targeted pytest. |
| AC7 | Full scoring service integration consumes `ChartSectResult`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`. |
| AC8 | No production triplicity constants or local doctrine tables are introduced. | Static scan: anti-constant and forbidden-pattern `rg` scans in validation evidence. |
| AC9 | Essential dignity scores remain unchanged. | Snapshot + regression tests: `test_traditional_golden_cases.py`. |
| AC10 | Persistent evidence artifacts exist. | Command: `rg -n "triplicity" _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence`. |
| AC11 | Public JSON remains unchanged. | Regression test: `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Audit runtime triplicity data and capture baseline (AC: AC1, AC5, AC10)
  - [ ] Subtask 1.1 - Inspect `essential_dignity_calculator.py`,
    `planet_dignity_scoring_service.py`, `contracts.py`, runtime reference
    modules and `astral_triplicity_ruler_assignments.json`.
  - [ ] Subtask 1.2 - Create `triplicity-runtime-audit-before.md` documenting
    load path, exact runtime field name, available fields, participating role
    support, scoring profile and usable fixtures.
  - [ ] Subtask 1.3 - Create `triplicity-golden-before.json`; if no dedicated
    prior CS-205 suite exists, record that absence as valid JSON.

- [ ] Task 2 - Add deterministic triplicity fixtures without local doctrine tables (AC: AC2, AC3, AC4, AC5, AC6)
  - [ ] Subtask 2.1 - Reuse existing runtime reference fixtures or builders.
  - [ ] Subtask 2.2 - Add explicit builders named like
    `make_day_triplicity_case`, `make_night_triplicity_case`,
    `make_non_triplicity_ruler_case` and
    `make_participating_triplicity_case_if_supported`.
  - [ ] Subtask 2.3 - Ensure helpers expose case inputs instead of hiding a
    second triplicity algorithm.

- [ ] Task 3 - Add dedicated day/night triplicity tests (AC: AC2, AC3, AC4, AC6)
  - [ ] Subtask 3.1 - Create or extend
    `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`.
  - [ ] Subtask 3.2 - Add
    `test_day_chart_uses_day_triplicity_ruler`.
  - [ ] Subtask 3.3 - Add
    `test_night_chart_uses_night_triplicity_ruler`.
  - [ ] Subtask 3.4 - Add
    `test_same_element_can_select_different_triplicity_ruler_by_sect`.
  - [ ] Subtask 3.5 - Add
    `test_non_ruler_does_not_receive_triplicity`.

- [ ] Task 4 - Add participating ruler proof or explicit evidence note (AC: AC5)
  - [ ] Subtask 4.1 - Determine whether runtime contains a participating
    triplicity role and whether the active scoring profile applies it.
  - [ ] Subtask 4.2 - Add `test_participating_triplicity_ruler_behavior` if
    supported.
  - [ ] Subtask 4.3 - If unsupported or not applied, document the exact runtime
    and scoring reason in audit and validation evidence without faking behavior.

- [ ] Task 5 - Add full scoring service integration coverage (AC: AC7, AC9)
  - [ ] Subtask 5.1 - Update
    `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
    or the dedicated golden file to exercise `PlanetDignityScoringService`.
  - [ ] Subtask 5.2 - Assert that `ChartSectResult.chart_sect` is the source of
    day/night selection.
  - [ ] Subtask 5.3 - Assert `essential_breakdown` includes triplicity and
    `essential_score` remains deterministic.

- [ ] Task 6 - Capture after snapshot and validation evidence (AC: AC4, AC5, AC8, AC9, AC10, AC11)
  - [ ] Subtask 6.1 - Create `triplicity-golden-after.json` with G1 to G6 using
    the curated shape.
  - [ ] Subtask 6.2 - Create `triplicity-golden-validation.md` with commands,
    results, snapshot comparison, participant status, score-change confirmation
    and public-payload-change confirmation.
  - [ ] Subtask 6.3 - Run targeted tests, regression tests, `ruff format .`,
    `ruff check .`, scans and evidence checks after venv activation.
  - [ ] Subtask 6.4 - Record allowed scan hits and confirm no forbidden
    production, seed, migration, frontend or public JSON diff.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartSectResult`;
  - `PlanetDignityResult`;
  - `EssentialDignityCalculator`;
  - `PlanetDignityScoringService`;
  - existing `AstrologyRuntimeReference` and `dignity_reference` builders;
  - existing CS-200/CS-204 golden helper style when appropriate.
- Do not recreate:
  - triplicity tables;
  - day/night ruler mappings;
  - element-to-ruler dictionaries;
  - scoring weights;
  - sect calculation;
  - runtime loading.
- Allowed in tests:
  - case IDs and labels;
  - explicit fixture inputs;
  - expected snapshot values read from the runtime-backed observed output.
- Not allowed in tests:
  - duplicate implementation of the production triplicity algorithm;
  - assertions that only check field existence;
  - broad full-payload snapshots;
  - helpers named so vaguely that they hide doctrine, such as
    `make_valid_dignity_case`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- local astrology constants in production;
- frontend or JSON builder triplicity derivation;
- seed/migration update without documented blocker and user decision.

Specific forbidden production constants:

- `TRIPLICITY_RULERS`
- `DAY_TRIPLICITY_RULERS`
- `NIGHT_TRIPLICITY_RULERS`
- `PARTICIPATING_TRIPLICITY_RULERS`
- `FIRE_TRIPLICITY`
- `EARTH_TRIPLICITY`
- `AIR_TRIPLICITY`
- `WATER_TRIPLICITY`

Specific forbidden production paths unless blocker approved:

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/app/domain/prediction/**`
- `migrations/**`
- `docs/db_seeder/**`

Specific forbidden imports in pure dignity code:

- `app.infra`
- `app.services`
- `app.api`
- `app.domain.prediction`
- `OpenAI`
- `AIEngineAdapter`
- `prompt`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect | CS-197 `ChartSectResult` owner | local test sect calculators |
| Triplicity runtime data | `AstrologyRuntimeReference.dignity_reference` | local triplicity dictionaries |
| Essential dignity calculation | `essential_dignity_calculator.py` | snapshot helper or fixture algorithm |
| Scoring orchestration | `planet_dignity_scoring_service.py` | calculator-only proof for integration behavior |
| Public JSON | CS-201 projection | CS-205 changes |
| Frontend expert panel | CS-202 frontend | CS-205 changes |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract or
  generated client is expected to change.
- Required generated-contract evidence:
  - validation markdown states no public payload change;
  - `backend/app/tests/unit/test_chart_json_builder.py` remains green.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py`
- `docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json`

Also inspect any existing runtime fixture builders discovered by `rg -n
"AstrologyRuntimeReference|dignity_reference|triplicity" backend/tests
backend/app -g "*.py"`.

## 18. Expected Files to Modify

Likely files:

- `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` -
  dedicated G1-G6 tests.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` -
  scoring service integration proof if not covered in the dedicated file.
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` -
  fixture reuse or explicit case builders when appropriate.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-runtime-audit-before.md` -
  runtime audit.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json` -
  baseline snapshot or absence marker.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json` -
  final curated snapshot.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-validation.md` -
  commands, results, scans and confirmations.

Likely tests:

- `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`

Files not expected to change:

- `backend/app/domain/astrology/dignities/**` - production doctrine is out of
  scope unless a documented bug is found.
- `backend/app/domain/astrology/advanced_conditions/**` - advanced conditions
  are out of scope.
- `backend/app/services/chart/json_builder.py` - public JSON must remain
  unchanged.
- `frontend/**` - frontend is out of scope.
- `backend/app/api/**` - no route change.
- `backend/app/infra/**` - no persistence change.
- `backend/app/domain/prediction/**` - prediction and LLM are out of scope.
- `migrations/**` - migrations are forbidden.
- `docs/db_seeder/**` - seed changes are forbidden.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Dependency changes are not allowed for CS-205.

## 20. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py
```

Regression tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
```

Quality:

```powershell
ruff format .
ruff check .
```

Anti-constant scans:

```powershell
$triplicityConstants = @(
  "TRIPLICITY_RULERS",
  "DAY_TRIPLICITY_RULERS",
  "NIGHT_TRIPLICITY_RULERS",
  "PARTICIPATING_TRIPLICITY_RULERS",
  "FIRE_TRIPLICITY",
  "EARTH_TRIPLICITY",
  "AIR_TRIPLICITY",
  "WATER_TRIPLICITY"
) -join "|"
rg -n $triplicityConstants backend/app -g "*.py"
$triplicityPatterns = @(
  "if .*chart_sect.*day",
  "if .*chart_sect.*night",
  "planet_code\s+in",
  'element\s*==\s*[''"]fire',
  'element\s*==\s*[''"]earth',
  'element\s*==\s*[''"]air',
  'element\s*==\s*[''"]water'
) -join "|"
rg -n $triplicityPatterns backend/app/domain/astrology/dignities -g "*.py"
```

Forbidden imports:

```powershell
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|prompt"
rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"
```

Forbidden path diff checks:

```powershell
git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder frontend
```

Evidence checks:

```powershell
Test-Path _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-runtime-audit-before.md
Test-Path _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json
Test-Path _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json
Test-Path _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-validation.md
rg -n "triplicity|day|night|participating|runtime|no score change|no public payload change" _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence
python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json
python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json
```

Story validation commands:

```powershell
$story = "_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 21. Regression Risks

- Risk: tests duplicate doctrine by embedding element-to-ruler mappings.
  - Guardrail: runtime audit, fixture review and anti-constant scans.
- Risk: triplicity becomes independent of chart sect.
  - Guardrail: G1/G2/G3 same-element day/night tests.
- Risk: production constants reappear.
  - Guardrail: forbidden constant scans over `backend/app`.
- Risk: participant ruler is faked or ignored silently.
  - Guardrail: test if supported, otherwise explicit audit and validation note.
- Risk: production changes slip into a test-only story.
  - Guardrail: forbidden path diff checks and no-score/no-public-payload
    snapshot confirmation.
- Risk: snapshots become too broad or volatile.
  - Guardrail: curated shape and exclusion list in section 4f.1.

## 22. Dev Agent Instructions

- Implement only this story.
- Implement only CS-205.
- Prefer tests and evidence over production changes.
- Treat CS-197 through CS-204 as canonical.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not change triplicity doctrine.
- Do not change scoring weights.
- Do not add runtime constants.
- Do not update seeds unless blocker is documented and approved by the user.
- Do not add frontend changes.
- Do not modify public JSON.
- Do not add LLM behavior or narrative interpretation.
- Do not create local triplicity tables or day/night ruler mappings.
- Do not mark a task complete without validation evidence.
- Do not mark the story complete without all evidence files.
- If participant triplicity is not supported by runtime or profile, document it
  instead of inventing behavior.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 23. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` -
  chart-level sect contract.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` -
  per-planet sect condition contract.
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` -
  advanced sect scoring integration.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md` -
  broad traditional golden case baseline.
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md` -
  explicit traditional conditions and existing G13/G14 context.
- `_condamad/stories/regression-guardrails.md` - applicable invariants and new
  `RG-132`.
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` -
  essential dignity owner.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  scoring orchestration owner.
- `backend/app/domain/astrology/dignities/contracts.py` - canonical dignity
  contracts.
- `docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json` -
  runtime seed reference for triplicity roles.
