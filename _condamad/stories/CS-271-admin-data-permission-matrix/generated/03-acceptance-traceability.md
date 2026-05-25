# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The permission matrix document exists. | `docs/architecture/admin-permission-matrix.md` created with a French global file comment. | `python -B -m pytest -q .\backend\tests\unit\test_admin_permission_matrix_contract.py --tb=short` PASS; `rg` matrix scan PASS. | PASS |
| AC2 | The four internal roles appear in the matrix. | Matrix rows for `ADMIN`, `MARKETER`, `TECHNO`, `ASTRO_EXPERT`. | Contract test `test_permission_matrix_covers_roles_domains_and_actions` PASS; targeted `rg` PASS. | PASS |
| AC3 | The four data domains are classified. | Domain table documents `business`, `technical`, `astrology`, `debug`. | Contract test covers every role/domain pair; targeted `rg` PASS. | PASS |
| AC4 | Birth data is marked sensitive. | Matrix and masking rules state `données de naissance` are sensitive and masked outside approved admin contexts. | Contract test `test_sensitive_and_debug_data_are_separated` PASS. | PASS |
| AC5 | Debug data categories are separated. | Debug domain separates `traces`, `prompts`, and `replay`; masking rule says a permission on one does not open the others. | Contract test `test_sensitive_and_debug_data_are_separated` PASS; targeted `rg` PASS. | PASS |
| AC6 | Matrix actions are complete. | Action table and matrix cover `read`, `search`, `export`, `replay`, `correct`. | Contract test `test_permission_matrix_covers_roles_domains_and_actions` PASS. | PASS |
| AC7 | Future roles grant no current access. | All `MARKETER`, `TECHNO`, `ASTRO_EXPERT` rows set `current_access` to `refuse` and `rbac_activation_state` to `inactive until RBAC`. | Contract test `test_future_roles_have_no_current_access_until_rbac` PASS. | PASS |
| AC8 | B2C client access is excluded. | Objective and hors-matrice sections explicitly exclude B2C client access. | Contract test `test_b2c_access_is_excluded_and_open_decisions_are_listed` PASS; targeted `rg` PASS. | PASS |
| AC9 | Open permission decisions are listed. | Dedicated `Decisions ouvertes` section lists `OPEN-ADMIN-PERM-001` through `OPEN-ADMIN-PERM-005`. | Contract test and targeted `rg` PASS. | PASS |
| AC10 | Runtime role state remains unchanged. | `backend/app/core/rbac.py` unchanged by this story; no target roles added to `VALID_ROLES`. | `python -B -c ... VALID_ROLES ...` PASS; contract tests import `VALID_ROLES` and assert target roles absent. | PASS |
| AC11 | Evidence artifacts are persisted. | Capsule generated files updated; evidence directory contains validation, surface status and source checklist files. | `condamad_validate.py` PASS after evidence update; final `git status --short -- <CS-271 paths>` recorded. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
