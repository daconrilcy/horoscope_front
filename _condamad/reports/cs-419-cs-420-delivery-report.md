# Delivery Report - cs-419-cs-420

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-31 21:52:43 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; current HEAD observed as `b1ad4516` |
| Stories covered | `CS-419`, `CS-420` |
| Source documents | `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`; `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md` |
| Story capsules | `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic`; `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2` |
| Diff source | Story final evidence and review artifacts; report-time `git status --short` only showed pre-existing `_condamad/run-state.json` modified before this report |
| Validation source | story-time evidence files, final review files, and Codex logs |
| Audits in series | None, per user instruction; no audit folder was provided for this series |

## 1. Executive summary

The series covers one backend contract story and one frontend rendering story for public natal interpretations. `CS-419` stabilized `/v1/natal/interpretation` so free short responses are public `short` readings and Basic complete responses expose canonical `basic_natal_interpretation_v2`; evidence is in `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/generated/10-final-evidence.md`. `CS-420` adapted `/natal` to render free short, Basic V2, narrative v1 and obsolete complete branches; evidence is in `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/generated/10-final-evidence.md`.

Final initiative status: `Requires business/QA validation`. Implementation and targeted validation evidence exist for both stories, final implementation reviews are `CLEAN`, and `_condamad/stories/story-status.md` marks both rows `done`. The remaining material gap is authenticated browser QA for the real `/natal` flow, explicitly not completed in `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/browser-qa.md`.

## 2. Initial context and trigger

The trigger is a mismatch between backend public interpretation contracts and frontend branch selection. The `CS-419` brief states that a valid free short response with `meta.level=short`, `use_case=natal_interpretation_short`, readable `interpretation`, and null `narrative_natal_reading_v1` / `basic_natal_interpretation_v2` was displayed by `/natal` as a complete reading to regenerate. The `CS-420` brief scopes the frontend correction: free short and Basic V2 must render their public content, while only complete legacy readings without modern public contracts keep the regeneration message.

No audit story is part of this series. The requested audit section is therefore `Not evidenced` beyond the explicit user statement "Aucun audit dans cette serie."

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-419` | Stabilize backend public `/v1/natal/interpretation` contract for free short and Basic V2 complete readings. | `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/00-story.md`; `generated/03-acceptance-traceability.md` | No frontend rendering, no live provider call, no quota/commercial change, no historical migration. |
| `CS-420` | Adapt React `/natal` rendering to display free short and Basic V2 public payloads without technical leaks. | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/00-story.md`; `generated/03-acceptance-traceability.md` | No backend change, no full page redesign, no old factual cards, no inline styles. |

## 4. Implementation summary

`CS-419` backend evidence:

