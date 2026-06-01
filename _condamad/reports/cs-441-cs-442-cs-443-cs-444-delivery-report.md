# Delivery Report - CS-441 / CS-442 / CS-443 / CS-444

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-06-02 00:02:11 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced |
| Stories covered | `CS-441`, `CS-442`, `CS-443`, `CS-444` |
| Source documents | `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`; `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`; `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`; `_story_briefs/cs-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal.md`; `_condamad/stories/story-status.md` |
| Story capsules | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy`; `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy`; `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy`; `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal` |
| Diff source | Story final evidence and code-review artifacts; report-time `git status --short` only showed `_condamad/run-state.json` dirty before report creation |
| Validation source | Story-time evidence in `generated/10-final-evidence.md`, `generated/11-code-review.md`, `evidence/validation.txt`, and Codex logs under `_condamad/codex-runs/` |
| Report-time validation | NOT RUN; this phase produced only the delivery report |
| Audits in this series | None, per user instruction. Story-local evidence audits are listed in section 6. |

## 1. Executive summary

The series closes the legacy natal generation correction chain after CS-440 found unresolved legacy runtime, prompt-source, and public API paths. `CS-441`, `CS-442`, `CS-443`, and `CS-444` are all recorded as `done` in `_condamad/stories/story-status.md`, and each final implementation review is `CLEAN` in its `generated/11-code-review.md`.

Final delivery status: `Delivered`. The delivery is supported by story-time targeted backend/frontend tests, lint, route/OpenAPI assertions, zero-hit scans, capsule validation, and clean review artifacts. Material gaps remain: no CI evidence is attached, no validation was rerun during this reporting phase, CS-441 recorded a full backend pytest failure outside its scope, and CS-442/CS-443/CS-444 explicitly skipped full-suite validation in favor of targeted suites.

## 2. Initial context and trigger

The trigger was the failed closure of earlier legacy-natal cleanup stories:

- `CS-441` corrected CS-436 after evidence showed `AIEngineAdapter.generate_natal_interpretation` still existed and was still called by `NatalInterpretationService`; source: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`.
- `CS-442` corrected CS-437 after evidence showed `admin_prompts.py`, tests, catalogues, and seeds could still reintroduce `natal_interpretation_short` or `natal_long_free`; source: `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`.
- `CS-443` corrected CS-438 after evidence showed historical public routes under `/v1/natal/interpretation(s)` were still mounted or preserved; source: `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`.
- `CS-444` closed CS-440 after CS-441 to CS-443, replacing partial/blocker wording with final zero-hit evidence; source: `_story_briefs/cs-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal.md`.

No audit story or audit folder belongs to this series, per the user-provided "Audits de la serie: Aucun audit dans cette serie." The relevant review findings came from implementation review artifacts, especially CS-443 `CR-1` and CS-444 blocker fixes.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-441` | Delete the provider-capable legacy runtime entry point `AIEngineAdapter.generate_natal_interpretation` and prevent provider construction through the old natal service. | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/00-story.md`; `generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Catalogues/seeds/scripts, public historical API deletion, frontend, migrations, and `_condamad/run-state.json` were out of scope. |
| `CS-442` | Remove prompt-source reintroduction paths for old natal use cases from admin prompts, catalogues, bootstrap, scripts, and positive fixtures. | `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/00-story.md`; `generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Runtime provider deletion belonged to CS-441; public API deletion belonged to CS-443; frontend was explicitly not touched. |
| `CS-443` | Remove historical public natal interpretation routes and frontend production calls, preserving modern `/v1/theme-natal/readings`. | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/00-story.md`; `generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Runtime provider deletion belonged to CS-441; prompt-source deletion belonged to CS-442; no compatibility `410` facade was allowed. |
| `CS-444` | Close CS-440 after corrections by proving strict zero-hit closure and updating CS-440 evidence/review/report status. | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/00-story.md`; `generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Did not implement missing functional removals; it verified and hardened closure after CS-441 to CS-443. |

## 4. Implementation summary

