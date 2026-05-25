# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The segmentation document exists. | `docs/architecture/admin-endpoint-domain-segmentation.md` created with a French global file comment. | `backend/tests/unit/test_admin_endpoint_segmentation_contract.py::test_segmentation_document_exists_and_defines_required_fields`; `evidence/validation.txt`. | PASS |
| AC2 | Admin route domains are separated. | The document separates `business`, `technical` and `astrology` route families in the contract table. | `rg` domain scan in `evidence/validation.txt`; runtime route inventory in `evidence/route-inventory.txt`. | PASS |
| AC3 | Domain families map to CS-271 roles. | The document maps families to `MARKETER`, `TECHNO` and `ASTRO_EXPERT` as CS-271 inactive target roles. | `backend/tests/unit/test_admin_endpoint_segmentation_contract.py::test_admin_domains_are_separated_and_mapped_to_cs271_roles`. | PASS |
| AC4 | Sensitive access-log fields are specified. | The logging section requires `actor`, `route_family`, `action` and `correlation_id`. | `backend/tests/unit/test_admin_endpoint_segmentation_contract.py::test_sensitive_logging_and_client_exclusions_are_documented`; `rg` logging scan. | PASS |
| AC5 | Internal OpenAPI rules are documented. | The document defines `OpenAPI interne`, `internal-admin`, `internal-technical` and `app.openapi()` verification rules. | `backend/tests/unit/test_admin_endpoint_segmentation_contract.py::test_internal_openapi_rules_do_not_publish_internal_projection_tokens`; existing OpenAPI neutrality tests. | PASS |
| AC6 | Client debug surfaces are excluded. | The document excludes client access to debug, replay, trace, prompt and full astrology runtime surfaces. | `rg` client exclusion scan; unit contract test. | PASS |
| AC7 | Runtime admin routes are inventoried. | `evidence/route-inventory.txt` records current `/v1/admin` route paths from `app.routes`; the test uses `TestClient`. | `backend/tests/unit/test_admin_endpoint_segmentation_contract.py::test_runtime_admin_routes_are_inventoried_without_route_surface_change`. | PASS |
| AC8 | Existing route surfaces stay unchanged. | No backend route or frontend source was modified by this story; scoped status evidence records pre-existing dirty app files separately. | `evidence/app-surface-status.txt`; `git diff --check --` scoped CS-272 paths. | PASS |
| AC9 | Evidence artifacts are persisted. | `evidence/validation.txt`, `route-inventory.txt`, `app-surface-status.txt` and `source-checklist.md` are present. | Python/check commands recorded in `evidence/validation.txt`; capsule validation. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
