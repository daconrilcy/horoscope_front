# Legacy scan results

<!-- Commentaire global: ces resultats CS-435 sont clos par le guard zero-hit CS-440. -->

Status: SUPERSEDED_BY_CS_440_ZERO_HIT_GUARD

CS-435 conservait un etat `PASS_WITH_CLASSIFIED_HITS`. CS-440 remplace cette
allowlist large par un audit borne et un invariant durable:

- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`;
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`;
- `RG-174`.

| Scan | Decision CS-440 | Proof |
|---|---|---|
| `natal_interpretation_short`, `natal_long_free` | zero unauthorized public/runtime generator hit | architecture guard + LLM extinction tests |
| `shouldRefreshShortAfterBasicUpgrade`, `forceRefresh` | zero runtime app hit; tests only for rejection/DOM denylist | bounded `rg` scans + frontend guard |
| `use_case_level` | absent du contrat public theme natal; tests only for rejection/gone endpoint | OpenAPI + TestClient |
| `variant_code` | canonical-active hors commande theme natal | entitlement/prediction/astrology classifications + product-action tests |
| `PROMPT_FALLBACK_CONFIGS`, `fallback_default` | governed by prompt fallback guards, not natal public generation | prompt governance tests |
