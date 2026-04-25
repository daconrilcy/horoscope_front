"""Tests unitaires pour NatalInterpretationService.

Couverture story 30-5:
- C1: 'question' absent de user_input pour level='complete'
- Contrôle inverse : 'question' présent pour level='short'
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.astrology.natal_calculation import (
    AspectResult,
    HouseResult,
    NatalResult,
    PlanetPosition,
)
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.user_birth_profile_service import UserBirthProfileData


def _make_natal_result() -> NatalResult:
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
        ],
        houses=[
            HouseResult(number=1, cusp_longitude=195.5),
            HouseResult(number=10, cusp_longitude=105.3),
        ],
        aspects=[
            AspectResult(
                aspect_code="trine",
                planet_a="sun",
                planet_b="moon",
                angle=120.0,
                orb=2.0,
            )
        ],
    )


def _make_birth_profile() -> UserBirthProfileData:
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )


def _make_gateway_result(use_case: str) -> GatewayResult:
    """Cree un GatewayResult valide (Pydantic) pour les tests."""
    structured = {
        "title": "Theme Natal Test",
        "summary": "Synthese de test narrative. " * 4,
        "sections": [
            {
                "key": "overall",
                "heading": "Vue d ensemble",
                "content": "Contenu section globale. " * 4,
            },
            {
                "key": "career",
                "heading": "Carriere",
                "content": "Contenu section carriere. " * 4,
            },
        ],
        "highlights": ["Point fort 1", "Point fort 2", "Point fort 3"],
        "advice": ["Conseil pratique 1", "Conseil pratique 2", "Conseil pratique 3"],
        "evidence": ["SUN_GEMINI_H10", "MOON_CANCER_H11"],
        "disclaimers": [],
    }
    return GatewayResult(
        use_case=use_case,
        request_id="req-test",
        trace_id="trace-test",
        raw_output="{}",
        structured_output=structured,
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=500,
            model="gpt-5",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            validation_status="valid",
            fallback_triggered=False,
            repair_attempted=False,
        ),
    )


def _make_free_short_gateway_result() -> GatewayResult:
    return GatewayResult(
        use_case="natal_long_free",
        request_id="req-free",
        trace_id="trace-free",
        raw_output=(
            '{"title":"Votre thème révèle une sensibilité vive qui cherche l harmonie.",'
            '"summary":"Resume free","accordion_titles":["Section 1","Section 2"]}'
        ),
        structured_output={
            "title": "Votre thème révèle une sensibilité vive qui cherche l harmonie.",
            "summary": "Resume free",
            "accordion_titles": ["Section 1", "Section 2"],
        },
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=200,
            model="gpt-5",
            prompt_version_id="hardcoded-v1",
            validation_status="valid",
            fallback_triggered=False,
            repair_attempted=False,
        ),
    )


def _make_empty_complete_gateway_result() -> GatewayResult:
    return GatewayResult(
        use_case="natal_interpretation",
        request_id="req-empty",
        trace_id="trace-empty",
        raw_output="{}",
        structured_output={
            "title": "Interprétation vide",
            "summary": "   ",
            "sections": [
                {"key": "overall", "heading": "Vue d ensemble", "content": "   "},
            ],
            "highlights": [],
            "advice": [],
            "evidence": [],
        },
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=200,
            model="gpt-5",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            validation_status="valid",
            fallback_triggered=False,
            repair_attempted=False,
        ),
    )


PERSONA_ID = "12345678-1234-5678-1234-567812345678"


def _patch_entitlement_snapshot(plan_code: str = "premium"):
    return patch(
        "app.services.entitlement.effective_entitlement_resolver_service."
        "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
        return_value=MagicMock(plan_code=plan_code),
    )


def _make_db_mock(has_persona: bool = True) -> MagicMock:
    """
    Retourne un mock de Session SQLAlchemy avec:
      - 1er db.execute -> cache miss (scalar_one_or_none = None)
      - 2eme db.execute -> persona trouvee si has_persona=True
    """
    mock_persona = MagicMock()
    mock_persona.name = "Luna"
    mock_persona.description = "Profil pedagogique et bienveillant."
    mock_persona.tone = "warm"
    mock_persona.verbosity = "medium"
    mock_persona.style_markers = ["langage clair", "nuance"]
    mock_persona.boundaries = ["ne pas etre fataliste"]
    mock_persona.allowed_topics = ["theme natal", "relations"]
    call_count = 0

    def _execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        result.scalar_one_or_none.return_value = (
            None if call_count == 1 else (mock_persona if has_persona else None)
        )
        return result

    db = MagicMock()
    db.execute.side_effect = _execute
    db.get.return_value = mock_persona
    return db


class TestNatalInterpretationServiceUserInput:
    """Verifie la construction de user_input transmis au gateway (story 30-5)."""

    @pytest.mark.asyncio
    async def test_complete_level_does_not_include_question(self):
        """
        C1 (story 30-5): 'question' ne doit PAS etre dans user_input pour level='complete'.
        """
        natal_result = _make_natal_result()
        birth_profile = _make_birth_profile()
        gw_result = _make_gateway_result("natal_interpretation")
        db = _make_db_mock(has_persona=True)

        mock_gw_instance = MagicMock()
        mock_gw_instance.execute_request = AsyncMock(return_value=gw_result)

        mock_persisted = MagicMock()
        mock_persisted.created_at = None

        with (
            patch("app.services.llm_generation.natal.interpretation_service.select"),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value={"SUN_LEO": ["Soleil en Lion"]},
            ),
            patch(
                "app.domain.llm.runtime.adapter.LLMGateway",
                return_value=mock_gw_instance,
            ),
            _patch_entitlement_snapshot(),
            patch(
                "app.services.llm_generation.natal.interpretation_service.UserNatalInterpretationModel",
                return_value=mock_persisted,
            ),
        ):
            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-abc",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=PERSONA_ID,
                locale="fr",
                question="Une question passee intentionnellement",
                request_id="req-test",
                trace_id="trace-test",
            )

        assert mock_gw_instance.execute_request.called
        request_sent = mock_gw_instance.execute_request.call_args.kwargs["request"]
        user_input_sent = request_sent.user_input

        assert user_input_sent.question is None
        assert user_input_sent.locale == "fr"

    @pytest.mark.asyncio
    async def test_short_level_includes_question(self):
        """Controle inverse: 'question' DOIT etre dans user_input pour level='short'."""
        natal_result = _make_natal_result()
        birth_profile = _make_birth_profile()
        gw_result = _make_gateway_result("natal_interpretation_short")

        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = None

        mock_gw_instance = MagicMock()
        mock_gw_instance.execute_request = AsyncMock(return_value=gw_result)

        mock_persisted = MagicMock()
        mock_persisted.created_at = None

        with (
            patch("app.services.llm_generation.natal.interpretation_service.select"),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value={"SUN_LEO": ["Soleil en Lion"]},
            ),
            patch(
                "app.domain.llm.runtime.adapter.LLMGateway",
                return_value=mock_gw_instance,
            ),
            _patch_entitlement_snapshot(),
            patch(
                "app.services.llm_generation.natal.interpretation_service.UserNatalInterpretationModel",
                return_value=mock_persisted,
            ),
        ):
            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-abc",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="short",
                persona_id=None,
                locale="fr",
                question="Ma vraie question de test",
                request_id="req-test",
                trace_id="trace-test",
            )

        request_sent = mock_gw_instance.execute_request.call_args.kwargs["request"]
        user_input_sent = request_sent.user_input
        assert user_input_sent.question == "Ma vraie question de test"

    @pytest.mark.asyncio
    async def test_short_level_default_question_when_none(self):
        natal_result = _make_natal_result()
        birth_profile = _make_birth_profile()
        gw_result = _make_gateway_result("natal_interpretation_short")

        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = None

        mock_gw_instance = MagicMock()
        mock_gw_instance.execute_request = AsyncMock(return_value=gw_result)

        mock_persisted = MagicMock()
        mock_persisted.created_at = None

        with (
            patch("app.services.llm_generation.natal.interpretation_service.select"),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value={"SUN_LEO": ["Soleil en Lion"]},
            ),
            patch(
                "app.domain.llm.runtime.adapter.LLMGateway",
                return_value=mock_gw_instance,
            ),
            _patch_entitlement_snapshot(),
            patch(
                "app.services.llm_generation.natal.interpretation_service.UserNatalInterpretationModel",
                return_value=mock_persisted,
            ),
        ):
            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-abc",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="short",
                persona_id=None,
                locale="fr",
                question=None,
                request_id="req-test",
                trace_id="trace-test",
            )

        request_sent = mock_gw_instance.execute_request.call_args.kwargs["request"]
        user_input_sent = request_sent.user_input
        assert "interprète" in user_input_sent.question.lower()


class TestNatalInterpretationServiceSchemaVersion:
    @pytest.mark.asyncio
    async def test_complete_level_sets_v2(self):
        natal_result = _make_natal_result()
        birth_profile = _make_birth_profile()
        gw_result = _make_gateway_result("natal_interpretation")
        db = _make_db_mock(has_persona=True)

        mock_gw_instance = MagicMock()
        mock_gw_instance.execute_request = AsyncMock(return_value=gw_result)

        mock_persisted = MagicMock()
        mock_persisted.created_at = None

        with (
            patch("app.services.llm_generation.natal.interpretation_service.select"),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value={"SUN_LEO": ["Soleil en Lion"]},
            ),
            patch(
                "app.domain.llm.runtime.adapter.LLMGateway",
                return_value=mock_gw_instance,
            ),
            _patch_entitlement_snapshot(),
            patch(
                "app.services.llm_generation.natal.interpretation_service.UserNatalInterpretationModel",
                return_value=mock_persisted,
            ),
        ):
            resp = await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-abc",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=PERSONA_ID,
                locale="fr",
                question=None,
                request_id="req-test",
                trace_id="trace-test",
            )

        assert resp.data.meta.schema_version == "v2"


class TestNatalInterpretationServiceModules:
    @pytest.mark.asyncio
    async def test_complete_module_bypasses_persistence_and_injects_module_context(self):
        natal_result = _make_natal_result()
        birth_profile = _make_birth_profile()
        gw_result = _make_gateway_result("natal_psy_profile")

        mock_persona = MagicMock()
        mock_persona.name = "Luna"
        mock_persona.description = "Profil pedagogique et bienveillant."
        mock_persona.tone = "warm"
        mock_persona.verbosity = "medium"
        mock_persona.style_markers = ["langage clair"]
        mock_persona.boundaries = ["ne pas etre fataliste"]
        mock_persona.allowed_topics = ["theme natal"]

        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = mock_persona
        db.get.return_value = mock_persona

        mock_gw_instance = MagicMock()
        mock_gw_instance.execute_request = AsyncMock(return_value=gw_result)

        with (
            patch("app.services.llm_generation.natal.interpretation_service.select"),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json",
                return_value={"planets": []},
            ),
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog",
                return_value={"SUN_LEO": ["Soleil en Lion"]},
            ),
            patch(
                "app.domain.llm.runtime.adapter.LLMGateway",
                return_value=mock_gw_instance,
            ),
            _patch_entitlement_snapshot(),
        ):
            resp = await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="chart-abc",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=PERSONA_ID,
                locale="fr",
                question=None,
                request_id="req-test",
                trace_id="trace-test",
                module="NATAL_PSY_PROFILE",
            )

        request_sent = mock_gw_instance.execute_request.call_args.kwargs["request"]
        assert request_sent.user_input.use_case == "natal_psy_profile"
        assert request_sent.context.extra_context["module"] == "NATAL_PSY_PROFILE"
        assert resp.data.meta.cached is False
        db.commit.assert_not_called()
        assert db.add.call_count == 1
