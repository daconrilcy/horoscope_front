# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | The internal manifest exists. | `backend/app/domain/astrology/runtime/transit_chart_manifest.py` defines `TransitChartManifest` and `build_transit_chart_manifest()`. | `python -B -m pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py backend/tests/architecture/test_api_contract_neutrality.py --tb=short`; `manifest-after.json`. | PASS |
| AC2 | `transit_chart_v1` is the manifest family. | Manifest reuses `SELECTED_TEMPORAL_FAMILY_CODE` from `temporal_technique_selection.py`. | Unit test `test_internal_manifest_exists_for_transit_chart_v1`; JSON snapshot field `family_code`. | PASS |
| AC3 | Internal inputs are declared. | Manifest inputs include natal reference, transit target, timezone, location policy and proof reference. | Unit test `test_manifest_declares_required_internal_inputs_and_outputs`. | PASS |
| AC4 | Internal outputs are declared. | Manifest outputs include transiting objects, transit-to-natal relationships, diagnostic trace keys and blocked status. | Unit test `test_manifest_declares_required_internal_inputs_and_outputs`. | PASS |
| AC5 | Proof prerequisites are listed. | Manifest imports CS-250 proof vocabulary from `astronomical_proof.py`. | Unit test `test_manifest_lists_cs250_proof_and_cs252_doctrine_prerequisites`; targeted `rg` proof scan. | PASS |
| AC6 | Doctrine prerequisites are listed. | Manifest resolves CS-252 doctrine governance entries for aspect and interpretation rules. | Unit test `test_manifest_lists_cs250_proof_and_cs252_doctrine_prerequisites`; targeted `rg` doctrine scan. | PASS |
| AC7 | Trace requirements are bounded. | Trace fields are redacted key/status descriptors and state that trace does not create replay storage. | Unit test `test_trace_requirements_are_redacted_and_do_not_create_replay_storage`; targeted `rg` replay/trace scan. | PASS |
| AC8 | Public API runtime is unchanged. | No API/frontend code changed; OpenAPI neutrality test added for `TransitChartManifest`. | `test_transit_chart_manifest_is_not_public_api_contract`; negative `rg` on `backend/app/api frontend/src` returned no matches. | PASS |
| AC9 | Future runtime stories are identified. | Follow-up story keys cover graph manifest, runner integration, projection contract and public API gate. | Unit test `test_follow_up_runtime_stories_are_identified_without_implementation`. | PASS |
| AC10 | Evidence artifacts are persisted. | Evidence files under CS-279 include manifest JSON, API neutrality and validation summary. | `condamad_validate.py` PASS after evidence updates. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
