# No Legacy / DRY Guardrails

## Forbidden

- `_legacy_payload_for_mock_db`
- `ReferenceDataService.get_active_reference_data` in natal calculation flow
- `sign_rulerships = {` inside `backend/app/services/natal`
- `payload.setdefault("sign_rulerships", ...)`
- synthetic `house_axes` or `aspect_orb_rules` fallback in services natal
- `EventDetector.ASPECTS_V1`
- local `ASPECTS = {` in prediction runtime
- silent fallback `orb_max=2.0`

## Canonical owners

- Natal reference: `AstrologyRuntimeReferenceRepository` and runtime contracts.
- Aspect angles/family: `AspectModel` + `AspectProfileData.angle/family_code`.
- Aspect orb rules: `PredictionContext.aspect_orb_rules`.
- Planet catalog: `app.domain.astrology.planet_catalog`.
- Zodiac order: `app.domain.astrology.zodiac.ordered_sign_codes`.

## Required negative evidence

- Natal fallback scan zero-hit.
- Aspect mapping scan zero-hit except `_STAR_DATA` / `_ASPECT_TONES` classified in exception register.
- Boundary scan zero-hit for astrology importing prediction.

## Exceptions

Only exact entries listed in `astrology-constant-exceptions.md`; no wildcard folder exception.
