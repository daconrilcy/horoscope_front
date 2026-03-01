from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.infra.db.models.llm_persona import PersonaTone, PersonaVerbosity
from app.infra.db.models.llm_prompt import PromptStatus


class LlmUseCaseConfigBase(BaseModel):
    display_name: str
    description: str
    output_schema_id: Optional[str] = None
    persona_strategy: str = "optional"
    safety_profile: str = "astrology"
    fallback_use_case_key: Optional[str] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    allowed_persona_ids: List[str] = Field(default_factory=list)


class LlmUseCaseConfig(LlmUseCaseConfigBase):
    key: str
    active_prompt_version_id: Optional[uuid.UUID] = None
    fallback_use_case_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LlmOutputSchemaBase(BaseModel):
    name: str
    json_schema: dict
    version: int = 1


class LlmOutputSchema(LlmOutputSchemaBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LlmPersonaBase(BaseModel):
    name: str
    description: Optional[str] = None
    tone: PersonaTone = PersonaTone.DIRECT
    verbosity: PersonaVerbosity = PersonaVerbosity.MEDIUM
    style_markers: List[str] = Field(default_factory=list)
    boundaries: List[str] = Field(default_factory=list)
    allowed_topics: List[str] = Field(default_factory=list)
    disallowed_topics: List[str] = Field(default_factory=list)
    formatting: dict = Field(
        default_factory=lambda: {"sections": True, "bullets": False, "emojis": False}
    )
    enabled: bool = True


class LlmPersonaCreate(LlmPersonaBase):
    pass


class LlmPersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tone: Optional[PersonaTone] = None
    verbosity: Optional[PersonaVerbosity] = None
    style_markers: Optional[List[str]] = None
    boundaries: Optional[List[str]] = None
    allowed_topics: Optional[List[str]] = None
    disallowed_topics: Optional[List[str]] = None
    formatting: Optional[dict] = None
    enabled: Optional[bool] = None


class LlmPersona(LlmPersonaBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LlmPromptVersionBase(BaseModel):
    developer_prompt: str
    model: str
    temperature: float = 0.7
    max_output_tokens: int = 2048
    fallback_use_case_key: Optional[str] = None


class LlmPromptVersionCreate(LlmPromptVersionBase):
    pass


class LlmPromptVersionUpdate(BaseModel):
    developer_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    fallback_use_case_key: Optional[str] = None


class LlmPromptVersion(LlmPromptVersionBase):
    id: uuid.UUID
    use_case_key: str
    status: PromptStatus
    created_by: str
    created_at: datetime
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
