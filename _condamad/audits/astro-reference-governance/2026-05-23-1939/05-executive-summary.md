# Executive Summary - Astro Reference Governance

This audit created the baseline for astrology rule source governance under `_condamad/audits/astro-reference-governance/2026-05-23-1939/`.

The current implementation is mixed: aspect orbs, many dignity weights, fixed-star catalogs and several interpretation profiles are DB/reference backed and versioned, while solar proximity thresholds, planetary motion profiles, sign weighting, house-strength weights and parts of interpretation profiling remain Python-owned. The highest-risk gaps are duplicated solar proximity thresholds, split motion/station threshold ownership and the absence of a guard that forces new thresholds or weights to be classified.

Recommended sequence:

1. CS-249 inventories and classifies every active rule source and static threshold.
2. CS-250 resolves the planetary condition thresholds into a versioned runtime reference or a documented Python-canonical exception.
3. CS-251 adds source-ownership guards so new thresholds, weights and profiles cannot appear silently.

The story-candidate file keeps one validator-compatible `SC-*` entry per source finding, but all entries route to the three required story keys: CS-249, CS-250 and CS-251.

No application code, seed data, migration or frontend file was intentionally changed by this audit.
