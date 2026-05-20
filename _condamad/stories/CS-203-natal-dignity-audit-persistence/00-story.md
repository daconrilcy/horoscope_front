# Story CS-203 natal-dignity-audit-persistence: Activer la persistance d'audit des dignites planetaires natales

Status: ready-to-dev

## 1. Objective

Activer l'ecriture d'audit des dignites planetaires natales calculees dans la table existante
`astral_chart_planet_dignity_results`, une ligne par planete et par resultat de theme.
Les scores, le payload public, les calculateurs astrologiques, le frontend et les routes API
ne doivent pas changer.

`chart_results.result_payload` reste la source de restitution publique. La table
`astral_chart_planet_dignity_results` devient une surface interne requetable pour audit,
comparaison et controle des scores, breakdowns, profil de scoring, version de reference,
tradition/systeme astral, contrat de secte du theme et condition de secte planetaire lorsque le schema le permet.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-20 pour CS-203, follow-up de CS-191, CS-197, CS-198, CS-199, CS-200, CS-201 et CS-202.
- Reason for change: le moteur calcule et expose maintenant des dignites avancees, mais la
  persistance detaillee par planete reste absente du flux `ChartResultService.persist_trace`.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/services/chart` with repository-layer integration in `backend/app/infra/db/repositories`
- In scope:
  - auditer le schema, le modele et le repository existants de `astral_chart_planet_dignity_results`;
  - activer l'ecriture des dignites calculees apres persistance du `chart_results` row et obtention de son identifiant DB;
  - consommer uniquement `NatalResult.dignities`, `PlanetDignityResult`, `ChartSectResult` et `PlanetSectCondition`;
  - utiliser l'upsert existant `DignityReferenceRepository.upsert_chart_planet_dignity_result`;
  - garantir l'idempotence pour le meme `chart_result_id + planet + score_profile + reference_version`;
  - ajouter tests service/repository, scans anti-recalcul et evidence persistante sous `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/`.
- Out of scope:
  - modifier les regles de dignites, `SectCalculator`, `PlanetSectConditionCalculator`,
    `PlanetDignityScoringService`, les conditions avancees, les dominantes ou
    l'adaptateur interpretatif;
  - modifier le frontend React, les routes API, les schemas HTTP publics, OpenAPI ou l'UI expert;
  - creer une route API d'audit ou lire la table d'audit pour construire `NatalResult`;
  - ajouter une interpretation narrative, un appel LLM, une dependance externe, un seed ou une migration Alembic sauf blocker documente et approuve.
- Explicit non-goals:
  - ne pas faire de `astral_chart_planet_dignity_results` la source de verite du calcul;
  - ne pas remplacer ni modifier `chart_results.result_payload`;
  - ne pas recalculer secte, condition de secte, dignites, hayz, joies, dominantes, profils ou signaux pendant la persistance;
  - ne pas dupliquer les donnees sensibles de naissance dans l'audit;
  - ne pas ajouter de fallback silencieux lors d'un echec d'audit;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-124`, `RG-125`, `RG-126`, `RG-127`, `RG-128`, `RG-129` ou `RG-130`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Brief archetype: audit-persistence-activation
- Archetype reason: une table d'audit et un upsert existent deja; la story active leur usage dans le flux canonique de persistance chart sans changer le contrat public.
- Archetype adaptation: `audit-persistence-activation` est le libelle du brief; `custom`
  est l'archetype CONDAMAD valide car aucun archetype standard ne couvre exactement une
  activation d'audit interne DB sans API publique.
- Additional validation rules:
  - les tests doivent comparer les lignes d'audit aux valeurs deja presentes dans `NatalResult.dignities` ou `chart_results.result_payload`;
  - les scans doivent prouver l'absence d'import de calculateurs dans le mapper/service audit et repository;
  - les artefacts before/after doivent documenter le lien `chart_results.id` vers les lignes d'audit.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `persist_trace` ecrit maintenant aussi les lignes d'audit de dignites;
  - les scores et breakdowns astrologiques restent inchanges;
  - le payload public et les endpoints existants restent inchanges;
  - l'echec d'ecriture audit n'est pas masque;
  - les nouvelles lignes d'audit sont le seul changement runtime attendu.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if:
  - le schema reel ne permet pas de lier une ligne d'audit a `chart_results.id` ou equivalent;
  - une migration devient necessaire pour stocker le lien minimal ou les champs minimaux requis.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | L'audit doit persister les resultats calcules depuis le runtime, sans recalcul ni lecture de regles DB comme source du resultat. |
