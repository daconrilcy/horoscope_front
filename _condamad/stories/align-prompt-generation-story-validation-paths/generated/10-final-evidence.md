# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `align-prompt-generation-story-validation-paths`
- Source story: `_condamad/stories/align-prompt-generation-story-validation-paths/00-story.md`
- Capsule path: `_condamad/stories/align-prompt-generation-story-validation-paths`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `M backend/horoscope.db`; Git also reported denied access to pytest artifact folders.
- Pre-existing dirty files: `backend/horoscope.db`
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrail registry: `_condamad/stories/regression-guardrails.md` read; `RG-010`, `RG-019`, `RG-020`, and `RG-022` applied.
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story was already present; status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this run. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped and completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated for this run. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated for this run. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated for this run. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Updated active paths in `converge-horoscope-daily-narration-assembly/00-story.md`, `formalize-consultation-guidance-prompt-ownership/00-story.md`, and `regression-guardrails.md`. | `rg` active obsolete path scan returns only classified forbidden examples, scan commands, and historical evidence. | PASS | Active story validation commands now use `app/tests/unit`. |
| AC2 | Reused existing collected test files under `backend/app/tests/unit`. | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py` passed: 32 tests. | PASS | Command ran from `backend/` after venv activation. |
| AC3 | Added `validation-path-audit.md` with historical and forbidden-reference allowlist. | `rg -n "historical|historique|historical-facade|forbidden-example|reintroduction-guard" _condamad\stories\align-prompt-generation-story-validation-paths\validation-path-audit.md` returned the expected classifications. | PASS | Historical obsolete path is limited to prior failed evidence. |
| AC4 | `validation-path-audit.md` defines the guard invariant; `RG-020` now points to a collected path and `RG-022` remains the durable invariant. | Obsolete path scan plus targeted pytest and topology guards passed. | PASS | No duplicate tests or compatibility path introduced. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/align-prompt-generation-story-validation-paths/00-story.md` | modified | Mark status/tasks complete. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/01-execution-brief.md` | added | Capsule execution brief. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/03-acceptance-traceability.md` | added | AC traceability and final statuses. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/04-target-files.md` | added | Target file and search map. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/05-implementation-plan.md` | added | Implementation plan. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/06-validation-plan.md` | added | Validation plan. | AC2-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/07-no-legacy-dry-guardrails.md` | added | No Legacy guardrails. | AC3-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/10-final-evidence.md` | added | Final proof. | AC1-AC4 |
| `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md` | added | Before/after audit and classification. | AC1, AC3, AC4 |
| `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` | modified | Allow structural validation of post-implementation `ready-for-review` stories. | AC2 |
| `.agents/skills/condamad-story-writer/scripts/self_tests/condamad_story_validate_selftest.py` | modified | Cover accepted `ready-for-review` status and rejected unknown status. | AC2 |
| `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` | modified | Replace obsolete seed validation path with collected path. | AC1, AC2 |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` | modified | Replace obsolete guidance and consultation validation paths with collected paths. | AC1, AC2 |
| `_condamad/stories/regression-guardrails.md` | modified | Replace obsolete `RG-020` guard command with collected path. | AC1, AC4 |

## Files deleted

None.

## Tests added or updated

