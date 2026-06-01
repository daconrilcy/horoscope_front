# Dev Log

## Preflight

- Initial `git status --short`: `_condamad/run-state.json` modified before this story; left untouched.
- Current branch: `main`.
- Story/status row: `CS-435` path and source brief match the user request.
- Capsule: missing generated files initially; repaired with helper.
- Guardrails: `RG-173` present in canonical registry.

## Search evidence

- Read target story and source brief.
- Read compact capsule summary after repair.
- Read targeted report excerpts for `plan=free`, short post-upgrade, accepted/rejected, public contract, concurrency and quota.
- Inspected targeted backend/product-action/slot/runtime tests and frontend natal tests.

## Implementation notes

- Added backend tests for replay, concurrency, entitlement freshness, public accepted-only reads, and legacy runtime extinction.
- Updated quota unit guard to prove only `accepted_now=True` debits quota.
- Updated frontend tests to assert no post-upgrade short-generation command and deny legacy controls in public DOM.
- Persisted evidence artifacts under story-local `evidence/`.
- Marked pre-implementation story drafting review as obsolete for implementation evidence.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py --repair-generated-only ... --with-optional` | PASS | Capsule repaired. |
| `condamad_validate.py <capsule>` | PASS | Initial capsule validation. |
| `ruff format <changed backend test files>` | PASS | Scoped format. |
| `ruff check backend` | PASS | Backend lint. |
| `python -B -m pytest -q <CS-435 targeted backend tests including product-action API> --tb=short` | PASS | 8 passed, 13 deselected. |
| `python -B -m pytest -q backend\tests\integration backend\tests\llm_orchestration -k "theme_natal or basic_full_reading or concurrency or entitlement" --tb=short` | PASS | 6 passed, 552 deselected. |
| `python -B -m pytest -q backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` | PASS | 6 passed. |
| `pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard` | PASS | 118 frontend tests. |
| `pnpm --dir frontend lint` | PASS | TypeScript lint configs. |
| `python -B -c "from backend.app.main import app; assert app.routes"` | PASS | Runtime routes. |
| `python -B -c "from backend.app.main import app; assert app.openapi().get('paths')"` | PASS | Runtime OpenAPI. |
| VS1-VS4 `rg` scans | PASS_WITH_CLASSIFIED_HITS | See `legacy-scan-results.md`. |
| Artifact existence check | PASS | Required evidence exists. |
| `git diff --check -- ...` | PASS | CRLF warnings only. |

## Issues encountered

- First capsule prepare attempt refused multiple CS ids, then created `_condamad/stories/cs-435`; removed that generated parallel capsule after path verification.
- Initial targeted backend run failed because a scan guard included a readonly route projection and a quota test patched too low; fixed both and reran PASS.

## Decisions made

- Deterministic Basic entitlement simulation is used instead of live Stripe checkout per story allowance.
- Scan evidence is classified rather than forced to zero-hit because old symbols remain in historical readonly, admin/config, and test surfaces.

## Final `git status --short`

- `M _condamad/run-state.json` (pre-existing, out of scope)
- `M _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/00-story.md`
- `M _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/generated/11-code-review.md`
- `M _condamad/stories/story-status.md`
- `M backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `M backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `M frontend/src/tests/natalInterpretation.test.tsx`
- `M frontend/src/tests/natalPublicDomGuard.test.tsx`
- `?? _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/`
- `?? _condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/generated/*.md`
- `?? backend/tests/integration/test_theme_natal_bigbang_replay.py`
- `?? backend/tests/integration/test_theme_natal_concurrency.py`
- `?? backend/tests/integration/test_theme_natal_entitlement_freshness.py`
- `?? backend/tests/integration/test_theme_natal_public_reads.py`
