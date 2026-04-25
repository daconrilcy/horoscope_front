import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.llm.runtime.contracts import (
    GatewayMeta,
    GatewayResult,
    NatalExecutionInput,
    UsageInfo,
)
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService


@pytest.mark.asyncio
async def test_interpret_calls_adapter_canonical(db):
    # Complete mock output for AstroResponse schemas
    full_output = {
        "title": "Title",
        "summary": "Summary",
        "sections": [
            {"key": "overall", "heading": "H1", "content": "C1"},
            {"key": "career", "heading": "H2", "content": "C2"},
        ],
        "highlights": ["H1", "H2", "H3"],
        "advice": ["A1", "A2", "A3"],
    }

    mock_res = GatewayResult(
        use_case="natal_interpretation",
        request_id="r",
        trace_id="t",
        raw_output='{"summary": "test"}',
        structured_output=full_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    persona_id = str(uuid.uuid4())

    with patch(
        "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_natal_interpretation",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_res

        # We need mock objects for the complex parameters
        natal_result = MagicMock()
        birth_profile = MagicMock(birth_time="12:00", birth_lat=48.8, birth_lon=2.3)

        # Mock dependencies
        with (
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json"
            ) as mock_chart,
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog"
            ) as mock_catalog,
        ):
            mock_chart.return_value = {"planets": []}
            mock_catalog.return_value = ["EVID"]

            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="c1",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=persona_id,
                locale="fr-FR",
                question=None,
                request_id="req-1",
                trace_id="tr-1",
                force_refresh=True,
            )

            mock_gen.assert_called_once()
            natal_input = mock_gen.call_args.kwargs["natal_input"]
            assert isinstance(natal_input, NatalExecutionInput)
            assert natal_input.use_case_key == "natal_interpretation"
            assert natal_input.persona_id == persona_id
            assert natal_input.user_id == 1


@pytest.mark.asyncio
async def test_generate_free_short_calls_adapter_canonical(db):
    mock_res = GatewayResult(
        use_case="natal_long_free",
        request_id="r",
        trace_id="t",
        raw_output='{"title": "t", "summary": "s", "accordion_titles": ["a"]}',
        structured_output={"title": "t", "summary": "s", "accordion_titles": ["a"]},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch(
        "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_natal_interpretation",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_res

        natal_result = MagicMock()
        birth_profile = MagicMock(birth_time="12:00", birth_lat=48.8, birth_lon=2.3)

        with (
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_chart_json"
            ) as mock_chart,
            patch(
                "app.services.llm_generation.natal.interpretation_service.build_enriched_evidence_catalog"
            ) as mock_catalog,
        ):
            mock_chart.return_value = {"planets": []}
            mock_catalog.return_value = ["EVID"]

            await NatalInterpretationService.interpret(
                db=db,
                user_id=1,
                chart_id="c1",
                natal_result=natal_result,
                birth_profile=birth_profile,
                level="complete",
                persona_id=None,
                locale="fr-FR",
                question=None,
                request_id="req-1",
                trace_id="tr-1",
                force_refresh=True,
                variant_code="free_short",
            )

            mock_gen.assert_called_once()
            natal_input = mock_gen.call_args.kwargs["natal_input"]
            assert natal_input.use_case_key == "natal_long_free"
            assert natal_input.variant_code == "free_short"
