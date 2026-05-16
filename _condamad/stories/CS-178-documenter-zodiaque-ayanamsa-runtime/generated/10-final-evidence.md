# Final Evidence CS-178

## Story status

done

## Preflight

- AGENTS.md lu.
- Regression guardrails lus.
- Existing owners inspected: `zodiac.py`, `ephemeris_provider.py`, `calculation_service.py`, docs ownership.

## Capsule validation

- Capsule générée avec `condamad_prepare.py`.
- Validation finale exécutée avec `condamad_validate.py`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Doc explains service -> provider -> longitude -> sign | doc scan passed | PASS |
| AC2 | Doc states `sign_from_longitude` does not apply ayanamsa | doc scan passed | PASS |
| AC3 | Doc cites exact test commands | tests passed | PASS |
| AC4 | No concurrent helper added | helper scan classified existing owners | PASS |

## Files changed

- `backend/docs/astrology-zodiac-runtime-contract.md`
- `backend/docs/ownership-index.md`

## Files deleted

None.

## Tests added or updated

No test file added; docs ownership index updated and existing guards cover it.

## Commands run

- `ruff format .` - PASS
- `ruff check .` - PASS
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected
- Backend startup `/docs` on `127.0.0.1:8015` - PASS, HTTP 200

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No runtime code helper added.
- No zodiac behavior changed.
- Docs ownership row added.

## Diff review

Scope limited to documentation and ownership evidence.

## Final worktree status

Dirty with intended story/code changes; no commit requested.

## Remaining risks

None identified.

## Suggested reviewer focus

Check wording around ayanamsa responsibility split.
