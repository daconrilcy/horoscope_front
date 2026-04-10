import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.llm_orchestration.admin_models import (
    LlmExecutionProfileCreate,
    PromptAssemblyConfig,
    PromptAssemblyTarget,
)
from app.llm_orchestration.feature_taxonomy import (
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
    assert_nominal_feature_allowed,
    is_nominal_feature_allowed,
    normalize_feature,
    normalize_subfeature,
)
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    LLMExecutionRequest,
)
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.execution_profile_registry import ExecutionProfileRegistry


def test_taxonomy_normalization_basic():
    """Test unitaire de la taxonomie (AC1, AC2, AC4, Task 4)."""
    assert normalize_feature(LEGACY_NATAL_FEATURE) == NATAL_CANONICAL_FEATURE
    assert normalize_feature("chat") == "chat"

    assert normalize_subfeature(NATAL_CANONICAL_FEATURE, "natal_interpretation") == "interpretation"
    assert normalize_subfeature(NATAL_CANONICAL_FEATURE, "short") == "short"
    assert normalize_subfeature("chat", "astrologer") == "astrologer"


def test_taxonomy_validation():
    """Test unitaire de la validation nominale (AC2, AC5)."""
    assert is_nominal_feature_allowed("natal") is True
    assert is_nominal_feature_allowed(LEGACY_NATAL_FEATURE) is False

    assert_nominal_feature_allowed("natal")
    with pytest.raises(ValueError) as exc:
        assert_nominal_feature_allowed(LEGACY_NATAL_FEATURE)
    assert "forbidden for nominal use" in str(exc.value)


def test_admin_models_normalization():
    """Test Story 66.23: Les modèles Pydantic admin REJETTENT les anciennes clés (AC2, AC5)."""
    # Valid canonical use case
    target = PromptAssemblyTarget(feature="natal", subfeature="interpretation")
    assert target.feature == "natal"
    assert target.subfeature == "interpretation"

    # Reject nominal legacy feature (AC2, AC5)
    with pytest.raises(ValueError) as exc:
        PromptAssemblyTarget(feature=LEGACY_NATAL_FEATURE, subfeature="interpretation")
    assert "forbidden for nominal use" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        PromptAssemblyConfig(
            feature=LEGACY_NATAL_FEATURE,
            subfeature="interpretation",
            feature_template_ref=uuid.uuid4(),
            execution_config={"model": "gpt-4o"},
        )
    assert "forbidden for nominal use" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        LlmExecutionProfileCreate(name="Test", model="gpt-4o", feature=LEGACY_NATAL_FEATURE)
    assert "forbidden for nominal use" in str(exc.value)


@pytest.mark.asyncio
async def test_gateway_normalization_in_execute_request():
    """Test Story 66.23: LLMGateway normalise en entrée (AC1, AC10)."""
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature=LEGACY_NATAL_FEATURE,
            subfeature="natal_interpretation",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(),
        request_id="test-req",
        trace_id="test-trace",
    )

    db = MagicMock(spec=Session)

    # On mock _resolve_plan pour voir ce qu'il reçoit
    with patch.object(gateway, "_resolve_plan", side_effect=ValueError("stop")) as mock_resolve:
        with pytest.raises(ValueError, match="stop"):
            await gateway.execute_request(request, db=db)

        # Le request passé à _resolve_plan doit être normalisé
        normalized_req = mock_resolve.call_args[0][0]
        assert normalized_req.user_input.feature == "natal"
        assert normalized_req.user_input.subfeature == "interpretation"


@pytest.mark.asyncio
async def test_assembly_registry_hardening():
    """Test Story 66.23: AssemblyRegistry REJETTE les clés legacy (AC11)."""
    db = MagicMock(spec=Session)
    registry = AssemblyRegistry(db)
    registry.invalidate_cache()

    # Reject nominal legacy feature (AC4, AC10)
    with pytest.raises(ValueError) as exc:
        await registry.get_active_config(
            feature=LEGACY_NATAL_FEATURE, subfeature="interpretation", plan="free"
        )
    assert "forbidden for nominal use" in str(exc.value)

    # BUT tolerate legacy subfeature with canonical feature (normalization only)
    with patch.object(registry, "_execute", new_callable=AsyncMock) as mock_exec:
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_exec.return_value = mock_res

        await registry.get_active_config(
            feature=NATAL_CANONICAL_FEATURE, subfeature="natal_interpretation", plan="free"
        )

        # Check that it normalized natal_interpretation -> interpretation
        first_stmt = mock_exec.call_args_list[0][0][0]
        compiled = first_stmt.compile()
        assert compiled.params["feature_1"] == NATAL_CANONICAL_FEATURE
        assert compiled.params["subfeature_1"] == "interpretation"


def test_execution_profile_registry_hardening():
    """Test Story 66.23: ExecutionProfileRegistry REJETTE les clés legacy (AC11)."""
    db = MagicMock(spec=Session)

    # Reject nominal legacy feature (AC4, AC10)
    with pytest.raises(ValueError) as exc:
        ExecutionProfileRegistry.get_active_profile(
            db, feature=LEGACY_NATAL_FEATURE, subfeature="interpretation"
        )
    assert "forbidden for nominal use" in str(exc.value)

    # Telerate legacy subfeature
    with patch.object(db, "execute") as mock_exec:
        mock_exec.return_value.scalar_one_or_none.return_value = None

        ExecutionProfileRegistry.get_active_profile(
            db, feature=NATAL_CANONICAL_FEATURE, subfeature="natal_interpretation"
        )

        first_stmt = mock_exec.call_args_list[0][0][0]
        compiled = first_stmt.compile()
        assert compiled.params["feature_1"] == NATAL_CANONICAL_FEATURE
        assert compiled.params["subfeature_1"] == "interpretation"
