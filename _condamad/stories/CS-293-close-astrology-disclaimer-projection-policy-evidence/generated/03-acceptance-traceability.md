# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | CS-284 policy document exists. | `docs/architecture/astrology-disclaimer-projection-policy.md` created with `policy_id: astrology_disclaimer_projection_policy`. | `python -B -c` path check PASS; `rg -n "astrology_disclaimer_projection_policy"` PASS. | PASS |
| AC2 | Existing disclaimers are inventoried. | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md` inventories backend, frontend, docs and briefs. | Bounded `rg` inventory scans recorded; source checklist PASS. | PASS |
| AC3 | Usage classes are explicit. | Policy and inventory classify natal, prediction, AI, degraded mode and missing birth time. | Targeted `rg` usage-class scan on policy/inventory PASS. | PASS |
| AC4 | B2C plan mapping is explicit. | Policy maps `beginner_summary_v1` and `client_interpretation_projection_v1` for `free`, `basic`, `premium`. | Targeted `rg` projection-plan scan PASS. | PASS |
| AC5 | LLM disclaimer authorship is blocked. | Policy states disclaimers are application-controlled and application code owns them; LLM does not create/rewrite/mutate. | Targeted `rg` LLM-boundary scan PASS. | PASS |
| AC6 | Degraded states are resolved. | Policy documents `no_time`, `degraded`, `BGS_DEGRADED_NO_TIME`, and guidance product gap owner/next action. | Targeted `rg` degraded-state and gap scan PASS. | PASS |
| AC7 | CS-284 final evidence exists. | CS-284 `evidence/` and `generated/10-final-evidence.md` created. | `python -B -c` path check PASS. | PASS |
| AC8 | Public API surface stays unchanged. | No backend API file modified; policy only. | `python -B -c "from app.main import app; ... app.openapi(); ... app.routes"` PASS. | PASS |
| AC9 | Regression tests stay green. | No runtime code changed. | `python -B -m pytest -q tests\architecture\test_api_contract_neutrality.py --tb=short` PASS: 21 passed; full `python -B -m pytest -q --tb=short` PASS: 3380 passed, 1 skipped, 1212 deselected. | PASS |
| AC10 | App source surfaces remain unchanged. | `backend/app`, `frontend/src`, `backend/migrations` untouched by this story. | Scoped `git status --short` shows only docs and CONDAMAD artifacts for this story plus pre-existing registry dirt. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
