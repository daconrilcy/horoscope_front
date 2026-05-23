# Execution Brief — CS-234-enrichir-profils-structurels-signes-db

## Primary objective

Implement story `CS-234-enrichir-profils-structurels-signes-db` exactly as defined in `../00-story.md`.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.

## Scoped implementation summary

- Add DB-backed sign seasonal quadrant, fertility, voice and form taxonomies.
- Persist non-null references from `astral_sign_profiles` to those taxonomies.
- Keep public API/runtime payloads unchanged.
- Keep `keywords_json` and `shadow_keywords_json` editorial only.
- Prove no local mappings were added in `backend/app/domain/astrology` or `backend/app/services/natal`.
