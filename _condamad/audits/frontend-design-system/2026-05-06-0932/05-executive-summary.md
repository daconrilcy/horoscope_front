<!-- Synthese executive de l'audit frontend design-system. -->

# Executive Summary - frontend-design-system

## Result

Post-refactor design-system governance is materially healthier than the previous audit. Token, fallback, inline-style, legacy-style, admin prompts, and visual-smoke guards pass. CSS fallbacks are down to two dynamic `--usage-progress` bridges, inline styles are down to five exact exceptions, and the admin prompts `legacy` runtime vocabulary targeted by `CS-070` is gone.

## Findings by Severity

- Critical: 0
- High: 0
- Medium: 3
- Low: 1
- Info: 3

## Top Risks

- `.astrologer-card-alias` remains active but unclassified, and the current guard does not catch alias-named selectors unless they contain `legacy`.
- Consultation i18n still shows `(Legacy)` labels; this needs a product decision before renaming.
- Hardcoded visual values remain broad across 106 candidate files, so the next migration must be cluster-scoped.

## Story Candidates

Story candidates: 3.

Recommended next action: implement `SC-001` first because it is small, has no product blocker if renamed, and improves the guard that protects future No Legacy work. Then decide `SC-002`, and continue `SC-003` by one bounded visual-value cluster.

## Validation

Frontend validation passed: targeted Vitest guard suite, `npm run lint`, and `npm run build`. Build still reports the known oversized main chunk warning.
