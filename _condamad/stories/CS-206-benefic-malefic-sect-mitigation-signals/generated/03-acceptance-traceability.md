# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime natures are audited. | Evidence audit of `astral_planet_natures` and runtime support. | Runtime audit file + seed/reference tests. | PASS |
| AC2 | `SectNatureMitigationCondition` exists. | Add immutable contract in `advanced_conditions/contracts.py`. | `test_sect_nature_mitigation_detector.py`. | PASS |
| AC3 | Malefic in sect gives `mitigated`. | Detector maps runtime malefic + `is_in_sect`. | Detector test. | PASS |
| AC4 | Malefic out of sect gives `aggravated`. | Detector maps runtime malefic + `is_out_of_sect`. | Detector test. | PASS |
| AC5 | Benefic in sect gives `supported`. | Detector maps runtime benefic + `is_in_sect`. | Detector test. | PASS |
| AC6 | Benefic out of sect gives `weakened`. | Detector maps runtime benefic + `is_out_of_sect`. | Detector test. | PASS |
| AC7 | Non-evaluable natures are explicit. | Detector emits neutral/unknown contract states. | Detector test. | PASS |
| AC8 | Missing or no-time sect conditions do not fabricate mitigation signals. | Detector skips missing `PlanetSectCondition`; no-time JSON keeps existing suppression. | Detector + JSON tests. | PASS |
| AC9 | `AdvancedConditionEngine` consumes runtime-supported codes. | Engine invokes detector and emits conditions only when runtime type/weight exists. | Engine test + seed/reference test. | PASS |
| AC10 | Public JSON serializes precomputed facts only. | `json_builder.py` serializes `TraditionalPlanetCondition.sect_nature_mitigation`. | JSON builder test + no-calculation scan. | PASS |
| AC11 | Traditional conditions integrate or document non-integration. | Normalizer attaches mitigation contract from advanced facts. | Traditional normalizer/golden tests. | PASS |
| AC12 | Downstream effects are runtime-governed. | Runtime type and neutral weight seed for `sect_nature_mitigation`; profiles enriched through existing engine. | Engine/profile tests + seed evidence. | PASS |
| AC13 | Listed score fields remain unchanged. | No dignity scoring code changed; snapshots compare dignity fields. | Natal/golden tests + evidence snapshot. | PASS |
| AC14 | Frontend displays facts without deriving them if frontend changes. | No frontend change expected if generic advanced facts are sufficient. | Frontend scans; npm checks not applicable if untouched. | PASS |
| AC15 | Local doctrine constants are absent. | No forbidden constants/imports/branches introduced. | RG-133 scans. | PASS |
| AC16 | Evidence references runtime. | Evidence files cite runtime source and validation commands. | Evidence files + `rg` checks. | PASS |
