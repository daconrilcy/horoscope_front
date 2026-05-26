# Story Candidates - frontend-ux-natal-projections - 2026-05-26-0622

## SC-001 - Close app-owned wording for `/natal` projection panel

- Source finding: F-001
- Suggested story title: Close `/natal` B2C Projection Wording Ownership
- Suggested archetype: frontend-wording-convergence
- Primary domain: frontend-ux
- Required contracts: Runtime Source of Truth; Ownership Routing; Contract Shape; Reintroduction Guard; Persistent Evidence; No Legacy / DRY.
- Draft objective: Review and, if needed, move or adjust app-owned labels, titles, state messages, and helper copy for `beginner_summary_v1` and `client_interpretation_projection_v1` so the projection panel is product-readable and canonical without changing backend projection payloads.
- Closure intent: full-closure
- Must include: Inventory every visible app-owned projection text in `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` and `frontend/src/i18n/natalChart.ts`; decide whether each text is acceptable, corrected, or product-decision-required; keep disclaimer copy owned by app i18n; keep projection transport in `frontend/src/api/astrologyProjections.ts`; keep rendering in existing natal interpretation owners.
- Validation hints: Run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation astrology-i18n natalChartApi`; run `node .\scripts\run-vite-logged.mjs vitest vitest run`; run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages -g "*.tsx"`; run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`; run a browser ledger for `/natal` if visible copy changes.
- Blockers: Stop for product decision if the desired distinction between beginner summary and client interpretation changes offer positioning, plan policy, legal tone, or backend payload content.
- Existing related story: `CS-308-revoir-wording-beginner-summary-client-interpretation` already matches this candidate and should be reused instead of creating a duplicate story.

## Exhaustive Files To Modify

For `F-001` / `SC-001`:

- Application files: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`; `frontend/src/i18n/natalChart.ts`; `frontend/src/features/natal-chart/NatalInterpretation.css` only if text changes reveal spacing or wrapping defects.
- Test files: `frontend/src/tests/natalInterpretation.test.tsx`; `frontend/src/tests/NatalChartPage.test.tsx` only if page-level wording expectations change; `frontend/src/tests/astrology-i18n.test.ts` if i18n ownership changes require coverage.
- Evidence files: CS-308 or successor story evidence folder for wording inventory, refused wording, browser ledger, and validation output.
- Files not to modify: `backend/app/**`; `backend/alembic/**`; `frontend/src/api/astrologyProjections.ts` except for test fixture alignment if absolutely required; package manifests; new UI dependency files.
- Stop condition: The finding is closed when the wording inventory proves every projection label/state/disclaimer-adjacent text is either canonical, corrected, or product-decision-required; targeted tests and static scans pass; browser evidence shows no text/control overlap after any copy change.

## Deferred Non-Domain Context

- Plan-level differentiation is covered by CS-309 and should not be folded into this UX wording candidate.
- Manual profile diversity checks are covered by CS-310.
- Analytics and degraded-state observability are covered by CS-311.

