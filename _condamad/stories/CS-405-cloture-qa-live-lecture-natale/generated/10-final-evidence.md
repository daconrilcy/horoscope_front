# Final Evidence - CS-405

## Story status

| Field | Value |
|---|---|
| Story key | `CS-405-cloture-qa-live-lecture-natale` |
| Implementation outcome | `BLOCKED` |
| Registry decision | Kept in development queue because live closure is incomplete |
| Reason | Basic `complete` still returns a V2 payload without `narrative_natal_reading_v1`; Free/Basic/Premium closure cannot be honestly handed to review. |

## Preflight

- `.git` present.
- Initial dirty file observed before edits: `_condamad/run-state.json`.
- `AGENTS.md`, target story and scoped guardrails were read.
- `story-status.md` row `CS-405` matches the target path and source brief.
- Existing `generated/11-code-review.md` was read and classified as obsolete pre-implementation review evidence.

## Capsule validation

| Command | Result |
|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --story-key CS-405-cloture-qa-live-lecture-natale` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-405-cloture-qa-live-lecture-natale` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-405-cloture-qa-live-lecture-natale --final` | BLOCKED: expected final gate refuses blocked/incomplete status. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | CS-390/395 before/after report evidence. | `cs-390-395-report-before.md`, `cs-390-395-report-after.md` | PASS |
| AC2 | CS-400/CS-405 report exists and contains the current blocked verdict. | Artifact checks PASS | PASS |
| AC3 | Free QA not available because the local test account is `basic`. | `api-snapshot.json` | BLOCKED |
| AC4 | Basic `complete` has no `narrative_natal_reading_v1`. | `api-complete-generation-response.json` | FAIL |
| AC5 | Premium browser QA not replayed after Basic blocker. | `frontend-targeted-tests.txt` only | BLOCKED |
| AC6 | Desktop/mobile captures exist but show no narrative accordions. | `browser-qa-basic.json`, screenshots | FAIL |
| AC7 | Vitest PASS, live `accordionCount = 0`. | `frontend-targeted-tests.txt`, `browser-qa-basic.json` | FAIL |
| AC8 | Backend tests PASS, live narrative sources absent. | `backend-targeted-tests.txt`, API response | FAIL |
| AC9 | Long entitlement tests PASS, live Basic regeneration does not produce narrative. | `backend-long-entitlement.txt`, API response | FAIL |
| AC10 | Quota/rejection tests PASS; not replayed as browser flow. | `backend-targeted-tests.txt`, `backend-long-entitlement.txt` | PASS_WITH_LIMITATIONS |
| AC11 | Coverage tests PASS; not confirmed in live payload. | `backend-targeted-tests.txt` | PASS_WITH_LIMITATIONS |
| AC12 | RG-155 to RG-158 listed; RG-155/RG-158 fail live. | `guard-rg155-158-report.txt` | PASS_WITH_LIMITATIONS |
| AC13 | Basic desktop/mobile screenshots persisted; Free/Premium absent. | `artifact-checks.txt` | PASS_WITH_LIMITATIONS |
| AC14 | Critical/major risks are explicit with follow-up references. | Report risk table | PASS |

## Files changed

- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/09-dev-log.md`
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/10-final-evidence.md`
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/11-code-review.md`
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/**`
- `output/playwright/cs-400-basic-desktop.png`
- `output/playwright/cs-400-basic-mobile.png`

## Files deleted

None.

## Tests added or updated

No application tests were added or updated. This story is a QA/reporting closure; runtime and static proof was captured under the story evidence directory.

## Commands run

| Command | Result |
|---|---|
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; Pop-Location` | PASS |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or quota or theme_astral)"; Pop-Location` | PASS, 30 passed |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py --tb=short; Pop-Location` | PASS, 16 passed |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_interpretation_endpoint.py --tb=short; Pop-Location` | PASS, 8 passed |
| `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode` | PASS, 90 passed |
| `pnpm --dir frontend lint` | PASS |
| `pnpm --dir frontend build` | PASS |
| `node _condamad\stories\CS-405-cloture-qa-live-lecture-natale\evidence\capture-browser-qa.cjs` | PASS command, FAIL product assertion: Basic accordions = 0 |
| `rg -n "RG-155|RG-156|RG-157|RG-158" _condamad\reports\cs-400-cloture-qa-live-lecture-natale.md` | PASS |
| `rg -n "fallback = response\.sections\[0\]" backend\app\services\llm_generation\natal` | PASS: no matches |
| `rg -n "check_and_consume" backend\app\api\v1\routers\public\natal_interpretation.py` | PASS: no matches |

## Commands skipped or blocked

| Command/Check | Status | Reason/Risk |
|---|---|---|
| Free browser QA | BLOCKED | Local test account is `basic`; changing plan after Basic live failure would not resolve the narrative blocker. |
| Premium browser QA | BLOCKED | Basic complete V3 runtime failed first; Premium closure would be misleading without the shared narrative pipeline. |
| `ruff format` | NOT_RUN | No Python file was modified. |
| Full backend `pytest -q` | NOT_RUN | Targeted and long natal suites passed; live browser/API already identified a blocking product failure. |

## DRY / No Legacy evidence

- No application code changed.
- No shim, alias, fallback, duplicate runtime path, dependency, route or migration added.
- Backend padding and quota scans are zero-hit on the story-owned surfaces.
- Frontend legacy marker hits are existing CSS/test references and are classified in `evidence/guard-frontend-legacy-scan.txt`; public DOM/browser checks remain separate evidence.

## Diff review

- Persisted deltas are limited to QA reports, story capsule evidence and browser screenshots.
- No runtime code, dependency manifest, migration or regression guardrail registry was changed.
- The CS-400 report was changed from an acceptable-with-limitations closure to a blocked live QA report because browser/API evidence contradicted positive closure.

## Final worktree status

Captured after validation in local git status. Pre-existing `_condamad/run-state.json` remains dirty and unrelated.

## Remaining risks

- Critical: Basic complete live generation downgrades to V2 and does not expose `narrative_natal_reading_v1`.
- Major: Free and Premium live QA remain unproven until the Basic complete V3 runtime path is fixed.
- Major: A positive closure report would be misleading if it cited only tests while browser QA fails.

## Suggested reviewer focus

Review the runtime mismatch between passing automated V3 guards and the authenticated Basic `complete` live response captured in `api-complete-generation-response.json`.

## Feedback loop routing

No-propagation: the reusable learning is already represented by follow-up stories `CS-406`, `CS-407` and `CS-408`; no new registry invariant is required.