| Baseline Snapshot | yes | L'etat avant/apres des lignes d'audit doit etre prouve pour un theme genere. |
| Ownership Routing | yes | Calcul, projection publique et persistance audit ont des owners differents a maintenir. |
| Allowlist Exception | no | Aucune exception large, alias legacy ou fallback doctrinal n'est autorise. |
| Contract Shape | yes | La forme des champs persistables doit etre explicite et alignee au schema existant. |
| Batch Migration | no | La story n'est pas une migration par lots et ne remplace pas plusieurs surfaces. |
| Reintroduction Guard | yes | Le repository/mapper audit ne doit jamais devenir un moteur de calcul. |
| Persistent Evidence | yes | Snapshots DB/test/scans sont requis pour fermer la story. |

Brief-level contract requirements not represented as CONDAMAD contract names:

- Idempotent Persistence: required; covered by AC6, Task 4 and after snapshot evidence.
- Transaction Boundary: required; covered by AC9, Task 3 and `dignity-audit-validation.md`.
- Public API Contract: required; covered by AC8, AC10, Generated Contract Check and forbidden path diffs.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.dignities`;
  - `PlanetDignityResult`;
  - `PlanetDignityResult.chart_sect`;
  - `PlanetDignityResult.sect_condition`;
  - `ChartResultService.persist_trace` apres creation de `ChartResultModel`.
- Runtime artifact:
  - DB schema `AstralChartPlanetDignityResultModel.__table__` / table `astral_chart_planet_dignity_results`;
  - `chart_results.result_payload["dignities"]` reste la trace publique principale;
  - `astral_chart_planet_dignity_results` stocke une copie d'audit par planete, liee a `chart_results.id`;
  - les JSON `essential_breakdown_json`, `accidental_breakdown_json`, `condition_summary_json` et `calculation_context_json` proviennent de champs deja calcules.
- Secondary evidence:
  - `pytest -q backend/app/tests/unit/test_chart_result_service.py`;
  - `pytest -q backend/app/tests/unit/test_chart_planet_dignity_audit_repository.py` when added;
  - AST guard/static scan over `backend/app/services/chart` and `backend/app/infra/db/repositories` for forbidden calculator imports.
- Forbidden sources:
  - runtime DB rules comme source de recalcul;
  - constantes locales de dignites, secte ou joies;
  - `SectCalculator`, `PlanetSectConditionCalculator`, `PlanetDignityScoringService`, `EssentialDignityCalculator`, `AccidentalDignityCalculator`, `AdvancedConditionEngine`;
  - payload frontend, projection JSON publique comme source unique lorsque `NatalResult` est disponible.
- Static scans alone are not sufficient because:
  - l'absence d'import de calculateurs ne prouve pas l'ecriture DB;
  - l'idempotence et la correspondance score/breakdown doivent etre validees par tests.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-before.json`
  - `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-persistence-audit-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-after.json`
  - `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-validation.md`
- Required baseline questions:
  - table name, model name, repository name and actual columns;
  - unique constraints and upsert key;
  - whether `chart_result_id` exists;
  - whether breakdown JSON and sect fields can be represented;
  - number of dignity planets in a generated `NatalResult`;
  - number of audit rows linked to the generated `chart_results.id` before implementation.
- Expected invariant:
  - `chart_results.result_payload.dignities` remains unchanged;
  - public JSON remains unchanged;
  - audit table gains or updates detailed rows;
  - re-running the same audit persistence for the same chart result does not duplicate rows.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | CS-203 role | Forbidden destination |
|---|---|---|---|
| Dignity calculation | `backend/app/domain/astrology/dignities/**` | consume result only | service/repository audit recalculation |
| Chart sect calculation | `SectCalculator` via `PlanetDignityScoringService` | persist snapshot only | mapper deriving day/night |
| Planet sect condition | `PlanetSectConditionCalculator` via scoring result | persist snapshot only | repository deriving planet doctrine |
| Public projection | `backend/app/services/chart/json_builder.py` | regression only | audit table as public source |
| Chart result persistence | `backend/app/services/chart/result_service.py` | integrate audit write | API route or frontend |
| Audit DB upsert | `backend/app/infra/db/repositories/dignity_reference_repository.py` | reuse existing upsert | duplicate repository/table |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason:
  - no broad allowlist, compatibility path, legacy alias or doctrinal fallback is allowed;
  - any retained scan hit must be exact, pre-existing and documented in `dignity-audit-validation.md`.

