# Story CS-201 natal-public-json-projection-cleanup: Stabiliser la projection JSON publique du theme natal

Status: ready-to-dev

## 1. Objective

Nettoyer, stabiliser et documenter la projection JSON publique du theme natal
apres CS-197 a CS-200.
`build_chart_json()` et le service de restitution publique doivent exposer les
faits deja presents dans `NatalResult` ou dans un payload persiste, sans
recalcul astrologique, sans alias obsolète et sans changement de route, de
methode HTTP ou de statut HTTP.

La sortie vise une surface directement consommable par le frontend et les
futures UI expertes. Les dignites, la secte chart-level, la condition de secte
par planete, les profils, les signaux, les conditions avancees, les dominantes,
l'adaptateur interpretatif et les blocs structurels doivent avoir une politique
de presence, neutralisation ou absence explicite et testee.

## 2. Trigger / Source

- Source type: follow-up story
- Source reference: brief utilisateur du 2026-05-20 pour CS-201, follow-up de CS-197, CS-198, CS-199 et CS-200.
- Reason for change: le domaine natal calcule des faits avances, mais la projection publique doit devenir une surface stable et auditable avant l'exploitation frontend CS-202.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/chart`
- In scope:
  - auditer `backend/app/services/chart/json_builder.py` et les tests de projection publique;
  - stabiliser la projection des blocs listés dans le brief CS-201:
    `dignities`, `dignities.sect`, `sect_condition`, profils, signaux,
    conditions avancees, dominantes, `interpretation_adapter` et blocs structurels;
  - verifier la projection en mode complet et en mode degrade sans heure quand le mode existe;
  - documenter la politique `computed and present`, `computed but empty`, `not available because of chart mode` et `missing because of old persisted payload`;
  - ajouter ou adapter les tests de contrat JSON public et les tests `ChartResultService`;
  - produire les snapshots et preuves persistantes sous `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/`.
- Out of scope:
  - modifier les calculateurs et moteurs de domaine: secte, condition de
    secte, conditions avancees, profils, signaux, dominantes ou `interpretation_adapter`;
  - modifier la doctrine, les scores, les poids runtime, les seeds, les migrations, les tables DB, les routes API, les methodes HTTP, les statuts HTTP ou le frontend React;
  - generer une interpretation narrative, des prompts LLM ou une route API;
  - changer les contrats de calcul CS-197, CS-198, CS-199 ou les cas golden CS-200.
- Explicit non-goals:
  - ne pas recalculer la secte, `sect_condition`, hayz, out-of-sect, rejoicing, dominantes, signaux, maisons, angles, points ou rulers dans `json_builder.py`;
  - ne pas ajouter `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy` ou `legacy_planet_sect`;
  - ne pas fabriquer des valeurs manquantes pour anciens payloads persistants;
  - ne pas masquer les donnees indisponibles par des fallbacks silencieux;
  - ne pas contourner `RG-108`, `RG-112`, `RG-115`, `RG-118`, `RG-119`, `RG-120`, `RG-121`, `RG-122`, `RG-123`, `RG-124`, `RG-125`, `RG-126`, `RG-127` ou `RG-128`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: api-contract-change
- Brief archetype: public-contract-projection-cleanup
- Archetype reason: la story touche une forme de payload public existante et doit figer un contrat JSON, sans ajouter de route ni changer les calculs.
- Archetype adaptation: `public-contract-projection-cleanup` est le libelle du brief; `api-contract-change` est l'archetype CONDAMAD valide le plus proche.
- Behavior change allowed: constrained
- Behavior change constraints:
  - les resultats astrologiques, scores, faits de secte, conditions avancees, dominantes et faits d'adaptation interpretative ne doivent pas changer;
  - seules la presence, la forme, l'ordre deterministe ou la nullabilite des champs publics peuvent changer quand la difference est documentee dans `public-json-validation.md`;
  - `json_builder.py` doit rester un projecteur et ne doit pas importer ou instancier de moteurs astrologiques;
  - les blocs publics doivent provenir de `NatalResult` ou du payload deja persiste;
  - aucun alias de compatibilite n'est autorise.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un champ public doit etre retire ou renomme
  au-dela des clarifications explicitement autorisees, ou si un ancien payload
  persiste ne peut pas etre projete sans recalcul.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La projection doit consommer `NatalResult` ou le payload persiste, pas les moteurs ni les references runtime directement. |
