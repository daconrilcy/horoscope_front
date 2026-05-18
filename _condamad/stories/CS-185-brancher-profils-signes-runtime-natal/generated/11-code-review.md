# CONDAMAD Code Review - CS-185

## Review target

- Story: `CS-185-brancher-profils-signes-runtime-natal`
- Scope reviewed: runtime backend astrology, DB-backed sign profiles, tests,
  guardrails and story evidence.
- Frontend: non applicable, no `frontend/**` change.

## Verdict

CLEAN

## Review iterations

- Iteration 1: 3 findings accepted.
- Iteration 2: no remaining evidence-backed issue after fixes and validation.
- Iteration 3: fresh review-fix-story pass on 2026-05-18; no new issue found.

## Findings fixed

### CR-1 Public reference-data payload changed

- Severity: High
- Status: FIXED
- Correction: `ReferenceRepository.get_reference_data()` keeps public
  `signs[]` as `{code, name}`. Runtime profile enrichment moved to
  `AstrologyRuntimeReferenceRepository._load_sign_profiles()`.
- Evidence: `test_public_reference_payload_keeps_sign_contract_unchanged`.

### CR-2 Runtime test factory used seed mapping fallback

- Severity: Medium
- Status: FIXED
- Correction: removed `SIGN_PROFILE_DATA` import from
  `tests/factories/astrology_runtime_reference_factory.py`; partial sign
  fixtures now fail unless profile fields are explicit.
- Evidence: `test_runtime_sign_profile_fixtures_do_not_import_seed_mappings`.

### CR-3 Missing profile error was ambiguous

- Severity: Low
- Status: FIXED
- Correction: runtime sign profile loading uses outer joins and preserves the
  affected sign code, raising `field=sign_profiles`.
- Evidence: `test_repository_rejects_missing_sign_profile_from_db`.

## Final validation evidence

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS
- `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS
- `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py tests/unit/domain/astrology/test_chart_signature.py` - PASS
- `pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py` - PASS
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py` - PASS
- `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` - PASS
- No Legacy scans for RG-114 and prediction boundary - PASS / `NO_MATCH`
- App import smoke test - PASS
- Story validate/lint - PASS

## Acceptance audit

- AC1: PASS, `AstrologyRuntimeReferenceRepository.load()` injects signs from
  `astral_sign_profiles` and taxonomy joins before mapping.
- AC2: PASS, `SignReferenceData` and `SignRuntimeData` require typed profile
  fields; no business `dict` crosses the domain boundary.
- AC3: PASS, missing sign profile is covered by
  `test_repository_rejects_missing_sign_profile_from_db`.
- AC4: PASS, builder propagates profile data and chart signature tests consume
  runtime elements/modalities.
- AC5: PASS, no unsupported structural field was invented.
- AC6: PASS, RG-093, RG-095, RG-107, RG-108, RG-112 and RG-114 evidence is
  present.
- AC7: PASS, before/after, OpenAPI impact and guard evidence artifacts exist.

## DRY / No Legacy audit

- No local `ELEMENT_BY_SIGN`, `MODALITY_BY_SIGN`, `POLARITY_BY_SIGN` or
  `SIGN_PROFILE_DATA` mapping in `app/domain/astrology` or `app/services/natal`.
- Public reference-data payload remains `{code, name}` for signs; runtime
  enrichment is isolated in the runtime repository.
- No compatibility shim, alias, fallback `unknown` or new dependency detected.

## Residual risk

Aucun risque restant identifie.
