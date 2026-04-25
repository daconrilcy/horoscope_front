from __future__ import annotations

import atexit
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.llm_settings import ai_engine_settings
from app.infra.db import session as db_session_module

_TEST_DB_ROOT = Path(__file__).resolve().parents[2] / ".tmp-pytest"
_TEST_DB_ROOT.mkdir(parents=True, exist_ok=True)
_TEST_DB_PATH = _TEST_DB_ROOT / f"horoscope-pytest-db-{uuid.uuid4().hex}.sqlite3"


def _cleanup_test_db_file() -> None:
    try:
        _TEST_DB_PATH.unlink(missing_ok=True)
    except PermissionError:
        # Pytest can still hold a SQLite connection when the interpreter exits.
        pass


atexit.register(_cleanup_test_db_file)


def _build_test_engine():
    engine = create_engine(
        f"sqlite:///{_TEST_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _connection_record):  # type: ignore[misc]
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return engine


_TEST_ENGINE = _build_test_engine()
_TEST_SESSION_LOCAL = sessionmaker(
    bind=_TEST_ENGINE,
    autoflush=False,
    autocommit=False,
    future=True,
)
_ORIGINAL_ENGINE = db_session_module.engine
_ORIGINAL_SESSION_LOCAL = db_session_module.SessionLocal
_ORIGINAL_LOCAL_SCHEMA_READY = db_session_module._local_schema_ready

# Global redirection for the whole pytest process.
# Many legacy tests import `engine` / `SessionLocal` directly from app.infra.db.session
# at module import time, so this patch must happen before those modules are imported.
db_session_module.engine = _TEST_ENGINE
db_session_module.SessionLocal = _TEST_SESSION_LOCAL
db_session_module._local_schema_ready = False


def _estimate_tokens(text: str) -> int:
    """Approxime le nombre de tokens pour les doubles de tests LLM."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@pytest.fixture(scope="session", autouse=True)
def _restore_global_db_session_module_after_app_tests() -> None:
    try:
        yield
    finally:
        db_session_module.engine = _ORIGINAL_ENGINE
        db_session_module.SessionLocal = _ORIGINAL_SESSION_LOCAL
        db_session_module._local_schema_ready = _ORIGINAL_LOCAL_SCHEMA_READY
        _TEST_ENGINE.dispose()


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
