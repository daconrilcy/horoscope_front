"""Transitional canonical entrypoint for Admin LLM prompt routes."""

from app.api.v1.routers.admin_llm import (
    ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER,
    ADMIN_MANUAL_EXECUTE_ROUTE_PATH,
    router,
)

__all__ = [
    "ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER",
    "ADMIN_MANUAL_EXECUTE_ROUTE_PATH",
    "router",
]
