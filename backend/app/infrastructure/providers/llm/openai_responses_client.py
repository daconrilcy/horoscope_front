from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
)
from app.llm_orchestration.models import (
    GatewayMeta,
    GatewayResult,
    UsageInfo,
    is_reasoning_model,
)

logger = logging.getLogger(__name__)


def _coerce_headers(raw_headers: Any) -> Dict[str, str]:
    """Best-effort conversion for SDK/test header objects."""
    if raw_headers is None:
        return {}
    if isinstance(raw_headers, dict):
        return {str(key): str(value) for key, value in raw_headers.items()}
    items = getattr(raw_headers, "items", None)
    if callable(items):
        try:
            return {str(key): str(value) for key, value in items()}
        except Exception:
            return {}
    return {}


class ResponsesClient:
    """
    Wrapper for the OpenAI Responses API (POST /v1/responses).
    Focuses on request shaping and transport.
    Explicitly disables SDK-level retries to allow application-level control.
    """

    def __init__(self) -> None:
        self._async_client: "AsyncOpenAI | None" = None

    def _ensure_configured(self) -> None:
        if not ai_engine_settings.is_openai_configured:
            raise ProviderNotConfiguredError("openai")

    async def _get_async_client(self) -> "AsyncOpenAI":
        if self._async_client is None:
            # Disable SDK-level retries (default is 2) to keep a single source of truth.
            self._async_client = AsyncOpenAI(
                api_key=ai_engine_settings.openai_api_key,
                max_retries=0,
            )
        return self._async_client

    @staticmethod
    def _to_typed_content_blocks(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert simple role/content messages to typed content blocks required by GPT-5.
        Format:
        - user/system/developer -> {"type": "input_text", "text": "..."}
        - assistant -> {"type": "output_text", "text": "..."}

        Idempotent: if content is already a list (typed blocks), returns as-is.
        Preserves all extra fields present on the message dict.
        """
        result = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                block_type = "output_text" if msg.get("role") == "assistant" else "input_text"
                result.append({**msg, "content": [{"type": block_type, "text": content}]})
            else:
                result.append(msg)
        return result

    async def execute(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_output_tokens: int = 1000,
        timeout_seconds: int = 30,
        request_id: str = "",
        trace_id: str = "",
        use_case: str = "",
        reasoning_effort: Optional[str] = None,
        verbosity: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> tuple[GatewayResult, Dict[str, str]]:
        """
        Execute a single request via the OpenAI Responses API.
        No retries here - retries are managed by ProviderRuntimeManager.
        Returns (GatewayResult, response_headers).
        """
        self._ensure_configured()
        client = await self._get_async_client()

        start_time = time.monotonic()

        # 1. GPT-5 requires typed content blocks.
        is_gpt5 = model == "gpt-5" or model.startswith("gpt-5-")
        effective_input = self._to_typed_content_blocks(messages) if is_gpt5 else messages

        # 2. Base parameters
        params: Dict[str, Any] = {
            "model": model,
            "input": effective_input,  # type: ignore
            "max_output_tokens": max_output_tokens,
            "timeout": timeout_seconds,
        }

        # 3. Reasoning and Temperature
        is_reasoning = is_reasoning_model(model)
        if is_reasoning:
            if reasoning_effort:
                params["reasoning"] = {"effort": reasoning_effort}
        else:
            params["temperature"] = temperature

        text_config: Dict[str, Any] = {}
        if is_gpt5 and verbosity:
            text_config["verbosity"] = verbosity

        if response_format:
            fmt = dict(response_format)
            if fmt.get("type") == "json_schema" and "json_schema" in fmt:
                nested = fmt.pop("json_schema")
                fmt.update(nested)

                def _enforce_strict(s: dict):
                    if isinstance(s, dict):
                        if s.get("type") == "object":
                            s["additionalProperties"] = False
                        for k, v in s.items():
                            if isinstance(v, (dict, list)):
                                _enforce_strict(v)
                    elif isinstance(s, list):
                        for item in s:
                            if isinstance(item, (dict, list)):
                                _enforce_strict(item)

                if fmt.get("strict") is True and "schema" in fmt:
                    _enforce_strict(fmt["schema"])

            text_config["format"] = fmt

        if text_config:
            params["text"] = text_config

        # Add tracing headers
        headers: Dict[str, str] = {}
        if request_id:
            headers["x-request-id"] = request_id
        if trace_id:
            headers["x-trace-id"] = trace_id
        if use_case:
            headers["x-use-case"] = use_case
        if headers:
            params["extra_headers"] = headers

        # Execute with raw response access to get headers (AC5)
        try:
            raw_api_response = await client.with_raw_response.responses.create(**params)
            response = raw_api_response.parse()
            resp_headers = _coerce_headers(getattr(raw_api_response, "headers", None))
        except Exception as err:
            # Story 66.33 Finding High: Extract headers from exception if available
            resp_headers = {}
            if hasattr(err, "response") and hasattr(err.response, "headers"):
                try:
                    resp_headers = _coerce_headers(err.response.headers)
                except Exception:
                    pass
            # Re-wrap error if it carries headers to propagate them
            setattr(err, "_provider_headers", resp_headers)
            if hasattr(err, "code"):
                setattr(err, "_provider_error_code", str(getattr(err, "code")))
            raise err

        latency_ms = int((time.monotonic() - start_time) * 1000)

        output_text = response.output_text if hasattr(response, "output_text") else ""

        usage = UsageInfo(
            input_tokens=response.usage.input_tokens if response.usage else 0,
            output_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            estimated_cost_usd=0.0,
        )

        structured_output: Any = None
        if response_format is not None and output_text:
            try:
                structured_output = json.loads(output_text)
            except (json.JSONDecodeError, ValueError):
                pass

        result = GatewayResult(
            use_case=use_case,
            request_id=request_id,
            trace_id=trace_id,
            raw_output=output_text,
            structured_output=structured_output,
            usage=usage,
            meta=GatewayMeta(
                latency_ms=latency_ms,
                model=response.model,
                cached=False,
            ),
        )
        return result, resp_headers

    # Removed _execute_with_retry as it's now handled by ProviderRuntimeManager
