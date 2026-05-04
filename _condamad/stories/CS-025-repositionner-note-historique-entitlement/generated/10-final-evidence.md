# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-025-repositionner-note-historique-entitlement
- Source story: `_condamad/stories/CS-025-repositionner-note-historique-entitlement/00-story.md`
- Capsule path: `_condamad/stories/CS-025-repositionner-note-historique-entitlement/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `story-status.md` modified; audit and CS-024/CS-025 untracked.
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails: `RG-040`, `RG-041`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | validated |
| `generated/01-execution-brief.md` | yes | yes | PASS | generated |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | generated |
| `generated/04-target-files.md` | yes | yes | PASS | generated |
| `generated/06-validation-plan.md` | yes | yes | PASS | generated |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | generated |
| `generated/10-final-evidence.md` | yes | yes | PASS | current file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Note moved to `docs/architecture/entitlements-canonical-platform.md`. | `test_entitlement_docs_runtime_parity.py` PASS. | PASS | |
| AC2 | Old `backend/docs` entitlement file deleted. | Ownership + entitlement tests PASS. | PASS | |
| AC3 | `backend/docs/ownership-index.md` no longer references old file. | `pytest -q app/tests/unit/test_backend_docs_ownership.py` PASS. | PASS | |
| AC4 | OpenAPI/table entitlement checks still active in parity test. | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py` PASS. | PASS | |
| AC5 | Content retained; only old path classified `delete`. | `entitlement-doc-path-after.md` removal audit. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `docs/architecture/entitlements-canonical-platform.md` | moved/untracked new path | Preserve historical note outside `backend/docs/`. | AC1 |
| `backend/docs/ownership-index.md` | modified | Remove stale ownership row. | AC2, AC3 |
| `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py` | modified | Read new path and guard old-path absence. | AC1, AC4 |

## Files deleted

- `backend/docs/entitlements-canonical-platform.md`

## Tests added or updated

- Updated `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_backend_docs_ownership.py` | `backend` | PASS | 0 | 3 passed |
| `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py` | `backend` | PASS | 0 | 4 passed |
| `ruff format .` | `backend` | PASS | 0 | 1 file reformatted |
| `ruff check .` | `backend` | PASS | 0 | all checks passed |
| `condamad_story_validate.py ...CS-025.../00-story.md` | repo root | PASS | 0 | story valid |
| `condamad_story_lint.py --strict ...CS-025.../00-story.md` | repo root | PASS | 0 | story lint clean |
| `rg -n "entitlements-canonical-platform\|Document status: historical-note" backend docs _condamad` | repo root | PASS | 0 | New doc path present; old-path hits are historical/story/test guard references. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full `pytest -q` | no | Story scope is documentation/tests governance only. | Wider unrelated regressions not covered. | Targeted ownership and entitlement parity tests passed. |

## DRY / No Legacy evidence

- No compatibility wrapper, alias, re-export, or fallback was introduced.
- Old entitlement doc path under `backend/docs/` is deleted.
- The retained document keeps `Document status: historical-note`.

## Diff review

- Scope limited to documentation move, ownership registry and parity guard.
- CS-024 was implemented in the same user-requested worktree; CS-025 evidence
  intentionally lists only the entitlement-owned files above.
- New moved file appears as untracked until the user asks for staging/commit.
- `git diff --check` PASS.

## Final worktree status

- Recorded after final review in chat and `generated/11-code-review.md`.

## Remaining risks

- None identified for CS-025.

## Suggested reviewer focus

- Confirm historical references in previous story/audit evidence should remain untouched.
