# Execution Brief — classify-converge-remaining-prompt-fallbacks

## Primary objective

Converger `PROMPT_FALLBACK_CONFIGS` vers les seules fixtures synthetiques
autorisees, documenter la decision des 8 cles auditees et garder le rejet
production `missing_assembly` pour les familles supportees.

## Boundaries

- Scope code: `backend/app/domain/llm/prompting`, tests LLM orchestration.
- Scope evidence: capsule `_condamad/stories/classify-converge-remaining-prompt-fallbacks`.
- Do not change HTTP admin contracts, renderer, provider wrapper, frontend, dependencies or
  canonical taxonomy.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Remove fallback prompt text instead of repointing it.
- Keep runtime metadata in `PROMPT_RUNTIME_DATA` when it is not prompt ownership.
- Keep `test_natal` and `test_guidance` only as exact synthetic fixtures.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `fallback-classification.md` contains before/after inventory and decisions for all 8 keys.
- `10-final-evidence.md` is complete.
