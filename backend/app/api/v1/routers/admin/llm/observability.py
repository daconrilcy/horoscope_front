"""Transitional canonical entrypoint for Admin LLM observability endpoints.

Historically, observability endpoints are hosted in the prompt catalog router.
This module gives them an explicit namespace without behavior change.
"""

from app.api.v1.routers.admin_llm import router

__all__ = ["router"]
