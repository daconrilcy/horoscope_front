# Executive Summary - backend-tests

The backend suite is not primarily a deletion problem; it is an ownership and discovery problem. Runtime collection from `backend` succeeds with 3164 tests, but static inventory finds 425 test files and 3285 test functions. The most important risk is that 64 files containing 304 static test functions sit outside configured pytest `testpaths`, including LLM and architecture guards.

Do not delete the story-numbered or legacy-heavy tests in bulk. Many appear to enforce active regression guardrails RG-001 through RG-009. The safer path is to first make discovery complete, then converge test roots, then reclassify story tests into durable guard suites.

Immediate priorities: fix default collection coverage, define a canonical backend test topology, and converge DB fixtures away from global `SessionLocal` monkeypatching. One no-op facade test can be removed or implemented quickly.
