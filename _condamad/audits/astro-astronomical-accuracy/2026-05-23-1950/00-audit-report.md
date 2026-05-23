# Audit Report - Astro Astronomical Accuracy

## Audit Scope

- Domain key: `astro-astronomical-accuracy`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: astronomical reliability of backend natal calculations, including `swisseph`, simplified engine, ephemeris evidence, temporal precision and edge golden chart needs.
- Output folder: `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 records that no prior `astro-astronomical-accuracy` child folder existed.
- Adjacent audit folders consulted: `_condamad/audits/astro-feature-coverage/2026-05-23-1905`, `_condamad/audits/astro-reference-governance/2026-05-23-1939`, `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`.
- Story keys consulted: `CS-237`, `CS-240`, `CS-241`, `CS-242`, plus guardrails RG-137 through RG-148.
- Active findings after current evidence: F-001, F-002, F-003, F-004 and F-005.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: adjacent RG-137 through RG-148 protect astrology runtime boundaries, but no exact astronomical-accuracy guardrail exists.
- Implementation files in audited domain: no application file is changed by this audit.
- Governance/test files in audited domain: only the six new audit artifacts are created.
- Deferred non-domain concerns: frontend UI, API display, DB migrations, seed edits and runtime behavior changes remain outside this audit.

## Astronomical Reliability Matrix

| controle | surface_actuelle | preuve_reproductible | risque_astronomique | risque_architecture | golden_chart_associee | story_candidate |
|---|---|---|---|---|---|---|
| `swisseph` production usage | `ephemeris_provider.calculate_planets`, `houses_provider.calculate_houses`, service engine resolution and bootstrap | E-006, E-008, E-014 | Medium: real SwissEph path exists but production mode must be enforced/proven. | High: simplified and SwissEph paths coexist. | Paris normal case | CS-240 |
| Simplified engine restriction outside test/dev | `build_natal_result(engine="simplified")`, graph branch, config `NATAL_ENGINE_SIMPLIFIED_ENABLED` | E-005, E-007, E-014 | High: simplified positions are deterministic, not astronomical. | High: duplicate active calculation responsibility. | none | CS-240 |
| Ephemeris version and hash | `bootstrap_swisseph`, `path_version`, `path_hash`, `EPHEMERIS_PATH_HASH`, required files | E-008, E-009 | Medium: reproducibility depends on configured file validation/hash. | Medium: traceability can be incomplete if hash is optional. | Paris normal case | CS-242 |
| Position reproducibility | `backend/app/tests/golden/pro_dataset_v1.json` and swisseph golden tests | E-013, E-016 | High: current golden data does not prove all required sensitive modes. | Low: existing dataset is versioned and reusable. | all eight required golden charts | CS-241 |
| UTC, timezone and DST | `natal_preparation.py`, fold-aware validation, temporal tests | E-010, E-011 | Medium: conversion logic is strong, but DST edge charts need explicit golden coverage. | Low: source ownership is clear. | DST ambiguous time; DST nonexistent time | CS-241 |
| UT versus TT | `jd_ut`, optional `delta_t_sec`, `jd_tt`, `time_scale` | E-010, E-011 | Medium: TT is traceable when enabled; expected accuracy policy needs golden proof. | Low: option path is explicit. | Paris normal case | CS-241 |
| Sidereal ayanamsa | Lahiri mapping and invariant warning in `ephemeris_provider.py` | E-006, E-012 | Medium: mode exists but requires external golden reference. | Low: provider owns the state reset. | Sidereal Lahiri case | CS-241 |
| Topocentric and altitude | `frame="topocentric"`, `swe.set_topo`, altitude default | E-006, E-012 | Medium: option exists but needs comparison to reference output. | Low: service validates missing coordinates. | topocentric case | CS-241 |
| High-latitude houses | `houses_provider.calculate_houses` uses `swe.houses_ex`; no complete edge golden proof | E-012, E-013 | Medium: polar/high-latitude behavior can be unstable depending on system. | Low: errors are explicit through `HousesCalcError`. | high latitude case | CS-241 |
| Placidus unstable behavior | Placidus is default house system and provider delegates to SwissEph | E-006, E-012, E-013 | Medium: edge behavior is not proven by a dedicated reference case. | Medium: product policy for Placidus failure/fallback is not encoded here. | Placidus edge case | CS-241 |
| Reference chart comparison | Versioned golden dataset exists | E-013 | High: coverage is incomplete for required scenarios. | Low: existing golden location is canonical. | all eight required golden charts | CS-241 |

## Golden Chart Objectives

| Golden chart | Objective | Required evidence |
|---|---|---|
| Paris normal case | Prove baseline tropical geocentric Placidus output for normal user input. | External reference values for planets, ASC/MC, key cusps, expected JDUT, tolerance and ephemeris metadata. |
| DST ambiguous time | Prove ambiguous local birth time is rejected or resolved by explicit policy. | Input using a repeated local time, expected `ambiguous_local_time` or approved disambiguation, timezone evidence. |
| DST nonexistent time | Prove nonexistent local birth time is rejected explicitly. | Input using DST gap, expected `nonexistent_local_time`, timezone evidence. |
| high latitude case | Prove house/angle behavior at high latitude. | External reference values or explicit expected failure policy for selected house system. |
| Sidereal Lahiri case | Prove Lahiri sidereal longitudes and ayanamsa trace. | Tropical/sidereal reference pair or authoritative sidereal expected positions. |
| topocentric case | Prove topocentric frame and altitude affect positions/angles as expected. | Geocentric versus topocentric reference outputs and altitude metadata. |
| whole sign case | Prove whole sign houses produce expected cusp/sign mapping. | External reference or deterministic house-system expectations tied to ASC sign. |
| Placidus edge case | Prove unstable Placidus behavior is handled intentionally. | Expected success/failure policy, high-latitude input, SwissEph result or explicit error contract. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` | used | E-001 | Source contract for scope, AC and no-code-change boundary. | None. |
| `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md` | used | E-002 | Source brief for required checks and golden charts. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-137..RG-148 | used | E-003 | Existing adjacent astrology invariants consulted before findings. | No exact astronomical accuracy guardrail exists. |
| `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | out-of-domain | E-004 | Adjacent coverage audit used only to bound non-accuracy feature gaps. | Not an astronomical accuracy audit. |
| `_condamad/audits/astro-reference-governance/2026-05-23-1939` | out-of-domain | E-004 | Adjacent rule-source audit used to avoid duplicating governance findings. | Not an accuracy proof audit. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | out-of-domain | E-004 | Adjacent exposure audit used to defer API/frontend exposure. | Not an accuracy proof audit. |
| `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md` | used | E-005 | Baseline document explicitly states simplified and `swisseph` paths coexist. | Documentation is context, not runtime proof alone. |
| `backend/app/domain/astrology/swisseph_runtime.py` | used | E-006 | Canonical lazy import surface for SwissEph. | Source inspection only; no app edit. |
| `backend/app/domain/astrology/ephemeris_provider.py` | used | E-006, E-012 | Owner of `swe.calc_ut`, sidereal Lahiri, topocentric flags and ayanamsa trace. | External reference comparison not run here. |
| `backend/app/domain/astrology/houses_provider.py` | used | E-006, E-012 | Owner of `swe.houses_ex`, Placidus, whole sign and topocentric house handling. | High-latitude behavior needs golden proof. |
| `backend/app/domain/astrology/natal_preparation.py` | used | E-010, E-011 | Owner of timezone, DST, JDUT and optional TT preparation. | No external astronomical chart comparison in this file. |
| `backend/app/domain/astrology/natal_calculation.py` | used | E-007, E-014 | Public domain facade and engine option carrier. | Default `engine="simplified"` remains a finding. |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` | used | E-007, E-014 | Graph nodes branch between simplified and `swisseph` providers. | No behavior changed. |
| `backend/app/core/config.py` | used | E-008 | Owner of engine, SwissEph, pro-mode and ephemeris environment settings. | Environment-specific production values were not available. |
| `backend/app/core/ephemeris.py` | used | E-008, E-009 | Owner of ephemeris bootstrap, required-file validation and path hash calculation. | Hash guarantee depends on runtime config. |
| `backend/app/services/natal/calculation_service.py` | used | E-008, E-009, E-014 | Service resolves engine and enforces successful bootstrap before `swisseph`. | Exact production deployment config not audited. |
| `backend/app/api/v1/routers/public/astrology_engine.py` | used | E-008, E-009, E-014 | Public API propagates engine and ephemeris metadata and contains compare behavior. | API changes are out of scope. |
| `backend/app/tests/golden/pro_dataset_v1.json` | test-only | E-013 | Existing versioned golden dataset for `swisseph`. | Does not cover all required CS-241 chart objectives. |
| `backend/app/tests/**` and `backend/tests/**` selected astrology tests | test-only | E-011, E-012, E-016 | Existing tests prove temporal, option and structural contracts. | No new tests were added by this audit. |
| `backend/app/**` outside selected astrology/config/service/API files | out-of-domain | E-001, E-015 | Inspected only through bounded scans; app-code changes are forbidden. | No refactor performed. |
| `frontend/src/**`, `backend/migrations/**`, `docs/db_seeder/**` modification surface | out-of-domain | E-001, E-015 | Explicitly forbidden by story and verified as unchanged by intended final diff. | Existing untracked docs/briefs predate this audit run. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: F-001 identifies duplicate active calculation responsibility between simplified and `swisseph` paths for natal positions/houses.
- No Legacy: this audit creates no wrapper, alias, fallback, compatibility route or runtime branch.
- Mono-domain: findings stay in backend astrology astronomical accuracy; API exposure, frontend display and reference-governance thresholds are deferred.
- Dependency direction: providers depend on `app.core.ephemeris` for the lock/bootstrap state; no new dependency or app-code delta is introduced.

