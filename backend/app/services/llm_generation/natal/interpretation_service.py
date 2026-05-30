# Service d'orchestration de la generation LLM natale.
"""Porte le service canonique de génération LLM pour le domaine natal."""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.domain.astrology.builders.aspect_runtime_builder import (
    build_aspect_structural_runtime_data,
)
from app.domain.astrology.interpretation.ai_narrative_input_builder import AINarrativeInputBuilder
from app.domain.astrology.interpretation.astral_point_interpretation import (
    AstralPointInterpretationService,
)
from app.domain.astrology.interpretation.client_interpretation_projection_v1_builder import (
    ClientInterpretationProjectionV1Builder,
)
from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION,
    LLMAstrologyInputV1Builder,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectInterpretiveProfileRuntimeData,
)
from app.domain.astrology.runtime.aspect_runtime_data import AspectInterpretiveHintResolver
from app.domain.llm.configuration.prompt_version_lookup import get_active_prompt_version
from app.domain.llm.prompting.narrative_natal_reading_v1 import (
    NARRATIVE_NATAL_READING_PAYLOAD_KEY,
    NarrativeNatalReadingV1,
)
from app.domain.llm.prompting.schemas import (
    AstroErrorResponseV3,
    AstroFreeResponseV1,
    AstroFreeSection,
    AstroResponseV1,
    AstroResponseV2,
    AstroResponseV3,
)
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import GatewayResult, NatalExecutionInput
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.infra.db.repositories.astral_point_interpretation_repository import (
    AstralPointInterpretationRepository,
)
from app.infra.db.repositories.astrology_runtime_reference_repository import (
    AstrologyRuntimeReferenceRepository,
)
from app.infra.db.repositories.llm.narrative_answer_audit_repository import (
    NarrativeAnswerAuditCreate,
    NarrativeAnswerAuditRepository,
)
from app.infra.observability.metrics import observe_duration
from app.services.api_contracts.public.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationResponse,
)
from app.services.api_contracts.public.natal_interpretation import (
    NatalInterpretationData as NatalGatewayInterpretationData,
)
from app.services.chart.json_builder import (
    build_chart_json,
)
from app.services.llm_generation.llm_token_usage_service import LlmTokenUsageService
from app.services.llm_generation.natal.narrative_natal_reading_builder import (
    build_narrative_natal_reading_v1,
)
from app.services.llm_generation.natal.narrative_natal_reading_validator import (
    build_semantic_integrity_rejection_outcome,
    build_technical_leak_rejection_outcome,
    validate_narrative_reading_public_text,
)
from app.services.llm_generation.natal.narrative_semantic_integrity import (
    NarrativeChapterSourceMissingError,
    is_narratively_invalid_complete_payload,
)
from app.services.llm_generation.natal.prompt_context import (
    _detect_degraded_mode,
    build_astral_point_interpretation_context,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    RejectedNarrativeAnswerOutcome,
    build_rejected_narrative_answer_outcome_from_payload,
    emit_rejected_narrative_answer_log,
)
from app.services.llm_generation.natal.stored_interpretation_payload import (
    CORRECTIVE_REGENERATION_PENDING_USE_CASE,
    NARRATIVE_ANSWER_AUDIT_USE_CASE,
    extract_accepted_interpretation_payload,
    is_public_natal_interpretation,
    is_rejected_interpretation,
    is_rejected_stored_payload,
    load_narrative_reading_from_payload,
)
from app.services.reference_data.astrology_translation_resolver import AstrologyTranslationResolver
from app.services.resources.templates.disclaimer_registry import get_disclaimers
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.services.user_profile.natal_chart_service import UserNatalChartReadData

logger = logging.getLogger(__name__)

_ENTITLEMENT_TO_CLIENT_PROJECTION_PLAN = {
    "none": "free",
    "free": "free",
    "basic": "basic",
    "premium": "premium",
}

MODULE_TO_USE_CASE_KEY: dict[str, str] = {
    "NATAL_PSY_PROFILE": "natal_psy_profile",
    "NATAL_SHADOW_INTEGRATION": "natal_shadow_integration",
    "NATAL_LEADERSHIP_WORKSTYLE": "natal_leadership_workstyle",
    "NATAL_CREATIVITY_JOY": "natal_creativity_joy",
    "NATAL_RELATIONSHIP_STYLE": "natal_relationship_style",
    "NATAL_COMMUNITY_NETWORKS": "natal_community_networks",
    "NATAL_VALUES_SECURITY": "natal_values_security",
    "NATAL_EVOLUTION_PATH": "natal_evolution_path",
}


def _restore_missing_aspect_interpretive_hints(
    natal_result: NatalResult,
    profiles: tuple[AspectInterpretiveProfileRuntimeData, ...],
) -> None:
    """Restaure les hints d'aspects absents sur les themes stockes avant CS-380."""
    aspect_school = str(
        getattr(natal_result.aspect_school, "value", natal_result.aspect_school)
    ).strip()
    profiles_by_code = {
        profile.aspect_code: profile for profile in profiles if profile.system_code == aspect_school
    }
    resolver = AspectInterpretiveHintResolver()
    for aspect in natal_result.aspects:
        if aspect.aspect_interpretive_hints is not None:
            continue
        profile = profiles_by_code.get(aspect.aspect_code)
        if profile is None:
            continue
        structural = build_aspect_structural_runtime_data(aspect)
        aspect.aspect_interpretive_hints = resolver.resolve(structural, profile)


def _repair_legacy_natal_result_for_interpretation(db: Session, natal_result: NatalResult) -> None:
    """Complete les faits runtime manquants avant projection LLM stricte."""
    if all(aspect.aspect_interpretive_hints is not None for aspect in natal_result.aspects):
        return
    runtime_reference = AstrologyRuntimeReferenceRepository(db).load(natal_result.reference_version)
    _restore_missing_aspect_interpretive_hints(
        natal_result,
        runtime_reference.aspects.interpretive_profiles,
    )


def _build_llm_astrology_input_v1(
    *,
    natal_result: NatalResult,
    chart_id: str,
    locale: str,
    current_plan: str,
    requested_plan: str,
) -> dict[str, object]:
    """Construit le contrat riche consomme par le prompt natal interne."""
    structured_facts = StructuredFactsV1Builder().build(
        natal_result,
        chart_id=chart_id,
        locale=locale,
    )
    ai_narrative_input = AINarrativeInputBuilder().build(
        natal_result,
        chart_id=chart_id,
        locale=locale,
    )
    client_projection = ClientInterpretationProjectionV1Builder().build(
        structured_facts,
        requested_plan=requested_plan,
        current_plan=current_plan,
    )
    return LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_narrative_input,
        client_interpretation_projection_v1=client_projection,
        evidence_refs=(),
        prompt_ref="natal.llm_astrology_input_v1.runtime",
    )


def _client_projection_plan_from_entitlement(plan_code: str) -> str:
    """Convertit le plan entitlement en plan B2C supporte par la projection."""
    normalized_plan = plan_code.strip().lower()
    try:
        return _ENTITLEMENT_TO_CLIENT_PROJECTION_PLAN[normalized_plan]
    except KeyError as exc:
        raise ValueError(f"unsupported client projection plan: {plan_code}") from exc


class NatalInterpretationMetadata(BaseModel):
    """Décrit les métadonnées attendues par les routes historiques `/users`."""

    generated_at: datetime = Field(default_factory=lambda: datetime_provider.utcnow())
    cached: bool = False
    degraded_mode: str | None = None
    tokens_used: int = 0
    latency_ms: int = 0


