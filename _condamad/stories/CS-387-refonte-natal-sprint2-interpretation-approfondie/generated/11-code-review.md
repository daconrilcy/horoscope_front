# CONDAMAD Code Review

## Review target

- Story: `CS-387-refonte-natal-sprint2-interpretation-approfondie`
- Scope: life domains, strengths, challenges, major aspects
- Review date: `2026-05-30`

## Applicable guardrails

- Applicable: `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-129`, `RG-150`, `RG-151`
- Not applicable: unrelated backend persistence and migration guardrails

## Findings

| ID | Severity | Category | Finding | Status |
|---|---|---|---|---|
| F-387-4 | **High** | AC5 / public contract | `chart_balance.dominant_aspects` serializes only `{ code, score, rank, source }`. `resolveMajorAspects` therefore reattaches a ranked aspect type to the first unused raw aspect of that type. With repeated `TRINE`, `SQUARE`, etc., the UI can display the wrong planet pair as a top-ranked aspect. | **Open**. Backend must publish a stable aspect identity (`planet_a`, `planet_b`, `aspect_code` or equivalent identifier) in the ranking contract. |
| F-387-5 | Medium | AC / i18n | Public Sprint 2 copy was hardcoded in French. | Fixed with centralized localized copy and propagated `lang`. |
| F-387-6 | Low | UX | Missing life-domain anchors could look like factual values. | Fixed with explicit localized unavailable copy. |

## Contract evidence

- Ranking construction: `backend/app/domain/astrology/interpretation/chart_signature.py`
- Ranking serialization: `backend/app/services/chart/json_builder.py`
- Ambiguous frontend reattachment: `frontend/src/features/natal-chart/natalPublicFacts.ts`

## Validation audit

- `npm test -- astrology-i18n NatalLifeDomains NatalKarmicSignature NatalChartPage` - PASS (`148` tests)
- `npm run lint` - PASS
- `npm run build` - PASS
- Validation cannot prove AC5 with repeated same-type aspects until the backend contract carries identity.

## Verdict

**CHANGES_REQUESTED**. CS-387 must remain open until ranked aspects retain stable identity end to end.
