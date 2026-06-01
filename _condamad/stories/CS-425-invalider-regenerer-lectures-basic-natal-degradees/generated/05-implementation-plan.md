# Implementation Plan - CS-425

## Architecture finding

Basic V2 cache compatibility was schema/engine based and did not enforce an editorial contract version or degraded baseline-token detection.

## Approach

Add a canonical Basic editorial contract version to the public Basic V2 contract, enforce it in the stored-payload compatibility helper, and classify known degraded baseline tokens before public cache reuse.

## Files

Use the existing Basic contract, stored payload helper, narrative validator, provider payload builder and targeted tests. Do not introduce a migration or frontend path.

## Tests

Extend `test_basic_natal_v2_cache_invalidation.py` and `test_basic_natal_reading_contracts.py`; preserve quota and rejected-boundary suites.

## No Legacy stance

No shim, fallback route, alias, duplicate token list, batch migration or legacy cache path is authorized.

## Rollback

Remove the editorial field/check and token helper changes, then remove the added tests and evidence artifacts.