class NatalInterpretationData(BaseModel):
    """Expose le format simplifié historique d'interprétation natal."""

    chart_id: str
    text: str
    summary: str
    key_points: list[str]
    advice: list[str]
    disclaimer: str
    metadata: NatalInterpretationMetadata


class NatalInterpretationServiceError(Exception):
    """Porte une erreur homogène pour les routes applicatives historiques."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def _parse_prompt_version_uuid(prompt_version_id: str | None) -> uuid.UUID | None:
    if not prompt_version_id:
        return None
    try:
        return uuid.UUID(prompt_version_id)
    except (ValueError, TypeError, AttributeError):
        return None


def _normalize_free_short_summary(summary: str) -> str:
    normalized = summary.strip()
    if not normalized:
        return normalized

    replacements = [
        (r"\b[Cc]et individu\b", "vous"),
        (r"\b[Cc]ette personne\b", "vous"),
        (r"\b[Ll]e natif\b", "vous"),
        (r"\b[Ll]a native\b", "vous"),
        (r"\b[Ii]l\b", "vous"),
        (r"\b[Ee]lle\b", "vous"),
        (r"\b[Ss]on thème\b", "votre thème"),
        (r"\b[Ss]a personnalité\b", "votre personnalité"),
        (r"\b[Ss]a sensibilité\b", "votre sensibilité"),
        (r"\b[Ss]es émotions\b", "vos émotions"),
        (r"\b[Ss]es relations\b", "vos relations"),
    ]
    for pattern, replacement in replacements:
        normalized = re.sub(pattern, replacement, normalized)

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _normalize_free_short_title(title: str, summary: str) -> str:
    normalized = _normalize_free_short_summary(title)
    normalized = normalized.strip(" .")
    if not normalized:
        fallback = _normalize_free_short_summary(summary).split(".")[0].strip()
        normalized = fallback.strip(" .")
    if not normalized:
        return "Votre thème révèle un équilibre singulier entre sensibilité et élan personnel"
    if normalized.lower() == "resume":
        normalized = "Votre thème révèle un équilibre singulier entre sensibilité et élan personnel"
    if not re.search(r"[.!?]$", normalized):
        normalized = f"{normalized}."
    return normalized


def _answer_type_for_audit(level: str, variant_code: str | None) -> str:
    """Determine la categorie d'audit CS-259 depuis le contexte de generation."""
    if variant_code == "free_short":
        return "free_short"
    if level == "short":
        return "basic"
    return "premium"


def _apply_narrative_answer_audit(
    model: UserNatalInterpretationModel,
    *,
    level: str,
    variant_code: str | None,
    schema_version: str,
    request_id: str,
    gateway_result: GatewayResult,
    persist_payload: dict[str, object],
    llm_astrology_input_v1: dict[str, object],
) -> None:
    """Renseigne l'audit narratif persistant sans exposer les donnees sensibles."""
    prompt_version = gateway_result.meta.prompt_version_id
    llm_input_hash = _llm_input_hash_for_audit(llm_astrology_input_v1)
    projection_version = _projection_version_for_audit(llm_astrology_input_v1)
    projection_hash = _projection_hash_for_audit(llm_astrology_input_v1)
    model.answer_id = f"{gateway_result.use_case}:{request_id}"
    model.answer_type = _answer_type_for_audit(level, variant_code)
    model.plan = gateway_result.meta.plan or "unknown"
    model.projection_version = projection_version
    model.projection_hash = projection_hash
    model.llm_input_version = _llm_input_version_for_audit(llm_astrology_input_v1)
    model.llm_input_hash = llm_input_hash
    model.prompt_version = prompt_version
    model.prompt_ref = f"llm_prompt_versions:{prompt_version}" if prompt_version else None
    model.prompt_snapshot_ref = None
    model.provider = gateway_result.meta.provider or "unknown"
    model.model = gateway_result.meta.model
    model.grounding_status = _grounding_status_for_audit(llm_astrology_input_v1)
    model.evidence_refs = _evidence_refs_for_audit(llm_astrology_input_v1)


def _persist_rejected_narrative_answer_audit(
    db: Session,
    *,
    user_id: int,
    chart_id: str,
    level: str,
    variant_code: str | None,
    gateway_result: GatewayResult,
    llm_astrology_input_v1: dict[str, object],
    rejected_outcome: RejectedNarrativeAnswerOutcome,
) -> None:
    """Persiste un rejet LLM via le repository audit sans l'exposer comme interpretation."""
    prompt_version_id = gateway_result.meta.prompt_version_id
    prompt_version = str(prompt_version_id) if prompt_version_id else "legacy_unavailable"
    repository = NarrativeAnswerAuditRepository(db)
    repository.create(
        NarrativeAnswerAuditCreate(
            answer_id=rejected_outcome.answer_id,
            answer_type=_answer_type_for_audit(level, variant_code),
            chart_id=chart_id,
            user_id=user_id,
            plan=gateway_result.meta.plan or "unknown",
            projection_version=_projection_version_for_audit(llm_astrology_input_v1),
            projection_hash=_projection_hash_for_audit(llm_astrology_input_v1),
            llm_input_version=_llm_input_version_for_audit(llm_astrology_input_v1),
            llm_input_hash=_llm_input_hash_for_audit(llm_astrology_input_v1),
            prompt_version=prompt_version,
            provider=gateway_result.meta.provider or "unknown",
            model=gateway_result.meta.model or "unknown",
            grounding_status="rejected",
            interpretation_payload={"client_message": rejected_outcome.client_message},
            use_case=NARRATIVE_ANSWER_AUDIT_USE_CASE,
            rejection_reason=rejected_outcome.rejection_reason,
            validation_context=rejected_outcome.validation_context,
            raw_answer_storage=rejected_outcome.raw_answer_storage,
            client_message=rejected_outcome.client_message,
        )
    )
    db.commit()


AcceptedCompleteAstroResponse = AstroResponseV1 | AstroResponseV2 | AstroResponseV3
PublicAstroResponse = AcceptedCompleteAstroResponse | AstroErrorResponseV3 | AstroFreeResponseV1


def _attach_narrative_reading_to_complete(
    *,
    interpretation: AcceptedCompleteAstroResponse,
    persist_payload: dict[str, object],
    llm_astrology_input_v1: dict[str, object],
    level: str,
    variant_code: str | None,
    answer_id: str,
    answer_type: str,
) -> tuple[
    NarrativeNatalReadingV1 | None,
    RejectedNarrativeAnswerOutcome | None,
    dict[str, object],
]:
    """Construit et valide la lecture narrative publique pour une sortie complete acceptee."""
    try:
        reading = build_narrative_natal_reading_v1(
            response=interpretation,
            llm_astrology_input_v1=llm_astrology_input_v1,
            level=level,
            variant_code=variant_code,
        )
    except NarrativeChapterSourceMissingError as exc:
        violations = [f"chapter_source_missing:{exc.chapter_key}"]
        return (
            None,
            build_semantic_integrity_rejection_outcome(
                answer_id=answer_id,
                answer_type=answer_type,
                raw_answer=persist_payload,
                violations=violations,
            ),
            persist_payload,
        )
    except ValidationError as exc:
        logger.warning(
            "Narrative natal reading unavailable for accepted complete response "
            "answer_id=%s error=%s",
            answer_id,
            exc,
        )
        return None, None, persist_payload
    violations = validate_narrative_reading_public_text(reading)
    if violations:
        rejection_builder = (
            build_semantic_integrity_rejection_outcome
            if any(
                marker in violation
                for violation in violations
                for marker in (
                    "duplicate_chapter",
                    "empty_used_astrological",
                    "chapter_empty:",
                    "chapter_source_missing",
                )
            )
            else build_technical_leak_rejection_outcome
        )
        return (
            None,
            rejection_builder(
                answer_id=answer_id,
                answer_type=answer_type,
                raw_answer=persist_payload,
                violations=violations,
            ),
            persist_payload,
        )
    merged_payload = {
        **persist_payload,
        NARRATIVE_NATAL_READING_PAYLOAD_KEY: reading.model_dump(),
    }
    return reading, None, merged_payload


