"""Transitional canonical entrypoint for Admin LLM release routes."""

from app.api.v1.routers.admin_llm_release import router

__all__ = ["router"]
