"""Tests unitaires pour le service d'interprétation du thème natal."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.astrology.natal_calculation import (
    AspectResult,
    HouseResult,
    NatalResult,
    PlanetPosition,
)
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.domain.llm.prompting.schemas import AstroResponseV1
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.services.api_contracts.public.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationResponse,
)
from app.services.api_contracts.public.natal_interpretation import (
    NatalInterpretationData as NatalGatewayInterpretationData,
)
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.llm_generation.natal.prompt_context import (
    _detect_degraded_mode,
    _format_longitude,
    _longitude_to_sign,
    build_natal_chart_summary,
)
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.services.user_profile.natal_chart_service import (
    UserNatalChartMetadata,
    UserNatalChartReadData,
)


def _make_natal_result() -> NatalResult:
    """Crée un NatalResult de test."""
    return NatalResult(
        reference_version="v1.0",
        ruleset_version="r1.0",
        house_system="placidus",
        prepared_input=BirthPreparedData(
            birth_datetime_local="1990-06-15T14:30:00+02:00",
            birth_datetime_utc="1990-06-15T12:30:00+00:00",
            timestamp_utc=645364200,
            julian_day=2448073.02,
            birth_timezone="Europe/Paris",
        ),
        planet_positions=[
            PlanetPosition(planet_code="sun", longitude=84.5, sign_code="gemini", house_number=10),
            PlanetPosition(
                planet_code="moon", longitude=112.3, sign_code="cancer", house_number=11
            ),
            PlanetPosition(
                planet_code="mercury", longitude=92.1, sign_code="cancer", house_number=10
            ),
            PlanetPosition(planet_code="venus", longitude=72.8, sign_code="gemini", house_number=9),
            PlanetPosition(planet_code="mars", longitude=25.5, sign_code="aries", house_number=7),
        ],
        houses=[
            HouseResult(number=1, cusp_longitude=195.5),
            HouseResult(number=4, cusp_longitude=285.2),
            HouseResult(number=7, cusp_longitude=15.5),
            HouseResult(number=10, cusp_longitude=105.3),
        ],
        aspects=[
            AspectResult(
                aspect_code="conjunction", planet_a="sun", planet_b="mercury", angle=0.0, orb=7.6
            ),
            AspectResult(
                aspect_code="square", planet_a="sun", planet_b="mars", angle=90.0, orb=4.0
            ),
            AspectResult(
                aspect_code="trine", planet_a="moon", planet_b="venus", angle=120.0, orb=0.5
            ),
            AspectResult(
                aspect_code="opposition", planet_a="mars", planet_b="venus", angle=180.0, orb=2.7
            ),
            AspectResult(
                aspect_code="sextile", planet_a="mercury", planet_b="venus", angle=60.0, orb=1.3
            ),
        ],
    )


def _make_natal_chart_read_data() -> UserNatalChartReadData:
    """Crée un UserNatalChartReadData de test."""
    return UserNatalChartReadData(
        chart_id="chart-123",
        result=_make_natal_result(),
        metadata=UserNatalChartMetadata(
            reference_version="v1.0",
            ruleset_version="r1.0",
        ),
        created_at=datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc),
    )


def _make_birth_profile() -> UserBirthProfileData:
    """Crée un UserBirthProfileData de test."""
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
    )


def _make_gateway_result(use_case: str) -> GatewayResult:
    """Crée un résultat gateway minimal pour exercer le parcours canonique natal."""
    return GatewayResult(
        use_case=use_case,
        request_id="req-test",
        trace_id="trace-test",
        raw_output="{}",
        structured_output={
            "title": "Titre natal",
            "summary": "Synthèse de test détaillée.",
            "sections": [
                {
                    "key": "overall",
                    "heading": "Vue d'ensemble",
                    "content": "Contenu principal.",
                },
                {
                    "key": "strengths",
                    "heading": "Forces",
                    "content": "Contenu complémentaire.",
                },
            ],
            "highlights": ["Point A", "Point B", "Point C"],
            "advice": ["Conseil A", "Conseil B", "Conseil C"],
            "evidence": ["SUN_GEMINI", "MOON_CANCER"],
        },
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=250,
            model="gpt-5",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            validation_status="valid",
            fallback_triggered=False,
            repair_attempted=False,
        ),
    )


class TestLongitudeToSign:
    """Tests pour _longitude_to_sign."""

    def test_aries(self) -> None:
        assert _longitude_to_sign(15.0) == "aries"

    def test_taurus(self) -> None:
        assert _longitude_to_sign(45.0) == "taurus"

    def test_gemini(self) -> None:
        assert _longitude_to_sign(75.0) == "gemini"

    def test_pisces(self) -> None:
        assert _longitude_to_sign(350.0) == "pisces"

    def test_wrap_around(self) -> None:
        assert _longitude_to_sign(370.0) == "aries"


class TestFormatLongitude:
    """Tests pour _format_longitude."""

    def test_exact_degree(self) -> None:
        assert _format_longitude(30.0) == "0°00'"

    def test_with_minutes(self) -> None:
        assert _format_longitude(15.5) == "15°30'"

    def test_partial_minutes(self) -> None:
        result = _format_longitude(84.5)
        assert result == "24°30'"


class TestDetectDegradedMode:
    """Tests pour _detect_degraded_mode."""

    def test_complete_profile_no_degradation(self) -> None:
        profile = _make_birth_profile()
        assert _detect_degraded_mode(profile) is None

    def test_no_time(self) -> None:
        profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="00:00",
            birth_place="Paris, France",
            birth_timezone="Europe/Paris",
        )
        assert _detect_degraded_mode(profile) == "no_time"

    def test_no_location_empty(self) -> None:
        profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="14:30",
            birth_place="",
            birth_timezone="Europe/Paris",
        )
        assert _detect_degraded_mode(profile) == "no_location"

    def test_no_location_unknown(self) -> None:
        profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="14:30",
            birth_place="unknown",
            birth_timezone="Europe/Paris",
        )
        assert _detect_degraded_mode(profile) == "no_location"

    def test_no_location_no_time(self) -> None:
        profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="00:00",
            birth_place="",
            birth_timezone="Europe/Paris",
        )
        assert _detect_degraded_mode(profile) == "no_location_no_time"


class TestBuildNatalChartSummary:
    """Tests pour build_natal_chart_summary."""

    def test_basic_summary(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris, France",
            birth_date="1990-06-15",
            birth_time="14:30",
        )

        assert "Thème natal né(e) le 1990-06-15 à 14:30 à Paris, France:" in summary
        assert "SOLEIL:" in summary
        assert "LUNE:" in summary
        assert "ASCENDANT:" in summary
        assert "ASPECTS MAJEURS:" in summary
        assert "MAISONS ANGULAIRES:" in summary

    def test_summary_contains_sun_position(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris",
            birth_date="1990-06-15",
            birth_time="14:30",
        )

        assert "Gémeaux" in summary
        assert "Maison 10" in summary

    def test_summary_contains_moon_position(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris",
            birth_date="1990-06-15",
            birth_time="14:30",
        )

        assert "Cancer" in summary
        assert "Maison 11" in summary

    def test_summary_contains_ascendant(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris",
            birth_date="1990-06-15",
            birth_time="14:30",
        )

        assert "Balance" in summary

    def test_summary_contains_aspects(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris",
            birth_date="1990-06-15",
            birth_time="14:30",
        )

        assert "conjonction" in summary
        assert "carré" in summary
        assert "trigone" in summary

    def test_degraded_mode_no_time(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="Paris",
            birth_date="1990-06-15",
            birth_time="00:00",
            degraded_mode="no_time",
        )

        assert "Non connue (interprétation des maisons approximative)" in summary

    def test_degraded_mode_no_location(self) -> None:
        natal_result = _make_natal_result()
        summary = build_natal_chart_summary(
            natal_result=natal_result,
            birth_place="",
            birth_date="1990-06-15",
            birth_time="14:30",
            degraded_mode="no_location",
        )

        assert "Non connu (Ascendant non disponible)" in summary


class TestNatalInterpretationService:
    """Tests pour NatalInterpretationService."""

    @pytest.mark.asyncio
    async def test_interpret_chart_success(self) -> None:
        natal_chart = _make_natal_chart_read_data()
        birth_profile = _make_birth_profile()
        db = MagicMock()

        response = NatalInterpretationResponse(
            data=NatalGatewayInterpretationData(
                chart_id="chart-123",
                use_case="natal_interpretation",
                interpretation=AstroResponseV1(
                    title="Titre",
                    summary="Synthèse du thème.",
                    sections=[
                        {
                            "key": "overall",
                            "heading": "Vue d'ensemble",
                            "content": "Texte détaillé",
                        },
                        {
                            "key": "strengths",
                            "heading": "Forces",
                            "content": "Points forts",
                        },
                    ],
                    highlights=["Point A", "Point B", "Point C"],
                    advice=["Conseil A", "Conseil B", "Conseil C"],
                    evidence=[],
                    disclaimers=["Disclaimer important."],
                ),
                meta=InterpretationMeta(
                    level="complete",
                    use_case="natal_interpretation",
                    validation_status="valid",
                    latency_ms=1200,
                ),
            ),
            disclaimers=["Disclaimer important."],
        )

        with patch.object(
            NatalInterpretationService,
            "interpret",
            new=AsyncMock(return_value=response),
        ) as mock_interpret:
            result = await NatalInterpretationService.interpret_chart(
                natal_chart=natal_chart,
                birth_profile=birth_profile,
                user_id=1,
                request_id="req-123",
                trace_id="trace-123",
                persona_id="persona-ignoree",
                db=db,
            )

        mock_interpret.assert_awaited_once_with(
            db=db,
            user_id=1,
            chart_id="chart-123",
            natal_result=natal_chart.result,
            birth_profile=birth_profile,
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-123",
            trace_id="trace-123",
            force_refresh=False,
            module=None,
            variant_code="free_short",
        )
        assert result.chart_id == "chart-123"
        assert "Synthèse du thème." in result.text
        assert result.summary == "Synthèse du thème."
        assert len(result.key_points) == 3
        assert result.metadata.cached is False
        assert result.metadata.latency_ms == 1200

    @pytest.mark.asyncio
    async def test_interpret_chart_degraded_mode(self) -> None:
        natal_chart = _make_natal_chart_read_data()
        birth_profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="00:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        db = MagicMock()
        response = NatalInterpretationResponse(
            data=NatalGatewayInterpretationData(
                chart_id="chart-123",
                use_case="natal_interpretation",
                interpretation=AstroResponseV1(
                    title="Titre",
                    summary="Synthèse",
                    sections=[
                        {"key": "overall", "heading": "Vue", "content": "Texte"},
                        {"key": "strengths", "heading": "Forces", "content": "Points"},
                    ],
                    highlights=["A", "B", "C"],
                    advice=["Conseil A", "Conseil B", "Conseil C"],
                    evidence=[],
                    disclaimers=["Disclaimer"],
                ),
                meta=InterpretationMeta(
                    level="complete",
                    use_case="natal_interpretation",
                    validation_status="valid",
                ),
                degraded_mode="no_time",
            ),
            disclaimers=["Disclaimer"],
        )

        with patch.object(
            NatalInterpretationService,
            "interpret",
            new=AsyncMock(return_value=response),
        ):
            result = await NatalInterpretationService.interpret_chart(
                natal_chart=natal_chart,
                birth_profile=birth_profile,
                user_id=1,
                request_id="req-456",
                db=db,
            )

        assert result.metadata.degraded_mode == "no_time"

    @pytest.mark.asyncio
    async def test_interpret_uses_shared_degraded_mode_detection(self) -> None:
        natal_result = _make_natal_result()
        birth_profile = UserBirthProfileData(
            birth_date="1990-06-15",
            birth_time="00:00",
            birth_place="Paris, France",
            birth_lat=48.8566,
            birth_lon=2.3522,
            birth_timezone="Europe/Paris",
        )
        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = []
        db.get.return_value = None

        with (
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ) as mock_build_chart_json,
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value=[],
            ),
            patch(
                "app.services.entitlement.effective_entitlement_resolver_service."
                "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
                return_value=MagicMock(plan_code="premium"),
            ),
            patch.object(NatalInterpretationService, "_record_token_usage"),
            patch(
                "app.services.llm_generation.natal.interpretation_service."
                "AIEngineAdapter.generate_natal_interpretation",
                new=AsyncMock(return_value=_make_gateway_result("natal_interpretation")),
            ),
        ):
            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-123",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=None,
                locale="fr-FR",
                question=None,
                request_id="req-shared-degraded-mode",
                trace_id="trace-shared-degraded-mode",
            )

        assert mock_build_chart_json.call_args.args[2] == "no_time"

    @pytest.mark.asyncio
    async def test_interpret_chart_timeout_error(self) -> None:
        natal_chart = _make_natal_chart_read_data()
        birth_profile = _make_birth_profile()

        with patch.object(
            NatalInterpretationService,
            "interpret",
            new=AsyncMock(side_effect=TimeoutError("AI Engine timeout")),
        ):
            with pytest.raises(NatalInterpretationServiceError) as exc_info:
                await NatalInterpretationService.interpret_chart(
                    natal_chart=natal_chart,
                    birth_profile=birth_profile,
                    user_id=1,
                    request_id="req-timeout",
                    db=MagicMock(),
                )

        assert exc_info.value.code == "ai_engine_timeout"