def _without_public_evidence(interpretation: PublicAstroResponse) -> PublicAstroResponse:
    """Retire les identifiants evidence internes de la projection publique."""
    return interpretation.model_copy(update={"evidence": []})


def _build_rejected_narrative_answer_outcome(
    *,
    level: str,
    variant_code: str | None,
    schema_version: str,
    request_id: str,
    gateway_result: GatewayResult,
    persist_payload: dict[str, object],
    llm_astrology_input_v1: dict[str, object],
) -> RejectedNarrativeAnswerOutcome | None:
    """Evalue le rejet CS-290 depuis les preuves CS-289 deja presentes."""
    projection_version = _projection_version_for_audit(llm_astrology_input_v1)
    projection_hash = _projection_hash_for_audit(llm_astrology_input_v1)
    return build_rejected_narrative_answer_outcome_from_payload(
        answer_id=f"{gateway_result.use_case}:{request_id}",
        answer_type=_answer_type_for_audit(level, variant_code),
        raw_answer=persist_payload,
        projection_version=projection_version,
        projection_hash=projection_hash,
        llm_input_version=_llm_input_version_for_audit(llm_astrology_input_v1),
        llm_input_hash=_llm_input_hash_for_audit(llm_astrology_input_v1),
        llm_astrology_input_v1=llm_astrology_input_v1,
    )


def _llm_input_provenance(llm_astrology_input_v1: dict[str, object]) -> dict[str, object]:
    """Lit la provenance canonique sans accepter de fallback silencieux invalide."""
    if not isinstance(llm_astrology_input_v1, dict):
        raise ValueError("llm_astrology_input_v1 audit payload is required")
    provenance = llm_astrology_input_v1.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("llm_astrology_input_v1 provenance is required for audit")
    return provenance


def _llm_input_hash_for_audit(llm_astrology_input_v1: dict[str, object]) -> str:
    """Retourne le hash prompt-visible canonique requis par l'audit."""
    llm_input_hash = _llm_input_provenance(llm_astrology_input_v1).get("llm_input_hash")
    if isinstance(llm_input_hash, str) and len(llm_input_hash) == 64:
        return llm_input_hash
    raise ValueError("llm_astrology_input_v1 llm_input_hash is required for audit")


def _llm_input_version_for_audit(llm_astrology_input_v1: dict[str, object]) -> str:
    """Aligne la version d'audit sur le contrat LLM interne quand il est present."""
    if isinstance(llm_astrology_input_v1, dict):
        contract_version = llm_astrology_input_v1.get("contract_version")
        if contract_version == LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION:
            return contract_version
    raise ValueError("llm_astrology_input_v1 contract_version is required for audit")


def _projection_hash_for_audit(llm_astrology_input_v1: dict[str, object]) -> str:
    """Garde `projection_hash` separe de l'identite complete du prompt LLM."""
    projection_hash = _llm_input_provenance(llm_astrology_input_v1).get("projection_hash")
    if isinstance(projection_hash, str) and len(projection_hash) == 64:
        return projection_hash
    raise ValueError("llm_astrology_input_v1 projection_hash is required for audit")


def _projection_version_for_audit(llm_astrology_input_v1: dict[str, object]) -> str:
    """Retourne la version de source qui porte le hash de projection."""
    evidence = (
        llm_astrology_input_v1.get("evidence") if isinstance(llm_astrology_input_v1, dict) else None
    )
    if not isinstance(evidence, dict):
        raise ValueError("llm_astrology_input_v1 projection evidence is required for audit")
    evidence_refs = evidence.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        raise ValueError("llm_astrology_input_v1 projection evidence refs are required for audit")
    for ref in evidence_refs:
        if not isinstance(ref, dict):
            continue
        if ref.get("source_type") != "projection_version" or ref.get("source_id") != "projection":
            continue
        source_version = ref.get("source_version")
        if isinstance(source_version, str) and source_version.strip():
            return source_version
    raise ValueError("llm_astrology_input_v1 projection source_version is required for audit")


def _grounding_status_for_audit(llm_astrology_input_v1: dict[str, object]) -> str:
    """Reporte le statut de preuve du contrat LLM quand aucun rejet n'a eu lieu."""
    if not isinstance(llm_astrology_input_v1, dict):
        raise ValueError("llm_astrology_input_v1 evidence is required for audit")
    evidence = llm_astrology_input_v1.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("llm_astrology_input_v1 evidence is required for audit")
    grounding_status = evidence.get("grounding_status")
    if isinstance(grounding_status, str):
        return grounding_status
    raise ValueError("llm_astrology_input_v1 grounding_status is required for audit")


def _evidence_refs_for_audit(llm_astrology_input_v1: dict[str, object]) -> list[object]:
    """Persiste les `evidence_refs` backend-only deja validees par le domaine."""
    if not isinstance(llm_astrology_input_v1, dict):
        raise ValueError("llm_astrology_input_v1 evidence_refs are required for audit")
    evidence = llm_astrology_input_v1.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("llm_astrology_input_v1 evidence_refs are required for audit")
    evidence_refs = evidence.get("evidence_refs")
    if isinstance(evidence_refs, list):
        return list(evidence_refs)
    raise ValueError("llm_astrology_input_v1 evidence_refs are required for audit")


