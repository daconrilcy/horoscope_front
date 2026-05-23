# Audit Report - Astro Reference Governance

## Audit Scope

- Domain key: `astro-reference-governance`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: governance of astrology rule sources across DB reference data, Python runtime, tests and doctrine docs.
- Output folder: `_condamad/audits/astro-reference-governance/2026-05-23-1939/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 records the empty same-domain root before this audit.
- Adjacent audit folders consulted: `_condamad/audits/astro-feature-coverage/2026-05-23-1905`, `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`, `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928`.
- Story keys consulted: `CS-237`, `CS-238`, `CS-239`, `CS-240`, plus guardrails RG-137 through RG-148.
- Active findings after current evidence: F-001, F-002, F-003, F-004, F-005 and F-006.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: RG-137 to RG-148 protect advanced planetary condition calculators, chart-object payloads and runtime boundaries, but no current guardrail protects rule source ownership as a complete governance matrix.
- Implementation files in audited domain: no file is changed by this audit.
- Governance/test files in audited domain: only the six new audit artifacts are created.
- Deferred non-domain concerns: API projection, frontend UI, DB migrations, seed edits, runtime calculator changes and story implementation remain outside this audit.

## Mandatory Governance Matrix

| Règle métier | Source actuelle | DB ou Python | Versionnée | Testée | Doctrine astrologique associée | Modifiable sans code |
| --- | --- | --- | --- | --- | --- | --- |
| Orbes | `docs/db_seeder/astrology/astral_aspect_orb_rules.json`; runtime loaders and `backend/app/domain/astrology/calculators/aspects.py` consume `AspectOrbRuleRuntimeData`. | DB + Python consumer | Oui côté DB via `reference_version_id`; Python consumer validates bounds. | Oui: `backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`, `backend/tests/architecture/test_astrology_runtime_boundary.py`. | Partielle: docs runtime aspectuelles existent, doctrine détaillée hors runtime. | Oui pour les valeurs DB; non pour la logique de résolution. |
| Poids de dominance | `docs/db_seeder/astrology/astral_dominance_score_weights.json`; `backend/app/domain/astrology/dominance/planet_dominance_engine.py`; `backend/app/domain/astrology/builders/sign_runtime_builder.py`. | Mixed | Partiel: poids DB versionnés pour dominance planétaire; poids de signes restent Python. | Oui partiel: `test_planet_dominance_engine.py`, `test_sign_runtime_builder.py`. | Partielle dans docs et micro-notes; pas de doctrine unique pour chaque facteur. | Partiel: poids DB modifiables, poids signe Python non. |
| Seuils de combustion | DB accidental dignity rules `8.5`; Python `SolarProximityThresholds.combust_max_distance_deg = 8.5`. | Mixed | DB oui; Python non versionné. | Oui: `test_contracts.py`, `test_solar_proximity_calculator.py`, `test_accidental_dignity_calculator.py`. | Micro-notes DB; pas de source doctrinale canonique liée au seuil Python. | DB oui pour dignity legacy; Python non pour advanced condition runtime. |
| Seuils de cazimi | DB accidental dignity rule `0.283`; Python `17.0 / 60.0`. | Mixed | DB oui; Python non versionné. | Oui: `test_contracts.py`, `test_solar_proximity_calculator.py`. | Micro-note DB; pas de doctrine canonique liée à la divergence `0.283` versus `17/60`. | DB oui pour dignity legacy; Python non pour advanced condition runtime. |
| Seuils d'under beams | DB accidental dignity rule max `17`; Python `under_beams_max_distance_deg = 15.0`; visibility threshold also uses `15.0` and `18.0`. | Mixed | DB oui; Python non versionné. | Oui: `test_contracts.py`, `test_solar_proximity_calculator.py`, `test_planetary_visibility_calculator.py`. | Micro-note DB; documentation doctrinale non canonique pour trancher `15` vs `17`. | DB oui pour dignity legacy; Python non pour advanced condition runtime. |
| Seuils de vitesse | DB relations `astral_speed_relations.json` and advanced weights; Python `DEFAULT_PLANETARY_MOTION_PROFILES` mean speeds and ratio thresholds. | Mixed | DB partiel; Python non versionné. | Oui: `test_planetary_motion_calculator.py`, `test_contracts.py`. | Documentation non canonique; no linked source for each mean speed. | Partiel: DB relation labels modifiables; Python profiles non. |
| Seuils de station | DB accidental dignity `absolute_speed_max_deg_per_day = 0.05`; Python motion profile uses `mean_speed * 0.05`; accidental calculator also defaults and compares to `0.05`. | Mixed | DB oui; Python non versionné. | Oui: `test_accidental_dignity_calculator.py`, `test_planetary_motion_calculator.py`. | Micro-note DB says threshold should be adapted by planet; no canonical doctrine binding the Python formula. | Partiel: one DB threshold modifiable, Python formula non. |
| Poids des maisons | DB house modalities/axis data; `HouseStrengthEvaluator` and `PlanetDominanceEngine` score angular/succedent/cadent in Python. | Mixed | DB metadata oui; Python weights non versionnés. | Oui partiel: `test_house_strength.py`, `test_planet_dominance_engine.py`. | Docs describe runtime surfaces; doctrinal scoring weights are not canonically sourced. | Non for current scoring constants. |
| Poids des dignités | `astral_essential_dignity_score_weights.json`, `astral_accidental_dignity_score_weights.json`, advanced condition weights; Python scoring service consumes them. | DB + Python consumer | Oui côté DB through score profiles/reference version. | Oui: `test_planet_dignity_scoring_service.py`, `test_traditional_golden_cases.py`, `test_triplicity_golden_cases.py`. | Partielle: reference sources exist for some dignity families, not complete in a single governance index. | Oui for DB weights. |
| Profils de signes | `astral_signs.json`, sign structural/translation data; `sign_runtime_builder.py` computes sign runtime weights in Python. | Mixed | DB data oui; Python weighting non versionné. | Oui partiel: `test_sign_runtime_data.py`, `test_sign_runtime_builder.py`. | `docs/recherches astro/tables-signes-et-roles.md` provides non-runtime context. | Partiel: sign metadata yes, runtime weight formula no. |
| Règles fixed stars | `astral_fixed_stars.json`, `astral_fixed_star_definitions.json`, `astral_fixed_star_keywords.json`; Python fixed-star calculators/selectors consume runtime data. | DB + Python consumer | Oui côté DB reference data; Python logic versioned by code only. | Oui: `test_fixed_star_runtime.py`, `test_fixed_star_conjunction_runtime.py`. | Partielle: DB keyword/profile text exists, doctrine source index incomplete. | Oui for star catalog/keywords; non for conjunction logic. |
| Règles d'aspects | `astral_aspect_definitions.json`, `astral_aspect_profiles.json`, `astral_aspect_orb_rules.json`; calculators and runtime contracts in Python. | DB + Python consumer | Oui côté DB for definitions/profiles/orbs. | Oui: aspect unit tests and architecture guards. | Runtime docs define structural vs interpretive layers; doctrine source is partial. | Oui for DB definitions/profiles/orbs; non for calculator algorithm. |
| Règles d'interprétation | DB interpretation profiles and adapter rules; Python catalogs under `interpretation/advanced_conditions` and projectors/builders. | Mixed | DB oui for seed profiles; Python catalogs non versionnés. | Oui partiel: `test_profile_runtime.py`, `test_signal_builder.py`, interpretation input tests. | Partielle; several docs are research/architecture context, not a governed doctrine registry. | Partiel: DB profiles yes, Python catalogs no. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-240-audit-reference-governance/00-story.md` | used | E-001 | Source contract for required domain, matrix, candidates and no-code-change scope. | None. |
| `_story_briefs/cs-240-audit-reference-governance-audit.md` | used | E-002 | Source brief for required rule families and validation expectations. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-137..RG-148 | used | E-003 | Existing invariants protect adjacent astrology runtime surfaces. | No exact rule-source governance guardrail exists. |
| `_condamad/audits/astro-reference-governance` | used | E-004 | Canonical output root for this audit domain. | No prior same-domain child folder existed. |
| `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | out-of-domain | E-005 | Adjacent product coverage audit used only for context. | Not a reference-governance audit. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | out-of-domain | E-005 | Adjacent exposure audit used to bound public/runtime projection concerns. | Not a source ownership audit. |
| `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928` | out-of-domain | E-005 | Adjacent payload audit used to avoid duplicating chart-object taxonomy findings. | Not a source ownership audit. |
| `docs/db_seeder/astrology/**` selected reference JSON files | used | E-006, E-007, E-008, E-009, E-010, E-011 | DB seed artifacts are current reference-data source evidence for orbs, dignities, dominance, aspects, fixed stars, signs and interpretation profiles. | Seed presence alone does not prove runtime consumption; paired with repository/runtime tests where available. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | used | E-012 | Runtime loader maps DB reference version to immutable astrology runtime reference. | Source inspection only; no DB migration or live DB query performed. |
| `backend/app/domain/astrology/planetary_conditions/contracts.py` | used | E-008, E-014 | Python owner of solar, visibility and motion threshold contracts. | No code change made. |
| `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py` | used | E-009, E-014 | Python owner of default mean speeds and station thresholds by formula. | No DB-backed profile found in this audit. |
| `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | used | E-008, E-009, E-015 | Python consumer of accidental dignity runtime rules and local speed comparison behavior. | No runtime refactor in scope. |
| `backend/app/domain/astrology/dominance/planet_dominance_engine.py` | used | E-010, E-015 | Python consumer of DB dominance weights and owner of some normalization/level thresholds. | No runtime refactor in scope. |
| `backend/app/domain/astrology/builders/sign_runtime_builder.py` | used | E-010, E-015 | Python owner of sign dominance weight formula. | No source-backed public decision says this formula should be DB-owned. |
| `backend/app/domain/astrology/calculators/aspects.py` and aspect runtime contracts | used | E-006, E-016 | Python consumer of DB aspect definitions and orb rules. | Aspect algorithm not audited for astronomical accuracy. |
| `backend/app/domain/astrology/fixed_stars/**` | used | E-011, E-017 | Python consumer/producer for fixed-star contacts from DB star catalog references. | Public exposure is out of domain. |
| `backend/app/domain/astrology/interpretation/**` selected profile/projector files | used | E-011, E-017 | Runtime interpretation profiles and projectors are part of current source ownership. | LLM prompt generation is out of domain. |
| `backend/tests/unit/domain/astrology/**` selected tests | test-only | E-014, E-015, E-016, E-017 | Deterministic tests prove current rules and contracts without modifying implementation. | Full astrology suite was not run. |
| `backend/tests/architecture/**` selected tests | test-only | E-016 | Architecture guards prove selected runtime boundaries. | No new guard was added by this audit. |
| `docs/architecture/astrology-runtime-surfaces.md` and `docs/recherches astro/**` selected docs | used | E-013 | Documentation context for runtime surfaces and doctrinal notes. | Research docs are not a complete versioned doctrine registry. |
| `backend/app/**` outside selected astrology/infra reference files | out-of-domain | E-001, E-019 | Inspected only through bounded scans; app changes are forbidden. | No refactor performed. |
| `frontend/src/**`, `backend/migrations/**`, `docs/db_seeder/**` modification surface | out-of-domain | E-001, E-019 | Explicitly forbidden by story and verified as unchanged by final diff. | No runtime behavior validated through UI/API. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: F-001 and F-002 identify duplicate active threshold ownership between DB reference rows and Python threshold/profile constants.
- No Legacy: no alias, shim, fallback, compatibility route or migration was created by this audit.
- Mono-domain: findings stay within astrology reference governance; implementation of DB migrations, runtime refactors and UI exposure is deferred.
- Dependency direction: source evidence shows DB/reference data flows through infra repositories into domain runtime contracts; no new reverse dependency or app-code delta is introduced.

## Exhaustive Active Finding Surface

- F-001: `docs/db_seeder/astrology/astral_accidental_dignity_rules.json`, `backend/app/domain/astrology/planetary_conditions/contracts.py`, `solar_proximity_calculator.py`, `planetary_visibility_calculator.py`, `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`, related tests. No file is to be changed by this audit.
- F-002: `docs/db_seeder/astrology/astral_accidental_dignity_rules.json`, `astral_speed_relations.json`, `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`, `planetary_motion_calculator.py`, `dignities/accidental_dignity_calculator.py`, related tests. No file is to be changed by this audit.
- F-003: `backend/app/domain/astrology/builders/sign_runtime_builder.py`, `interpretation/house_strength.py`, `dominance/planet_dominance_engine.py`, DB dominance/house seed files and related tests. No file is to be changed by this audit.
- F-004: DB interpretation profile seed files and Python interpretation profile catalogs/projectors. No file is to be changed by this audit.
- F-005: selected docs under `docs/architecture` and `docs/recherches astro`, DB `astral_sources.json` and reference-source files. No file is to be changed by this audit.
- F-006: governance/test guard surface only: future guardrails or tests must cover rule-source ownership. No app file is to be changed by this audit.

## Deferred Non-Domain Context

- `backend/app/domain/prediction/**` has transit/prediction orb logic visible in broad scans, but prediction reference governance is outside this audit.
- API serializers, frontend presentation, admin/debug tooling, DB migrations and seed-edit stories are deferred to implementation stories generated from this audit.
