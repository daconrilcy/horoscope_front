"""Shim de compatibilité : ``LLMGateway`` vit dans ``app.domain.llm.runtime.gateway``.

Les types de requête/réponse importés historiquement depuis ce module sont réexportés
depuis ``app.llm_orchestration.models`` (story 70-15).
"""

from app.domain.llm.configuration.assemblies import (
    assemble_developer_prompt,
    resolve_assembly,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    GatewayResult,
    LLMExecutionRequest,
)

__all__ = [
    "LLMGateway",
    "ExecutionContext",
    "ExecutionFlags",
    "ExecutionUserInput",
    "GatewayResult",
    "LLMExecutionRequest",
    "assemble_developer_prompt",
    "resolve_assembly",
]