## 4f. Contract Shape

- Contract type:
  - internal DB audit row in `astral_chart_planet_dignity_results`.
- Fields:
  - actual inspected schema includes `chart_result_id`, `planet_id`, `score_profile_id`,
    `astral_system_id`, `reference_version_id`, numeric score fields, JSON
    breakdown/context fields and `created_at`.
- Required fields:
  - `chart_result_id`;
  - `planet_id` resolved from existing `PlanetModel.code`;
  - `score_profile_id` resolved from existing `AstralDiginityScoreProfileModel.code`;
  - `astral_system_id` resolved from existing `AstralSystemModel.name`;
  - `reference_version_id` resolved from existing `ReferenceVersionModel.version`;
  - `essential_score`, `accidental_score`, `total_score`;
  - `functional_strength_score`, `expression_quality_score`, `intensity_score`;
  - `essential_breakdown_json`, `accidental_breakdown_json`;
  - `condition_summary_json`, including chart sect and planet sect condition;
  - `calculation_context_json`, including source/result metadata without birth data.
- Optional fields:
  - `user_id` is not present on the audit table and must not be duplicated unless an approved migration adds it;
  - `updated_at` is not present in the inspected model and must not trigger a migration by itself.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Public API surfaces unchanged:
  - `GET /v1/users/me/natal-chart/latest`;
  - `POST /v1/users/me/natal-chart`;
  - public chart JSON payload;
  - frontend expert panel payload.
