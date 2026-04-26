"""Canonical namespace for Admin LLM routers."""

from app.api.v1.routers.admin.llm.assemblies import router as assemblies_router
from app.api.v1.routers.admin.llm.consumption import router as consumption_router
from app.api.v1.routers.admin.llm.prompts import (
    ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER,
    ADMIN_MANUAL_EXECUTE_ROUTE_PATH,
)
from app.api.v1.routers.admin.llm.prompts import router as prompts_router
from app.api.v1.routers.admin.llm.releases import router as releases_router
from app.api.v1.routers.admin.llm.sample_payloads import router as sample_payloads_router

__all__ = [
    "ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER",
    "ADMIN_MANUAL_EXECUTE_ROUTE_PATH",
    "assemblies_router",
    "consumption_router",
    "prompts_router",
    "releases_router",
    "sample_payloads_router",
]
