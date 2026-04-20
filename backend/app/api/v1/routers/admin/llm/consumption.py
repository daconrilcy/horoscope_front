"""Transitional canonical entrypoint for Admin LLM consumption routes."""

from app.api.v1.routers.admin_llm_consumption import router

__all__ = ["router"]
