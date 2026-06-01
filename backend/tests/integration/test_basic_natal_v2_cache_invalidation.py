# Commentaire global: preuves cache pour les interpretations natales Basic V2.
"""Verifie que seules les lectures Basic V2 versionnees sont servies depuis le cache."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import patch

import pytest

from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import NatalExecutionInput
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.natal.stored_interpretation_payload import (
    contains_degraded_basic_natal_baseline_token,
    has_compatible_basic_natal_interpretation_v2,
)
from app.tests.helpers.natal_result_factory import make_natal_result
from tests.integration.basic_natal_v2_helpers import (
    basic_birth_profile,
    basic_entitlement_snapshot,
    basic_runtime_plan,
    gateway_result_from_draft,
    persisted_basic_payload,
    valid_basic_draft,
)


def _persist_complete_basic_row(
    db,
    *,
    user_id: int,
    payload: dict[str, object],
    chart_id: str = "chart-basic-cache",
) -> UserNatalInterpretationModel:
    """Insere une ligne complete Basic compatible avec la cle cache publique."""
    db.query(UserNatalInterpretationModel).filter(
        UserNatalInterpretationModel.user_id == user_id
    ).delete(synchronize_session=False)
    db.commit()
    row = UserNatalInterpretationModel(
        user_id=user_id,
        chart_id=chart_id,
        level=InterpretationLevel.COMPLETE,
        use_case="natal_interpretation",
        variant_code="single_astrologer",
        persona_id=None,
        interpretation_payload=payload,
        was_fallback=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _without_editorial_version(payload: dict[str, object]) -> dict[str, object]:
    """Retire la version editoriale pour simuler une ligne CS-418 degradee."""
    stale = deepcopy(payload)
    nested = stale["basic_natal_interpretation_v2"]
    assert isinstance(nested, dict)
    nested.pop("basic_editorial_contract_version", None)
    return stale


def _with_old_editorial_version(payload: dict[str, object]) -> dict[str, object]:
    """Remplace la version editoriale par une version anterieure incompatible."""
    stale = deepcopy(payload)
    nested = stale["basic_natal_interpretation_v2"]
    assert isinstance(nested, dict)
    nested["basic_editorial_contract_version"] = "basic-natal-editorial-legacy"
    return stale


def _with_degraded_baseline_token(payload: dict[str, object]) -> dict[str, object]:
    """Injecte un marqueur de baseline degradee dans une lecture sinon compatible."""
    stale = deepcopy(payload)
    nested = stale["basic_natal_interpretation_v2"]
    assert isinstance(nested, dict)
    interpretation = nested["interpretation"]
    assert isinstance(interpretation, dict)
    interpretation["introduction"] = "Cette lecture s'appuie uniquement sur un socle minimal."
    return stale


@pytest.mark.parametrize(
    ("payload_factory", "reason"),
    [
        (
            lambda plan: {
                "summary": "Ancienne lecture Basic",
                "sections": [{"content": "obsolete"}],
            },
            "legacy_payload",
        ),
        (
            lambda plan: _without_editorial_version(persisted_basic_payload(plan)),
            "missing_editorial_version",
        ),
        (
            lambda plan: _with_old_editorial_version(persisted_basic_payload(plan)),
            "old_editorial_version",
        ),
        (
            lambda plan: _with_degraded_baseline_token(persisted_basic_payload(plan)),
            "degraded_baseline_token",
        ),
    ],
)
@pytest.mark.asyncio
async def test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row(
    db, payload_factory, reason: str
) -> None:
    """Prouve qu'une ligne Basic degradee est ignoree et regeneree."""
    chart_id = f"chart-basic-cache-{reason}"
    user_id = 419
    plan = basic_runtime_plan(chart_id=chart_id)
    _persist_complete_basic_row(
        db,
        user_id=user_id,
        chart_id=chart_id,
        payload=payload_factory(plan),
    )
    draft = valid_basic_draft(plan)
    captured_inputs: list[NatalExecutionInput] = []

    async def fake_generate_natal_interpretation(
        natal_input: NatalExecutionInput, db: Any | None = None
    ):
        captured_inputs.append(natal_input)
        return gateway_result_from_draft(natal_input, draft)

    with (
        patch.object(
            AIEngineAdapter,
            "generate_natal_interpretation",
            side_effect=fake_generate_natal_interpretation,
        ),
        patch(
            "app.services.entitlement.effective_entitlement_resolver_service."
            "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
            return_value=basic_entitlement_snapshot(user_id=user_id),
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "LlmTokenUsageService.record_usage"
        ),
        patch.object(type(db), "refresh", lambda self, instance: None),
    ):
        response = await NatalInterpretationService.interpret(
            db=db,
            user_id=user_id,
            chart_id=chart_id,
            natal_result=make_natal_result(),
            birth_profile=basic_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-cache-regen",
            trace_id="trace-basic-cache-regen",
            force_refresh=False,
            variant_code="single_astrologer",
        )

    assert len(captured_inputs) == 1
    assert response.data.meta.cached is False
    assert response.data.basic_natal_interpretation_v2 is not None


@pytest.mark.asyncio
async def test_compatible_basic_cache_is_served_without_gateway_call(db) -> None:
    """Prouve qu'une ligne Basic V2 compatible reste reutilisable."""
    plan = basic_runtime_plan(chart_id="chart-basic-cache-compatible")
    row = _persist_complete_basic_row(
        db,
        user_id=420,
        chart_id="chart-basic-cache-compatible",
        payload=persisted_basic_payload(plan),
    )
    assert "basic_natal_interpretation_v2" in row.interpretation_payload
    nested = row.interpretation_payload["basic_natal_interpretation_v2"]
    assert nested["basic_editorial_contract_version"] == "basic-natal-editorial-v1"
    assert not NatalInterpretationService._is_empty_complete_payload(row.interpretation_payload)
    assert has_compatible_basic_natal_interpretation_v2(row.interpretation_payload)

    with patch.object(AIEngineAdapter, "generate_natal_interpretation") as gateway_mock:
        response = await NatalInterpretationService.interpret(
            db=db,
            user_id=420,
            chart_id="chart-basic-cache-compatible",
            natal_result=make_natal_result(),
            birth_profile=basic_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-cache-hit",
            trace_id="trace-basic-cache-hit",
            force_refresh=False,
            variant_code="single_astrologer",
        )

    gateway_mock.assert_not_called()
    assert response.data.meta.cached is True
    assert response.data.meta.id == row.id
    assert response.data.meta.schema_version == "basic_natal_interpretation_v2"
    assert response.data.basic_natal_interpretation_v2 is not None
    assert (
        response.data.basic_natal_interpretation_v2.basic_editorial_contract_version
        == "basic-natal-editorial-v1"
    )


def test_degraded_baseline_tokens_make_basic_payload_incompatible() -> None:
    """Verrouille la detection centrale des fragments Basic degradees."""
    plan = basic_runtime_plan(chart_id="chart-basic-cache-token")
    payload = _with_degraded_baseline_token(persisted_basic_payload(plan))

    assert contains_degraded_basic_natal_baseline_token(payload)
    assert not has_compatible_basic_natal_interpretation_v2(payload)
