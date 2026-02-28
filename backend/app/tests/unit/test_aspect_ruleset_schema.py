"""Tests unitaires pour le schema de ruleset aspects schools versionnees (story 24-1).

Couvre:
- AC1: validation schema ruleset — code, angle, default_orb_deg obligatoires avec bornes
- AC1: orb_luminaries_override_deg et orb_pair_overrides valides/invalides
- AC2: serialization metadata — aspect_school et aspect_rules_version presents
"""

from __future__ import annotations

import pytest

from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_birth_input(
    birth_lat: float = 48.85,
    birth_lon: float = 2.35,
) -> BirthInput:
    return BirthInput(
        birth_date="1990-06-15",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        place_resolved_id=1,
    )


def _make_reference_data(
    aspects: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    default_aspects = [
        {"code": "conjunction", "angle": 0, "default_orb_deg": 8.0},
        {"code": "opposition", "angle": 180, "default_orb_deg": 8.0},
    ]
    return {
        "version": "1.0.0",
        "planets": [{"code": "sun", "name": "Sun"}],
        "signs": [{"code": "aries", "name": "Aries"}, {"code": "taurus", "name": "Taurus"}],
        "houses": [{"number": n, "name": f"House {n}"} for n in range(1, 13)],
        "aspects": aspects if aspects is not None else default_aspects,
    }


def _swisseph_positions_mock(
    jdut: float, planet_codes: list[str], **kwargs: object
) -> list[dict[str, object]]:
    return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]


def _swisseph_houses_mock(
    jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
) -> tuple[list[dict[str, object]], str]:
    return [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers], "placidus"


# ---------------------------------------------------------------------------
# AC1 — Validation schema ruleset: code, angle, default_orb_deg
# ---------------------------------------------------------------------------


