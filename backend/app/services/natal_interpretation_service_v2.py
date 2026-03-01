from __future__ import annotations

import json
import logging
from typing import Literal, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationData,
    NatalInterpretationResponse,
)
from app.domain.astrology.natal_calculation import NatalResult
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import InputValidationError
from app.llm_orchestration.schemas import AstroResponseV1
from app.services.chart_json_builder import build_chart_json, build_evidence_catalog
from app.services.user_birth_profile_service import UserBirthProfileData

logger = logging.getLogger(__name__)


class NatalInterpretationServiceV2:
    """
    Service for natal interpretation using LLM Gateway V2.
    """

    @staticmethod
    async def interpret(
        db: Session,
        chart_id: str,
        natal_result: NatalResult,
        birth_profile: UserBirthProfileData,
        level: Literal["short", "complete"],
        persona_id: Optional[str],
        locale: str,
        question: Optional[str],
        request_id: str,
        trace_id: str,
    ) -> NatalInterpretationResponse:
        # 1. Normalization (N1)
        # Determine degraded mode from birth_profile
        no_time = birth_profile.birth_time is None
        no_location = birth_profile.birth_lat is None or birth_profile.birth_lon is None

        degraded_mode_str = None
        if no_time and no_location:
            degraded_mode_str = "no_location_no_time"
        elif no_time:
            degraded_mode_str = "no_time"
        elif no_location:
            degraded_mode_str = "no_location"

        chart_json_dict = build_chart_json(natal_result, birth_profile, degraded_mode_str)
        evidence_catalog = build_evidence_catalog(chart_json_dict)

        # 2. Use case selection
        use_case_key = (
            "natal_interpretation" if level == "complete" else "natal_interpretation_short"
        )

        # 3. Persona resolution (AC3)
        persona_name = None
        if level == "complete" and not persona_id:
            raise InputValidationError("persona_id is required for complete interpretation.")

        if persona_id:
            try:
                persona = db.execute(
                    select(LlmPersonaModel).where(LlmPersonaModel.id == persona_id)
                ).scalar_one_or_none()
                if persona:
                    persona_name = persona.name
                else:
                    logger.warning(f"Persona {persona_id} not found in DB")
                    # We strictly require the persona for 'complete' level
                    # For 'short' level, we might allow falling back if needed, 
                    # but it's cleaner to be strict if an ID was provided.
                    raise InputValidationError(f"Persona {persona_id} not found.")
            except InputValidationError:
                raise
            except Exception as e:
                logger.error(f"Error resolving persona {persona_id}: {e}")
                raise

        # 4. Build user_input vs context (AC4)
        # Always include question and locale in user_input for stability
        user_input = {
            "chart_json": chart_json_dict,
            "question": question or "Interprète mon thème natal.",
            "locale": locale,
        }

        context = {
            "locale": locale,
            "chart_json": json.dumps(chart_json_dict, ensure_ascii=False),  # STRING for Jinja
            "evidence_catalog": evidence_catalog,
            "use_case": use_case_key,
        }
        if persona_id:
            context["persona_id"] = persona_id
        if persona_name:
            context["persona_name"] = persona_name

        # 5. Call Gateway
        gateway = LLMGateway()
        gateway_result = await gateway.execute(
            use_case=use_case_key,
            user_input=user_input,
            context=context,
            request_id=request_id,
            trace_id=trace_id,
            db=db,
        )

        # 6. Handle result and map to schema
        if not gateway_result.structured_output:
            logger.error(f"Gateway returned no structured output for {use_case_key}")
            raise RuntimeError("Gateway returned no structured output")

        # Gateway meta to our InterpretationMeta
        meta = InterpretationMeta(
            level=level,
            use_case=gateway_result.use_case,
            persona_id=persona_id or gateway_result.meta.persona_id,
            persona_name=persona_name,
            prompt_version_id=gateway_result.meta.prompt_version_id,
            validation_status=gateway_result.meta.validation_status,
            repair_attempted=gateway_result.meta.repair_attempted,
            fallback_triggered=gateway_result.meta.fallback_triggered,
            was_fallback=gateway_result.meta.fallback_triggered,
            latency_ms=gateway_result.meta.latency_ms,
            request_id=request_id,
        )

        # Mapping structured_output to AstroResponseV1
        interpretation = AstroResponseV1(**gateway_result.structured_output)

        return NatalInterpretationResponse(
            data=NatalInterpretationData(
                chart_id=chart_id,
                use_case=gateway_result.use_case,
                interpretation=interpretation,
                meta=meta,
                degraded_mode=degraded_mode_str,
            )
        )
