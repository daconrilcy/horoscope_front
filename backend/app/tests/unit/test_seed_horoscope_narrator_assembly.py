from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.configuration.assembly_resolver import PLAN_RULES_REGISTRY
from app.domain.llm.prompting.narrator_contract import NARRATOR_OUTPUT_SCHEMA
from app.infra.db.models.llm.llm_assembly import (
    AssemblyComponentResolutionState,
    PromptAssemblyConfigModel,
)
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import PromptStatus
from app.ops.llm.bootstrap.seed_horoscope_narrator_assembly import (
    HOROSCOPE_DAILY_NARRATION_PROMPT,
    HOROSCOPE_DAILY_PLAN_RULES,
    _keep_latest_published_and_archive_rest,
    seed_horoscope_narrator_assembly,
)


@dataclass
class _FakePublishedRow:
    id: str
    published_at: datetime
    created_at: datetime
    status: PromptStatus = PromptStatus.PUBLISHED


def test_keep_latest_published_and_archive_rest_keeps_newest_row() -> None:
    db = MagicMock()
    oldest = _FakePublishedRow(
        id="old",
        created_at=datetime.now(UTC) - timedelta(days=2),
        published_at=datetime.now(UTC) - timedelta(days=2),
    )
    newest = _FakePublishedRow(
        id="new",
        created_at=datetime.now(UTC) - timedelta(days=1),
        published_at=datetime.now(UTC) - timedelta(days=1),
    )

    winner = _keep_latest_published_and_archive_rest(
        db,
        [oldest, newest],
        label="prompt:horoscope_daily",
    )

    assert winner is newest
    assert newest.status == PromptStatus.PUBLISHED
    assert oldest.status == PromptStatus.ARCHIVED
    db.flush.assert_called_once()


def test_narrator_output_schema_is_strictly_openai_compatible() -> None:
    time_windows = NARRATOR_OUTPUT_SCHEMA["properties"]["time_window_narratives"]
    assert time_windows["required"] == ["nuit", "matin", "apres_midi", "soiree"]
    assert set(time_windows["properties"]) == {"nuit", "matin", "apres_midi", "soiree"}
    assert time_windows["additionalProperties"] is False

    daily_advice = NARRATOR_OUTPUT_SCHEMA["properties"]["daily_advice"]
    assert daily_advice["type"] == "object"
    assert daily_advice["required"] == ["advice", "emphasis"]

    assert NARRATOR_OUTPUT_SCHEMA["properties"]["main_turning_point_narrative"]["type"] == "string"


def test_horoscope_daily_narration_prompt_owns_durable_instructions() -> None:
    assert "Génère uniquement du JSON valide" in HOROSCOPE_DAILY_NARRATION_PROMPT
    assert "Profil védique" in HOROSCOPE_DAILY_NARRATION_PROMPT
    assert "Ne produis pas de phrases creuses" in HOROSCOPE_DAILY_NARRATION_PROMPT
    assert "time_window_narratives" in HOROSCOPE_DAILY_NARRATION_PROMPT


def test_horoscope_daily_plan_rules_own_daily_synthesis_lengths() -> None:
    free_rule = PLAN_RULES_REGISTRY[HOROSCOPE_DAILY_PLAN_RULES["free"]]
    premium_rule = PLAN_RULES_REGISTRY[HOROSCOPE_DAILY_PLAN_RULES["premium"]]

    assert free_rule.instruction is not None
    assert "strictement 7 à 8 phrases complètes" in free_rule.instruction
    assert "450 à 700 caractères" in free_rule.instruction
    assert premium_rule.instruction is not None
    assert "strictement 10 à 12 phrases complètes" in premium_rule.instruction


def test_seed_wires_horoscope_daily_assemblies_to_narration_plan_rules(
    db_session: Session,
) -> None:
    db_session.add(
        LlmPersonaModel(
            code="daily-seed-test",
            name="Daily seed test",
            description="Persona minimal pour valider le seed gouverné.",
            enabled=True,
        )
    )
    db_session.commit()

    seed_horoscope_narrator_assembly(db_session)

    prompt = db_session.scalar(
        select(PromptAssemblyConfigModel)
        .where(PromptAssemblyConfigModel.feature == "horoscope_daily")
        .where(PromptAssemblyConfigModel.subfeature == "narration")
        .where(PromptAssemblyConfigModel.plan == "free")
        .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
    ).feature_template.developer_prompt
    assert "Ne produis pas de phrases creuses" in prompt

    for plan, plan_rule in HOROSCOPE_DAILY_PLAN_RULES.items():
        assembly = db_session.scalar(
            select(PromptAssemblyConfigModel)
            .where(PromptAssemblyConfigModel.feature == "horoscope_daily")
            .where(PromptAssemblyConfigModel.subfeature == "narration")
            .where(PromptAssemblyConfigModel.plan == plan)
            .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
        )

        assert assembly is not None
        assert assembly.plan_rules_ref == plan_rule
        assert assembly.plan_rules_state == AssemblyComponentResolutionState.ENABLED.value
