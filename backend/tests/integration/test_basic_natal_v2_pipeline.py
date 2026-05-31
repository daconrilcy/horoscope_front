# Commentaire global: preuves d'integration du pipeline Basic natal V2.
"""Valide plan, payload provider, validation et persistance versionnee Basic V2."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy import text

from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import NatalExecutionInput
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.natal.stored_interpretation_payload import (
    BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY,
)
from app.tests.helpers.natal_result_factory import make_natal_result
from tests.integration.basic_natal_v2_helpers import (
    basic_birth_profile,
    basic_entitlement_snapshot,
    basic_runtime_plan,
    gateway_result_from_draft,
    valid_basic_draft,
)

CS423_FORBIDDEN_PUBLIC_TOKENS = (
    "cette lecture s'appuie uniquement",
    "Ce repere retient",
    "avec une confiance editoriale controlee",
    "Luminaire: moon",
    "Position planetaire:",
    "north node",
    "south node",
)


@pytest.mark.asyncio
async def test_basic_complete_builds_plan_payload_validates_and_persists_versions(db) -> None:
    """Prouve le chemin runtime complet Basic V2 avec un gateway fake valide."""
    chart_id = "chart-basic-v2"
    plan = basic_runtime_plan(chart_id=chart_id)
    provider_draft = valid_basic_draft(plan)
    captured_inputs: list[NatalExecutionInput] = []

    async def fake_generate_natal_interpretation(
        natal_input: NatalExecutionInput, db: Any | None = None
    ):
        captured_inputs.append(natal_input)
        return gateway_result_from_draft(natal_input, provider_draft)

    with (
        patch.object(
            AIEngineAdapter,
            "generate_natal_interpretation",
            side_effect=fake_generate_natal_interpretation,
        ),
        patch(
            "app.services.entitlement.effective_entitlement_resolver_service."
            "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
            return_value=basic_entitlement_snapshot(),
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "LlmTokenUsageService.record_usage"
        ),
        patch.object(type(db), "refresh", lambda self, instance: None),
    ):
        response = await NatalInterpretationService.interpret(
            db=db,
            user_id=418,
            chart_id=chart_id,
            natal_result=make_natal_result(),
            birth_profile=basic_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-v2",
            trace_id="trace-basic-v2",
            force_refresh=True,
            variant_code="single_astrologer",
        )

    assert len(captured_inputs) == 1
    natal_input = captured_inputs[0]
    assert natal_input.plan == "basic"
    assert natal_input.basic_natal_prompt_payload is not None
    assert natal_input.basic_natal_prompt_payload["sections"]
    serialized_prompt_payload = json.dumps(natal_input.basic_natal_prompt_payload)
    assert "natal_data" not in serialized_prompt_payload
    assert "chart_json" not in serialized_prompt_payload

    assert response.data.meta.schema_version == "basic_natal_interpretation_v2"
    assert response.data.basic_natal_interpretation_v2 is not None
    assert response.data.basic_natal_interpretation_v2.engine_version == "basic-natal-reading-v1"
    assert response.data.basic_natal_interpretation_v2.schema_version == (
        "basic_natal_interpretation_v2"
    )
    assert response.data.basic_natal_interpretation_v2.taxonomy_version
    assert response.data.basic_natal_interpretation_v2.salience_version
    assert response.data.basic_natal_interpretation_v2.prompt_version
    assert response.data.basic_natal_interpretation_v2.validator_version

    persisted = (
        db.execute(
            text("SELECT interpretation_payload FROM user_natal_interpretations WHERE id = :id"),
            {"id": response.data.meta.id},
        )
        .mappings()
        .one()
    )
    persisted_payload = json.loads(persisted["interpretation_payload"])
    basic_payload = persisted_payload[BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY]
    assert basic_payload["engine_version"] == "basic-natal-reading-v1"
    assert basic_payload["schema_version"] == "basic_natal_interpretation_v2"
    assert basic_payload["taxonomy_version"] == "basic-natal-theme-taxonomy-v1"
    assert basic_payload["salience_version"] == "basic-natal-salience-v1"
    assert basic_payload["prompt_version"] == "basic-natal-draft-prompt-v1"
    assert basic_payload["validator_version"] == "basic-natal-validator-v1"
    serialized_basic_payload = json.dumps(basic_payload, ensure_ascii=False)
    for token in CS423_FORBIDDEN_PUBLIC_TOKENS:
        assert token not in serialized_basic_payload
