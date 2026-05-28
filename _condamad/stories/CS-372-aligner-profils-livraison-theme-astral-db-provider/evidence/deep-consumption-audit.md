# Deep Consumption Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `THEME_ASTRAL_DELIVERY_PROFILES["deep"]` | runtime constant | dead | No authorized active consumer found in scoped runtime after implementation. | `expanded` and `complete` are explicit canonical depths, without redirecting `deep`. | Deleted from active constants. | `rg -n "deep" app/domain/llm/configuration/theme_astral_contracts.py` returned no matches. | none |
| Published `theme_astral` assembly with `plan="deep"` | persisted active row | dead | Existing DB rows from pre-CS-372 seed runs only. | No replacement mapping; stale rows are archived. | Seed archives non-canonical published plans. | `test_theme_astral_seed_archives_stale_deep_assembly` PASS. | none |
| `resolve_active_theme_astral_prompt_contract(depth="deep")` | active resolver input | dead | No external active consumer proven by scoped story evidence. | Callers must request `essential`, `expanded`, or `complete`. | Explicit `ValueError`, no fallback. | Persistence test asserts `deep` is rejected. | none |
| Persistence test mentions of `deep` | test guard | historical-facade | Regression guard only. | Not applicable. | Retained to prove archival and rejection. | `rg -n "deep" tests/integration/test_theme_astral_prompt_contract_persistence.py`. | none |
| Docs/examples/report mentions of `deep` | human evidence | historical-facade | Reviewers and future implementers. | Canonical docs name `essential`, `expanded`, `complete`. | Retained only when explicitly marked non-runtime history. | `depths-after.txt`. | none |
