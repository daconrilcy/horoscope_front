# CS-276 Implementation Review

Verdict: CLEAN

## Scope

- Story reviewed: `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md`.
- Source brief: `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md`.
- Tracker row: `_condamad/stories/story-status.md` entry `CS-276`, status `done`.
- Review type: implementation review after fix loop.

## Iterations

- Iteration 1: found missing audit evidence for denied consultations and fragile validation commands.
- Iteration 2: full backend pytest found guardrail registry and public/internal OpenAPI drift.
- Iteration 3: fresh review after fixes found no actionable issue.
- Iteration 4: brief-alignment pass found missing audit evidence for admin `source_missing` consultations, then fixed and revalidated.
- Iteration 5: full backend pytest found the new source-missing commit missing from the SQL-boundary allowlist, then fixed and
  revalidated.

## Findings Fixed

### F1 — Denied consultations were not journalized

- Severity: medium.
- Evidence: `backend/app/api/v1/routers/admin/chart_diagnostics.py` previously rejected non-admin users before calling
  `AdminChartDiagnosticsService`.
- Fix: added audited admin-only dependency and `AdminChartDiagnosticsService.record_failed_consultation`.
- Validation: `test_admin_chart_diagnostics_rejects_non_admin_user` now asserts a failed `admin_chart_diagnostics_consulted`
  audit event with sanitized target id and `insufficient_role`.

### F2 — Validation commands were too broad or order-dependent

- Severity: low.
- Evidence: `VC3` used OpenAPI string splitting by `/v1/public`, and `VC8` scanned all `backend/tests`, including unrelated
  replay/audit tests.
- Fix: changed `VC3` to inspect `app.openapi()["paths"]` and bounded `VC8` to the diagnostic service owner.
- Validation: updated `evidence/validation.txt`; CONDAMAD story validation and strict lint passed.

### F3 — Architecture guardrails were not synchronized with the new admin route

- Severity: medium.
- Evidence: full backend pytest reported router-root audit, SQL-boundary allowlist, test DB topology and public/internal OpenAPI
  failures for the new diagnostic route and tests.
- Fix: updated router audit evidence, SQL boundary evidence, DB test classification and public-only OpenAPI assertions.
- Validation: review-fix regression pytest passed; full backend pytest passed.

### F4 — Missing diagnostic sources were not journalized

- Severity: medium.
- Evidence: a valid admin consultation returning `404` for a missing chart source did not write an `audit_events` row.
- Fix: `AdminChartDiagnosticsService.get_chart_diagnostics` now records a failed consultation with `source_missing`, and the API
  commits the audit event before returning the typed error.
- Validation: `test_admin_chart_diagnostics_missing_source_is_typed` asserts the failed audit event and verifies that the raw chart
  reference is not returned in error details.

### F5 — SQL-boundary evidence was stale after the missing-source audit fix

- Severity: low.
- Evidence: full backend pytest failed
  `test_api_sql_boundary_debt_matches_exact_allowlist` for `db.commit` in `get_admin_chart_diagnostics`.
- Fix: added the exact CS-276 allowlist row for the source-missing audit commit.
- Validation: the targeted SQL-boundary test passed, then full backend pytest passed.

## Acceptance Criteria Review

- AC1/AC2: route and OpenAPI exposure are proven by runtime assertions and architecture tests.
- AC3/AC4: admin success and non-admin denial are covered through `TestClient`.
- AC5: response redaction and raw sensitive-field absence are covered by unit tests and targeted scan.
- AC6: successful, denied and missing-source consultation logs are covered by integration tests.
- AC7: missing source returns typed `admin_chart_diagnostics_source_missing` without the raw chart reference.
- AC8/AC9: service has no replay or narrative-answer-audit import; architecture guard covers forbidden imports.
- AC10: route, service and contract ownership uniqueness is guarded.
- AC11: evidence files are present; the before snapshot remains reconstructed as documented.

## Validation

PASS:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
```

PASS:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format --check app\api\v1\routers\admin\chart_diagnostics.py app\services\ops\admin_chart_diagnostics.py app\tests\integration\test_admin_chart_diagnostics_api.py
```

PASS:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q app\tests\integration\test_admin_chart_diagnostics_api.py tests\unit\test_admin_chart_diagnostics_redaction.py tests\architecture\test_admin_chart_diagnostics_boundaries.py --tb=short
```

7 passed, 4 deselected in 11.48s.

PASS:

```powershell
.\.venv\Scripts\Activate.ps1
python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-276-admin-chart-diagnostics-v1\00-story.md
python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-276-admin-chart-diagnostics-v1\00-story.md
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-276-admin-chart-diagnostics-v1
```

PASS:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q --tb=short
```

3295 passed, 1 skipped, 1195 deselected in 395.48s.

## Propagation

- no-propagation: corrections are local to CS-276 implementation, tests and evidence.

## Residual Risk

- AC11 before snapshot is reconstructed, as documented in final evidence.
