# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `admin_answer_audit_v1` is documented. | `docs/architecture/admin-answer-audit-api.md` defines the canonical contract and route family. | `rg -n "admin_answer_audit..." docs/architecture/admin-answer-audit-api.md _story_briefs/...` PASS; targeted pytest PASS. | PASS |
| AC2 | Admin use cases are explicit. | Contract section `Cas d'usage admin` defines consultation, diagnostic review and reponses rejetées. | Targeted `rg` PASS; `test_admin_answer_audit_contract_documents_required_shape` PASS. | PASS |
| AC3 | Consultable fields are explicit. | Contract sections `Champs de liste` and `Champs de detail` include `answer_id`, `evidence_refs`, `provider`, `model`, `prompt_version`. | Targeted `rg` PASS; targeted pytest PASS. | PASS |
| AC4 | Filters are explicit. | Contract section `Filtres de liste` defines `status`, `plan`, `created_from`, `created_to`, `provider`, `model`. | Targeted `rg` PASS; targeted pytest PASS. | PASS |
| AC5 | Birth data is masked. | Contract section `Masquage des donnees de naissance` forbids exact raw birth fields by default. | `test_admin_answer_audit_contract_masks_raw_birth_data_by_default` PASS, including `birth_lat` and `birth_lon`. | PASS |
| AC6 | Permission errors are explicit. | Contract section `Permissions et erreurs` documents `401`, `403`, `404`, `503`. | Targeted `rg` PASS; targeted pytest PASS. | PASS |
| AC7 | Rejected answers are consultable. | Contract list/detail fields include `status: rejected` and `rejection_reason`. | Targeted `rg` PASS; targeted pytest PASS. | PASS |
| AC8 | Chart diagnostics stay separate. | Contract section `Separation des owners` keeps `admin_chart_diagnostics_v1` separate. | Targeted `rg` PASS; targeted pytest PASS. | PASS |
| AC9 | Runtime route exposure is unchanged. | No router/model/repository/migration/frontend file added for this API. | Route-neutrality and forbidden-path tests PASS; app/frontend answer-audit scan returned exit 1 = PASS no matches. | PASS |
| AC10 | Protected route behavior is specified. | Contract specifies future `require_admin_user` dependency and auth/error behavior. | `python -B -m pytest -q app/tests/integration/test_admin_answer_audit_contract.py --tb=short` PASS. | PASS |
| AC11 | Application source surfaces remain unchanged. | Only doc, backend integration test and CONDAMAD evidence/status files were changed for CS-267. | `git status --short -- backend/app frontend/src` recorded unrelated dirty files plus the CS-267 test; no runtime app/frontend source change. | PASS |
| AC12 | Evidence artifacts are persisted. | `validation.txt`, `app-surface-status.txt`, `source-checklist.md`, generated trace/final/review evidence updated. | `condamad_validate.py _condamad/stories/CS-267-admin-answer-audit-api` PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
