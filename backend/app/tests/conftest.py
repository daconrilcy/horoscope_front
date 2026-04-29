"""Configuration pytest globale pour isoler les tests `app/tests`."""

from __future__ import annotations

import os

import pytest

from app.tests.helpers.db_session import (
    app_test_database_url,
    dispose_app_test_engine,
    override_app_test_db_session,
)

os.environ["DATABASE_URL"] = app_test_database_url()

from app.core.llm_settings import ai_engine_settings
from app.infra.db.session import get_db_session
from app.main import app


def _estimate_tokens(text: str) -> int:
    """Approxime le nombre de tokens pour les doubles de tests LLM."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@pytest.fixture(scope="session", autouse=True)
def _dispose_app_test_db_after_app_tests() -> None:
    try:
        yield
    finally:
        dispose_app_test_engine()


@pytest.fixture(autouse=True)
def _install_app_test_db_dependency_override() -> None:
    """Route explicitement les dépendances FastAPI vers la DB de test canonique."""
    app.dependency_overrides[get_db_session] = override_app_test_db_session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture(autouse=True)
def _install_llm_adapter_test_generators(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permet aux tests d'injecter des doubles explicites sans code de test en production."""
    from app.domain.llm.runtime.adapter import AIEngineAdapter
    from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
    from app.tests.helpers.llm_adapter_stub import (
        get_test_chat_generator,
        get_test_guidance_generator,
        reset_test_generators,
    )

    original_chat = AIEngineAdapter.generate_chat_reply
    original_guidance = AIEngineAdapter.generate_guidance
    original_openai_api_key = ai_engine_settings.openai_api_key
    reset_test_generators()

    async def _chat_wrapper(*args, **kwargs):
        messages = kwargs.get("messages", args[0] if len(args) > 0 else [])
        context = kwargs.get("context", args[1] if len(args) > 1 else {})
        user_id = kwargs.get("user_id", args[2] if len(args) > 2 else 0)
        request_id = kwargs.get("request_id", args[3] if len(args) > 3 else "test-request")
        trace_id = kwargs.get("trace_id", args[4] if len(args) > 4 else "test-trace")
        locale = kwargs.get("locale", args[5] if len(args) > 5 else "fr-FR")
        generator = get_test_chat_generator()
        if generator is None:
            try:
                return await original_chat(*args, **kwargs)
            except Exception as error:
                if ai_engine_settings.openai_api_key:
                    raise
                error_message = str(error).lower()
                if "provider" not in error_message and "unavailable" not in error_message:
                    raise
                raw_output = "Reponse test hors provider."
                return GatewayResult(
                    use_case="chat_astrologer",
                    request_id=str(request_id),
                    trace_id=str(trace_id),
                    raw_output=raw_output,
                    usage=UsageInfo(
                        input_tokens=_estimate_tokens(" ".join(m["content"] for m in messages)),
                        output_tokens=_estimate_tokens(raw_output),
                    ),
                    meta=GatewayMeta(latency_ms=0, model="test-model"),
                )

        result = await generator(messages, context, user_id, request_id, trace_id, locale)
        if isinstance(result, GatewayResult):
            return result
        raw_output = str(result)
        return GatewayResult(
            use_case="chat_astrologer",
            request_id=str(request_id),
            trace_id=str(trace_id),
            raw_output=raw_output,
            usage=UsageInfo(
                input_tokens=_estimate_tokens(" ".join(m["content"] for m in messages)),
                output_tokens=_estimate_tokens(raw_output),
            ),
            meta=GatewayMeta(latency_ms=0, model="test-model"),
        )

    async def _guidance_wrapper(*args, **kwargs):
        use_case = kwargs.get("use_case", args[0] if len(args) > 0 else "guidance_daily")
        context = kwargs.get("context", args[1] if len(args) > 1 else {})
        user_id = kwargs.get("user_id", args[2] if len(args) > 2 else 0)
        request_id = kwargs.get("request_id", args[3] if len(args) > 3 else "test-request")
        trace_id = kwargs.get("trace_id", args[4] if len(args) > 4 else "test-trace")
        locale = kwargs.get("locale", args[5] if len(args) > 5 else "fr-FR")
        generator = get_test_guidance_generator()
        if generator is None:
            try:
                return await original_guidance(*args, **kwargs)
            except Exception as error:
                if ai_engine_settings.openai_api_key:
                    raise
                error_message = str(error).lower()
                if "provider" not in error_message and "unavailable" not in error_message:
                    raise
                raw_output = f"Guidance test hors provider pour {use_case}."
                return GatewayResult(
                    use_case=str(use_case),
                    request_id=str(request_id),
                    trace_id=str(trace_id),
                    raw_output=raw_output,
                    usage=UsageInfo(
                        input_tokens=_estimate_tokens(
                            " ".join(str(value) for value in context.values() if value)
                        ),
                        output_tokens=_estimate_tokens(raw_output),
                    ),
                    meta=GatewayMeta(latency_ms=0, model="test-model"),
                )

        result = await generator(use_case, context, user_id, request_id, trace_id, locale)
        if isinstance(result, GatewayResult):
            return result
        raw_output = str(result)
        return GatewayResult(
            use_case=str(use_case),
            request_id=str(request_id),
            trace_id=str(trace_id),
            raw_output=raw_output,
            usage=UsageInfo(
                input_tokens=_estimate_tokens(" ".join(str(v) for v in context.values() if v)),
                output_tokens=_estimate_tokens(raw_output),
            ),
            meta=GatewayMeta(latency_ms=0, model="test-model"),
        )

    monkeypatch.setattr(AIEngineAdapter, "generate_chat_reply", staticmethod(_chat_wrapper))
    monkeypatch.setattr(AIEngineAdapter, "generate_guidance", staticmethod(_guidance_wrapper))
    yield
    ai_engine_settings.openai_api_key = original_openai_api_key
    reset_test_generators()
