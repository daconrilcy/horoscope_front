from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.ops.llm.eval_harness import run_eval


@pytest.fixture
def mock_gateway():
    with patch("app.ops.llm.eval_harness.LLMGateway") as mock:
        instance = mock.return_value
        instance.execute = AsyncMock()
        yield instance


@pytest.fixture
def fixtures_path():
    # Use the real fixtures path for testing the logic with real files
    return "app/tests/eval_fixtures/natal_interpretation_short"


@pytest.mark.asyncio
async def test_eval_harness_short_all_pass(mock_gateway, fixtures_path):
    """Teste que le harness passe quand le Gateway retourne des résultats valides."""
    # Mock un résultat valide pour AstroResponse_v1
    mock_gateway.execute.return_value = GatewayResult(
        use_case="natal_interpretation_short",
        request_id="test",
        trace_id="test",
        raw_output="{}",
        structured_output={
            "title": "Test Titre Long",
            "summary": (
                "Résumé de test qui est suffisamment long pour passer la "
                "validation de longueur requise de cinquante caractères."
            ),
            "sections": [
                {"key": "overall", "heading": "Vue d'ensemble", "content": "Contenu..."},
                {"key": "career", "heading": "Carrière", "content": "Contenu..."},
            ],
            "highlights": ["H1", "H2", "H3"],
            "advice": ["A1", "A2", "A3"],
            "evidence": ["E1", "E2"],
        },
        usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20, estimated_cost_usd=0),
        meta=GatewayMeta(
            latency_ms=100,
            cached=False,
            prompt_version_id="v1",
            model="gpt-4o-mini",
            validation_status="valid",
        ),
    )

    db = MagicMock()
    report = await run_eval("natal_interpretation_short", "v1", fixtures_path, db)

    assert report.total > 0
    assert report.passed == report.total
    assert report.failure_rate == 0.0
    assert not report.blocked_publication


@pytest.mark.asyncio
async def test_eval_harness_partial_failure(mock_gateway, fixtures_path):
    """Teste le taux d'échec quand certains résultats sont invalides."""

    valid_res = GatewayResult(
        use_case="natal_interpretation_short",
        request_id="test",
        trace_id="test",
        raw_output="{}",
        structured_output={
            "title": "Valid Title",
            "summary": (
                "Résumé de test qui est suffisamment long pour passer la "
                "validation de longueur requise de cinquante caractères."
            ),
            "sections": [
                {"key": "overall", "heading": "H", "content": "C"},
                {"key": "career", "heading": "H2", "content": "C2"},
            ],
            "highlights": ["1", "2", "3"],
            "advice": ["1", "2", "3"],
            "evidence": ["E1", "E2"],
        },
        usage=UsageInfo(input_tokens=0, output_tokens=0, total_tokens=0, estimated_cost_usd=0),
        meta=GatewayMeta(
            latency_ms=0,
            cached=False,
            prompt_version_id="v1",
            model="gpt-4o-mini",
            validation_status="valid",
        ),
    )

    invalid_res = GatewayResult(
        use_case="natal_interpretation_short",
        request_id="test",
        trace_id="test",
        raw_output="{}",
        structured_output={
            "title": "Short",  # Too short
            "summary": "Too short",
            "sections": [],
            "highlights": [],
            "advice": [],
            "evidence": [],
        },
        usage=UsageInfo(input_tokens=0, output_tokens=0, total_tokens=0, estimated_cost_usd=0),
        meta=GatewayMeta(
            latency_ms=0,
            cached=False,
            prompt_version_id="v1",
            model="gpt-4o-mini",
            validation_status="invalid",
        ),
    )

    # Return valid then invalid then valid...
    from itertools import cycle

    mock_gateway.execute.side_effect = cycle([valid_res, invalid_res])

    db = MagicMock()
    report = await run_eval("natal_interpretation_short", "v1", fixtures_path, db)

    assert report.total > 0
    # failure_rate should be > 0 because cycle alternates valid/invalid
    assert 0.0 < report.failure_rate < 1.0


@pytest.mark.asyncio
async def test_eval_harness_empty_fixtures():
    """Teste le comportement si le chemin n'existe pas."""
    db = MagicMock()
    report = await run_eval("non_existent", "v1", "/tmp/non_existent_path", db)
    assert report.total == 0
    assert report.failure_rate == 0.0