## Exhaustive Active Finding Surface

- F-001: `backend/app/core/config.py`, `backend/app/services/natal/calculation_service.py`, `backend/app/domain/astrology/natal_calculation.py`, `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`, `backend/app/api/v1/routers/public/astrology_engine.py`, selected engine tests. No file is changed by this audit.
- F-002: `backend/app/tests/golden/pro_dataset_v1.json`, existing golden/test files, temporal tests and future CS-241 golden suite. No file is changed by this audit.
- F-003: `backend/app/core/ephemeris.py`, `backend/app/services/natal/calculation_service.py`, chart-result persistence/API metadata owners to be selected by CS-242. No file is changed by this audit.
- F-004: `backend/app/domain/astrology/ephemeris_provider.py`, `backend/app/domain/astrology/houses_provider.py`, option tests and future CS-241 golden edge cases. No file is changed by this audit.
- F-005: future guardrail/test ownership only; no current guardrail update is justified by a new durable runtime invariant in this audit.

## Deferred Non-Domain Context

- Rule-source ownership and doctrine thresholds remain covered by `_condamad/audits/astro-reference-governance/2026-05-23-1939`.
- Runtime surface exposure and frontend/API product display are deferred to exposure/product-data audits.
- Prediction-specific `swisseph` usage under `backend/app/domain/prediction/**` is outside this natal astrology accuracy audit.
