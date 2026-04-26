"""Construction et audit de l'exécution manuelle LLM admin."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.api.v1.constants import ADMIN_MANUAL_LLM_EXECUTE_SURFACE
from app.api.v1.schemas.routers.admin.llm.prompts import (
    AdminCatalogManualExecuteResponseData,
    AdminResolvedAssemblyView,
)
from app.core.sensitive_data import Sink, sanitize_payload
from app.domain.llm.runtime.contracts import GatewayResult
from app.services.llm_generation.anonymization_service import (
    LLMAnonymizationError,
    anonymize_text,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)


def _json_pretty_admin(value: Any) -> str:
    """Produit une représentation JSON lisible pour les opérateurs admin."""
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _build_admin_developer_message_bundle(
    *,
    main_prompt: str,
    persona_block: str | None,
    include_persona: bool,
) -> str:
    """Assemble les messages développeur visibles dans la prévisualisation admin."""
    messages: list[str] = [f"[DEVELOPER MESSAGE 1 / main]\n{main_prompt}"]
    if include_persona and persona_block:
        messages.append(f"[DEVELOPER MESSAGE 2 / persona overlay]\n{persona_block}")
    return "\n\n".join(messages)


def _anonymize_for_admin_manual_execute(text: str, *, field: str) -> str:
    """Ne pas faire échouer la réponse opérateur si l'anonymisation est indisponible."""
    try:
        return anonymize_text(text)
    except LLMAnonymizationError as exc:
        logger.warning("admin manual execute: anonymization skipped for %s: %s", field, exc)
        return "[anonymization_unavailable]"


def _build_admin_manual_execute_response_payload(
    *,
    built: AdminResolvedAssemblyView,
    result: GatewayResult,
    manifest_entry_id: str,
    sample_payload_id: uuid.UUID,
    request_id: str,
    trace_id: str,
    use_case_key: str,
) -> AdminCatalogManualExecuteResponseData:
    """Construit le payload opérateur: prompt, paramètres runtime, sorties et redaction."""
    rendered = built.transformation_pipeline.rendered_prompt
    prompt_sent = _anonymize_for_admin_manual_execute(
        rendered if rendered else "", field="prompt_sent"
    )

    structured = result.structured_output
    structured_sanitized: dict[str, Any] | None = None
    if isinstance(structured, dict):
        structured_sanitized = sanitize_payload(structured, Sink.ADMIN_API)
    parseable = structured_sanitized is not None

    meta = result.meta
    runtime_params = sanitize_payload(
        {
            "translated_provider_params": meta.translated_provider_params or {},
            "reasoning_profile": meta.reasoning_profile,
            "verbosity_profile": meta.verbosity_profile,
            "output_mode": meta.output_mode,
            "tool_mode": meta.tool_mode,
            "max_output_tokens_source": meta.max_output_tokens_source,
            "model_override_active": meta.model_override_active,
            "prompt_version_id": meta.prompt_version_id,
            "output_schema_id": meta.output_schema_id,
            "schema_version": meta.schema_version,
        },
        Sink.ADMIN_API,
    )

    raw_out = _anonymize_for_admin_manual_execute(result.raw_output or "", field="raw_output")
    val_errors: list[str] | None = None
    if meta.validation_errors:
        val_errors = [
            _anonymize_for_admin_manual_execute(line, field="meta_validation_error")
            for line in meta.validation_errors
        ]

    return AdminCatalogManualExecuteResponseData(
        manifest_entry_id=manifest_entry_id,
        sample_payload_id=str(sample_payload_id),
        use_case_key=use_case_key,
        provider=meta.provider or "openai",
        model=meta.model,
        request_id=request_id,
        trace_id=trace_id,
        gateway_request_id=result.request_id,
        prompt_sent=prompt_sent,
        resolved_runtime_parameters=runtime_params,
        raw_output=raw_out,
        structured_output=structured_sanitized,
        structured_output_parseable=parseable,
        validation_status=meta.validation_status,
        execution_path=meta.execution_path,
        meta_validation_errors=val_errors,
        latency_ms=meta.latency_ms,
        admin_manual_execution=True,
        usage_input_tokens=result.usage.input_tokens,
        usage_output_tokens=result.usage.output_tokens,
    )


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: Any,
) -> None:
    """Enregistre un événement d'audit admin avec détails normalisés."""
    from app.domain.audit.safe_details import to_safe_details

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            status=status,
            details=to_safe_details(details),
        ),
    )


def _record_admin_manual_execution_audit(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    manifest_entry_id: str,
    sample_payload_id: uuid.UUID,
    status: Literal["success", "failed"],
    details: dict[str, Any],
) -> None:
    """Trace l'exécution manuelle d'un sample LLM depuis le catalogue admin."""
    _record_audit_event(
        db,
        request_id=request_id,
        actor=actor,
        action="llm_catalog_execute_sample",
        target_type="llm_manifest_entry",
        target_id=manifest_entry_id,
        status=status,
        details={
            "execution_surface": ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
            "manifest_entry_id": manifest_entry_id,
            "sample_payload_id": str(sample_payload_id),
            **details,
        },
    )