| Baseline Snapshot | yes | La forme publique avant/apres doit etre capturee pour prouver les invariants et les differences autorisees. |
| Ownership Routing | yes | Les responsabilites de calcul et de projection doivent rester chez leurs owners canoniques. |
| Allowlist Exception | no | Aucune exception large, alias ou fallback n'est autorise; seuls les hits de scans exacts peuvent etre documentes comme preuves. |
| Contract Shape | yes | Les champs publics, nullabilites et noms de serialisation doivent etre explicites. |
| Batch Migration | no | La story ne migre pas plusieurs surfaces concurrentes et ne cree pas de payload parallele. |
| Reintroduction Guard | yes | Les recalculs, imports de moteurs, constantes doctrinales et alias legacy doivent rester bloques. |
| Persistent Evidence | yes | Audits, snapshots, validation et scans doivent rester dans le dossier de story. |

Brief-level contract requirements not represented as CONDAMAD contract names:

- Public Payload Stability: le payload public doit devenir directement
  exploitable par le frontend et les futures UI expertes.
- No Calculation in Projection: `json_builder.py` doit serialiser les faits
  deja produits, sans instancier de moteur astrologique.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `app.domain.astrology.natal_calculation.NatalResult`;
  - `chart_results.result_payload` pour les payloads deja persistants;
  - contrats deja produits par les owners de domaine: `ChartSectResult`,
    `PlanetSectCondition`, `PlanetDignityResult`, profils, signaux, conditions
    avancees, dominantes et `interpretation_adapter`.
- Runtime artifact:
  - sortie JSON de `build_chart_json()` sur au moins un cas complet;
  - payload persiste relu via `ChartResultService` quand le test de service couvre l'ancien payload ou la persistance;
  - tests de contrat `NatalResult` et golden cases CS-200.
  - AST guard/static import scan over `backend/app/services/chart/json_builder.py` for projection ownership.
- Secondary evidence:
  - tests unitaires `backend/app/tests/unit/test_chart_json_builder.py`;
  - tests `backend/app/tests/unit/test_chart_result_service.py`;
  - scans interdits sur `json_builder.py` et les surfaces astrology concernees;
  - snapshots `public-json-before.json` et `public-json-after.json`.