No backend tests were added or modified. Existing tests under `backend/app/tests/unit` provide the runtime evidence.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md` | `backend/` after venv activation | PASS | 0 | CONDAMAD story validation passed. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md` | `backend/` after venv activation | PASS | 0 | CONDAMAD story lint passed. |
| `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py` | `backend/` after venv activation | PASS | 0 | 32 tests passed. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\self_tests\condamad_story_validate_selftest.py` | `backend/` after venv activation | PASS | 0 | 46 validator self-tests passed. |
| `pytest -q app/tests/unit/test_backend_pytest_collection.py app/tests/unit/test_backend_test_topology.py` | `backend/` after venv activation | PASS | 0 | 9 tests passed. |
| `rg -n "pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py|pytest -q tests/unit/test_guidance_service.py|pytest -q tests/unit/test_consultation_generation_service.py" _condamad\stories` | repo root | PASS | 0 | Hits are classified as forbidden examples, scan commands, audit before rows, or historical evidence. |
| `rg -n "historical|historique|historical-facade|forbidden-example|reintroduction-guard" _condamad\stories\align-prompt-generation-story-validation-paths\validation-path-audit.md` | repo root | PASS | 0 | Expected classifications found. |
| `ruff check .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py .agents\skills\condamad-story-writer\scripts\self_tests\condamad_story_validate_selftest.py` | repo root after venv activation | PASS | 0 | All checks passed for modified validator files. |
| `ruff format --check .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py .agents\skills\condamad-story-writer\scripts\self_tests\condamad_story_validate_selftest.py` | repo root after venv activation | PASS | 0 | Modified validator files already formatted after mechanical formatting. |
| `ruff check .` | `backend/` after venv activation | PASS | 0 | All checks passed. |
| `ruff format --check .` | `backend/` after venv activation | PASS | 0 | 1246 files already formatted. |
| `pytest -q` | `backend/` after venv activation | PASS | 0 | 3521 passed, 12 skipped in 595.80s. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git warned that LF will be replaced by CRLF for touched markdown files. |
| `git diff --stat` | repo root | PASS | 0 | Tracked diff includes story markdown/guardrail files, the CONDAMAD story validator and self-tests, plus pre-existing `backend/horoscope.db`. |
| `git status --short` | repo root | PASS | 0 | Shows expected story files plus pre-existing `backend/horoscope.db`; Git reports denied access to pytest artifact folders. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app startup | no | Documentation-only story; no runtime backend/frontend code changed. | Low. | Full backend pytest and lint passed. |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` | current story and audit files | forbidden-example / reintroduction-guard | keep classified references only | PASS |
| `pytest -q tests/unit/test_guidance_service.py` | current story and audit files | forbidden-example / reintroduction-guard | keep classified references only | PASS |
| `pytest -q tests/unit/test_consultation_generation_service.py` | current story and audit files | forbidden-example / reintroduction-guard | keep classified references only | PASS |
| `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` | `converge-horoscope-daily-narration-assembly/generated/10-final-evidence.md` | allowed historical reference | keep historical evidence | PASS |

No wrapper, alias, duplicated backend test file, or collection-root change was introduced.

## Diff review

- Tracked diff reviewed for story markdown/guardrail files and the CONDAMAD story validator/self-test files touched by this fix.
- New generated capsule and audit files are story-scope artifacts.
- `backend/horoscope.db` was already dirty before editing and was not intentionally changed by this story.
- No backend or frontend application source changed.

## Final worktree status

```text
 M .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py
 M .agents/skills/condamad-story-writer/scripts/self_tests/condamad_story_validate_selftest.py
 M _condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md
 M _condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md
 M _condamad/stories/regression-guardrails.md
 M backend/horoscope.db
?? _condamad/stories/align-prompt-generation-story-validation-paths/generated/
?? _condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md
```

Git also reports denied access when walking some pytest artifact directories:
`.codex-artifacts/pytest-basetemp/`, `.codex-artifacts/tmp/pytest-of-cyril/`,
and `artifacts/pytest-basetemp/`.

## Remaining risks

- `backend/horoscope.db` remains a pre-existing dirty binary file outside this story's scope.
- Historical obsolete path text remains intentionally in final evidence and forbidden-example guard text; reviewers should distinguish those from active validation commands.

## Suggested reviewer focus

- Confirm the active validation commands in the two corrected stories now use `app/tests/unit`.
- Confirm the audit classifications are acceptable for remaining obsolete-path text.
- Confirm `RG-020` and `RG-022` together cover guidance/consultation and prompt-generation validation path drift.
