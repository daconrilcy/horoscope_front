# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The internal role model document exists. | `docs/architecture/internal-role-model.md` created with a French global file comment. | `python -B -m pytest -q .\backend\tests\unit\test_internal_role_model_contract.py --tb=short` PASS; `rg` document scan PASS. | PASS |
| AC2 | The four internal roles are defined. | Role fiches define `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`. | `rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT" .\docs\architecture\internal-role-model.md` PASS. | PASS |
| AC3 | `ADMIN` is the only active internal role. | Document states `ADMIN` is the only operational role in the target quartet and excludes pre-existing runtime roles from that model. | `test_runtime_rbac_does_not_activate_future_internal_roles` PASS. | PASS |
| AC4 | Future roles grant no current access. | Future role fiches are `target-only` with `Aucun acces courant`; runtime roles are not aliases for target roles. | `test_future_internal_roles_are_target_only_without_current_access` PASS. | PASS |
| AC5 | B2C subjects are separate from internal roles. | Document section `Frontiere des sujets` separates clients B2C from internal roles. | `test_internal_role_model_document_defines_required_roles_and_boundaries` PASS; `rg` scan PASS. | PASS |
| AC6 | B2B subjects are separate from internal roles. | Document section `Frontiere des sujets` separates comptes B2B from internal roles. | `test_internal_role_model_document_defines_required_roles_and_boundaries` PASS; `rg` scan PASS. | PASS |
| AC7 | Admin surfaces are identified. | Document lists dashboard, audit, content, logs, support and related admin families. | `test_role_model_reuses_existing_admin_surface_documentation` PASS. | PASS |
| AC8 | Permission matrix dependency is listed. | Document names CS-271 as dependency for permission decomposition. | `rg` scan for `CS-271` and permissions PASS. | PASS |
| AC9 | Route surfaces remain unchanged. | No route, auth, migration or frontend file was edited for this story. | `rg -n "MARKETER|TECHNO|ASTRO_EXPERT" .\backend\app .\frontend\src .\backend\migrations ...` exit 1 = PASS/no matches; scoped `git status` recorded pre-existing unrelated dirty files only. | PASS |
| AC10 | Evidence artifacts are persisted. | Capsule generated files, `source-checklist.md` and evidence files updated under CS-270. | `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-270-internal-role-model` PASS after evidence update. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
