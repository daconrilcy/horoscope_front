"""Canonical assembly resolution/admin entrypoints."""

from app.domain.llm.configuration.assembly_admin_service import AssemblyAdminService
from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.configuration.assembly_resolver import (
    assemble_developer_prompt,
    resolve_assembly,
)

__all__ = [
    "AssemblyAdminService",
    "AssemblyRegistry",
    "assemble_developer_prompt",
    "resolve_assembly",
]
