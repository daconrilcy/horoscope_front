# Execution Brief — CS-009-separer-projection-publique-enrichissement-llm

## Primary objective

Make public prediction projection deterministic by moving horoscope daily narrative enrichment out of `backend/app/prediction/public_projection.py` and into an explicit service path under `backend/app/services`.

## Boundaries

- Preserve public V4 JSON/OpenAPI shape.
- Keep persisted LLM narrative projection inside the deterministic assembler.
- Route new LLM narrative generation through the canonical horoscope daily narration service.
- Propagate caller-provided `request_id` and `trace_id`; do not generate them in projection.

## Non-goals

- No LLM provider refactor.
- No frontend contract change.
- No full migration of `app.prediction`.
- No duplicate public assembler.

## Write rules

- Do not introduce compatibility wrappers, aliases, fallbacks, re-exports, or a second narrator.
- Do not add dependencies.
- Do not broaden the route/API behavior beyond moving the LLM ownership.

## Done when

- AC1-AC5 in `03-acceptance-traceability.md` are `PASS`.
- Required tests, Ruff, scans and before/after snapshot artifacts are recorded.
- `story-status.md` marks CS-009 as `ready-to-review`.