class NatalInterpretationService:
    """Orchestre le rendu, la persistance et la projection applicative du natal."""

    @staticmethod
    def _record_token_usage(
        db: Session,
        *,
        user_id: int,
        gateway_result: GatewayResult,
    ) -> None:
        """
        Record natal LLM usage for observability without consuming user chat quota.
        """
        LlmTokenUsageService.record_usage(
            db,
            user_id=user_id,
            feature_code="natal_interpretation",
            quotas=[],
            provider_model=gateway_result.meta.model,
            tokens_in=gateway_result.usage.input_tokens,
            tokens_out=gateway_result.usage.output_tokens,
            request_id=gateway_result.request_id,
        )

    @staticmethod
    def _compose_legacy_text(interpretation: object) -> str:
        """Reconstruit un texte lisible pour les routes historiques `/users`."""
        sections = getattr(interpretation, "sections", []) or []
        section_texts = [
            section.content.strip()
            for section in sections
            if hasattr(section, "content") and isinstance(section.content, str) and section.content
        ]
        summary = getattr(interpretation, "summary", "")
        return "\n\n".join([part for part in [summary, *section_texts] if part]).strip()

    @staticmethod
    def _to_legacy_payload(response: NatalInterpretationResponse) -> NatalInterpretationData:
        """Projette la réponse canonique vers le format simplifié historique."""
        interpretation = response.data.interpretation
        disclaimer = "\n".join(response.disclaimers)
        highlights = list(getattr(interpretation, "highlights", []) or [])
        advice = list(getattr(interpretation, "advice", []) or [])

        return NatalInterpretationData(
            chart_id=response.data.chart_id,
            text=NatalInterpretationService._compose_legacy_text(interpretation),
            summary=getattr(interpretation, "summary", ""),
            key_points=highlights,
            advice=advice,
            disclaimer=disclaimer,
            metadata=NatalInterpretationMetadata(
                cached=response.data.meta.cached,
                degraded_mode=response.data.degraded_mode,
                latency_ms=response.data.meta.latency_ms or 0,
            ),
        )

    @staticmethod
    async def interpret_chart(
        natal_chart: UserNatalChartReadData,
        birth_profile: UserBirthProfileData,
        user_id: int,
        request_id: str,
        trace_id: str | None = None,
        persona_id: str | None = None,
        db: Session | None = None,
    ) -> NatalInterpretationData:
        """Maintient le contrat des routes `/users` via la variante canonique free short."""
        if db is None:
            raise NatalInterpretationServiceError(
                code="natal_db_required",
                message="A database session is required for natal interpretation.",
                details={"request_id": request_id},
            )

        try:
            response = await NatalInterpretationService.interpret(
                db=db,
                user_id=user_id,
                chart_id=natal_chart.chart_id,
                natal_result=natal_chart.result,
                birth_profile=birth_profile,
                level="complete",
                # Les routes historiques `/users` ne doivent pas ouvrir un parcours
                # premium implicite ni persister un variant_code vide.
                persona_id=None,
                locale="fr-FR",
                question=None,
                request_id=request_id,
                trace_id=trace_id or request_id,
                force_refresh=False,
                module=None,
                variant_code="free_short",
            )
        except Exception as error:
            error_code = getattr(error, "code", "ai_engine_error")
            if "timeout" in str(error_code).lower() or isinstance(error, TimeoutError):
                error_code = "ai_engine_timeout"
            raise NatalInterpretationServiceError(
                code=str(error_code),
                message=f"AI Engine error: {error}",
                details={"request_id": request_id},
            ) from error

        return NatalInterpretationService._to_legacy_payload(response)

    @staticmethod
    def _is_empty_complete_payload(payload: dict[str, object] | None) -> bool:
        if not isinstance(payload, dict):
            return True

        summary = payload.get("summary")
        has_summary = isinstance(summary, str) and bool(summary.strip())

        sections = payload.get("sections")
        has_section_content = False
        if isinstance(sections, list):
            has_section_content = any(
                isinstance(section, dict)
                and (
                    isinstance(section.get("content"), str)
                    and bool(section.get("content", "").strip())
                )
                for section in sections
            )

        return not (has_summary or has_section_content)

    @staticmethod
    def _is_invalid_complete_interpretation(
        model: UserNatalInterpretationModel,
    ) -> bool:
        if model.level != InterpretationLevel.COMPLETE:
            return False
        if model.variant_code == "free_short" or model.use_case == "natal_long_free":
            return False
        payload = (
            model.interpretation_payload if isinstance(model.interpretation_payload, dict) else None
        )
        if NatalInterpretationService._is_empty_complete_payload(payload):
            return True
        if isinstance(payload, dict) and is_narratively_invalid_complete_payload(payload):
            return True
        return False

    @staticmethod
    def claim_corrective_regeneration_eligibility(
        db: Session,
        *,
        user_id: int,
        variant_code: str | None,
    ) -> tuple[int, str] | None:
        """Reserve atomiquement une lecture invalide pour une regeneration corrective."""
        stmt = (
            select(UserNatalInterpretationModel)
            .where(
                UserNatalInterpretationModel.user_id == user_id,
                UserNatalInterpretationModel.level == InterpretationLevel.COMPLETE,
                UserNatalInterpretationModel.variant_code == variant_code,
            )
            .order_by(
                UserNatalInterpretationModel.created_at.desc(),
                UserNatalInterpretationModel.id.desc(),
            )
        )
        rows = list(db.execute(stmt).scalars().all())
        invalid_rows = [
            row
            for row in rows
            if NatalInterpretationService._is_invalid_complete_interpretation(row)
            and is_public_natal_interpretation(row)
        ]
        valid_rows = [
            row
            for row in rows
            if not NatalInterpretationService._is_invalid_complete_interpretation(row)
            and is_public_natal_interpretation(row)
        ]
        if not invalid_rows or valid_rows:
            return None

        candidate = invalid_rows[0]
        original_use_case = candidate.use_case
        claimed = db.execute(
            update(UserNatalInterpretationModel)
            .where(
                UserNatalInterpretationModel.id == candidate.id,
                UserNatalInterpretationModel.use_case == original_use_case,
            )
            .values(use_case=CORRECTIVE_REGENERATION_PENDING_USE_CASE)
        )
        if claimed.rowcount != 1:
            db.rollback()
            return None
        db.commit()
        return candidate.id, original_use_case

    @staticmethod
    def release_corrective_regeneration_claim(
        db: Session,
        *,
        interpretation_id: int,
        original_use_case: str,
    ) -> None:
        """Restaure une reservation corrective si la generation n'aboutit pas."""
        db.execute(
            update(UserNatalInterpretationModel)
            .where(
                UserNatalInterpretationModel.id == interpretation_id,
                UserNatalInterpretationModel.use_case == CORRECTIVE_REGENERATION_PENDING_USE_CASE,
            )
            .values(use_case=original_use_case)
        )
        db.commit()

    @staticmethod
    def _purge_rejected_interpretation(
        db: Session,
        model: UserNatalInterpretationModel,
    ) -> bool:
        """Supprime une interpretation rejetee qui ne doit pas etre relue cote public."""
        if model.use_case == NARRATIVE_ANSWER_AUDIT_USE_CASE:
            return False
        if not is_rejected_interpretation(model):
            return False
        logger.warning(
            "Deleting rejected persisted natal interpretation user_id=%s id=%s use_case=%s",
            model.user_id,
            model.id,
            model.use_case,
        )
        db.delete(model)
        return True

    @staticmethod
    def _deserialize_persisted_interpretation(
        model: UserNatalInterpretationModel,
        *,
        level: Literal["short", "complete"],
        locale: str,
    ) -> tuple[
        AstroResponseV3
        | AstroErrorResponseV3
        | AstroResponseV2
        | AstroResponseV1
        | AstroFreeResponseV1,
        str,
    ]:
        if is_rejected_interpretation(model):
            raise NatalInterpretationServiceError(
                code="interpretation_rejected",
                message=(
                    "Stored interpretation was rejected by output policy and "
                    "cannot be exposed as a valid natal interpretation"
                ),
            )

        disclaimers = get_disclaimers(locale)
        raw_payload = (
            model.interpretation_payload if isinstance(model.interpretation_payload, dict) else {}
        )
        if is_rejected_stored_payload(raw_payload):
            raise NatalInterpretationServiceError(
                code="interpretation_rejected",
                message=(
                    "Stored interpretation payload contains rejection metadata and "
                    "cannot be deserialized as AstroResponse"
                ),
            )
        base_payload = extract_accepted_interpretation_payload(raw_payload)
        full_payload = {**base_payload, "disclaimers": disclaimers}

        if level == "complete" and model.variant_code == "free_short":
            return AstroFreeResponseV1(**full_payload), "v1"

        schema_version = "v1"
        if level == "complete":
            use_v3 = settings.natal_schema_version == "v3"
            if use_v3:
                try:
                    return AstroResponseV3(**base_payload), "v3"
                except Exception:
                    try:
                        return AstroErrorResponseV3(**base_payload), "v3_error"
                    except Exception:
                        try:
                            return AstroResponseV2(**full_payload), "v2"
                        except Exception:
                            return AstroResponseV1(**full_payload), schema_version
            try:
                return AstroResponseV2(**full_payload), "v2"
            except Exception:
                return AstroResponseV1(**full_payload), schema_version

        return AstroResponseV1(**full_payload), schema_version

    @staticmethod
    async def interpret(
        db: Session,
        user_id: int,
        chart_id: str,
        natal_result: NatalResult,
        birth_profile: UserBirthProfileData,
        level: Literal["short", "complete"],
        persona_id: Optional[str],
        locale: str,
        question: Optional[str],
        request_id: str,
        trace_id: str,
        force_refresh: bool = False,
        module: Optional[
            Literal[
                "NATAL_PSY_PROFILE",
                "NATAL_SHADOW_INTEGRATION",
                "NATAL_LEADERSHIP_WORKSTYLE",
                "NATAL_CREATIVITY_JOY",
                "NATAL_RELATIONSHIP_STYLE",
                "NATAL_COMMUNITY_NETWORKS",
                "NATAL_VALUES_SECURITY",
                "NATAL_EVOLUTION_PATH",
            ]
        ] = None,
        variant_code: Optional[str] = None,
    ) -> NatalInterpretationResponse:
        persona_uuid: uuid.UUID | None = None
        if persona_id:
            try:
                persona_uuid = uuid.UUID(persona_id)
            except (ValueError, TypeError):
                persona_uuid = None

        # Thematic modules must always bypass cache and DB persistence to avoid
        # mixing generic/premium cached payloads with module-specific responses.
        is_thematic_module = bool(module and level == "complete")
        effective_force_refresh = force_refresh or is_thematic_module

        # 0. Check for existing persisted interpretation
        if not effective_force_refresh:
            db_level = (
                InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE
            )
            stmt = select(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.user_id == user_id,
                UserNatalInterpretationModel.level == db_level,
            )
            if level == "complete":
                stmt = stmt.where(UserNatalInterpretationModel.persona_id == persona_uuid)
            else:
                stmt = stmt.where(UserNatalInterpretationModel.persona_id.is_(None))

            # story 64.3: variant_code must match for cached complete interpretations
            if level == "complete":
                stmt = stmt.where(UserNatalInterpretationModel.variant_code == variant_code)

            stmt = stmt.order_by(
                UserNatalInterpretationModel.created_at.desc(),
                UserNatalInterpretationModel.id.desc(),
            )

            existing_rows = list(db.execute(stmt).scalars().all())
            valid_existing_rows: list[UserNatalInterpretationModel] = []
            deleted_any = False
            for row in existing_rows:
                if row.use_case == CORRECTIVE_REGENERATION_PENDING_USE_CASE:
                    continue
                if NatalInterpretationService._is_invalid_complete_interpretation(row):
                    logger.warning(
                        (
                            "Deleting empty persisted natal interpretation "
                            "user_id=%s id=%s use_case=%s"
                        ),
                        user_id,
                        row.id,
                        row.use_case,
                    )
                    db.delete(row)
                    deleted_any = True
                    continue
                if NatalInterpretationService._purge_rejected_interpretation(db, row):
                    deleted_any = True
                    continue
                valid_existing_rows.append(row)

            if deleted_any:
                db.commit()

            existing = valid_existing_rows[0] if valid_existing_rows else None
            if len(existing_rows) > 1:
                logger.warning(
                    "Multiple cached natal interpretations found for unique key; keeping latest "
                    "user_id=%s level=%s persona_id=%s duplicates=%s",
                    user_id,
                    db_level.value,
                    persona_id,
                    len(existing_rows),
                )
            if existing:
                # Avoid serving stale cached payloads produced with an archived prompt version.
                active_prompt = get_active_prompt_version(db, existing.use_case)
                active_prompt_id = str(active_prompt.id) if active_prompt else None
                existing_prompt_id = (
                    str(existing.prompt_version_id) if existing.prompt_version_id else None
                )
                if (
                    active_prompt_id
                    and existing_prompt_id
                    and active_prompt_id != existing_prompt_id
                ):
                    logger.info(
                        "Ignoring stale cached interpretation chart_id=%s use_case=%s "
                        "stored_prompt=%s active_prompt=%s",
                        chart_id,
                        existing.use_case,
                        existing_prompt_id,
                        active_prompt_id,
                    )
                    existing = None

            if existing:
                interpretation, schema_version = (
                    NatalInterpretationService._deserialize_persisted_interpretation(
                        existing,
                        level=level,
                        locale=locale,
                    )
                )

                meta = InterpretationMeta(
                    id=existing.id,
                    level=level,
                    use_case=existing.use_case,
                    persona_id=str(existing.persona_id) if existing.persona_id else None,
                    persona_name=existing.persona_name,
                    prompt_version_id=str(existing.prompt_version_id)
                    if existing.prompt_version_id
                    else None,
                    schema_version="unknown",  # Will be set by format method
                    validation_status="valid",
                    was_fallback=existing.was_fallback,
                    request_id=request_id,
                    cached=True,
                    persisted_at=existing.created_at,
                    module=module,
                )
                return NatalInterpretationService.format_interpretation_response(
                    existing, meta, locale
                )

        # 1. Normalization (N1)
        degraded_mode_str = _detect_degraded_mode(birth_profile)

        labels = AstrologyTranslationResolver(db).resolve_labels(
            language_code=locale,
            user_id=user_id,
        )
        _repair_legacy_natal_result_for_interpretation(db, natal_result)
        chart_json_dict = build_chart_json(natal_result, birth_profile, degraded_mode_str, labels)
        interpreted_astral_points = ()
        astral_points = getattr(natal_result, "astral_points", ())
        if astral_points:
            interpreted_astral_points = AstralPointInterpretationService(
                AstralPointInterpretationRepository(db)
            ).build_context(
                natal_result,
                language_code=locale,
            )
        astral_point_context = build_astral_point_interpretation_context(interpreted_astral_points)
        astro_context = json.dumps(astral_point_context, ensure_ascii=False)

        # 3. Use case selection
        if level == "complete" and variant_code == "free_short":
            return await NatalInterpretationService._generate_free_short(
                db=db,
                user_id=user_id,
                chart_id=chart_id,
                natal_result=natal_result,
                birth_profile=birth_profile,
                chart_json_dict=chart_json_dict,
                astro_context=astro_context,
                locale=locale,
                request_id=request_id,
                trace_id=trace_id,
                degraded_mode_str=degraded_mode_str,
            )

        if level == "complete" and module:
            use_case_key = MODULE_TO_USE_CASE_KEY.get(module, "natal_interpretation")
        else:
            use_case_key = (
                "natal_interpretation" if level == "complete" else "natal_interpretation_short"
            )

        # 3.5 Resolve Plan (Story 66.20)
        from app.services.entitlement.effective_entitlement_resolver_service import (
            EffectiveEntitlementResolverService,
        )

        entitlements = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
            db, app_user_id=user_id
        )
        user_plan = entitlements.plan_code
        projection_plan = _client_projection_plan_from_entitlement(user_plan)
        llm_astrology_input_v1 = _build_llm_astrology_input_v1(
            natal_result=natal_result,
            chart_id=chart_id,
            locale=locale,
            current_plan=projection_plan,
            requested_plan=projection_plan,
        )

        # 4. Call AIEngineAdapter (Story 66.7)
        effective_question = question
        if level == "short":
            if not effective_question:
                effective_question = "Interprète mon thème natal."
        else:
            # Story 30-5: level complete does not take a question
            effective_question = None

        persona_name = None
        if persona_id:
            persona = db.get(LlmPersonaModel, uuid.UUID(persona_id))
            if persona:
                persona_name = persona.name

        natal_input = NatalExecutionInput(
            use_case_key=use_case_key,
            locale=locale,
            level=level,
            llm_astrology_input_v1=llm_astrology_input_v1,
            persona_id=persona_id,
            plan=user_plan,
            validation_strict=level == "complete",
            question=effective_question,
            astro_context=astro_context,
            module=module,
            variant_code=variant_code,
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )

        gateway_result = await AIEngineAdapter.generate_natal_interpretation(
            natal_input=natal_input, db=db
        )

        NatalInterpretationService._record_token_usage(
            db,
            user_id=user_id,
            gateway_result=gateway_result,
        )

        # 5. Handle result and map to schema
        if not gateway_result.structured_output:
            logger.error(f"Gateway returned no structured output for {use_case_key}")
            raise RuntimeError("Gateway returned no structured output")

        disclaimers = get_disclaimers(locale)
        base_output = (
            gateway_result.structured_output
            if isinstance(gateway_result.structured_output, dict)
            else {}
        )
        full_output = {**base_output, "disclaimers": disclaimers}

        if level == "complete" and variant_code != "free_short":
            if NatalInterpretationService._is_empty_complete_payload(base_output):
                logger.error(
                    "Gateway returned empty complete interpretation request_id=%s use_case=%s",
                    request_id,
                    use_case_key,
                )
                raise RuntimeError("empty complete interpretation")

        # Mapping structured_output to AstroResponseV1/V2/V3 (Story 30-8 T7.4)
        schema_version = "v1"
        use_v3 = settings.natal_schema_version == "v3"

        if level == "complete" and not gateway_result.meta.fallback_triggered:
            if use_v3:
                # complete + v3 flag → try v3 first, then v3_error, then v2, then v1
                try:
                    # AstroResponseV3 does NOT have disclaimers in schema
                    interpretation: (  # noqa: E501
                        AstroResponseV3 | AstroErrorResponseV3 | AstroResponseV2 | AstroResponseV1
                    ) = AstroResponseV3(**base_output)
                    schema_version = "v3"
                except Exception as exc:
                    logger.debug(f"AstroResponseV3 deserialization failed: {exc}")
                    try:
                        interpretation = AstroErrorResponseV3(**base_output)
                        schema_version = "v3_error"
                    except Exception as exc2:
                        logger.debug(f"AstroErrorResponseV3 deserialization failed: {exc2}")
                        logger.warning(
                            "V3 deserialization failed, falling back to V2 for request_id=%s",
                            request_id,
                        )
                        try:
                            interpretation = AstroResponseV2(**full_output)
                            schema_version = "v2"
                        except Exception:
                            interpretation = AstroResponseV1(**full_output)
            else:
                # complete (payant) → schéma v2
                try:
                    interpretation = AstroResponseV2(**full_output)
                    schema_version = "v2"
                except Exception as exc:
                    logger.warning(
                        "V2 deserialization failed (%s), falling back to V1 for request_id=%s",
                        exc,
                        request_id,
                    )
                    interpretation = AstroResponseV1(**full_output)
        else:
            # short (gratuit) ou fallback vers short → schéma v1
            interpretation = AstroResponseV1(**full_output)

        narrative_reading: NarrativeNatalReadingV1 | None = None
        narrative_rejection: RejectedNarrativeAnswerOutcome | None = None

        # Observe metrics
        if hasattr(interpretation, "summary"):
            observe_duration("natal_summary_len", float(len(interpretation.summary)))
        if hasattr(interpretation, "sections"):
            for _section in interpretation.sections:
                if hasattr(_section, "content"):
                    observe_duration("natal_section_len", float(len(_section.content)))

        # Gateway meta to our InterpretationMeta
        meta = InterpretationMeta(
            id=None,
            level=level,
            use_case=gateway_result.use_case,
            persona_id=persona_id or gateway_result.meta.persona_id,
            persona_name=persona_name,
            prompt_version_id=gateway_result.meta.prompt_version_id,
            schema_version=schema_version,
            validation_status=gateway_result.meta.validation_status,
            repair_attempted=gateway_result.meta.repair_attempted,
            fallback_triggered=gateway_result.meta.fallback_triggered,
            was_fallback=gateway_result.meta.fallback_triggered,
            latency_ms=gateway_result.meta.latency_ms,
            request_id=request_id,
            cached=False,
            module=module,
        )

        # 7. Persist interpretation
        db_level = InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE

        # Story 30-8 T7.4: Ensure persisted payload does NOT contain disclaimers if it's V3
        # (The gateway structured_output shouldn't have them, but we sanitize to be sure)
        persist_payload = (
            gateway_result.structured_output
            if isinstance(gateway_result.structured_output, dict)
            else {}
        )
        if schema_version.startswith("v3") and "disclaimers" in persist_payload:
            persist_payload = persist_payload.copy()
            persist_payload.pop("disclaimers", None)

        if (
            level == "complete"
            and variant_code != "free_short"
            and isinstance(interpretation, (AstroResponseV1, AstroResponseV2, AstroResponseV3))
        ):
            narrative_reading, narrative_rejection, persist_payload = (
                _attach_narrative_reading_to_complete(
                    interpretation=interpretation,
                    persist_payload=persist_payload,
                    llm_astrology_input_v1=llm_astrology_input_v1,
                    level=level,
                    variant_code=variant_code,
                    answer_id=f"{gateway_result.use_case}:{request_id}",
                    answer_type=_answer_type_for_audit(level, variant_code),
                )
            )

        rejected_outcome = narrative_rejection or _build_rejected_narrative_answer_outcome(
            level=level,
            variant_code=variant_code,
            schema_version=schema_version,
            request_id=request_id,
            gateway_result=gateway_result,
            persist_payload=persist_payload,
            llm_astrology_input_v1=llm_astrology_input_v1,
        )
        if rejected_outcome is not None:
            emit_rejected_narrative_answer_log(
                logger,
                outcome=rejected_outcome,
                request_id=request_id,
                trace_id=trace_id,
                use_case=gateway_result.use_case,
            )
            try:
                _persist_rejected_narrative_answer_audit(
                    db,
                    user_id=user_id,
                    chart_id=chart_id,
                    level=level,
                    variant_code=variant_code,
                    gateway_result=gateway_result,
                    llm_astrology_input_v1=llm_astrology_input_v1,
                    rejected_outcome=rejected_outcome,
                )
            except Exception as audit_exc:
                db.rollback()
                logger.exception(
                    "Failed to persist rejected natal interpretation audit "
                    "request_id=%s use_case=%s error=%s",
                    request_id,
                    gateway_result.use_case,
                    audit_exc,
                )
            interpretation = AstroFreeResponseV1(
                title="",
                summary=rejected_outcome.client_message,
                sections=[],
                highlights=[],
                advice=[],
                evidence=[],
                disclaimers=disclaimers,
            )
            meta.validation_status = "rejected"
            return NatalInterpretationResponse(
                data=NatalGatewayInterpretationData(
                    chart_id=chart_id,
                    use_case=gateway_result.use_case,
                    interpretation=interpretation,
                    meta=meta,
                    degraded_mode=degraded_mode_str,
                ),
                disclaimers=disclaimers,
            )

        try:
            if not is_thematic_module:
                unique_stmt = select(UserNatalInterpretationModel).where(
                    UserNatalInterpretationModel.user_id == user_id,
                    UserNatalInterpretationModel.level == db_level,
                )
                if db_level == InterpretationLevel.SHORT:
                    unique_stmt = unique_stmt.where(
                        UserNatalInterpretationModel.persona_id.is_(None)
                    )
                else:
                    unique_stmt = unique_stmt.where(
                        UserNatalInterpretationModel.persona_id == persona_uuid
                    )
                unique_stmt = unique_stmt.order_by(
                    UserNatalInterpretationModel.created_at.desc(),
                    UserNatalInterpretationModel.id.desc(),
                )

                rows = list(db.execute(unique_stmt).scalars().all())
                primary = rows[0] if rows else None
                for duplicate in rows[1:]:
                    db.delete(duplicate)

                prompt_version_uuid = _parse_prompt_version_uuid(
                    gateway_result.meta.prompt_version_id
                )
                if primary is None:
                    primary = UserNatalInterpretationModel(
                        user_id=user_id,
                        chart_id=chart_id,
                        level=db_level,
                        use_case=gateway_result.use_case,
                        variant_code=variant_code,
                        persona_id=persona_uuid,
                        persona_name=persona_name,
                        prompt_version_id=prompt_version_uuid,
                        interpretation_payload=persist_payload,
                        was_fallback=gateway_result.meta.fallback_triggered,
                        degraded_mode=degraded_mode_str,
                    )
                    _apply_narrative_answer_audit(
                        primary,
                        level=level,
                        variant_code=variant_code,
                        schema_version=schema_version,
                        request_id=request_id,
                        gateway_result=gateway_result,
                        persist_payload=persist_payload,
                        llm_astrology_input_v1=llm_astrology_input_v1,
                    )
                    db.add(primary)
                else:
                    primary.chart_id = chart_id
                    primary.use_case = gateway_result.use_case
                    primary.variant_code = variant_code
                    primary.persona_id = persona_uuid
                    primary.persona_name = persona_name
                    primary.prompt_version_id = prompt_version_uuid
                    primary.interpretation_payload = persist_payload
                    primary.was_fallback = gateway_result.meta.fallback_triggered
                    primary.degraded_mode = degraded_mode_str
                    _apply_narrative_answer_audit(
                        primary,
                        level=level,
                        variant_code=variant_code,
                        schema_version=schema_version,
                        request_id=request_id,
                        gateway_result=gateway_result,
                        persist_payload=persist_payload,
                        llm_astrology_input_v1=llm_astrology_input_v1,
                    )

                db.flush()
                db.refresh(primary)
                meta.id = primary.id
                meta.persisted_at = primary.created_at
        except Exception as persist_exc:
            db.rollback()
            logger.exception(
                "Failed to persist natal interpretation request_id=%s use_case=%s error=%s",
                request_id,
                gateway_result.use_case,
                persist_exc,
            )
            raise

        return NatalInterpretationResponse(
            data=NatalGatewayInterpretationData(
                chart_id=chart_id,
                use_case=gateway_result.use_case,
                interpretation=_without_public_evidence(interpretation),
                meta=meta,
                degraded_mode=degraded_mode_str,
                narrative_natal_reading_v1=narrative_reading,
            ),
            disclaimers=disclaimers,
        )

    @staticmethod
    async def _generate_free_short(
        db: Session,
        user_id: int,
        chart_id: str,
        natal_result: NatalResult,
        birth_profile: UserBirthProfileData,
        chart_json_dict: dict,
        astro_context: str,
        locale: str,
        request_id: str,
        trace_id: str,
        degraded_mode_str: str | None,
    ) -> NatalInterpretationResponse:
        """
        Génère une interprétation restreinte pour les utilisateurs free.
        Appelle un prompt unique 'natal_long_free' qui produit title + summary + accordion_titles.
        """
        use_case_key = "natal_long_free"

        # 3.5 Resolve Plan (Story 66.20)
        from app.services.entitlement.effective_entitlement_resolver_service import (
            EffectiveEntitlementResolverService,
        )

        entitlements = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
            db, app_user_id=user_id
        )
        user_plan = entitlements.plan_code
        projection_plan = _client_projection_plan_from_entitlement(user_plan)
        llm_astrology_input_v1 = _build_llm_astrology_input_v1(
            natal_result=natal_result,
            chart_id=chart_id,
            locale=locale,
            current_plan=projection_plan,
            requested_plan="free",
        )

        natal_input = NatalExecutionInput(
            use_case_key=use_case_key,
            locale=locale,
            level="complete",  # Free short is mapped to complete level in persistence
            llm_astrology_input_v1=llm_astrology_input_v1,
            persona_id=None,
            plan=user_plan,
            validation_strict=False,
            question=None,
            astro_context=astro_context,
            module=None,
            variant_code="free_short",
            user_id=user_id,
            request_id=request_id,
            trace_id=trace_id,
        )

        gateway_result = await AIEngineAdapter.generate_natal_interpretation(
            natal_input=natal_input, db=db
        )

        NatalInterpretationService._record_token_usage(
            db,
            user_id=user_id,
            gateway_result=gateway_result,
        )

        if not gateway_result.structured_output:
            logger.error(f"Gateway returned no structured output for {use_case_key}")
            raise RuntimeError("Gateway returned no structured output")

        disclaimers = get_disclaimers(locale)
        structured = gateway_result.structured_output

        # Story 64.3: map accordion_titles from LLM output to AstroFreeResponseV1.
        # For the free plan, only headings are returned (no section content).
        accordion_titles = structured.get("accordion_titles") or []
        free_sections = [
            AstroFreeSection(key=f"section_{i}", heading=title, content="")
            for i, title in enumerate(accordion_titles)
        ]

        interpretation = AstroFreeResponseV1(
            title=_normalize_free_short_title(
                str(structured.get("title", "")),
                str(structured.get("summary", "")),
            ),
            summary=_normalize_free_short_summary(structured.get("summary", "")),
            sections=free_sections,
            disclaimers=disclaimers,
        )

        meta = InterpretationMeta(
            id=None,
            level="complete",
            use_case=use_case_key,
            persona_id=None,
            persona_name=None,
            prompt_version_id=gateway_result.meta.prompt_version_id,
            schema_version="v1",
            validation_status=gateway_result.meta.validation_status,
            was_fallback=gateway_result.meta.fallback_triggered,
            latency_ms=gateway_result.meta.latency_ms,
            request_id=request_id,
            cached=False,
        )

        # Persistence
        persist_payload = interpretation.model_dump()
        rejection_source_payload = structured if isinstance(structured, dict) else persist_payload
        rejected_outcome = _build_rejected_narrative_answer_outcome(
            level="complete",
            variant_code="free_short",
            schema_version="v1",
            request_id=request_id,
            gateway_result=gateway_result,
            persist_payload=rejection_source_payload,
            llm_astrology_input_v1=llm_astrology_input_v1,
        )
        if rejected_outcome is not None:
            emit_rejected_narrative_answer_log(
                logger,
                outcome=rejected_outcome,
                request_id=request_id,
                trace_id=trace_id,
                use_case=gateway_result.use_case,
            )
            try:
                _persist_rejected_narrative_answer_audit(
                    db,
                    user_id=user_id,
                    chart_id=chart_id,
                    level="complete",
                    variant_code="free_short",
                    gateway_result=gateway_result,
                    llm_astrology_input_v1=llm_astrology_input_v1,
                    rejected_outcome=rejected_outcome,
                )
            except Exception as audit_exc:
                db.rollback()
                logger.exception(
                    "Failed to persist rejected free_short natal audit request_id=%s error=%s",
                    request_id,
                    audit_exc,
                )
            interpretation = AstroFreeResponseV1(
                title="",
                summary=rejected_outcome.client_message,
                sections=[],
                highlights=[],
                advice=[],
                evidence=[],
                disclaimers=disclaimers,
            )
            meta.validation_status = "rejected"
            return NatalInterpretationResponse(
                data=NatalGatewayInterpretationData(
                    chart_id=chart_id,
                    use_case=use_case_key,
                    interpretation=interpretation,
                    meta=meta,
                    degraded_mode=degraded_mode_str,
                ),
                disclaimers=disclaimers,
            )

        prompt_version_uuid = _parse_prompt_version_uuid(gateway_result.meta.prompt_version_id)

        stmt_existing = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.user_id == user_id,
            UserNatalInterpretationModel.chart_id == chart_id,
            UserNatalInterpretationModel.level == InterpretationLevel.COMPLETE,
            UserNatalInterpretationModel.variant_code == "free_short",
        )
        existing_rows = list(
            db.execute(
                stmt_existing.order_by(
                    UserNatalInterpretationModel.created_at.desc(),
                    UserNatalInterpretationModel.id.desc(),
                )
            )
            .scalars()
            .all()
        )
        primary = existing_rows[0] if existing_rows else None
        for duplicate in existing_rows[1:]:
            db.delete(duplicate)

        if primary is None:
            primary = UserNatalInterpretationModel(
                user_id=user_id,
                chart_id=chart_id,
                level=InterpretationLevel.COMPLETE,
                use_case=use_case_key,
                variant_code="free_short",
                persona_id=None,
                persona_name=None,
                prompt_version_id=prompt_version_uuid,
                interpretation_payload=persist_payload,
                was_fallback=gateway_result.meta.fallback_triggered,
                degraded_mode=degraded_mode_str,
            )
            _apply_narrative_answer_audit(
                primary,
                level="complete",
                variant_code="free_short",
                schema_version="v1",
                request_id=request_id,
                gateway_result=gateway_result,
                persist_payload=persist_payload,
                llm_astrology_input_v1=llm_astrology_input_v1,
            )
            db.add(primary)
        else:
            primary.use_case = use_case_key
            primary.prompt_version_id = prompt_version_uuid
            primary.interpretation_payload = persist_payload
            primary.was_fallback = gateway_result.meta.fallback_triggered
            primary.degraded_mode = degraded_mode_str
            _apply_narrative_answer_audit(
                primary,
                level="complete",
                variant_code="free_short",
                schema_version="v1",
                request_id=request_id,
                gateway_result=gateway_result,
                persist_payload=persist_payload,
                llm_astrology_input_v1=llm_astrology_input_v1,
            )

        db.flush()
        meta.id = primary.id
        meta.persisted_at = primary.created_at or datetime_provider.utcnow()

        return NatalInterpretationResponse(
            data=NatalGatewayInterpretationData(
                chart_id=chart_id,
                use_case=use_case_key,
                interpretation=_without_public_evidence(interpretation),
                meta=meta,
                degraded_mode=degraded_mode_str,
            ),
            disclaimers=disclaimers,
        )

    @staticmethod
    def list_interpretations(
        db: Session,
        user_id: int,
        chart_id: Optional[str] = None,
        level: Optional[Literal["short", "complete"]] = None,
        persona_id: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[UserNatalInterpretationModel], int]:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.user_id == user_id,
            UserNatalInterpretationModel.use_case != NARRATIVE_ANSWER_AUDIT_USE_CASE,
        )
        if chart_id:
            stmt = stmt.where(UserNatalInterpretationModel.chart_id == chart_id)
        if level:
            db_level = (
                InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE
            )
            stmt = stmt.where(UserNatalInterpretationModel.level == db_level)
        if persona_id:
            try:
                stmt = stmt.where(UserNatalInterpretationModel.persona_id == uuid.UUID(persona_id))
            except (ValueError, TypeError):
                pass
        if module:
            # Match use_case based on module mapping if possible
            use_case = MODULE_TO_USE_CASE_KEY.get(module, module)
            stmt = stmt.where(UserNatalInterpretationModel.use_case == use_case)

        rows = list(
            db.execute(stmt.order_by(UserNatalInterpretationModel.created_at.desc()))
            .scalars()
            .all()
        )
        valid_rows: list[UserNatalInterpretationModel] = []
        deleted_any = False
        for row in rows:
            if row.use_case == CORRECTIVE_REGENERATION_PENDING_USE_CASE:
                continue
            if NatalInterpretationService._is_invalid_complete_interpretation(row):
                db.delete(row)
                deleted_any = True
                continue
            if NatalInterpretationService._purge_rejected_interpretation(db, row):
                deleted_any = True
                continue
            if not is_public_natal_interpretation(row):
                continue
            valid_rows.append(row)

        if deleted_any:
            db.commit()

        total = len(valid_rows)
        return valid_rows[offset : offset + limit], total

    @staticmethod
    def delete_interpretation(
        db: Session,
        user_id: int,
        interpretation_id: int,
        request_id: str,
        actor_role: str = "user",
    ) -> bool:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.id == interpretation_id,
            UserNatalInterpretationModel.user_id == user_id,
        )
        item = db.execute(stmt).scalar_one_or_none()
        if not item:
            return False

        # Audit before delete
        from app.domain.audit.safe_details import NatalInterpretationAuditDetails
        from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

        audit_payload = AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=user_id,
            actor_role=actor_role,
            action="natal_interpretation_deleted",
            target_type="natal_interpretation",
            target_id=str(interpretation_id),
            status="success",
            details=NatalInterpretationAuditDetails(
                target_interpretation_id=interpretation_id,
                chart_id=item.chart_id,
                level=item.level.value,
                persona_id=str(item.persona_id) if item.persona_id else None,
                created_at=item.created_at.isoformat(),
                deleted_at=datetime_provider.utcnow().isoformat(),
            ).model_dump(exclude_none=True),
        )

        db.delete(item)
        db.commit()

        try:
            AuditService.record_event(db, payload=audit_payload)
        except Exception as e:
            logger.warning(f"Failed to record audit event for interpretation deletion: {e}")

        return True

    @staticmethod
    def get_interpretation_by_id(
        db: Session,
        user_id: int,
        interpretation_id: int,
    ) -> Optional[UserNatalInterpretationModel]:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.id == interpretation_id,
            UserNatalInterpretationModel.user_id == user_id,
        )
        item = db.execute(stmt).scalar_one_or_none()
        if item and not is_public_natal_interpretation(item):
            if is_rejected_interpretation(item):
                NatalInterpretationService._purge_rejected_interpretation(db, item)
                db.commit()
            return None
        if item and NatalInterpretationService._is_invalid_complete_interpretation(item):
            db.delete(item)
            db.commit()
            return None
        return item

    @staticmethod
    def format_interpretation_response(
        model: UserNatalInterpretationModel,
        meta: InterpretationMeta,
        locale: str,
    ) -> NatalInterpretationResponse:
        """
        Formats a UserNatalInterpretationModel into a NatalInterpretationResponse.
        Handles schema versioning (v1, v2, v3).
        """
        meta.id = model.id
        disclaimers = get_disclaimers(locale)
        level = "complete" if model.level == InterpretationLevel.COMPLETE else "short"
        interpretation, schema_version = (
            NatalInterpretationService._deserialize_persisted_interpretation(
                model,
                level=level,
                locale=locale,
            )
        )

        meta.schema_version = schema_version
        raw_payload = (
            model.interpretation_payload if isinstance(model.interpretation_payload, dict) else {}
        )
        narrative_reading = load_narrative_reading_from_payload(raw_payload)

        return NatalInterpretationResponse(
            data=NatalGatewayInterpretationData(
                chart_id=model.chart_id,
                use_case=model.use_case,
                interpretation=_without_public_evidence(interpretation),
                meta=meta,
                degraded_mode=model.degraded_mode,
                narrative_natal_reading_v1=narrative_reading,
            ),
            disclaimers=disclaimers,
        )
