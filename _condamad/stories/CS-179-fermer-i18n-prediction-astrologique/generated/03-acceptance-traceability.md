# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Inventaire des mappings FR prediction complet avant modification. | Added `prediction-i18n-before.md`. | Baseline scan and consumer list recorded. | Passed |
| AC2 | Plus de source FR DB-backed dans `public_astro_vocabulary.py`. | Replaced local FR mappings with injected label contract adapter. | Resolver tests and forbidden-symbol scans passed. | Passed |
| AC3 | Plus de labels FR locaux dans `astrologer_prompt_builder.py`. | Removed local label mappings and require injected labels. | `tests/unit/prediction/test_astrologer_prompt_builder.py` passed. | Passed |
| AC4 | Les projections prediction gardent leurs cles de payload. | Kept projection keys and injected label source into consumers. | Public projection, daily events, foundation, time window tests and V4 `--long` integration tests passed. | Passed |
| AC5 | Le retour de mappings FR prediction est bloque. | Extended localization guard. | `app/tests/unit/test_astrology_localization_guardrails.py` passed. | Passed |
| AC6 | L'audit after prouve zero residu in-domain. | Added `prediction-i18n-after.md`. | After scans zero-hit and residual marker found. | Passed |
