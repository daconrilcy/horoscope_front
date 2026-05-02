"""Verifie l'ownership LLM canonique des consultations thematiques."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.api_contracts.public.consultation import (
    ConsultationGenerateRequest,
    ConsultationStatus,
    FallbackMode,
    PrecisionLevel,
    SafeguardIssue,
)
from app.services.consultation.precheck_service import ConsultationPrecheckService
from app.services.llm_generation.consultation_generation_service import (
    ConsultationGenerationService,
)
from app.services.llm_generation.guidance.guidance_service import GuidanceService
from scripts.seed_consultation_templates import CONSULTATION_TEMPLATE_SEEDS


@pytest.mark.asyncio
async def test_precheck_refusal_returns_without_guidance_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un refus precheck reste un chemin metier sans prompt LLM."""
    db = MagicMock()
    request = ConsultationGenerateRequest(
        consultation_type="period",
        question="Vais-je guerir de mon cancer ?",
    )
    monkeypatch.setattr(
        ConsultationPrecheckService,
        "precheck",
        MagicMock(
            return_value=SimpleNamespace(
                status=ConsultationStatus.blocked,
                precision_level=PrecisionLevel.blocked,
                fallback_mode=FallbackMode.safeguard_refused,
                safeguard_issue=SafeguardIssue.health,
            )
        ),
    )
    guidance_call = AsyncMock()
    monkeypatch.setattr(
        GuidanceService,
        "request_contextual_guidance_async",
        guidance_call,
    )

    result = await ConsultationGenerationService.generate(
        db=db,
        user_id=42,
        request=request,
        request_id="rid-refused",
    )

    assert result.consultation_id == "refused_rid-refused"
    assert result.status == ConsultationStatus.blocked
    assert result.fallback_mode == FallbackMode.safeguard_refused
    assert result.sections == []
    guidance_call.assert_not_called()


def test_consultation_prompt_content_is_not_mapped_to_developer_prompt() -> None:
    """Garde AST legere contre une promotion de prompt_content en prompt provider."""
    source = (
        Path(__file__).resolve().parents[2]
        / "services"
        / "llm_generation"
        / "consultation_generation_service.py"
    )
    content = source.read_text(encoding="utf-8")

    assert "prompt_content" in content
    assert "developer_prompt" not in content


def test_consultation_template_seed_prompt_content_stays_product_objective() -> None:
    """Bloque les consignes LLM durables dans les objectifs catalogue consultation."""
    forbidden_markers = (
        "analyse ",
        "analyse le",
        "analyse les",
        "aide l'utilisateur",
        "compare ",
        "concentre-toi",
        "genere ",
        "génère ",
        "reponds ",
        "réponds ",
        "reste ",
        "tu dois",
        "utilise ",
    )

    for template in CONSULTATION_TEMPLATE_SEEDS:
        prompt_content = str(template["prompt_content"]).casefold()

        assert len(prompt_content) <= 90
        assert not any(marker in prompt_content for marker in forbidden_markers)
