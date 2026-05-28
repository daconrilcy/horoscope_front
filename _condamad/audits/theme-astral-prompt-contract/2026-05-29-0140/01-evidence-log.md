# Evidence Log

| ID | Evidence type | Command / Source | Result | Inspected path | Surface | Reproducible result | Limitation |
|---|---|---|---|---|---|---|---|
| E-001 | git_status | `git status --short` | PASS | repository root | worktree preflight | Only pre-existing untracked `_condamad/run-state.json` was present before audit writes. | Does not include later audit artifacts. |
| E-002 | source_read | `Get-Content _condamad/stories/regression-guardrails.md` | PASS | `_condamad/stories/regression-guardrails.md` | guardrail registry | Registry exists and contains RG-002, RG-022, and prompt-generation invariants. | Large registry was consulted by scoped search and reading, not fully quoted. |
| E-003 | source_read | `Get-Content _condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/00-audit-report.md` | PASS | prior audit folder | prior closure ledger | Prior audit status was `closed` with provider-call limitation F-001. | Prior status was rechecked against current evidence. |
| E-004 | source_read | `Get-Content .../generated/10-final-evidence.md` for CS-372 through CS-376 | PASS | `_condamad/stories/CS-372*` through `CS-376*` | upstream story ledger | All five upstream stories record PASS or done status; CS-376 records provider call skipped without opt-in. | Evidence files are self-reported story artifacts. |
| E-005 | source_read | `Get-Content` story and brief | PASS | `_condamad/stories/CS-377.../00-story.md`, `_story_briefs/cs-377...md` | CS-377 contract | Target expects final adversarial audit and no code correction. | None. |
| E-006 | inventory_scan | `rg --files ...` | PASS | backend and CONDAMAD prompt-generation paths | audit inventory | Target code, tests, docs, examples and prior reports were inventoried. | Inventory was scoped to story paths. |
| E-007 | pytest | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py tests/llm_orchestration/test_theme_astral_provider_smoke.py --tb=short` | PASS | `backend/tests/**theme_astral*` | targeted runtime tests | `16 passed, 1 skipped, 9 deselected in 1.14s`. | One provider smoke test skipped by default. |
| E-008 | rg_scan | `rg -n 'deep\|essential\|expanded\|complete\|delivery_profile\|birth_context\|birth_date\|birth_time_local\|birth_place' app tests ..\_condamad\docs ..\_condamad\examples` | PASS | `backend/app`, `backend/tests`, docs, examples | delivery profiles and birth context | Required target terms appear in runtime, tests, docs and examples; broad hits include out-of-domain natal examples/tests. | Scan is broad and requires interpretation. |
| E-009 | rg_scan | `rg -n 'chart_json\|natal_data\|llm_astrology_input_v1\|legacy\|free\|basic\|premium\|"plan"' app tests ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1` | PASS | `backend/app`, `backend/tests`, target examples | old carriers and plan labels | Target examples have only filenames/docs/intermediate commercial labels; runtime/test hits are guards or non-domain flows. | Broad scan includes many unrelated flows. |
| E-010 | pytest | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_smoke.py -m provider_smoke --tb=short` | SKIPPED | `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` | provider smoke opt-in | `1 skipped, 3 deselected in 0.78s`, confirming external provider call did not run without opt-in. | Does not prove real provider behavior. |
| E-011 | json_inspection | `python -S -B -c` JSON inspection plus `Select-String` birth-context lines | FAIL | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json` | provider example birth context | All three provider payloads have `birth_date`, `birth_time_local`, `birth_place.city`, `country`, `timezone`, `latitude`, `longitude` equal to null while `chart_id` embeds `1973-04-24 11:00 Europe/Paris Paris France`. | Runtime tests still pass; drift is in official examples/docs. |
| E-012 | json_inspection | `python -S -B -c` source material summary plus `Select-String source_ref interpretive_text production-like` | PASS | target example JSON and README | interpretation material source quality | Free, basic, premium payloads have non-empty interpretation text and explicit `source_ref`; README discloses DB-seeded and production-like fixture mix. | Some families remain fixture-backed by design. |
| E-013 | lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | PASS | `backend` | backend lint | `All checks passed!`. | Check-only lint, no formatting. |
| E-014 | json_inspection | `python -S -B -c` JSON forbidden-value walk | PASS | target provider examples | plan and old-carrier payload values | No exact string values or keys among `plan`, `free`, `basic`, `premium`, `chart_json`, `natal_data`, `llm_astrology_input_v1` were found inside target provider payload values or keys. | Filenames and README still contain commercial labels by design. |
| E-015 | audit_validation | `.\.venv\Scripts\Activate.ps1; python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/theme-astral-prompt-contract/2026-05-29-0140` and `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/theme-astral-prompt-contract/2026-05-29-0140` | PASS | `_condamad/audits/theme-astral-prompt-contract/2026-05-29-0140` | domain audit artifact contract | `CONDAMAD domain audit validation passed.` and `CONDAMAD domain audit lint passed.` | Validates artifact contract and lint only; it does not close F-001. |

## Evidence Interpretation Notes

- Negative scans were interpreted as expected success when they targeted provider payload values or target runtime owner files.
- Broad hits in tests and unrelated flows were classified as `test-only` or `out-of-domain`, not as active `theme_astral` prompt carriers.
- The F-001 example drift is not inferred from static grep alone; it is backed by JSON structural inspection of the official provider payload files.

## E-001 Worktree Preflight

- Command/source: `git status --short`.
- Repository-relative inspected path: repository root.
- Inspected surface: worktree state.
- Result: PASS. Only pre-existing untracked `_condamad/run-state.json` was present before audit writes.
- Limitation: Does not include later audit artifacts.

## E-002 Regression Guardrails

- Command/source: `Get-Content _condamad/stories/regression-guardrails.md`.
- Repository-relative inspected path: `_condamad/stories/regression-guardrails.md`.
- Inspected surface: guardrail registry.
- Result: PASS. Registry exists and contains RG-002, RG-022, and prompt-generation invariants.
- Limitation: Large registry was consulted by scoped search and reading, not fully quoted.

## E-003 Prior Same-Domain Audit

- Command/source: `Get-Content _condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/00-audit-report.md`.
- Repository-relative inspected path: `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/`.
- Inspected surface: prior closure ledger.
- Result: PASS. Prior audit status was `closed` with provider-call limitation F-001.
- Limitation: Prior status was rechecked against current evidence.

## E-004 Upstream Story Ledger

- Command/source: `Get-Content .../generated/10-final-evidence.md` for CS-372 through CS-376.
- Repository-relative inspected path: `_condamad/stories/CS-372*` through `_condamad/stories/CS-376*`.
- Inspected surface: upstream story evidence.
- Result: PASS. All five upstream stories record PASS or done status; CS-376 records provider call skipped without opt-in.
- Limitation: Evidence files are self-reported story artifacts.

## E-005 CS-377 Contract

- Command/source: `Get-Content` story and brief.
- Repository-relative inspected path: `_condamad/stories/CS-377.../00-story.md`, `_story_briefs/cs-377...md`.
- Inspected surface: CS-377 contract.
- Result: PASS. Target expects final adversarial audit and no code correction.
- Limitation: None.

## E-006 Audit Inventory

- Command/source: `rg --files ...`.
- Repository-relative inspected path: backend and CONDAMAD prompt-generation paths.
- Inspected surface: audit file inventory.
- Result: PASS. Target code, tests, docs, examples and prior reports were inventoried.
- Limitation: Inventory was scoped to story paths.

## E-007 Targeted Runtime Tests

- Command/source: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py tests/llm_orchestration/test_theme_astral_provider_smoke.py --tb=short`.
- Repository-relative inspected path: `backend/tests/**theme_astral*`.
- Inspected surface: targeted runtime tests.
- Result: PASS. `16 passed, 1 skipped, 9 deselected in 1.14s`.
- Limitation: One provider smoke test skipped by default.

## E-008 Delivery Profile And Birth Context Scan

- Command/source: `rg -n 'deep|essential|expanded|complete|delivery_profile|birth_context|birth_date|birth_time_local|birth_place' app tests ..\_condamad\docs ..\_condamad\examples`.
- Repository-relative inspected path: `backend/app`, `backend/tests`, docs, examples.
- Inspected surface: delivery profiles and birth context.
- Result: PASS. Required target terms appear in runtime, tests, docs and examples; broad hits include out-of-domain natal examples/tests.
- Limitation: Scan is broad and requires interpretation.

## E-009 Old Carrier And Plan Scan

- Command/source: `rg -n 'chart_json|natal_data|llm_astrology_input_v1|legacy|free|basic|premium|"plan"' app tests ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1`.
- Repository-relative inspected path: `backend/app`, `backend/tests`, target examples.
- Inspected surface: old carriers and plan labels.
- Result: PASS. Target examples have only filenames/docs/intermediate commercial labels; runtime/test hits are guards or non-domain flows.
- Limitation: Broad scan includes many unrelated flows.

## E-010 Provider Smoke Opt-In

- Command/source: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_smoke.py -m provider_smoke --tb=short`.
- Repository-relative inspected path: `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py`.
- Inspected surface: provider smoke opt-in.
- Result: SKIPPED. `1 skipped, 3 deselected in 0.78s`, confirming external provider call did not run without opt-in.
- Limitation: Does not prove real provider behavior.

## E-011 Provider Example Birth Context

- Command/source: `python -S -B -c` JSON inspection plus `Select-String` birth-context lines.
- Repository-relative inspected path: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json`.
- Inspected surface: provider example birth context.
- Result: FAIL. All three provider payloads have `birth_date`, `birth_time_local`, `birth_place.city`, `country`, `timezone`, `latitude`, `longitude` equal to null while `chart_id` embeds `1973-04-24 11:00 Europe/Paris Paris France`.
- Limitation: Runtime tests still pass; drift is in official examples/docs.

## E-012 Interpretation Material Source Quality

- Command/source: `python -S -B -c` source material summary plus `Select-String source_ref interpretive_text production-like`.
- Repository-relative inspected path: target example JSON and README.
- Inspected surface: interpretation material source quality.
- Result: PASS. Free, basic, premium payloads have non-empty interpretation text and explicit `source_ref`; README discloses DB-seeded and production-like fixture mix.
- Limitation: Some families remain fixture-backed by design.

## E-013 Backend Ruff Check

- Command/source: `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`.
- Repository-relative inspected path: `backend`.
- Inspected surface: backend lint.
- Result: PASS. `All checks passed!`.
- Limitation: Check-only lint, no formatting.

## E-014 Provider Payload Forbidden Value Walk

- Command/source: `python -S -B -c` JSON forbidden-value walk.
- Repository-relative inspected path: target provider examples.
- Inspected surface: plan and old-carrier payload values.
- Result: PASS. No exact string values or keys among `plan`, `free`, `basic`, `premium`, `chart_json`, `natal_data`, `llm_astrology_input_v1` were found inside target provider payload values or keys.
- Limitation: Filenames and README still contain commercial labels by design.

## E-015 Domain Audit Artifact Validation

- Command/source: `.\.venv\Scripts\Activate.ps1; python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/theme-astral-prompt-contract/2026-05-29-0140` and `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/theme-astral-prompt-contract/2026-05-29-0140`.
- Repository-relative inspected path: `_condamad/audits/theme-astral-prompt-contract/2026-05-29-0140`.
- Inspected surface: domain audit artifact contract.
- Result: PASS. `CONDAMAD domain audit validation passed.` and `CONDAMAD domain audit lint passed.`
- Limitation: Validates artifact contract and lint only; it does not close F-001.
