# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: remove-root-route-removal-audit-validator
- Source story: `_condamad/stories/remove-root-route-removal-audit-validator/00-story.md`
- Capsule path: `_condamad/stories/remove-root-route-removal-audit-validator/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/remove-root-route-removal-audit-validator/00-story.md`
- Initial `git status --short`: untracked story folders under `_condamad/stories/`, including this story; permission warnings for existing pytest artifact directories.
- Pre-existing dirty files: untracked `_condamad/stories/classify-critical-load-scenarios/`, `_condamad/stories/classify-natal-cross-tool-dev-report/`, `_condamad/stories/formalize-scripts-ownership/`, `_condamad/stories/harden-local-dev-stack-script/`, `_condamad/stories/portable-llm-release-readiness/`, `_condamad/stories/remove-root-route-removal-audit-validator/`.
- AGENTS.md files considered: root `AGENTS.md`.
- Capsule generated: yes, with explicit `--story-key remove-root-route-removal-audit-validator`.
- Regression guardrails considered: `RG-001`, `RG-015`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific objective and halt conditions. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 mapped and passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and forbidden areas listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Targeted tests, scans, quality, regression, and diff checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Removed path and negative evidence defined. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed with command evidence. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `removal-audit.md` classifies `scripts/validate_route_removal_audit.py` as `dead`; `reference-baseline.txt` persisted. | Baseline scan persisted; audit table has decision `delete`. | PASS | No external-active blocker found. |
| AC2 | `scripts/validate_route_removal_audit.py` deleted; no wrapper, alias, relocation, or replacement command added. | `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` returned no hits. | PASS | The guard test avoids preserving the literal root script path as an active command. |
| AC3 | Historical `remove-historical-facade-routes` story and generated evidence no longer cite the removed root command as executable. | `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes` returned no hits. | PASS | Historical proof remains as prose evidence. |
| AC4 | Added `backend/app/tests/unit/test_scripts_ownership.py`; registered it in `ops-quality-test-ownership.md`. | `pytest -q app/tests/unit/test_scripts_ownership.py` and `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` passed. | PASS | RG-015 ownership remains explicit. |
| AC5 | `00-story.md` validates; capsule evidence completed. | `condamad_story_validate.py` and `condamad_story_lint.py --strict` passed. | PASS | Story status moved to `ready-for-review`. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/remove-root-route-removal-audit-validator/00-story.md` | modified | Mark tasks/status complete. | AC5 |
| `_condamad/stories/remove-root-route-removal-audit-validator/removal-audit.md` | added | Persist dead/delete classification. | AC1 |
| `_condamad/stories/remove-root-route-removal-audit-validator/reference-baseline.txt` | added | Persist before-scan evidence. | AC1 |
| `_condamad/stories/remove-root-route-removal-audit-validator/reference-after.txt` | added | Persist after-scan evidence. | AC1, AC2 |
| `_condamad/stories/remove-root-route-removal-audit-validator/generated/*` | added/modified | Execution, traceability, validation, guardrails, dev log, final evidence. | AC1-AC5 |
| `_condamad/stories/remove-historical-facade-routes/00-story.md` | modified | Stop advertising the removed root command. | AC3 |
| `_condamad/stories/remove-historical-facade-routes/generated/03-acceptance-traceability.md` | modified | Preserve historical validation evidence without root command. | AC3 |
| `_condamad/stories/remove-historical-facade-routes/generated/06-validation-plan.md` | modified | Replace obsolete executable command with historical evidence note. | AC3 |
| `_condamad/stories/remove-historical-facade-routes/generated/10-final-evidence.md` | modified | Preserve historical result while noting later removal. | AC3 |
| `backend/app/tests/unit/test_scripts_ownership.py` | added | Guard against root script reintroduction. | AC4 |
| `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | modified | Register the new scripts ownership guard. | AC4 |

## Files deleted

| File | Purpose | Related AC |
|---|---|---|
| `scripts/validate_route_removal_audit.py` | Remove dead one-off root validator. | AC2 |

## Tests added or updated

| File | Test | Purpose |
|---|---|---|
| `backend/app/tests/unit/test_scripts_ownership.py` | `test_route_removal_audit_validator_is_not_root_script` | Fails if the removed root script returns. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty state captured; permission warnings on existing pytest artifact directories. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\remove-root-route-removal-audit-validator\00-story.md --story-key remove-root-route-removal-audit-validator --with-optional` | repo root after venv activation | PASS | 0 | Capsule generated at requested story key. |
| `rg -n "validate_route_removal_audit.py\|validate_route_removal_audit" . -g '!artifacts/**' -g '!.codex-artifacts/**'` | repo root | PASS | 0 | Baseline/after scans persisted; remaining hits are current evidence, historical audit artifacts, and guard references. |
| `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` | repo root | PASS | 0 | No active consumer hit after deletion. |
| `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes` | repo root | PASS | 0 | No historical root command citation remains. |
| `pytest -q app/tests/unit/test_scripts_ownership.py` | `backend/` after venv activation | PASS | 0 | 1 passed. |
| `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend/` after venv activation | PASS | 0 | 3 passed. |
| `ruff check .` | `backend/` after venv activation | PASS | 0 | All checks passed. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\remove-root-route-removal-audit-validator\00-story.md` | repo root after venv activation | PASS | 0 | CONDAMAD story validation PASS. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\remove-root-route-removal-audit-validator\00-story.md` | repo root after venv activation | PASS | 0 | CONDAMAD story lint PASS. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\remove-root-route-removal-audit-validator` | repo root after venv activation | PASS | 0 | CONDAMAD capsule validation PASS. |
| `ruff format .; ruff check .; pytest -q` | `backend/` after venv activation | FAIL | 124 | Grouped command timed out after 604s; rerun as separate commands below. |
| `ruff format .` | `backend/` after venv activation | PASS | 0 | 1248 files left unchanged. |
| `ruff check .` | `backend/` after venv activation | PASS | 0 | All checks passed. |
| `pytest -q` | `backend/` after venv activation | PASS | 0 | 3525 passed, 12 skipped in 692.95s. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; stat omits untracked new story/test files. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reported LF-to-CRLF warnings for touched markdown files. |
| `git status --short` | repo root | PASS | 0 | Final dirty state recorded below; permission warnings remain for existing artifact directories. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All planned required commands were run. | None | Not applicable. |

## DRY / No Legacy evidence

| Pattern | File/surface | Classification | Action | Status |
|---|---|---|---|---|
| `scripts/validate_route_removal_audit.py` | root `scripts/` file | active_legacy_removed | Deleted file. | PASS |
| `validate_route_removal_audit.py` in `scripts backend frontend docs` | active supported surfaces | negative_evidence | No hits after deletion. | PASS |
| `validate_route_removal_audit.py` in historical story capsule | historical command citation | documentation_updated | Removed root command citations from historical story/generated files. | PASS |
| `validate_route_removal_audit.py` in current story/audit evidence | current evidence | allowed_historical_reference | Kept because this story must name the removed path and persist before/after scans. | PASS |
| `validate_route_removal_audit` split string in `test_scripts_ownership.py` | test guard | test_guard_expected_hit | Kept to make reintroduction fail without preserving a nominal root command. | PASS |
| `validate_route_removal_audit.py` in `_condamad/audits/scripts-ops/2026-05-02-1847` | source audit artifacts | allowed_historical_reference | Kept as immutable source evidence for this story. | PASS |

No wrapper, alias, fallback, relocation, re-export, or replacement validator was introduced.

## Diff review

- `git diff --stat`: expected tracked changes in historical story evidence, ownership registry, and deleted root script. Untracked new capsule/test files are expected but not included by default in stat output.
- `git diff --check`: PASS; only LF-to-CRLF warnings on touched markdown files.
- Runtime backend/frontend files were not modified.
- The only backend code added is a focused architecture guard test.

## Final worktree status

```text
 M _condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md
 M _condamad/stories/remove-historical-facade-routes/00-story.md
 M _condamad/stories/remove-historical-facade-routes/generated/03-acceptance-traceability.md
 M _condamad/stories/remove-historical-facade-routes/generated/06-validation-plan.md
 M _condamad/stories/remove-historical-facade-routes/generated/10-final-evidence.md
 D scripts/validate_route_removal_audit.py
?? _condamad/stories/classify-critical-load-scenarios/
?? _condamad/stories/classify-natal-cross-tool-dev-report/
?? _condamad/stories/formalize-scripts-ownership/
?? _condamad/stories/harden-local-dev-stack-script/
?? _condamad/stories/portable-llm-release-readiness/
?? _condamad/stories/remove-root-route-removal-audit-validator/
?? backend/app/tests/unit/test_scripts_ownership.py
```

`git status --short` also reports permission warnings for existing `.codex-artifacts/pytest-*` and `artifacts/pytest-basetemp/` directories.

## Remaining risks

- None for the implemented scope.
- Historical source audit files under `_condamad/audits/scripts-ops/2026-05-02-1847/` still mention the removed path as source evidence; they are classified as allowed historical references.

## Suggested reviewer focus

- Confirm the `dead` classification in `removal-audit.md` is acceptable.
- Review whether the new `test_scripts_ownership.py` guard and RG-015 registry row are the desired long-term protection for root script cleanup.
