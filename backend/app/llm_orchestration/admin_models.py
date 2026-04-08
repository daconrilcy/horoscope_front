from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.models import is_reasoning_model


class PromptAssemblyTarget(BaseModel):
    """Target identifying a unique assembly configuration."""

    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"


class ExecutionConfigAdmin(BaseModel):
    """Execution parameters for an assembly config."""

    model: str
    temperature: Optional[float] = 0.7
    max_output_tokens: int = 2048
    timeout_seconds: int = 30
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None
    verbosity: Optional[Literal["verbose", "normal", "concise"]] = None
    fallback_model: Optional[str] = None

    @model_validator(mode="after")
    def validate_provider_params(self) -> "ExecutionConfigAdmin":
        is_reasoning = is_reasoning_model(self.model)
        
        if is_reasoning:
            if self.temperature is not None:
                raise ValueError("Temperature must be None for reasoning models")
        else:
            if self.reasoning_effort is not None:
                raise ValueError("Reasoning effort is only supported for reasoning models")
                
        if self.fallback_model:
            is_fallback_reasoning = is_reasoning_model(self.fallback_model)
            if is_fallback_reasoning != is_reasoning:
                raise ValueError("Fallback model must be from the same family (reasoning vs standard)")
                
        return self


class PromptAssemblyConfig(BaseModel):
    """Pydantic model for reading/writing assembly configurations."""

    id: Optional[uuid.UUID] = None
    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"

    feature_template_ref: uuid.UUID
    subfeature_template_ref: Optional[uuid.UUID] = None
    persona_ref: Optional[uuid.UUID] = None
    plan_rules_ref: Optional[str] = None

    execution_config: ExecutionConfigAdmin
    output_contract_ref: Optional[str] = None

    feature_enabled: bool = True
    subfeature_enabled: bool = True
    persona_enabled: bool = True
    plan_rules_enabled: bool = True

    status: PromptStatus = PromptStatus.DRAFT
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ResolvedAssembly(BaseModel):
    """Intermediate artifact between admin config and execution plan."""

    target: PromptAssemblyTarget
    
    feature_template_id: uuid.UUID
    feature_template_prompt: str
    
    subfeature_template_id: Optional[uuid.UUID] = None
    subfeature_template_prompt: Optional[str] = None
    
    template_source: Literal["explicit_subfeature", "fallback_default"]
    
    persona_ref: Optional[uuid.UUID] = None
    persona_block: Optional[str] = None
    
    plan_rules_content: Optional[str] = None
    
    execution_config: ExecutionConfigAdmin
    output_contract_ref: Optional[str] = None
    policy_layer_content: str


class PlaceholderInfo(BaseModel):
    """Info about an injectable variable in a prompt."""

    name: str
    type: str
    origin: str
    example: str


class DraftPublishResponse(BaseModel):
    """Result of a publish operation."""

    assembly_id: uuid.UUID
    status: str
    published_at: datetime
    archived_count: int


class PromptAssemblyPreview(BaseModel):
    """Full preview of a rendered assembly config."""

    target: PromptAssemblyTarget
    
    # Prompt blocks
    feature_block: str
    subfeature_block: Optional[str] = None
    persona_block: Optional[str] = None
    plan_rules_block: Optional[str] = None
    
    template_source: str
    
    # Final rendered prompt (concatenated blocks + rendered variables)
    rendered_developer_prompt: str
    
    # Separated layers
    hard_policy_block: str  # Immutable layer
    output_contract_ref: Optional[str] = None
    
    # Available variables for the feature
    available_variables: List[PlaceholderInfo]
    
    # Execution parameters
    resolved_execution_config: ExecutionConfigAdmin
    
    draft_preview: bool = True