class TestAspectRulesetSchemaValidation:
    """Validation que chaque aspect du ruleset contient code, angle, default_orb_deg."""

    def test_valid_aspect_with_all_fields_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Un aspect valide avec code, angle, default_orb_deg ne leve pas d'erreur."""
        ref = _make_reference_data(
            aspects=[
                {"code": "conjunction", "angle": 0, "default_orb_deg": 8.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        assert result is not None

    def test_aspect_missing_default_orb_deg_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Un aspect sans default_orb_deg est invalide et leve NatalCalculationError."""
        ref = _make_reference_data(
            aspects=[
                {"code": "conjunction", "angle": 0},  # pas de default_orb_deg
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        with pytest.raises(NatalCalculationError) as exc_info:
            build_natal_result(
                birth_input=_make_birth_input(),
                reference_data=ref,
                ruleset_version="1.0.0",
                engine="swisseph",
                birth_lat=48.85,
                birth_lon=2.35,
            )
        assert exc_info.value.code == "invalid_reference_data"
        assert "default_orb_deg" in str(exc_info.value.details)

    def test_aspect_default_orb_deg_zero_is_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """default_orb_deg=0 (aspect exact) est desormais valide."""
        ref = _make_reference_data(
            aspects=[
                {"code": "conjunction", "angle": 0, "default_orb_deg": 0.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        assert result is not None

    def test_aspect_default_orb_deg_exceeds_max_is_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """default_orb_deg=16.0 (hors bornes: doit etre <= MAX_ORB_DEG=15) est invalide."""
        ref = _make_reference_data(
            aspects=[
                {"code": "conjunction", "angle": 0, "default_orb_deg": 16.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        with pytest.raises(NatalCalculationError) as exc_info:
            build_natal_result(
                birth_input=_make_birth_input(),
                reference_data=ref,
                ruleset_version="1.0.0",
                engine="swisseph",
                birth_lat=48.85,
                birth_lon=2.35,
            )
        assert exc_info.value.code == "invalid_reference_data"

    def test_aspect_default_orb_deg_at_max_boundary_is_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """default_orb_deg=15.0 (egal a MAX_ORB_DEG=15) est valide."""
        ref = _make_reference_data(
            aspects=[
                {"code": "conjunction", "angle": 0, "default_orb_deg": 15.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        assert result is not None


# ---------------------------------------------------------------------------
# AC1 — Overrides: orb_luminaries_override_deg et orb_pair_overrides
# ---------------------------------------------------------------------------


class TestAspectOrbOverrides:
    """Validation des overrides d'orbes dans le ruleset."""

    def test_orb_luminaries_override_deg_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """orb_luminaries_override_deg valide est accepte."""
        ref = _make_reference_data(
            aspects=[
                {
                    "code": "conjunction",
                    "angle": 0,
                    "default_orb_deg": 8.0,
                    "orb_luminaries_override_deg": 10.0,
                },
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        assert result is not None

    def test_orb_luminaries_override_deg_out_of_bounds_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """orb_luminaries_override_deg hors bornes leve NatalCalculationError."""
        ref = _make_reference_data(
            aspects=[
                {
                    "code": "conjunction",
                    "angle": 0,
                    "default_orb_deg": 8.0,
                    "orb_luminaries_override_deg": 20.0,  # > MAX_ORB_DEG
                },
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        with pytest.raises(NatalCalculationError) as exc_info:
            build_natal_result(
                birth_input=_make_birth_input(),
                reference_data=ref,
                ruleset_version="1.0.0",
                engine="swisseph",
                birth_lat=48.85,
                birth_lon=2.35,
            )
        assert exc_info.value.code == "invalid_reference_data"

    def test_orb_pair_overrides_out_of_bounds_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """orb_pair_overrides avec valeur hors bornes leve NatalCalculationError."""
        ref = _make_reference_data(
            aspects=[
                {
                    "code": "conjunction",
                    "angle": 0,
                    "default_orb_deg": 8.0,
                    "orb_pair_overrides": {"sun-moon": 20.0},  # > MAX_ORB_DEG
                },
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        with pytest.raises(NatalCalculationError) as exc_info:
            build_natal_result(
                birth_input=_make_birth_input(),
                reference_data=ref,
                ruleset_version="1.0.0",
                engine="swisseph",
                birth_lat=48.85,
                birth_lon=2.35,
            )
        assert exc_info.value.code == "invalid_reference_data"

    def test_orb_pair_overrides_zero_is_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """orb_pair_overrides avec valeur 0 est desormais valide."""
        ref = _make_reference_data(
            aspects=[
                {
                    "code": "conjunction",
                    "angle": 0,
                    "default_orb_deg": 8.0,
                    "orb_pair_overrides": {"sun-moon": 0.0},
                },
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        assert result is not None


# ---------------------------------------------------------------------------
# AC2 — Serialization metadata: aspect_school et aspect_rules_version
# ---------------------------------------------------------------------------


class TestAspectSchoolMetadataSerialization:
    """Serialization: aspect_school et aspect_rules_version presents dans NatalResult."""

    def test_natal_result_has_aspect_school_field(self) -> None:
        """NatalResult doit avoir le champ aspect_school."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        payload = result.model_dump()
        assert "aspect_school" in payload

    def test_natal_result_has_aspect_rules_version_field(self) -> None:
        """NatalResult doit avoir le champ aspect_rules_version."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        payload = result.model_dump()
        assert "aspect_rules_version" in payload

    def test_natal_result_default_aspect_school_is_modern(self) -> None:
        """Le default de aspect_school est 'modern'."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        assert result.aspect_school == "modern"

    def test_natal_result_aspect_school_accepts_classic(self) -> None:
        """aspect_school='classic' est accepte."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            aspect_school="classic",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        assert result.aspect_school == "classic"

    def test_natal_result_aspect_school_accepts_strict(self) -> None:
        """aspect_school='strict' est accepte."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            aspect_school="strict",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        assert result.aspect_school == "strict"

    def test_natal_result_aspect_rules_version_defaults_to_ruleset_version(self) -> None:
        """aspect_rules_version est une string presente dans le payload."""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            aspect_rules_version="modern-1.0.0",
            house_system="placidus",
            prepared_input=BirthPreparedData(
                birth_datetime_local="1990-06-15T12:00:00+02:00",
                birth_datetime_utc="1990-06-15T10:00:00Z",
                timestamp_utc=645350400,
                julian_day=2448057.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )
        assert result.aspect_rules_version == "modern-1.0.0"
        payload = result.model_dump()
        assert payload["aspect_rules_version"] == "modern-1.0.0"

    def test_build_natal_result_propagates_aspect_school(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """build_natal_result propage aspect_school dans NatalResult."""
        ref = _make_reference_data()
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
            aspect_school="classic",
            aspect_rules_version="classic-1.0.0",
        )
        assert result.aspect_school == "classic"
        assert result.aspect_rules_version == "classic-1.0.0"

    def test_natal_result_model_dump_contains_aspect_school_and_version(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Le model_dump() de NatalResult expose aspect_school et aspect_rules_version."""
        ref = _make_reference_data()
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
            aspect_school="modern",
            aspect_rules_version="modern-1.0.0",
        )
        payload = result.model_dump()
        assert payload.get("aspect_school") == "modern"
        assert payload.get("aspect_rules_version") == "modern-1.0.0"

    def test_natal_result_legacy_payload_validation_compatibility(self) -> None:
        """NatalResult.model_validate() accepte payload sans les nouveaux champs."""
        legacy_payload = {
            "reference_version": "1.0.0",
            "ruleset_version": "1.0.0",
            "house_system": "placidus",
            "prepared_input": {
                "birth_datetime_local": "1990-06-15T12:00:00+02:00",
                "birth_datetime_utc": "1990-06-15T10:00:00Z",
                "timestamp_utc": 645350400,
                "julian_day": 2448057.0,
                "birth_timezone": "Europe/Paris",
            },
            "planet_positions": [],
            "houses": [],
            "aspects": [],
            # Pas de aspect_school, ni aspect_rules_version
        }
        result = NatalResult.model_validate(legacy_payload)
        assert result.aspect_school == "modern"  # default
        assert result.aspect_rules_version is not None  # a une valeur par defaut
