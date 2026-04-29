import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.domain.llm.configuration.admin_models import (
    PromptAssemblyConfig,
)
from app.domain.llm.configuration.assembly_admin_service import AssemblyAdminService
from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.configuration.execution_profile_registry import ExecutionProfileRegistry
from app.domain.llm.governance.feature_taxonomy import (
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
)
from app.infra.db.models.llm.llm_prompt import PromptStatus


@pytest.mark.asyncio
async def test_assembly_registry_hardening(monkeypatch):
    """Test Story 66.23: AssemblyRegistry REJETTE les clés legacy (AC11)."""
    db = MagicMock(spec=Session)
    registry = AssemblyRegistry(db)
    registry.invalidate_cache()

    # Mock ReleaseService to avoid real DB calls or snapshot logic
    from app.ops.llm.release_service import ReleaseService

    async def _fake_get_active_id(_db):
        return None

    monkeypatch.setattr(ReleaseService, "get_active_release_id", _fake_get_active_id)

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
        target_stmt = mock_exec.call_args_list[1][0][0]
        compiled = str(target_stmt.compile(compile_kwargs={"literal_binds": True}))
        assert NATAL_CANONICAL_FEATURE in compiled
        assert "interpretation" in compiled


def test_execution_profile_registry_hardening(monkeypatch):
    """Test Story 66.23: ExecutionProfileRegistry REJETTE les clés legacy (AC11)."""
    db = MagicMock(spec=Session)

    # Mock ReleaseService to avoid real DB calls
    from app.ops.llm.release_service import ReleaseService

    async def _fake_get_active_id(_db):
        return None

    monkeypatch.setattr(ReleaseService, "get_active_release_id", _fake_get_active_id)

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

        target_stmt = mock_exec.call_args_list[1][0][0]
        compiled = str(target_stmt.compile(compile_kwargs={"literal_binds": True}))
        assert NATAL_CANONICAL_FEATURE in compiled
        assert "interpretation" in compiled


@pytest.mark.asyncio
async def test_assembly_admin_service_hardening():
    """Test Story 66.23: AssemblyAdminService REJETTE les clés legacy sur create (AC11)."""
    db = MagicMock(spec=Session)
    service = AssemblyAdminService(db)

    # Rejette feature legacy
    try:
        config_in = PromptAssemblyConfig(
            feature=LEGACY_NATAL_FEATURE,
            subfeature="interpretation",
            plan="free",
            locale="fr-FR",
            feature_template_ref=uuid.uuid4(),
            execution_config={"model": "gpt-4o"},
            interaction_mode="structured",
            user_question_policy="none",
            status=PromptStatus.DRAFT,
            created_by="admin@test.com",
        )
    except Exception as e:
        # Pydantic validation error expected here if the model blocks it directly
        assert "forbidden for nominal use" in str(e)
        return

    with pytest.raises(ValueError) as exc:
        await service.create_draft(config_in, "admin@test.com")
    assert "forbidden for nominal use" in str(exc.value)

    # Normalise subfeature legacy
    config_sub_legacy = PromptAssemblyConfig(
        feature=NATAL_CANONICAL_FEATURE,
        subfeature="natal_interpretation",
        plan="free",
        locale="fr-FR",
        feature_template_ref=uuid.uuid4(),
        execution_config={"model": "gpt-4o"},
        interaction_mode="structured",
        user_question_policy="none",
        status=PromptStatus.DRAFT,
        created_by="admin@test.com",
    )

    # Mock the internal DB check for template existence
    with patch("app.domain.llm.configuration.assembly_admin_service.db_resolve_prompt_prompt"):
        with patch.object(db, "add") as mock_add:
            await service.create_draft(config_sub_legacy, "admin@test.com")
            added_model = mock_add.call_args[0][0]
            assert added_model.subfeature == "interpretation"


@pytest.mark.asyncio
async def test_execution_profile_admin_hardening():
    """Test Story 66.23: ExecutionProfile validation REJETTE les clés legacy (AC11)."""
    # Ici on teste via le validateur SQLAlchemy injecté dans le modèle
    from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel

    prof = LlmExecutionProfileModel(
        name="Test",
        feature=LEGACY_NATAL_FEATURE,
        model="m",
        provider="openai",  # Must have provider to publish
        created_by="t",
    )

    with pytest.raises(ValueError) as exc:
        prof.status = PromptStatus.PUBLISHED

    assert "forbidden for nominal use" in str(exc.value)
