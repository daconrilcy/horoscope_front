"""Canonical assembly resolution/admin entrypoints."""

from app.llm_orchestration.services.assembly_admin_service import AssemblyAdminService
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import (
    assemble_developer_prompt,
    resolve_assembly,
)

__all__ = [
    "AssemblyAdminService",
    "AssemblyRegistry",
    "assemble_developer_prompt",
    "resolve_assembly",
]