- `backend/app/services/llm_generation/natal/interpretation_service.py`: final evidence says free short rows now expose public `data.use_case` / `data.meta.use_case` as `natal_interpretation_short` and `data.meta.level=short`, while keeping internal runtime owner `natal_long_free`.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py`: final evidence records new integration coverage for free short and Basic V2 public branches.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/public-contract-before.json` and `public-contract-after.json`: before/after snapshots for the public contract delta.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/generated/11-code-review.md`: final review verdict `CLEAN`.

`CS-420` frontend evidence:

- `frontend/src/api/natal-chart/index.ts` and `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`: final evidence says Basic V2 API/view data contracts were added.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: final evidence says branch order renders narrative v1 first, Basic V2 second, free public rendering third, obsolete complete fallback last.
- `frontend/src/features/natal-chart/NatalInterpretation.css`: final evidence says new public rendering styles are centralized in CSS, with no inline style additions.
- Deleted legacy surfaces: `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`, `NatalInterpretationLegacyBody.tsx`, and `frontend/src/tests/natalInterpretationEvidence.test.ts`, evidenced in `CS-420` final evidence.
- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/generated/11-code-review.md`: final review verdict `CLEAN`.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-419` | Free short is public `meta.level=short`, readable `AstroFreeResponseV1`, has disclaimers, no narrative v1 requirement, no Basic V2 payload. | `CS-419` brief and `00-story.md` AC1-AC4, AC14 | `interpretation_service.py`; `generated/10-final-evidence.md` AC1-AC4, AC14 | `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short --long`: PASS, 4 passed; `public-contract-after.json` | Delivered |
| `CS-419` | Basic complete exposes non-null canonical Basic V2 version block and public synthesis. | `CS-419` brief and `00-story.md` AC5-AC8 | `BasicNatalInterpretationV2` carried as canonical response field; `generated/10-final-evidence.md` AC5-AC8 | Basic V2 pipeline/cache/contract pytest commands PASS in `evidence/validation.txt` | Delivered |
| `CS-419` | Public accepted payloads exclude technical markers. | Guardrails `RG-150`, `RG-152`, `RG-154`, `RG-155`, `RG-164`-`RG-168` in `00-story.md` | Public denylist assertions expanded for `chart_json` and `natal_data`; `generated/11-code-review.md` | Targeted denylist scans classified in `evidence/validation.txt`; accepted public payload tests PASS | Delivered |
| `CS-419` | Route/OpenAPI remain registered. | `00-story.md` AC13 | Existing public FastAPI route remains | Route and OpenAPI python assertions PASS in `generated/10-final-evidence.md` | Delivered |
| `CS-420` | Free short renders title, summary, sections, highlights, advice and disclaimers, without regeneration message. | `CS-420` brief and `00-story.md` AC1-AC3 | `NatalInterpretationContent.tsx`; `natalInterpretation.test.tsx`; `generated/10-final-evidence.md` | `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`: PASS, 119 tests in final validation summary | Delivered |
| `CS-420` | Basic V2 renders public title, introduction, themes, conclusion, limitations, disclaimers and evidence label/meaning only. | `CS-420` brief and `00-story.md` AC4-AC6 | API/view data Basic V2 types; Basic V2 renderer in `NatalInterpretationContent.tsx` | `pnpm --dir frontend build`: PASS; `pnpm --dir frontend lint`: PASS; DOM guard tests and scans PASS in `evidence/validation.txt` | Delivered |
| `CS-420` | Complete legacy without modern contract keeps regeneration message. | `CS-420` brief and `00-story.md` AC7 | `ni-content-card--missing-narrative` branch retained for obsolete complete only | `natalPublicDomGuard` assertions PASS in `generated/10-final-evidence.md` | Delivered |
| `CS-420` | Narrative v1 keeps accessible accordions. | Guardrail `RG-158`; `00-story.md` AC8 | `NatalInterpretation.tsx` injects existing `NatalNarrativeReading`; no duplicate narrative renderer | `rg -n "natal-narrative-reading__toggle" frontend/src/features/natal-chart/NatalNarrativeReading.tsx`: PASS | Delivered |
| `CS-420` | DOM technical markers, legacy classes/components and inline styles remain absent. | Guardrails `RG-153`, `RG-154`, `RG-168`; `00-story.md` AC9-AC10 | Legacy evidence/body components deleted; CSS centralized | VC4/VC5/VC6 `rg` scans zero-hit in `evidence/validation.txt` | Delivered |
| Series | Real authenticated `/natal` flow proves live free short rendering for test user. | `CS-420` brief QA locale requirement | Not evidenced; browser QA only reached login redirect | `browser-qa.md`: route protection observed, authenticated flow not run | Requires business/QA validation |

## 6. Evidence of completion

### Code evidence

- `backend/app/services/llm_generation/natal/interpretation_service.py`: `CS-419` final evidence anchors free-short public classification and Basic V2 preservation.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py`: proves free short and Basic complete public contract branches.
- `frontend/src/api/natal-chart/index.ts`: carries frontend Basic V2 public response types for `CS-420`.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: owns branch selection and public rendering for free short, Basic V2, narrative v1 injection, and complete legacy fallback.
- `frontend/src/features/natal-chart/NatalInterpretation.css`: centralizes new `ni-public-*` rendering styles, supporting the no-inline-style AC.

### Test evidence

- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/validation.txt`: backend targeted lint, pytest, route/OpenAPI assertions and scans.
- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/validation.txt`: frontend targeted/full Vitest, lint, build, scans and story validation.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/generated/11-code-review.md`: final implementation review `CLEAN`.
- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/generated/11-code-review.md`: final implementation review `CLEAN`.

### Documentation evidence

- `_condamad/stories/story-status.md` rows `CS-419` and `CS-420`: both marked `done` with paths and source briefs dated 2026-05-31.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/generated/03-acceptance-traceability.md`: all CS-419 ACs `PASS`.
- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/generated/03-acceptance-traceability.md`: all CS-420 ACs `PASS`.

### Operational evidence

