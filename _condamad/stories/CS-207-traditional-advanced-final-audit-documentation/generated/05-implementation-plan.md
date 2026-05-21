# Implementation Plan

## Current Finding

CS-207 is a documentation and closure audit story. The repository already contains completed CS-197 through CS-206 story records, evidence directories, runtime/domain tests, frontend expert panel tests, and active regression guardrails `RG-124` through `RG-134`.

## Approach

1. Keep production code unchanged.
2. Produce the required persistent evidence package under this story.
3. Classify scan hits narrowly instead of introducing allowlists.
4. Validate the closure through targeted backend tests, frontend tests/checks, backend quality checks, story validation, evidence existence checks, and JSON validation.
5. Mark the story done only after an independent review pass is clean.

## Files To Modify

- Generated capsule evidence under `generated/`.
- Required closure evidence under `evidence/`.
- Story status registry after review closure.

## Tests And Checks

- Targeted backend pytest chain from the story validation plan.
- Frontend `NatalExpertPanel` test, lint, build, and documented typecheck script adaptation.
- Required `rg` scans.
- `ruff format .`, `ruff check .`.
- Story validation/lint scripts.
- Final `python -m json.tool` on final status JSON.

## No Legacy Stance

No compatibility path, shim, alias, fallback, broad allowlist, or local doctrine constant is added. Scan hits are classified one by one at the owner level.