`CS-441` removed `AIEngineAdapter.generate_natal_interpretation` from `backend/app/domain/llm/runtime/adapter.py` and removed provider-capable `NatalExecutionInput` / `use_case_key="natal_interpretation"` construction from `backend/app/services/llm_generation/natal/interpretation_service.py`. Its final evidence also records readonly historical reads preserved and architecture guards updated in `backend/tests/architecture/test_llm_legacy_extinction.py`.

`CS-442` removed old natal prompt-source entries from `backend/app/services/llm_generation/admin_prompts.py`, LLM configuration/prompt catalog surfaces, bootstrap, scripts, and positive test fixtures. It physically deleted old seed/script files listed in `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/generated/10-final-evidence.md` and classified remaining old-key hits in `evidence/legacy-source-allowlist.md`.

`CS-443` removed the historical public route module `backend/app/api/v1/routers/public/natal_interpretation.py`, updated route registration in `backend/app/api/v1/routers/registry.py`, and removed frontend production calls from natal-chart surfaces. The implementation review found stale tests preserving `410 Gone` behavior, then converted them to strict absence guards; evidence is in `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/generated/11-code-review.md`.

`CS-444` updated CS-440 closure artifacts and tightened the final zero-hit boundary. Its review records fixes to CS-440 report wording, CS-444 status/evidence, and remaining old free-preview markers in `backend/app/services/llm_generation/natal/interpretation_service.py`, with guard coverage in `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-441` | `generate_natal_interpretation` removed from `backend/app`. | CS-441 brief AC1 | `backend/app/domain/llm/runtime/adapter.py` deletion; `generated/10-final-evidence.md` AC1 | `rg -n "generate_natal_interpretation" backend/app backend/tests backend/app/tests` PASS no matches in `evidence/validation.txt`; targeted pytest PASS | Delivered |
| `CS-441` | Old service no longer builds provider request/runtime input. | CS-441 brief AC2-AC5 | `backend/app/services/llm_generation/natal/interpretation_service.py`; architecture guard `test_natal_legacy_service_does_not_build_runtime_input` listed in final evidence | `rg -n 'NatalExecutionInput|use_case_key' ...` PASS no matches; targeted pytest PASS | Delivered |
| `CS-441` | Historical readonly and modern `theme_natal` behavior preserved. | CS-441 brief AC5-AC8 | Final evidence lists readonly service behavior and `ThemeNatalBasicFullReadingRuntime` as Basic owner | Targeted pytest `64 passed, 23 deselected`; review rerun `80 passed, 22 deselected` in `generated/11-code-review.md` | Delivered |
| `CS-442` | Old prompt keys no longer seedable or nominal admin/catalogue fixtures. | CS-442 brief AC1-AC6 | `admin_prompts.py`, configuration/catalog/bootstrap/scripts, deleted seed files; final evidence file list | Orchestration suite `53 passed`; architecture suite `23 passed`; admin integration `34 passed`; scans PASS_WITH_CLASSIFIED_RESIDUALS in `evidence/validation.txt` | Delivered |
| `CS-442` | Residual old-key hits classified, not executable prompt-source reintroduction. | CS-442 brief AC7-AC11 | `evidence/legacy-source-allowlist.md`; `evidence/legacy-source-hits-after.txt`; prompt cartography updated | Startup/OpenAPI check PASS; persistent evidence path check PASS; review verdict CLEAN | Delivered |
| `CS-443` | `/v1/natal/interpretation(s)` absent from runtime and OpenAPI. | CS-443 brief AC1-AC3 | Deleted `backend/app/api/v1/routers/public/natal_interpretation.py`; registry update; route snapshots | Runtime route/OpenAPI assertions PASS; backend review/fix suite `38 passed`; architecture guard PASS | Delivered |
| `CS-443` | Frontend no longer calls historical public URLs; modern route remains. | CS-443 brief AC4-AC8 | `frontend/src/api/natal-chart/index.ts`; `frontend/src/features/natal-chart/NatalInterpretation.tsx`; `route-consumption-audit.md` | Vitest targeted `4 files / 136 tests`; `pnpm --dir frontend lint` PASS; production URL scan PASS no matches | Delivered |
| `CS-443` | Stale `410 Gone` tests corrected to absence guards. | CS-443 code review CR-1 | `generated/11-code-review.md` lists stale tests and fix | Review/fix backend pytest initially FAIL then PASS `38 passed`; final brief/code alignment rerun PASS | Delivered |
| `CS-444` | CS-441 to CS-443 are done and CS-440 blockers closed. | CS-444 brief AC1, AC6-AC11 | `_condamad/stories/story-status.md`; CS-440 `generated/11-code-review.md`; CS-444 `generated/10-final-evidence.md` | `condamad_validate.py` for CS-444 and CS-440 PASS; CS-440 review verdict CLEAN | Delivered |
| `CS-444` | Strict zero-hit closure for runtime/public legacy patterns. | CS-444 brief AC2-AC5 | `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`; CS-440 audit update | Scans for `generate_natal_interpretation`, old public URLs, and positive mocks PASS no matches; old-key scan classified to extinction denylist only | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/llm/runtime/adapter.py`: CS-441 final evidence states the `AIEngineAdapter.generate_natal_interpretation` method was deleted.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: CS-441 evidence states provider-capable legacy runtime construction was removed; CS-444 evidence states old free-preview use-case markers were removed from public formatting.
- `backend/app/services/llm_generation/admin_prompts.py`, `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`: CS-442 final evidence lists these as prompt-source cleanup surfaces.
- `backend/app/api/v1/routers/registry.py`: CS-443 final evidence lists this as the public router registration surface updated after deleting the historical route module.
- `frontend/src/api/natal-chart/index.ts` and `frontend/src/features/natal-chart/NatalInterpretation.tsx`: CS-443 final evidence lists these as frontend production surfaces changed away from historical URLs.

### Test evidence

- `backend/tests/architecture/test_llm_legacy_extinction.py`: CS-441 final evidence says it guards the removed adapter entry point and old runtime input builder.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`: CS-443 and CS-444 evidence says it guards public route/OpenAPI absence and RG-174 legacy-natal inventory.
- `frontend/src/tests/natalInterpretation.test.tsx`, `frontend/src/tests/natalChartApi.test.tsx`, `frontend/src/tests/natalPublicDomGuard.test.tsx`, `frontend/src/tests/NatalChartPage.test.tsx`: CS-443/CS-444 validation logs record the targeted frontend natal suite at `136 passed`.

