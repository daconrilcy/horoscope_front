"""Canonical observability router for Admin LLM endpoints."""

from fastapi import APIRouter

from app.api.v1.routers.admin.llm.prompts import (
    LlmCallLogListResponse,
    LlmDashboardResponse,
    get_dashboard,
    list_call_logs,
    purge_logs,
    replay_request,
)

router = APIRouter(prefix="/v1/admin/llm", tags=["admin-llm"])
router.add_api_route(
    "/call-logs", list_call_logs, methods=["GET"], response_model=LlmCallLogListResponse
)
router.add_api_route(
    "/dashboard", get_dashboard, methods=["GET"], response_model=LlmDashboardResponse
)
router.add_api_route("/replay", replay_request, methods=["POST"], response_model=dict)
router.add_api_route("/call-logs/purge", purge_logs, methods=["POST"], response_model=dict)

__all__ = ["router"]
