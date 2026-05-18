# Implementation Plan - CS-186

## Findings

- All listed failures stop before natal calculation because test payloads contain partial signs.
- CS-185 intentionally made the factory strict; weakening it would regress CR-2.

## Plan

1. Add a small `complete_sign_payloads()` helper to the test factory with explicit canonical profile data.
2. Replace affected test sign payloads with the helper.
3. Keep `_complete_sign_payload()` unchanged so partial fixtures still fail.
4. Run targeted tests, guards, scans, lint and backend regression.

## Rollback

Revert the helper and call-site imports if validation reveals a better existing helper. Do not change production runtime behavior.