### Documentation and evidence artifacts

- `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/removal-audit.md`: story-local deletion/keep decisions for runtime removal.
- `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/legacy-source-removal-audit.md` and `evidence/legacy-source-allowlist.md`: story-local classification of prompt-source residuals.
- `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/route-consumption-audit.md`: route consumption evidence for frontend/backend API removal.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`: final CS-440 closure audit updated by CS-444.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`: CS-444 review says this report was corrected from partial/blocker wording to `done`.

### Operational evidence

- `_condamad/codex-runs/cs-441-dev-story.log`, `cs-441-implementation-review-fix.log`, `cs-441-final-validation.log`: Codex run logs for CS-441 implementation/review/validation.
- `_condamad/codex-runs/cs-442-dev-story.log`, `cs-442-implementation-review-fix.log`, `cs-442-final-validation.log`: Codex run logs for CS-442 implementation/review/validation.
- `_condamad/codex-runs/cs-443-dev-story.log`, `cs-443-implementation-review-fix.log`, `cs-443-final-validation.log`: Codex run logs for CS-443 implementation/review/validation.
- `_condamad/codex-runs/cs-444-dev-story.log`, `cs-444-implementation-review-fix.log`, `cs-444-final-validation.log`: Codex run logs for CS-444 implementation/review/validation.
- `_condamad/codex-runs/cs-441-to-cs-444-delivery-report-delivery-report.log`: report-generation session log; it records the delivery-report source collection commands.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | targeted | PASS | CS-441 `evidence/validation.txt`; CS-442 `evidence/validation.txt`; CS-443 `evidence/validation.txt`; CS-444 `evidence/validation.txt` | Backend lint passed in story-time validation. |
| `ruff format <changed/touched Python files>` | targeted | PASS | CS-441/CS-442/CS-443/CS-444 `evidence/validation.txt` | Format commands were scoped to changed/touched files. |
| CS-441 targeted pytest paths | targeted | PASS | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/validation.txt` | `64 passed, 23 deselected`; review artifact also records `80 passed, 22 deselected`. |
| CS-441 zero-hit scans for `generate_natal_interpretation`, `NatalExecutionInput`, `use_case_key` | targeted | PASS | CS-441 `evidence/validation.txt`; `generated/10-final-evidence.md` | No matches for removed runtime/provider path. |
| `python -B -m pytest -q --tb=short` | full suite | FAIL | CS-441 `evidence/validation.txt`; CS-441 `generated/10-final-evidence.md` | `9 failed, 3552 passed, 2 skipped, 1284 deselected`; documented as out-of-scope repository-level debt for CS-441. |
| CS-442 orchestration/admin/architecture/script suites | targeted | PASS | CS-442 `evidence/validation.txt` | `53 passed`, `23 passed`, `34 passed`, `6 passed`. |
| CS-442 old-key and deleted-seed scans | targeted | PASS | CS-442 `evidence/validation.txt`; `evidence/legacy-source-allowlist.md` | PASS_WITH_CLASSIFIED_RESIDUALS / PASS_WITH_GUARD_HITS; residuals classified. |
| CS-443 backend integration with `--long` and architecture guard | targeted | PASS | CS-443 `evidence/validation.txt`; `generated/11-code-review.md` | Initial stale-test issue fixed; final review/fix backend suite `38 passed`. |
| CS-443 runtime route/OpenAPI absence and production URL scans | targeted | PASS | CS-443 `evidence/validation.txt`; `evidence/forbidden-scan-after.txt` | Historical public paths absent; modern `/v1/theme-natal/readings` present. |
| CS-443 targeted frontend Vitest and lint | targeted | PASS | CS-443 `evidence/validation.txt` | `4 files / 136 tests`; `pnpm --dir frontend lint` PASS. |
| CS-444 backend architecture/LLM guard suite | targeted | PASS | CS-444 `evidence/validation.txt`; `generated/11-code-review.md` | `54 passed`. |
| CS-444 backend theme natal product/read suite | targeted | PASS | CS-444 `evidence/validation.txt` | Final alignment records `50 passed` with `--long` and public free/basic contract. |
| CS-444 frontend targeted natal suite and lint | targeted | PASS | CS-444 `evidence/validation.txt` | `136 passed`; lint PASS. |
| CS-444 zero-hit scans and RG-174 registry scan | targeted | PASS | CS-444 `evidence/validation.txt` | Generator/public route/positive mock scans no-match; old-key residual limited to `natalPublicDomGuard` extinction denylist. |
| `condamad_validate.py` for CS-440 and CS-444 final capsules | targeted | PASS | CS-444 `evidence/validation.txt` | Both final capsule validations passed. |
| CI validation | external | NOT RUN | Not evidenced | No CI output or commit range was provided in the available artifacts. |
| Report-time test/lint rerun | targeted | NOT RUN | This report | User requested a non-interactive report-only phase; no implementation validation was rerun. |
| Full backend suite after CS-442/CS-443/CS-444 | full suite | SKIPPED | CS-442/CS-443/CS-444 `generated/10-final-evidence.md` and `evidence/validation.txt` | Targeted suites and lint were used; full suite not rerun for these stories. |
| Full frontend suite after CS-443/CS-444 | full suite | SKIPPED | CS-443/CS-444 `generated/10-final-evidence.md` and `evidence/validation.txt` | Targeted natal suites and lint were used. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- `CS-443` review found stale tests preserving removed public endpoints as `410 Gone`; those tests were corrected and rerun clean. Evidence: `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/generated/11-code-review.md`, finding `CR-1`.
- `CS-444` review found closure artifacts and `interpretation_service.py` still contradicted the strict zero-hit closure; fixes were applied and rerun. Evidence: `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/generated/11-code-review.md`.
- An unintended helper-generated `_condamad/stories/cs-444/` folder was created during CS-444 capsule repair and removed after path verification. Evidence: CS-444 `generated/10-final-evidence.md` and `evidence/validation.txt`.

### Known limits

- CS-441 full backend pytest failed with 9 failures outside CS-441 scope. Evidence: `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/validation.txt`.
- CS-442, CS-443, and CS-444 did not run full backend/frontend suites; they used targeted story suites, scans, lint, runtime assertions, and capsule validation. Evidence: each story's `generated/10-final-evidence.md`.
- `_condamad/run-state.json` was dirty before the stories/report and was left out of scope. Evidence: CS-441/CS-442/CS-443/CS-444 final evidence preflight blocks and report-time `git status --short`.
- No CI evidence, commit range, or production/live QA evidence is attached. Evidence: absent from provided source artifacts; marked `NOT RUN` / `Not evidenced` in this report.

### Assumptions

- The delivery status uses the story-time validation artifacts as authoritative because the user requested a report-only phase and prohibited application-code changes.
- Remaining old-key literals are accepted only where classified by RG-174 and CS-440/CS-442 evidence as readonly historical, admin-only, rejection guard, or extinction/proof-test evidence. Evidence: CS-442 `evidence/legacy-source-allowlist.md`, CS-444 `evidence/validation.txt`, and CS-440 `generated/11-code-review.md`.

## 9. Residual risks

- Repository-wide regression risk remains because CS-441 recorded full backend pytest as `FAIL` outside its story scope. Impact: unrelated router/model namespace or seed/catalogue debt can still block a future full-suite gate. Mitigation: run and fix a dedicated full-suite stabilization story before release.
- CI parity is not evidenced. Impact: local story-time validation may not cover CI-only environment/configuration differences. Mitigation: attach CI run output for the final branch/commit.
- External consumers of removed public endpoints `/v1/natal/interpretation(s)` receive no compatibility route. Impact: intentional breaking change could affect clients still using the legacy API. Evidence: CS-443 brief forbids a compatibility facade; CS-443 final evidence lists this as expected residual risk.
- `frontend/src/api/natal-chart/index.ts` returns an empty history list until a dedicated modern public list contract exists. Evidence: CS-443 final evidence remaining risks.
- Future drift risk: readonly/admin/test residual old-key classifications must not become public runtime generation. Evidence: CS-444 and CS-440 reviews require RG-174 classifications to remain strict.

## 10. Evidence gaps

- CI output: Not evidenced.
- Commit range and immutable release SHA: Not evidenced.
- Report-time validation rerun: NOT RUN.
- Full backend suite green after the whole CS-441 to CS-444 series: Not evidenced; CS-441 recorded a full-suite FAIL and later stories did not rerun the full suite.
- Full frontend suite green after the whole series: Not evidenced; targeted frontend natal suites passed.
- Live/manual product QA for deleted public endpoints and frontend actions: Not evidenced.
- Audits in this series: none provided; no audit-story findings or candidates exist to link beyond story-local evidence audit files.

## 11. Recommended next actions

1. Run a final CI or local full backend regression gate on the completed branch and resolve or explicitly waive the failures first recorded in CS-441 `evidence/validation.txt`.
2. Attach CI output or a final immutable commit SHA to close the current `Not evidenced` release-provenance gap.
3. Decide whether the modern `/v1/theme-natal/readings` surface needs a replacement list/history or PDF-template contract, because CS-443 intentionally removed legacy history/PDF-template routes.
4. Keep RG-174 as the release guard for future natal changes and reject any movement of classified old-key residuals into public/runtime generation.

## 12. Final delivery status

`Delivered`

All four stories are `done` in `_condamad/stories/story-status.md`, and each implementation review is `CLEAN` in its story-local `generated/11-code-review.md`. Required story-time targeted validation passed for runtime deletion, prompt-source cleanup, public API removal, frontend call removal, CS-440 closure, zero-hit scans, lint, and capsule validation. The delivery remains release-risky until CI or a full post-series regression run proves the repository-wide suite is green.