- Static scans alone are not sufficient for this story because:
  - l'absence d'import de moteur ne prouve pas que la sortie publique conserve les objets CS-197/CS-198;
  - les modes degrade et anciens payloads doivent etre prouves par comportement JSON, pas seulement par lecture de code.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-before.json`
  - `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-projection-audit-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json`
  - `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-validation.md`
- Required snapshot blocks:
  - `dignities`
  - `dignities.sect`
  - `dignities.planets[*].sect_condition`
  - `planet_condition_profiles`
  - `planet_condition_signals`
  - `advanced_conditions`
  - `dominant_planets`
  - `interpretation_adapter`
  - `astral_points`
  - `houses`
  - `angles`
  - `signs_runtime`
  - `house_rulers`
  - `chart_balance`
- Comparison rule:
  - scores, advanced conditions, condition profiles, dominance values and `interpretation_adapter` facts must not change;
  - allowed differences are limited to documented shape, presence, ordering and nullability changes;
  - volatile timestamps, request IDs, DB IDs and hashes should be excluded from curated snapshots.
- Expected invariant:
  - no score, advanced condition, condition profile, dominance value, `interpretation_adapter` fact, route, method, HTTP status code, frontend file, DB migration or seed change.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Positions, points, houses, angles and signs runtime | `natal_calculation.py` and runtime builders | `json_builder.py` recalculation |
| Chart sect | `backend/app/domain/astrology/dignities/sect_calculator.py` | `backend/app/services/chart/json_builder.py` inference |
| Planet sect condition | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | projection or downstream recalculation |
| Dignity scoring | `backend/app/domain/astrology/dignities/**` | JSON builder or tests as doctrine engine |
| Condition profiles and signals | `backend/app/domain/astrology/condition/**` | projection thresholds or prompt logic |
| Advanced conditions | `backend/app/domain/astrology/advanced_conditions/**` | JSON builder condition detection |
| Dominant planets | `backend/app/domain/astrology/dominance/**` | JSON builder ruler/angularity/elevation scoring |
| Interpretation adapter facts | `backend/app/domain/astrology/interpretation_adapters/**` | JSON builder narrative, prompt or LLM generation |
| Public chart JSON shape | `backend/app/services/chart/json_builder.py` | domain calculation ownership |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: no broad allowlist or implementation exception is allowed. Exact scan
  hits must be documented in `public-json-validation.md` with a reason and
  affected file.

## 4f. Contract Shape

- Contract type:
  - existing public chart JSON payload shape produced by `build_chart_json()` and persisted by `ChartResultService`.
- Fields:
  - `dignities.score_profile`, `dignities.tradition`, `dignities.reference_version`, `dignities.sect`, `dignities.planets`;
  - `dignities.sect.chart_sect`, `sun_horizon_position`, `sun_above_horizon`, `calculation_basis`, `reference_system`;
  - `dignities.planets[*].sect_condition` fields: `planet_code`,
    `chart_sect`, `intrinsic_sect`, `planet_sect_condition`, boolean flags,
    `calculation_basis` and `reference_system`;
  - `planet_condition_profiles`, `planet_condition_signals`, `advanced_conditions`, `dominant_planets`, `interpretation_adapter`;
  - `astral_points`, `houses`, `angles`, `signs_runtime`, `house_rulers`, `chart_balance`.
- Required fields:
  - `dignities.sect` is required as the CS-197 object when dignity results are computed;
  - `dignities.planets[*].sect_condition` is required as the CS-198 object for newly computed dignity results;
  - computed list outputs with no entries serialize as `[]`;
  - computed map outputs with no entries serialize as `{}`;
  - unavailable time-dependent blocks preserve the current mode-specific neutralization behavior.
- Optional fields:
  - missing blocks from old persisted payloads may remain absent, `null`, `{}` or `[]` only according to the documented existing project convention;
  - `dominant_planets` and `interpretation_adapter` may be `null` in no-time modes if that is the existing neutralization contract.
- Status codes:
  - no HTTP endpoint, method or HTTP status code is modified by this story.
- Serialization names:
  - canonical public names are the field names listed above;
  - forbidden names include `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`.
- Frontend type impact:
  - no frontend change in this story; the stable payload prepares future CS-202 consumption.
- Generated contract impact:
  - inspect OpenAPI, Pydantic response models, generated clients or TypeScript generated contracts if present;
  - if chart JSON remains dynamically shaped, record `Chart JSON remains dynamically shaped and is not represented by a generated client contract.` in `public-json-validation.md`.
- Public target shape:
  - `dignities` exposes score profile metadata, `sect` as the CS-197 object,
    planet scores, `sect_condition` as the CS-198 object and breakdown lists;
  - `planet_condition_profiles` is a map keyed by planet code with functional
    axes, `ranking_score`, `condition_level`, `breakdown` and
    `explanation_facts`;
  - `planet_condition_signals` is a map keyed by planet code with precomputed
    signal entries: `code`, `axis`, `level`, bounds, value, use, weight and hint;
  - `advanced_conditions` is a list of detected condition facts with code,
    type, score effect, axis weights and evidence;
  - `dominant_planets` exposes top planet, chart ruler, most elevated planet
    and ranked planet factors when available;
  - `interpretation_adapter` exposes factual arrays only: signals, themes,
    topics, axes, tension, support, critical patterns and narrative priorities.
- Public target shape rules:
  - `json_builder.py` must not compute thresholds, detect conditions,
    classify planets, build prompts or create narrative interpretation;
  - empty computed list outputs serialize as `[]`;
  - empty computed map outputs serialize as `{}`;
  - unavailable time-dependent outputs follow the existing neutralization mode;
  - old persisted payload gaps are not fabricated.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: the story stabilizes one public projection surface and must not create a second payload form or staged compatibility shape.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `evidence/public-json-before.json` | Capturer le payload initial et, si possible, un cas no-time. |
| Before audit | `evidence/public-json-projection-audit-before.md` | Cartographier projection, neutralisation et anciens payloads. |
| After snapshot | `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json` | Capturer les memes cas apres stabilisation. |
| Validation summary | `evidence/public-json-validation.md` | Enregistrer commandes, resultats, comparaison, scans et surfaces non modifiees. |

`public-json-validation.md` must record added fields, removed fields, renamed
fields, nullability changes, ordering changes, no-change score fields and
no-change astrology facts.

## 4i. Reintroduction Guard

- Guard target:
  - prevent astrology calculation, doctrine constants, legacy aliases and missing-block fabrication from entering the public projection layer.
- Forbidden examples:
  - imports or instantiations in `json_builder.py` of sect calculators,
    dignity scoring services, advanced condition engines, profile/signal
    builders, dominance engines, adapter engines, SwissEph or `swe`;
  - legacy fields: `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`;
  - production constants for sect planets, horizon houses, joys or planetary
    joys;
  - forbidden projection logic: house membership checks, chart sect
    comparisons for recomputation, planet membership checks, score threshold
    comparisons, condition axis threshold comparisons, prompt construction or
    LLM calls.
- Architecture guard against reintroduction:
  - targeted pytest assertions on JSON shape;
  - scans listed in the validation plan;
  - forbidden symbols in `json_builder.py` must fail the scan if reintroduced;
  - validation markdown must classify allowed hits and fail review on unclassified forbidden hits.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/services/chart/json_builder.py` -
  `build_chart_json()` already projects the advanced and structural chart
  blocks, with no-time neutralization for houses, house rulers, dominants and
  `interpretation_adapter`.
- Evidence 2: `backend/app/services/chart/json_builder.py` -
  `_serialize_chart_sect()` and `_serialize_planet_sect_condition()` validate
  the CS-197/CS-198 object shapes.
- Evidence 3: `backend/app/services/chart/json_builder.py` -
  `_serialize_condition_profiles()` and `_serialize_condition_signals()`
  currently expose envelope metadata plus nested `planets`.
- Evidence 4: `backend/app/tests/unit/test_chart_json_builder.py` - existing
  tests assert sect object shape, per-planet `sect_condition`, advanced
  conditions, dominants, `interpretation_adapter` and no-time neutralization.
- Evidence 5: `backend/app/tests/unit/test_chart_result_service.py` -
  persistence tests assert advanced blocks and prove pre-CS-198 payloads can
  validate without `sect_condition`.
- Evidence 6: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` contains the source fields required by the brief.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants
  `RG-108`, `RG-112`, `RG-115`, `RG-118` to `RG-127` were consulted; `RG-128`
  is added by this story.

## 6. Target State

After implementation:

- `build_chart_json()` serializes all relevant natal fact blocks consistently from `NatalResult` or from already persisted payloads.
- `dignities.sect` remains the explicit CS-197 object and never regresses to a string.
- `dignities.planets[*].sect_condition` remains the explicit CS-198 object for newly computed dignity results.
- Advanced public blocks are present when available, empty when computed empty, and neutralized only according to existing chart-mode behavior.
- Old persisted payloads missing new blocks do not trigger recalculation or fabricated defaults.
- Snapshots and validation markdown document before/after public payload shape, generated contract impact and scan results.
- No frontend, DB, seed, migration, route, method, status-code, dependency or astrology calculation code changes are made.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - projection must not recreate DB-backed reference vocabularies as local constants.
  - `RG-112` - astrology constants and fallbacks must not return in backend astrology or chart services.
  - `RG-115` - astral points remain computed by the natal runtime and only serialized publicly.
  - `RG-118` - dignity calculators remain pure owners of dignity facts; projection must not score.
  - `RG-119` - condition profiles remain derived from dignity results, not projection thresholds.
  - `RG-120` - condition signal thresholds must not be encoded in JSON projection.
  - `RG-121` - dominance calculation remains owned by `PlanetDominanceEngine`.
  - `RG-122` - advanced condition detection remains owned by `AdvancedConditionEngine`.
  - `RG-123` - interpretation adapter remains factual and non-narrative.
  - `RG-124` - chart-level sect contract remains canonical in `dignities.sect`.
  - `RG-125` - per-planet sect condition remains canonical in `dignities.planets[*].sect_condition`.
  - `RG-126` - advanced sect scoring consumes canonical facts and must not be rebuilt in projection.
  - `RG-127` - CS-200 golden cases must remain stable unless doctrine/runtime changes are approved.
  - `RG-128` - public JSON projection must serialize natal facts only and must not calculate astrology.
- Non-applicable invariants:
  - `RG-001` to `RG-009` - API route/facade invariants are outside scope because this story does not change route registration.
  - `RG-131` and frontend API invariants, if present later, are outside scope because no frontend files are modified.
- Required regression evidence:
  - public JSON before/after snapshots;
  - targeted projection and service tests;
  - golden case test command from CS-200;
  - scans for forbidden imports, aliases, constants, horizon tuples and generated contract impact.
- Allowed differences:
  - documented JSON shape, presence, ordering and nullability differences only;
  - no score, condition, dominance or astrology fact delta.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `dignities.sect` is the CS-197 object. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC2 | New `sect_condition` entries use the CS-198 object. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC3 | Advanced public blocks have tested present/empty serialization. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC4 | Structural blocks serialize or neutralize only. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC5 | `json_builder.py` has no forbidden engine imports. | `rg -n $projectionForbidden backend/app/services/chart/json_builder.py`. |
| AC6 | Forbidden sect compatibility names are absent. | `rg -n $legacyAliasPattern backend/app backend/tests -g "*.py"`. |
| AC7 | No-time modes preserve neutralization. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC8 | Old persisted payload gaps do not recalculate facts. | `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC9 | Generated contract impact is checked or documented. | `python -c "from backend.app.main import app; app.openapi()"`. |
| AC10 | Required evidence artifacts mention all public blocks named by the contract. | `rg -n $evidencePattern $storyEvidence`. |
| AC11 | CS-200 golden cases still pass. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. |
| AC12 | No adjacent frontend/API/DB surface changes. | `python -c "from backend.app.main import app; app.openapi()"`; `git diff --name-only -- $adjacentSurfaces`. |
| AC13 | Score values do not change. | `rg -n "no-change score" $storyEvidence/public-json-validation.md`. |
| AC14 | Astrology fact values do not change. | `rg -n "no-change astrology" $storyEvidence/public-json-validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Audit current projection and capture baseline (AC: AC3, AC4, AC5, AC10)
  - [ ] Inspect all files listed in section 18 before editing.
  - [ ] Create `public-json-projection-audit-before.md` answering the required
    field mapping, neutralization, import and old-payload questions.
  - [ ] The audit must answer which `NatalResult` fields are projected,
    dropped, renamed, synthesized and neutralized in no-time mode.
  - [ ] The audit must answer whether `json_builder.py` imports calculators,
    inspects sect strings, house numbers or planet lists, or supports old payloads.
  - [ ] Create `public-json-before.json` with at least one full chart case and, if supported, the no-time/degraded equivalent.

- [ ] Task 2 - Stabilize `dignities` projection (AC: AC1, AC2, AC5, AC6)
  - [ ] Ensure `_serialize_dignities()` consumes precomputed dignity aggregate and chart sect facts only.
  - [ ] Preserve `dignities.sect` and `dignities.planets[*].sect_condition` object forms.
  - [ ] Add assertions for required CS-197 and CS-198 fields and forbidden legacy aliases.

- [ ] Task 3 - Stabilize advanced public blocks (AC: AC3, AC5, AC11)
  - [ ] Serialize condition profiles, condition signals, advanced conditions, dominants and `interpretation_adapter` from precomputed data only.
  - [ ] Preserve deterministic order where upstream order is deterministic, or document the serialization ordering.
  - [ ] Add tests for present, computed-empty and unavailable/missing cases.

- [ ] Task 4 - Stabilize structural blocks and degraded modes (AC: AC4, AC7)
  - [ ] Verify `astral_points`, `houses`, `angles`, `signs_runtime`, `house_rulers` and `chart_balance` projection rules.
  - [ ] Preserve no-time/no-location neutralization behavior without changing calculation rules.
  - [ ] Add or update tests documenting mode-specific behavior.

- [ ] Task 5 - Cover old persisted payload behavior (AC: AC8)
  - [ ] Add or update a service/projection test for missing `interpretation_adapter`,
    dominants, signals and missing post-CS-198 `sect_condition` fields where feasible.
  - [ ] Cover old payload behavior for missing `dignities.sect` where feasible;
    the projection must not invent a fake chart sect object.
  - [ ] Document selected missing-block convention in `public-json-validation.md`.

- [ ] Task 6 - Check generated contracts and capture after evidence (AC: AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Inspect whether OpenAPI, Pydantic response models, generated clients or TypeScript contracts model chart JSON.
  - [ ] Create `public-json-after.json` using the same cases as the before snapshot.
  - [ ] Create `public-json-validation.md` with commands, results,
    comparison summary, scan results, generated contract check,
    non-touched-surface confirmation and no-change astrology facts.

- [ ] Task 7 - Run validation and record results (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Run targeted tests, golden cases, regression tests, Ruff and scans from section 21 after activating `.venv`.
  - [ ] Record skipped commands with exact reason and risk if any command cannot run.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `NatalResult` fields and existing contract dataclasses for source facts;
  - existing serializer helpers in `backend/app/services/chart/json_builder.py` when they only map already computed fields;
  - existing `backend/app/tests/unit/test_chart_json_builder.py` fixtures and focused assertions where practical;
  - existing `ChartResultService` persistence flow for persisted payload evidence;
  - CS-200 golden cases for no-regression proof.
- Do not recreate:
  - sect calculation;
  - planet sect condition calculation;
  - dignity scoring;
  - advanced condition detection;
  - condition profile scoring;
  - signal threshold matching;
  - dominance scoring;
  - interpretation adapter rule matching;
  - house, angle, point, sign runtime or ruler calculation.
- Shared abstraction allowed only if:
  - it is a narrow serialization helper;
  - it has no calculator/engine imports;
  - it does not inspect doctrine lists, score thresholds, house horizon tuples or planet classifications;
  - it reduces duplicated projection code already present in the targeted files.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- fabricated defaults for missing persisted blocks

Specific forbidden symbols / paths:

- calculator, scoring, advanced-condition, profile/signal, dominance, adapter engine,
  SwissEph or `swe` imports in `backend/app/services/chart/json_builder.py`;
- `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`;
- `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`, `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`, `ABOVE_HORIZON_HOUSES`, `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`, `PLANETARY_JOYS`;
- new files under `frontend/**`, `backend/app/api/**`, `backend/app/infra/**`, `backend/app/domain/prediction/**`, `migrations/**` or `docs/db_seeder/**`;
- new route, renamed endpoint, changed HTTP method, changed HTTP status code or auth behavior change.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public chart JSON projection shape | `backend/app/services/chart/json_builder.py` | API routes, frontend components, domain calculators |
| Chart result persistence/reload behavior | `backend/app/services/chart/result_service.py` | JSON builder recalculation, API handlers |
| Natal fact graph | `backend/app/domain/astrology/natal_calculation.py` | projection helpers, frontend inference |
| Dignity, sect and advanced astrology facts | `backend/app/domain/astrology/**` owners listed in section 4d | services/chart recalculation |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

Use this section because the story affects a public payload surface.

Required generated-contract evidence:

- inspect whether chart JSON is modeled by OpenAPI schema, Pydantic response model, generated TypeScript client or generated schema;
- if a generated contract exists, update only the documented JSON shape and capture before/after evidence;
- if no generated contract exists, write exactly this sentence in `public-json-validation.md`:

```text
Chart JSON remains dynamically shaped and is not represented by a generated client contract.
```

No route, method, HTTP status code or auth change is allowed.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- generated contract/schema/client files if repository inspection finds chart JSON modeling.

## 19. Expected Files to Modify

Likely files:

- `backend/app/services/chart/json_builder.py` - stabilize public projection, missing-block handling and serializer shape.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-before.json` - before snapshot.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-projection-audit-before.md` - before audit.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json` - after snapshot.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-validation.md` - validation summary.

Likely tests:

- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON shape, missing-block and degraded-mode coverage.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted payload behavior and no-recalculation proof.

Possible tests:

- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - only if `NatalResult` contract assertions need to document current fields.
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` - only if snapshot selectors need to include projection proof without changing doctrine.

Files not expected to change:

- `frontend/**` - frontend consumption is reserved for CS-202.
- `backend/app/api/**` - no route, method, HTTP status code or auth behavior change.
- `backend/app/infra/**` - no persistence model or repository changes.
- `backend/app/domain/prediction/**` - unrelated domain.
- `backend/app/domain/astrology/dignities/**` - no calculation changes expected.
- `backend/app/domain/astrology/advanced_conditions/**` - no detection changes expected.
- `backend/app/domain/astrology/condition/**` - no profile/signal scoring changes expected.
- `backend/app/domain/astrology/dominance/**` - no dominance scoring changes expected.
- `backend/app/domain/astrology/interpretation_adapters/**` - no `interpretation_adapter` rule changes expected.
- `migrations/**` - no DB schema changes.
- `docs/db_seeder/**` - no seed changes.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run from repository root after activating the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

Relevant regression tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py
```

Quality checks:

```powershell
ruff format .
ruff check .
```

Projection no-calculation scans:

```powershell
$projectionForbiddenTerms = @(
  "SectCalculator",
  "PlanetSectConditionCalculator",
  "PlanetDignityScoringService",
  "EssentialDignityCalculator",
  "AccidentalDignityCalculator",
  "AdvancedConditionEngine",
  "PlanetConditionProfileService",
  "PlanetConditionSignalBuilder",
  "PlanetDominanceEngine",
  "InterpretationAdapterEngine",
  "SwissEph",
  "swe"
)
$projectionForbidden = $projectionForbiddenTerms -join "|"
rg -n $projectionForbidden backend/app/services/chart/json_builder.py
```

Legacy alias scans:

```powershell
$legacyAliasTerms = @(
  "sect_legacy",
  "legacy_sect",
  "sect_code",
  "chart_sect_code",
  "planet_sect_code",
  "planet_sect_legacy",
  "sect_score_legacy",
  "legacy_planet_sect"
)
$legacyAliasPattern = $legacyAliasTerms -join "|"
rg -n $legacyAliasPattern backend/app backend/tests -g "*.py"
```

Doctrine constant scans:

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS" backend/app -g "*.py"
```

Horizon tuple scans:

```powershell
rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart -g "*.py"
```

Forbidden import scans in pure astrology domains:

```powershell
$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"
$roots = @(
  "backend/app/domain/astrology/dignities",
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/condition",
  "backend/app/domain/astrology/dominance",
  "backend/app/domain/astrology/interpretation_adapters"
)
rg -n $forbidden $roots -g "*.py"
```

Evidence checks:

```powershell
$storyEvidence = "_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence"
Test-Path "$storyEvidence/public-json-before.json"
Test-Path "$storyEvidence/public-json-projection-audit-before.md"
Test-Path "$storyEvidence/public-json-after.json"
Test-Path "$storyEvidence/public-json-validation.md"
$evidenceTerms = @(
  "dignities",
  "sect_condition",
  "planet_condition_profiles",
  "planet_condition_signals",
  "advanced_conditions",
  "dominant_planets",
  "interpretation_adapter",
  "astral_points",
  "houses",
  "angles",
  "signs_runtime",
  "house_rulers",
  "chart_balance",
  "generated client contract",
  "generated contract",
  "no recalculation",
  "no-change score",
  "no-change astrology"
)
$evidencePattern = $evidenceTerms -join "|"
rg -n $evidencePattern $storyEvidence
```

Adjacent surface checks:

```powershell
$adjacentSurfaces = @(
  "frontend",
  "backend/app/api",
  "backend/app/infra",
  "migrations",
  "docs/db_seeder"
)
git diff --name-only -- $adjacentSurfaces
```

Story validation after authoring:

```powershell
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md
```

Skipped-command rule:

- If any command cannot run, record the exact command, reason, risk and fallback evidence in `public-json-validation.md`.

## 22. Regression Risks

- Risk: projection recalculates astrology while tests only check shape.
  - Guardrail: forbidden import scans, no-calculation tests using precomputed objects, and `RG-128`.
- Risk: `dignities.sect` regresses to a string or duplicate alias.
  - Guardrail: CS-197 shape assertions, legacy alias scans and public snapshot.
- Risk: per-planet `sect_condition` disappears or becomes optional for new results.
  - Guardrail: CS-198 object assertions in `test_chart_json_builder.py`.
- Risk: advanced blocks remain nested or omitted in a way frontend consumers must infer.
  - Guardrail: contract map, before/after snapshot and targeted JSON assertions.
- Risk: old persisted payloads break or silently get fabricated facts.
  - Guardrail: persisted payload test and validation documentation.
- Risk: no-time mode leaks unreliable dominance or `interpretation_adapter` data.
  - Guardrail: existing no-time tests must be preserved or expanded.
- Risk: generated client or OpenAPI contract silently drifts.
  - Guardrail: generated contract check result in `public-json-validation.md`.
- Risk: snapshot becomes too broad and brittle.
  - Guardrail: curated snapshots excluding volatile IDs/timestamps/hashes.
- Risk: brief-level target shapes are weakened during implementation.
  - Guardrail: contract shape tests and evidence must cover each public block named in section 4f.

## 23. Dev Agent Instructions

- Implement only this story.
- Implement only CS-201.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through repointing, soft-disable, wrapper, alias, fallback or re-export.
- Do not change astrology calculation code unless a blocker is found and documented before implementation.
- Do not add frontend changes, DB migrations, seed updates, routes, methods, HTTP status code changes, auth changes, prompts or LLM calls.
- Do not fabricate missing fields for old persisted payloads.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved markers or hidden residual in-domain work.

## 24. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` - chart-level sect contract.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` - per-planet sect condition contract.
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` - advanced sect scoring consumption.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md` - golden cases and downstream invariants.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` - advanced dignity source facts.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - condition profile source facts.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` - condition signal source facts.
- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - dominant planet source facts.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` - advanced condition source facts.
- `_condamad/stories/CS-196-interpretation-adapter-layer/00-story.md` - interpretation adapter source facts.
- `_condamad/stories/regression-guardrails.md` - shared regression invariants.
- `backend/app/services/chart/json_builder.py` - public chart JSON projection owner.
- `backend/app/domain/astrology/natal_calculation.py` - `NatalResult` source fact graph.