- Serialization names:
  - preserve existing DB column names;
  - public JSON snake_case names remain unchanged;
  - forbidden aliases: `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - no OpenAPI or generated public client impact is expected.
- Forbidden persisted facts:
  - birth date, birth time, birth location text, raw latitude/longitude, timezone and user-entered place string must not be duplicated in audit rows.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la story active l'ecriture dans une table existante pour les nouveaux flux de persistance; elle ne migre pas l'historique ni plusieurs surfaces concurrentes.

## 4h. Persistent Evidence Artifacts

Required artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `evidence/dignity-audit-before.json` | Counts before activation. |
| Schema audit | `evidence/dignity-audit-persistence-audit-before.md` | Table, model, upsert. |
| After snapshot | `evidence/dignity-audit-after.json` | Rows, score checks, idempotence. |
| Validation record | `evidence/dignity-audit-validation.md` | Commands, scans, transaction notes. |

The validation artifact must include:

- commands run;
- repository/service validation;
- snapshot comparison;
- idempotence result;
- failure behavior;
- schema limitations documented as blockers;
- allowed scan hits;
- confirmation public payload unchanged;
- confirmation frontend unchanged;
- confirmation no migration/seed change or documented blocker.

## 4i. Reintroduction Guard

- Guard type:
  - tests service/repository proving persistence consumes precomputed result fields;
  - static scans over audit persistence code for forbidden calculators and constants;
  - regression tests for public JSON and golden cases.
- Forbidden calculator imports in audit persistence code:
  - `SectCalculator`;
  - `PlanetSectConditionCalculator`;
  - `PlanetDignityScoringService`;
  - `EssentialDignityCalculator`;
  - `AccidentalDignityCalculator`;
  - `AdvancedConditionEngine`;
  - `PlanetConditionProfileService`;
  - `PlanetConditionSignalBuilder`;
  - `PlanetDominanceEngine`;
  - `InterpretationAdapterEngine`.
- Forbidden doctrine constants in audit persistence code:
  - `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`,
    `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`, `ABOVE_HORIZON_HOUSES`,
    `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`, `PLANETARY_JOYS`, `HAYZ_RULES`.
- Conditional allowed hits:
  - existing domain imports inside `backend/app/domain/astrology/dignities/**` are not audit persistence code;
  - pre-existing non-audit service imports must be documented with file, line and reason.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/services/chart/result_service.py` -
  `ChartResultService.persist_trace` creates a `ChartResultRepository` row and returns only
  `chart_id`; it does not currently call the dignity audit upsert.
- Evidence 2: `backend/app/infra/db/models/dignity_reference.py` -
  `AstralChartPlanetDignityResultModel` maps `astral_chart_planet_dignity_results` with
  `chart_result_id`, score fields, JSON fields and the expected unique key.
- Evidence 3: `backend/app/infra/db/repositories/dignity_reference_repository.py` -
  `ChartPlanetDignityResultInput` and `upsert_chart_planet_dignity_result` already exist
  and resolve planet, score profile, system and reference version through DB rows.
- Evidence 4: `docs/db_seeder/astrology/astral_chart_planet_dignity_results.json` - seed metadata describes the table as a runtime audit table and contains no seed data.
- Evidence 5: `backend/app/domain/astrology/dignities/contracts.py` - `PlanetDignityResult` contains scores, breakdowns, `ChartSectResult` and optional `PlanetSectCondition`.
- Evidence 6: `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  calculators own score and sect computation before persistence; audit must not call it.
- Evidence 7: `backend/app/tests/unit/test_chart_result_service.py` - existing tests verify `persist_trace`, public payload preservation and CS-197/CS-198 payload fields.
- Evidence N: `_condamad/stories/regression-guardrails.md` - shared regression invariants consulted before story scope was finalized.

Assumptions to verify during implementation:

- no separate repository test for `upsert_chart_planet_dignity_result` already exists;
- the existing SQLite/Alembic test harness creates the audit table from the inspected SQLAlchemy model;
- `AstralSystemModel.name` accepts the `PlanetDignityResult.tradition` value currently produced as `traditional`; otherwise document the blocker before changing mapping or schema.

## 6. Target State

After implementation:

- every successful natal chart persistence writes one audit row per `NatalResult.dignities` planet;
- each audit row is linked to the persisted `chart_results.id`;
- stored scores and breakdowns match the corresponding `PlanetDignityResult`;
- `condition_summary_json` stores chart-level sect and per-planet sect condition when present;
- `calculation_context_json` stores minimal non-sensitive trace data such as source, `chart_id`, input hash, profile, tradition/reference version and source field names;
- re-running the audit write for the same chart result updates or leaves the same N rows;
- old payloads/results without dignities do not fabricate audit rows;
- public chart JSON, frontend and API routes remain unchanged;
- no repository/service audit code imports or instantiates calculators.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - audit persistence must not recreate runtime reference data as constants.
  - `RG-112` - astrology constants and fallbacks must not return.
  - `RG-118` - dignity calculators remain pure runtime-backed engines; audit consumes results only.
  - `RG-124` - chart-level sect contract remains canonical and is persisted as snapshot only.
  - `RG-125` - per-planet sect condition remains canonical and is persisted as snapshot only.
  - `RG-126` - advanced sect scoring remains a consumer of canonical facts; audit must not derive them.
  - `RG-127` - golden traditional cases remain stable.
  - `RG-128` - public JSON projection remains a projection, not a calculator or audit reader.
  - `RG-129` - frontend remains display-only and untouched.
  - `RG-130` - dignity audit persistence consumes calculated results and must not become a calculator.
- Non-applicable invariants:
  - API route guardrails outside chart result persistence - no route is added, removed or renamed.
  - frontend visual/style guardrails - frontend files are out of scope.
- Required regression evidence:
  - repository tests;
  - chart result service tests;
  - payload unchanged test;
  - idempotence test;
  - no-recalculation scans;
  - golden cases targeted test;
  - evidence snapshots.
- Allowed differences:
  - new audit rows in `astral_chart_planet_dignity_results`;
  - new backend service/repository mapper/tests;
  - new persistent evidence files;
  - no public JSON, score, frontend, API route, seed or migration change expected.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Audit table/model/repository are documented. | Evidence profile: `schema_inspection`; `Test-Path` audit file + `rg "upsert|unique"`. |
| AC2 | Successful chart result persistence writes one dignity audit row per planet. | Evidence profile: `runtime_behavior_check`; service/repository pytest. |
| AC3 | Audit row scores match `NatalResult.dignities[*]`. | Evidence profile: `deterministic_test`; pytest comparing row fields to payload/result. |
| AC4 | Chart-level sect is persisted. | Evidence profile: `json_contract_shape`; `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC5 | Planet sect condition is persisted. | Evidence profile: `json_contract_shape`; `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC6 | Audit write is idempotent for the same chart result. | Evidence profile: `deterministic_test`; idempotence pytest and after snapshot. |
| AC7 | Audit persistence does not recalculate dignities or sect. | Evidence profile: `reintroduction_guard`; forbidden scan + precomputed-result pytest. |
| AC8 | Public chart JSON remains unchanged. | Evidence profile: `baseline_before_after_diff`; `test_chart_json_builder.py` and payload comparison note. |
| AC9 | Audit write failure behavior is explicit. | Evidence profile: `runtime_behavior_check`; failure-path pytest or transaction note. |
| AC10 | Forbidden paths unchanged. | Evidence profile: `targeted_forbidden_symbol_scan`; Validation Plan diff + `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC11 | Golden cases still pass. | Evidence profile: `deterministic_test`; `test_traditional_golden_cases.py`. |
| AC12 | Persistent evidence artifacts exist with required keywords. | Evidence profile: `persistent_evidence`; `Test-Path` and `rg` checks. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter le schema et capturer la baseline (AC: AC1, AC12)
  - [ ] Subtask 1.1 - Inspecter `backend/app/infra/db/models/dignity_reference.py`,
    `backend/app/infra/db/repositories/dignity_reference_repository.py`,
    `backend/app/infra/db/models/chart_result.py` et le repository chart result.
  - [ ] Subtask 1.2 - Creer `dignity-audit-persistence-audit-before.md` avec table,
    modele, colonnes, contraintes, upsert, lien `chart_result_id`, JSON fields et limites schema.
  - [ ] Subtask 1.3 - Creer `dignity-audit-before.json` sans donnees de naissance sensibles.

- [ ] Task 2 - Definir le mapping audit depuis les resultats calcules (AC: AC2, AC3, AC4, AC5, AC7)
  - [ ] Subtask 2.1 - Ajouter un mapper interne etroit, par exemple `backend/app/services/chart/dignity_audit_mapper.py`, en absence de helper equivalent.
  - [ ] Subtask 2.2 - Mapper `PlanetDignityResult` vers `ChartPlanetDignityResultInput` sans importer de calculateurs.
  - [ ] Subtask 2.3 - Placer `chart_sect` et `sect_condition` dans `condition_summary_json`; placer metadata non sensible dans `calculation_context_json`.

- [ ] Task 3 - Integrer l'upsert au flux `persist_trace` (AC: AC2, AC6, AC9)
  - [ ] Subtask 3.1 - Conserver le `ChartResultModel` retourne par `ChartResultRepository.create` pour obtenir `model.id`.
  - [ ] Subtask 3.2 - Appeler le repository audit apres creation du chart result et avant retour de `chart_id`.
  - [ ] Subtask 3.3 - Ne pas entourer l'ecriture audit d'un `try/except` silencieux; documenter la transaction avec le commit appelant.

- [ ] Task 4 - Ajouter ou renforcer les tests repository/service (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC9)
  - [ ] Subtask 4.1 - Tester l'upsert idempotent par cle fonctionnelle existante.
  - [ ] Subtask 4.2 - Tester `persist_trace` ecrit N lignes liees a `chart_results.id`.
  - [ ] Subtask 4.3 - Tester scores, breakdowns, chart sect, planet sect condition et absence de fabrication pour `dignities=[]`.
  - [ ] Subtask 4.4 - Tester ou documenter le comportement d'echec d'audit.

- [ ] Task 5 - Preserver la projection publique (AC: AC8, AC10, AC11)
  - [ ] Subtask 5.1 - Executer `backend/app/tests/unit/test_chart_json_builder.py`.
  - [ ] Subtask 5.2 - Executer les golden cases et tests de scoring ciblés.
  - [ ] Subtask 5.3 - Verifier que `frontend/**`, `backend/app/api/**`, `docs/db_seeder/**` et `backend/migrations/**` ne changent pas, sauf blocker documente.

- [ ] Task 6 - Ajouter les gardes anti-recalcul (AC: AC7, AC10, AC12)
  - [ ] Subtask 6.1 - Executer les scans de calculateurs interdits sur `backend/app/services/chart` et `backend/app/infra/db/repositories`.
  - [ ] Subtask 6.2 - Executer les scans d'alias legacy et constantes doctrinales.
  - [ ] Subtask 6.3 - Documenter les hits autorises avec fichier, ligne et raison.

- [ ] Task 7 - Capturer l'evidence apres implementation (AC: AC1, AC6, AC8, AC9, AC12)
  - [ ] Subtask 7.1 - Creer `dignity-audit-after.json` avec count payload, count rows, samples disponibles, comparaison scores/breakdowns et idempotence.
  - [ ] Subtask 7.2 - Creer `dignity-audit-validation.md` avec commandes, resultats,
    scans, transaction boundary, public payload unchanged, frontend unchanged et no migration/seed change.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartResultService.persist_trace` as canonical persistence flow;
  - `ChartResultRepository.create` for `chart_results`;
  - `DignityReferenceRepository.upsert_chart_planet_dignity_result` for audit rows;
  - `ChartPlanetDignityResultInput` unless a smaller DTO is needed before repository input;
  - `NatalResult.dignities` and `PlanetDignityResult` as computed source;
  - `ChartSectResult` and `PlanetSectCondition` as canonical sect contracts.
- Do not recreate:
  - dignity calculation;
  - sect calculation;
  - planet sect condition calculation;
  - essential dignity matching;
  - accidental dignity matching;
  - advanced condition detection;
  - runtime reference loading;
  - public JSON projection.
- Shared abstraction allowed only if:
  - it is a pure field mapper from calculated result to audit input and removes duplication in tests/service.
- Not allowed:
  - mapper that fills missing scores;
  - mapper that creates fake sect data;
  - mapper that derives planet sect from planet code;
  - repository code that imports calculators.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- local astrology constants;
- audit table read path for public response;
- seed or migration changes without documented blocker and approval.

Specific forbidden symbols:

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
- `HAYZ_RULES`
- `SectCalculator`
- `PlanetSectConditionCalculator`
- `PlanetDignityScoringService`
- `EssentialDignityCalculator`
- `AccidentalDignityCalculator`
- `AdvancedConditionEngine`
- `PlanetConditionProfileService`
- `PlanetConditionSignalBuilder`
- `PlanetDominanceEngine`
- `InterpretationAdapterEngine`

Specific forbidden paths to modify unless blocker is documented:

- `frontend/**`
- `backend/app/api/**`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/prediction/**`
- `docs/db_seeder/**`
- `backend/migrations/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Dignity calculation | `backend/app/domain/astrology/dignities/**` | service/repository audit recalculation |
| Chart sect calculation | `SectCalculator` through scoring service | mapper/repository deriving sect |
| Planet sect condition | `PlanetSectConditionCalculator` through scoring service | planet-code constants in audit mapper |
| Advanced conditions | `backend/app/domain/astrology/advanced_conditions/**` | audit persistence |
| Public projection | `backend/app/services/chart/json_builder.py` | audit table read path |
| Chart result persistence | `backend/app/services/chart/result_service.py` | API route or frontend |
| Dignity audit persistence | `DignityReferenceRepository` and existing audit table | parallel audit table/repository |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract or generated client is affected.

## 17. Files to Inspect First

Codex doit inspecter avant edition:

- `backend/app/services/chart/result_service.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/migrations/`
- `docs/db_seeder/astrology/astral_chart_planet_dignity_results.json`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`

Alembic lives under `backend/migrations/`; inspect it before deciding whether a migration is needed.

## 18. Expected Files to Modify

Likely files:

- `backend/app/services/chart/result_service.py` - integrate audit write after chart result creation.
- `backend/app/services/chart/dignity_audit_mapper.py` - new pure mapper when no equivalent exists.
- `backend/app/infra/db/repositories/dignity_reference_repository.py` - minimal upsert/input adaptation only for a missing required field.

Likely tests:

- `backend/app/tests/unit/test_chart_result_service.py` - service integration, no payload change, failure behavior.
- `backend/app/tests/unit/test_chart_planet_dignity_audit_repository.py` - repository upsert and idempotence, when this test file is added.
- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON regression.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` - targeted scoring regression.
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` - golden stability.

Evidence files:

- `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-before.json`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-persistence-audit-before.md`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-after.json`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-validation.md`

Files not expected to change:

- `frontend/**` - no UI or frontend API change.
- `backend/app/api/**` - no route or HTTP contract change.
- `backend/app/domain/astrology/dignities/sect_calculator.py` - sect calculation unchanged.
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` - per-planet sect condition unchanged.
- `backend/app/domain/astrology/advanced_conditions/**` - advanced conditions out of scope.
- `backend/app/domain/astrology/condition/**` - condition profiles/signals out of scope.
- `backend/app/domain/astrology/dominance/**` - dominants out of scope.
- `backend/app/domain/astrology/interpretation_adapters/**` - interpretation adapter out of scope.
- `backend/app/domain/prediction/**` - prediction out of scope.
- `docs/db_seeder/**` - seed change not expected.
- `backend/migrations/**` - migration not expected unless blocker is documented and approved.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only when explicitly listed here with justification.
- Justification: existing SQLAlchemy repository/model, Pydantic/domain contracts and pytest coverage are sufficient.

## 20. Validation Plan

All Python commands must be run after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
pytest -q backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

When repository tests are added:

```powershell
pytest -q backend/app/tests/unit/test_chart_planet_dignity_audit_repository.py
```

Relevant regression tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
```

Quality checks:

```powershell
ruff format .
ruff check .
```

No-recalculation scans:

```powershell
rg -n "SectCalculator|PlanetSectConditionCalculator|PlanetDignityScoringService" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"
rg -n "EssentialDignityCalculator|AccidentalDignityCalculator|AdvancedConditionEngine" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"
rg -n "PlanetConditionProfileService|PlanetConditionSignalBuilder" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"
rg -n "PlanetDominanceEngine|InterpretationAdapterEngine" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"
```

Legacy alias scans:

```powershell
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"
```

Doctrine constant scans:

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS" backend/app -g "*.py"
rg -n "ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES" backend/app -g "*.py"
```

Forbidden path diff check:

```powershell
git diff -- frontend backend/app/api docs/db_seeder backend/migrations
git diff -- backend/app/domain/astrology/dignities/sect_calculator.py
git diff -- backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py
git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition
git diff -- backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters
git diff -- backend/app/domain/prediction
```

Evidence checks:

```powershell
Test-Path _condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-before.json
Test-Path _condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-persistence-audit-before.md
Test-Path _condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-after.json
Test-Path _condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/dignity-audit-validation.md
rg -n "audit|idempotent|chart_result|dignities|sect_condition|public payload unchanged|no recalculation" _condamad/stories/CS-203-natal-dignity-audit-persistence/evidence
```

Story validation commands:

```powershell
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md
```

## 21. Regression Risks

- Risk: audit persistence recalculates dignities.
  - Guardrail: no-calculation scans and mapper tests using precomputed dignity results.
- Risk: duplicate audit rows.
  - Guardrail: upsert key documentation and idempotence tests over row count.
- Risk: public payload changes accidentally.
  - Guardrail: `test_chart_json_builder.py`, `test_chart_result_service.py` and before/after evidence.
- Risk: audit rows drift from payload.
  - Guardrail: tests comparing row scores and JSON breakdowns to `NatalResult.dignities`.
- Risk: sensitive birth data duplicated.
  - Guardrail: audit shape review and evidence documenting persisted fields.
- Risk: failure silently ignored.
  - Guardrail: no broad `try/except`; explicit failure behavior test or transaction note.
- Risk: migration creep.
  - Guardrail: use existing model/repository first; stop on schema blocker before migration.
- Risk: audit becomes source of truth.
  - Guardrail: no public response reads from audit table; `json_builder.py` remains regression-only.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Treat CS-197 through CS-202 as completed and canonical.
- Do not change dignity calculation, sect calculation, planet sect condition calculation, public JSON projection, frontend or API routes.
- Do not introduce new dependencies.
- Do not add LLM behavior, prediction behavior, seeds or Alembic migrations unless a documented schema blocker is approved by the user.
- Do not add local astrology constants, aliases, compatibility paths or silent fallbacks.
- Do not read audit rows to build `NatalResult` or any public response.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in evidence.
- Do not preserve legacy behavior for convenience.
- Ne pas marquer la story complete sans fichiers d'evidence et commandes de validation.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified
  fallback, compatibility, legacy, migration-only, shim, alias, TODO or hidden residual work.

## 23. References

- `CS-191 advanced-planet-dignity-engine` - source des `PlanetDignityResult` calcules.
- `CS-197 sect-audit-explicit-contract` - contrat chart-level de secte.
- `CS-198 planet-sect-condition-normalization` - contrat de condition de secte par planete.
- `CS-199 advanced-sect-scoring-integration` - integration canonique des faits de secte dans le scoring.
- `CS-200 hellenistic-medieval-golden-cases` - golden cases a preserver.
- `CS-201 natal-public-json-projection-cleanup` - projection publique a ne pas modifier.
- `CS-202 natal-expert-panel` - consommation frontend a ne pas toucher.
- `_condamad/stories/regression-guardrails.md` - invariants applicables et nouvel invariant `RG-130`.
- `docs/db_seeder/astrology/astral_chart_planet_dignity_results.json` - metadata de la table audit existante.
