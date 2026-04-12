import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.llm_orchestration.services.config_coherence_validator import (
    ConfigCoherenceValidator,
)
from app.llm_orchestration.services.execution_profile_registry import (
    ExecutionProfileRegistry,
)


@pytest.mark.asyncio
async def test_validate_assembly_accepts_waterfall_profile_without_explicit_ref(db):
    ExecutionProfileRegistry.invalidate_cache()

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="chat",
        developer_prompt="{{last_user_msg}}",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test",
    )
    use_case = LlmUseCaseConfigModel(key="chat", display_name="Chat", description="test")
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Chat Waterfall",
        feature="chat",
        subfeature="astrologer",
        provider="openai",
        model="gpt-4o-mini",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    config = PromptAssemblyConfigModel(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        feature_template_ref=prompt.id,
        execution_config={"model": "gpt-4o-mini", "max_output_tokens": 512},
        status=PromptStatus.DRAFT,
        created_by="test",
    )

    db.add_all([use_case, prompt, profile, config])
    db.commit()
    db.refresh(config)

    validator = ConfigCoherenceValidator(db)
    result = await validator.validate_assembly(config)

    assert result.is_valid is True
    assert result.errors == []


@pytest.mark.asyncio
async def test_validate_assembly_accepts_uuid_output_contract_ref(db):
    ExecutionProfileRegistry.invalidate_cache()

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="chat",
        developer_prompt="{{last_user_msg}}",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test",
    )
    use_case = LlmUseCaseConfigModel(key="chat", display_name="Chat", description="test")
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Chat Explicit",
        feature="chat",
        subfeature="astrologer",
        provider="openai",
        model="gpt-4o-mini",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    schema = LlmOutputSchemaModel(
        id=uuid.uuid4(),
        name="ChatResponse_v1",
        json_schema={"type": "object"},
    )
    config = PromptAssemblyConfigModel(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        feature_template_ref=prompt.id,
        execution_profile_ref=profile.id,
        execution_config={"model": "gpt-4o-mini", "max_output_tokens": 512},
        output_contract_ref=str(schema.id),
        status=PromptStatus.DRAFT,
        created_by="test",
    )

    db.add_all([use_case, prompt, profile, schema, config])
    db.commit()
    db.refresh(config)

    validator = ConfigCoherenceValidator(db)
    result = await validator.validate_assembly(config)

    assert result.is_valid is True
    assert result.errors == []


@pytest.mark.asyncio
async def test_scan_active_configurations_ignores_older_published_versions(monkeypatch):
    validator = ConfigCoherenceValidator(SimpleNamespace())

    older = SimpleNamespace(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        published_at=datetime.now(timezone.utc) - timedelta(days=1),
        created_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    newer = SimpleNamespace(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        published_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    class _Scalars:
        def all(self):
            return [older, newer]

    class _Result:
        def scalars(self):
            return _Scalars()

    validated = []

    async def _fake_execute(_stmt):
        return _Result()

    async def _fake_validate(config):
        validated.append(config)
        return SimpleNamespace(is_valid=True, errors=[])

    monkeypatch.setattr(validator, "_execute", _fake_execute)
    monkeypatch.setattr(validator, "validate_assembly", _fake_validate)

    results = await validator.scan_active_configurations()

    assert results == []
    assert validated == [newer]
