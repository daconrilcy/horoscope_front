# Final Evidence — CS-263-generic-projection-endpoint-contract

## Story status

- Validation outcome: PASS
- Ready for review: no
- Final tracker status: done
- Story key: CS-263-generic-projection-endpoint-contract
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-263-generic-projection-endpoint-contract`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: run; pre-existing dirty files exist for CS-256 to CS-261 capsules and architecture docs unrelated to CS-263.
- Pre-existing dirty files: unrelated `_condamad/stories/CS-256*` to `CS-261*`, `_condamad/audits/ai-traceability/`, and several `docs/architecture/*` files were present before CS-263 edits.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status updated to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Completed for CS-263 scope. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC11 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Target and forbidden files documented. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands updated to actual checks. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Capsule guardrails present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `docs/architecture/generic-projection-endpoint-contract.md` documents `POST /v1/astrology/projections`. | Required `rg` scan PASS. | PASS | Contract only; no route. |
| AC2 | Payload table names `chart_id`, `birth_input`, `projection_type`, `projection_version`, `persist`. | Required `rg` scan PASS. | PASS | JSON key names exact. |
| AC3 | `projection_version` is marked mandatory and no fallback version is allowed. | Targeted mandatory wording scan PASS. | PASS | |
| AC4 | Source selection table defines exactly one of existing `chart_id` or `birth_input`. | Targeted chart source scan PASS. | PASS | |
| AC5 | Contract separates chart lookup, chart calculation, projection construction and authorization. | Targeted service separation scan PASS. | PASS | |
| AC6 | Controlled status/error table covers invalid input, auth, unknown chart, unavailable calculation/projection and invalid version. | Targeted error scan PASS. | PASS | Blocking/logged dependency rule included. |
| AC7 | B2C access by `projection_type`, plan or entitlement is documented. | Targeted access scan PASS. | PASS | |
| AC8 | Internal technical projections and raw/debug/prompt/provider/audit surfaces are denied to B2C clients. | Targeted internal-denial scan PASS. | PASS | |
| AC9 | Backend and frontend runtime surfaces unchanged. | `app.openapi()` absent PASS; `app.routes` absent PASS; `TestClient` 404 PASS; runtime/frontend `rg` absence PASS. | PASS | |
| AC10 | B2B API remains out of scope. | Contract B2B wording scan PASS; runtime route absence PASS. | PASS | |
| AC11 | Evidence artifacts persisted. | `condamad_validate.py` PASS. | PASS | |

## Files changed

- `docs/architecture/generic-projection-endpoint-contract.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/01-execution-brief.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/04-target-files.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/06-validation-plan.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/10-final-evidence.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/app-surface-status.txt`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/source-checklist.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- none; story is documentation plus runtime-neutral validation. Existing backend test suite was run.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Pre-existing unrelated dirty files recorded. |
| `condamad_prepare.py ... --story-key CS-263-generic-projection-endpoint-contract` | repo root with venv | PASS | 0 | Generated missing capsule files. |
| `condamad_validate.py _condamad\stories\CS-263-generic-projection-endpoint-contract` | repo root with venv | PASS | 0 | Capsule valid before and after evidence. |
| `rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs` | repo root | PASS | 0 | Required contract terms found. |
| `rg -n "projection_version.*obligatoire|..." docs\architecture\generic-projection-endpoint-contract.md` | repo root | PASS | 0 | Required rules found in contract. |
| `rg -n "/v1/astrology/projections" backend\app frontend\src` | repo root | PASS | 1 treated as expected absence | No runtime/frontend match. |
| `python -B -c "... app.openapi() ..."` | `backend` with venv | PASS | 0 | `/v1/astrology/projections` absent from OpenAPI. |
| `python -B -c "... app.routes ..."` | `backend` with venv | PASS | 0 | `/v1/astrology/projections` absent from runtime routes. |
| `python -B -c "... TestClient ..."` | `backend` with venv | PASS | 0 | POST returns 404. |
| `ruff check .` | `backend` with venv | PASS | 0 | All checks passed. |
| `python -B -m pytest -q tests/architecture/test_api_contract_neutrality.py` | `backend` with venv | PASS | 0 | 15 passed. |
| `python -B -m pytest -q --tb=short` | `backend` with venv | PASS | 0 | 3236 passed, 1 skipped, 1182 deselected. |
| `rg -n "source-checklist\.txt" _condamad\stories\CS-263-generic-projection-endpoint-contract` | repo root | PASS | 1 treated as expected absence | No stale non-canonical source checklist reference remains. |
| `rg -n "source-checklist\.md" _condamad\stories\CS-263-generic-projection-endpoint-contract` | repo root | PASS | 0 | Canonical source checklist path present. |
| `git diff --check -- docs/... _condamad/stories/CS-263...` | repo root | PASS | 0 | No whitespace errors. |

## Commands skipped or blocked

- none

## Review/fix iteration notes

- Iteration 1 finding: source checklist evidence path drifted from the story contract path to a non-canonical text-extension artifact.
- Fix: renamed the artifact to `source-checklist.md` and updated generated evidence references.
- Fresh implementation review after the fix: CLEAN.

## DRY / No Legacy evidence

- One canonical endpoint contract document added.
- No compatibility route, shim, alias, fallback, duplicate active endpoint document, runtime service, router, persistence object, migration, frontend screen or generated client was created.
- Negative runtime/frontend scan for `/v1/astrology/projections`: PASS no matches.
- B2B and internal technical projections are explicitly excluded in the contract.

## Diff review

- `git diff --stat -- docs/architecture/generic-projection-endpoint-contract.md _condamad/stories/CS-263-generic-projection-endpoint-contract _condamad/stories/story-status.md`: run during final review.
- `git diff --check -- docs/architecture/generic-projection-endpoint-contract.md _condamad/stories/CS-263-generic-projection-endpoint-contract`: PASS.

## Final worktree status

- CS-263 changed files only plus pre-existing unrelated dirty files from other stories/docs.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Review the contract wording for the exact B2C authorization matrix and whether `structured_facts_v1` should remain non-direct B2C by default.

## Feedback loop routing

- no-propagation: validation passed; no reusable process failure or guardrail gap identified.
