from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.llm_orchestration.admin_models import PromptAssemblyTarget
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
    """Test Story 66.23: Les modèles Pydantic admin normalisent automatiquement (AC2, AC10)."""
    target = PromptAssemblyTarget(feature=LEGACY_NATAL_FEATURE, subfeature="natal_interpretation")
    assert target.feature == "natal"
    assert target.subfeature == "interpretation"
    
    with pytest.raises(ValueError):
        # Even after normalization, if we somehow passed something that is still not allowed
        # (Though normalize_feature converts it to 'natal' which is allowed)
        # We test that assert_nominal_feature_allowed is called.
        # Here we mock normalize_feature to return the legacy one to trigger error
        with patch("app.llm_orchestration.admin_models.normalize_feature") as mock_norm:
            mock_norm.return_value = LEGACY_NATAL_FEATURE
            PromptAssemblyTarget(feature="any")

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
async def test_assembly_registry_normalization():
    """Test Story 66.23: AssemblyRegistry normalise ses lookups (AC11)."""
    db = MagicMock(spec=Session)
    registry = AssemblyRegistry(db)
    
    # On mock _execute pour renvoyer un résultat vide mais sans crasher
    with patch.object(registry, "_execute", new_callable=AsyncMock) as mock_exec:
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_exec.return_value = mock_res
        
        await registry.get_active_config(
            feature=LEGACY_NATAL_FEATURE, subfeature="natal_interpretation", plan="free"
        )
        
        # On vérifie les appels à _execute
        # Il y a 3 patterns de recherche dans get_active_config
        assert mock_exec.call_count >= 1
        first_stmt = mock_exec.call_args_list[0][0][0]
        
        # Pour vérifier le contenu du statement SQL, 
        # on regarde les paramètres liés ou le SQL compilé
        compiled = first_stmt.compile()
        assert compiled.params["feature_1"] == "natal"
        assert compiled.params["subfeature_1"] == "interpretation"

def test_execution_profile_registry_normalization():
    """Test Story 66.23: ExecutionProfileRegistry normalise ses lookups (AC11)."""
    db = MagicMock(spec=Session)
    
    with patch.object(db, "execute") as mock_exec:
        mock_exec.return_value.scalar_one_or_none.return_value = None
        
        ExecutionProfileRegistry.get_active_profile(
            db, feature=LEGACY_NATAL_FEATURE, subfeature="natal_interpretation"
        )
        
        # On vérifie le premier appel
        assert mock_exec.call_count >= 1
        first_stmt = mock_exec.call_args_list[0][0][0]
        compiled = first_stmt.compile()
        assert compiled.params["feature_1"] == "natal"
        assert compiled.params["subfeature_1"] == "interpretation"