- `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/browser-qa.md`: dev server started on `http://127.0.0.1:5174/`; `/natal` redirected to `/login?returnTo=%2Fnatal`; screenshot path recorded.
- `_condamad/codex-runs/cs-419-final-validation.log`: story validation and strict lint PASS after venv activation.
- `_condamad/codex-runs/cs-420-final-validation.log`: story validation and strict lint PASS after venv activation.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | targeted | PASS | `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/validation.txt` | Backend lint clean during story validation. |
| `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short --long` | targeted | PASS | `CS-419` validation evidence | 4 passed. |
| `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short --long` | targeted | PASS | `CS-419` validation evidence | 1 passed. |
| `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short --long` | targeted | PASS | `CS-419` validation evidence | 2 passed. |
| `python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short` | targeted | PASS | `CS-419` and `CS-420` evidence | 18 passed. |
| `python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short --long` | targeted | PASS | `CS-419` validation evidence | 18 passed. |
| `python -B -m pytest -q --tb=short` | full suite | FAIL | `CS-419` final evidence and `evidence/validation.txt` | 3671 passed, 2 skipped, 1259 deselected, 1 unrelated failure in `tests/architecture/test_astrology_doctrine_governance_guardrails.py`. |
| `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` | targeted | PASS | `CS-420` validation evidence | 119 tests passed in final validation summary. |
| `pnpm --dir frontend test` | full suite | PASS | `CS-420` final evidence | First run had unrelated `router.test.tsx` failure; isolated router rerun passed; second full run passed with 1301 passed, 8 skipped. |
| `pnpm --dir frontend build` | targeted | PASS | `CS-420` validation evidence | TypeScript/Vite build passed. |
| `pnpm --dir frontend lint` | targeted | PASS | `CS-420` validation evidence | Frontend lint passed. |
| CS-420 inline-style scan VC4 | targeted | PASS | `CS-420` validation evidence | `rg -n "style=\\{" ...`: zero hit. |
| CS-420 legacy symbol/class scan VC5 | targeted | PASS | `CS-420` validation evidence | Forbidden legacy symbols/classes zero hit. |
| CS-420 technical marker scan VC6 | targeted | PASS | `CS-420` validation evidence | Forbidden public marker scan zero hit. |
| Authenticated Browser QA on `/natal` with test user | manual | NOT RUN | `_condamad/stories/CS-420-adapter-page-natal-rendu-free-basic-v2/evidence/browser-qa.md` | Backend/auth services were not started; only login redirect was observed. |
| Report-time lint/tests | targeted | NOT RUN | This report generation phase | User requested report only; no code applicatif modified. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- `CS-420` final evidence says authenticated Browser QA was not rerun because backend/auth services were not started. This deviates from the brief's Browser QA expectation for `/natal` with `daconrilcy@hotmail.com`.
- `CS-419` full backend pytest did not pass completely; final evidence classifies the remaining failure as unrelated and pre-existing, not fixed by this series.

### Known limits

- `CS-420` live rendering of real API payloads is evidenced by mocked Vitest fixtures plus backend contract tests, not by an authenticated browser session consuming the real backend. Evidence: `CS-420` final evidence "Runtime rendering of real API payloads remains covered by mocked Vitest fixtures and backend contract tests."
- `CS-419` backend full suite remains limited by one unrelated architecture guard failure. Evidence: `CS-419` final evidence and `evidence/validation.txt`.

### Assumptions

- The report treats `_condamad/stories/story-status.md` rows `done` and final review verdicts `CLEAN` as completion provenance, but not as substitutes for the explicit command evidence listed above.
- The report treats the user's statement "Aucun audit dans cette serie" as authoritative for audit coverage.

## 9. Residual risks

- Authenticated QA gap: a real logged-in `/natal` session with `daconrilcy@hotmail.com` was not evidenced after CS-420. Impact: mocked fixtures could miss integration/auth/data-shape drift. Mitigation: start backend/auth stack and complete Browser QA for the test user.
- Backend full-suite gap: `python -B -m pytest -q --tb=short` failed once in an unrelated architecture governance guard. Impact: release confidence is lower than a fully green backend run. Mitigation: resolve or explicitly waive `tests/architecture/test_astrology_doctrine_governance_guardrails.py::test_rule_marker_surfaces_are_declared_in_doctrine_governance`.
- Frontend full-suite rerun caveat: `pnpm --dir frontend test` passed after rerun, but first exposed an unrelated `router.test.tsx` failure. Impact: possible test isolation flake remains. Mitigation: track router test flakiness if it recurs in CI.

## 10. Evidence gaps

- Commit range for the implementation series is `Not evidenced`; only current branch `main` and HEAD `b1ad4516` were observed during report generation.
- No CI run URL or external CI log was provided.
- Authenticated browser QA is `NOT RUN`; only local route startup and login redirect are evidenced.
- No audit findings, risks or candidates are linked because the series explicitly has no audit stories.

## 11. Recommended next actions

1. Run authenticated Browser QA for `/natal` with `daconrilcy@hotmail.com` after starting backend/auth services, then append the result to `CS-420` browser evidence.
2. Triage the unrelated backend architecture guard failure recorded in `CS-419` evidence before treating the backend full suite as release-green.
3. If this series is released, include the `PASS_WITH_RERUN` frontend full-suite note and the authenticated QA gap in release notes or handoff.

## 12. Final delivery status

`Requires business/QA validation`

Both stories have implementation evidence, AC traceability, targeted validation, `CLEAN` final reviews, and `done` tracker rows. The initiative is not marked simply `Delivered` because the expected authenticated `/natal` Browser QA is explicitly absent, and backend full-suite validation has a documented unrelated failure. Those gaps are visible and bounded, but they require QA/business acceptance or follow-up validation before final release confidence.
