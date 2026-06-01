# Commentaire global: runtime Basic full-reading non-live pour le contrat theme natal.
"""Execute la lecture Basic complete via un fake provider deterministe et auditable."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domain.astrology.natal_calculation import NatalResult
from app.domain.llm.runtime.theme_astral_provider_payload_builder import (
    build_basic_natal_prompt_payload,
)
from app.domain.theme_natal.generation_contracts import (
    resolve_theme_natal_generation_contract,
)
from app.domain.theme_natal.generation_schemas import (
    ThemeNatalBasicPublicChapter,
    ThemeNatalBasicPublicReading,
    ThemeNatalBasicRawProviderResponse,
    ThemeNatalFreePublicReading,
    ThemeNatalFreeRawProviderResponse,
)
from app.domain.theme_natal.product_action_resolver import resolve_theme_natal_reading_action
from app.domain.theme_natal.product_contract import (
    ThemeNatalEntitlementTier,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingDecisionStatus,
    ThemeNatalReadingProductDecision,
    ThemeNatalReadingProductEntitlement,
)
from app.infra.db.models.llm_generation_run import LLM_GENERATION_RUN_STATUS_ACCEPTED
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal.basic_natal_runtime_material import (
    build_basic_natal_reading_plan_for_runtime,
)
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)

_BASIC_PROVIDER_SCHEMA_VERSION = "theme_natal_basic_full_raw_v1"
_FREE_PROVIDER_SCHEMA_VERSION = "theme_natal_free_preview_raw_v1"
_TECHNICAL_LEAK_TOKENS = (
    "raw_provider_response",
    "parsed_raw_response",
    "generation_contract_hash",
    "generation_contract_snapshot_id",
    "prompt_hash",
    "data_hash",
    "provider_mode",
)
_MECHANICAL_PHRASES = (
    "en tant qu'ia",
    "en tant que modele",
    "je ne peux pas",
    "voici votre lecture",
)
_BASIC_SECTION_KEYS = ("identity", "resources", "relationships", "growth")


class ThemeNatalFakeProviderMode(StrEnum):
    """Modes de sortie controles du fake provider Basic."""

    VALID = "valid"
    INVALID_JSON = "invalid_json"
    UNKNOWN_FIELD = "unknown_field"
    EMPTY_SOURCE = "empty_source"
    INVENTED_FACT = "invented_fact"
    TECHNICAL_LEAK = "technical_leak"
    MECHANICAL_PHRASE = "mechanical_phrase"
    SHORT_SECTION = "short_section"


@dataclass(frozen=True, slots=True)
class ThemeNatalBasicFullReadingRuntimeRequest:
    """Entree stable du runtime Basic sans dependance au provider live."""

    user_id: int
    chart_id: str
    chart_numeric_id: int
    locale: str
    client_request_id: str
    provider_mode: ThemeNatalFakeProviderMode = ThemeNatalFakeProviderMode.VALID
    access_result: NatalChartLongEntitlementResult | None = None


@dataclass(frozen=True, slots=True)
class ThemeNatalBasicFullReadingRuntimeResult:
    """Resultat auditable d'une tentative Basic full-reading."""

    accepted: bool
    cached: bool
    slot_id: int
    run_id: int | None
    provider_mode: ThemeNatalFakeProviderMode
    decision: ThemeNatalReadingProductDecision
    generation_contract_key: str
    generation_contract_hash: str
    generation_contract_snapshot_id: str
    data_hash: str
    prompt_payload: dict[str, object]
    public_payload: dict[str, object] | None
    rejection_reason: dict[str, object] | None


class ThemeNatalBasicFullReadingRuntime:
    """Orchestre le premier chemin executable Basic sans appel LLM externe."""

    def generate(
        self,
        db: Session,
        *,
        natal_result: NatalResult,
        request: ThemeNatalBasicFullReadingRuntimeRequest,
    ) -> ThemeNatalBasicFullReadingRuntimeResult:
        """Execute la generation fake-provider et persiste slot/run selon l'acceptation."""
        decision = _resolve_basic_generation_decision(request)
        contract = decision.contract
        if (
            decision.status is not ThemeNatalReadingDecisionStatus.GENERATE_WITH_CONTRACT_KEY
            or contract is None
            or contract.contract_key is None
        ):
            raise ValueError("Basic full-reading generation contract is required")

        snapshot = resolve_theme_natal_generation_contract(contract.contract_key)
        reading_plan = build_basic_natal_reading_plan_for_runtime(
            natal_result=natal_result,
            chart_id=request.chart_id,
            locale=request.locale,
        )
        prompt_payload = build_basic_natal_prompt_payload(reading_plan)
        data_hash = _stable_hash(prompt_payload)
        slot_key = ThemeNatalReadingSlotKey(
            user_id=request.user_id,
            chart_id=request.chart_id,
            product_plan=contract.entitlement.tier.value,
            output_variant=contract.output_variant,
            contract_version=snapshot.generation_contract_key,
        )
        cached_slot = ThemeNatalReadingSlotService.get_public_slot_by_key(db, key=slot_key)
        if cached_slot is not None:
            return ThemeNatalBasicFullReadingRuntimeResult(
                accepted=True,
                cached=True,
                slot_id=cached_slot.id,
                run_id=cached_slot.source_generation_run_id,
                provider_mode=request.provider_mode,
                decision=decision,
                generation_contract_key=snapshot.generation_contract_key,
                generation_contract_hash=snapshot.generation_contract_hash,
                generation_contract_snapshot_id=snapshot.generation_contract_snapshot_id,
                data_hash=data_hash,
                prompt_payload=prompt_payload,
                public_payload=dict(cached_slot.public_payload or {}),
                rejection_reason=None,
            )

        prompt_hash = _stable_hash(
            {
                "prompt_contract": snapshot.contract.prompt_contract.model_dump(mode="json"),
                "prompt_payload": prompt_payload,
            }
        )
        claim = ThemeNatalReadingSlotService.claim_generation_run(
            db,
            key=slot_key,
            client_request_id=request.client_request_id,
            prompt_hash=prompt_hash,
            data_hash=data_hash,
            engine_profile_version=snapshot.engine_profile_version,
            output_schema_version=snapshot.output_schema_version,
            generation_contract_key=snapshot.generation_contract_key,
            generation_contract_hash=snapshot.generation_contract_hash,
            generation_contract_snapshot_id=snapshot.generation_contract_snapshot_id,
            provider_mode=request.provider_mode.value,
        )
        if (
            not claim.created_run
            and claim.run.status == LLM_GENERATION_RUN_STATUS_ACCEPTED
            and claim.slot.public_payload is not None
        ):
            return ThemeNatalBasicFullReadingRuntimeResult(
                accepted=True,
                cached=True,
                slot_id=claim.slot.id,
                run_id=claim.run.id,
                provider_mode=request.provider_mode,
                decision=decision,
                generation_contract_key=snapshot.generation_contract_key,
                generation_contract_hash=snapshot.generation_contract_hash,
                generation_contract_snapshot_id=snapshot.generation_contract_snapshot_id,
                data_hash=data_hash,
                prompt_payload=prompt_payload,
                public_payload=dict(claim.slot.public_payload),
                rejection_reason=None,
            )

        raw_provider_text = _fake_basic_provider_response(
            mode=request.provider_mode,
            prompt_payload=prompt_payload,
        )
        parsed_raw, validation_errors = _parse_and_validate_basic_provider_response(
            raw_provider_text=raw_provider_text,
            prompt_payload=prompt_payload,
        )
        raw_provider_response = _raw_provider_evidence(raw_provider_text, parsed_raw)
        if parsed_raw is None:
            rejection_reason = {
                "code": "theme_natal_basic_provider_rejected",
                "provider_mode": request.provider_mode.value,
            }
            ThemeNatalReadingSlotService.record_rejected_run(
                db,
                run_id=claim.run.id,
                raw_provider_response=raw_provider_response,
                parsed_raw_response=None,
                validation_errors=validation_errors,
                rejection_reason=rejection_reason,
            )
            return ThemeNatalBasicFullReadingRuntimeResult(
                accepted=False,
                cached=False,
                slot_id=claim.slot.id,
                run_id=claim.run.id,
                provider_mode=request.provider_mode,
                decision=decision,
                generation_contract_key=snapshot.generation_contract_key,
                generation_contract_hash=snapshot.generation_contract_hash,
                generation_contract_snapshot_id=snapshot.generation_contract_snapshot_id,
                data_hash=data_hash,
                prompt_payload=prompt_payload,
                public_payload=None,
                rejection_reason=rejection_reason,
            )

        public_payload = _project_basic_public_payload(parsed_raw).model_dump(mode="json")
        claim.run.raw_provider_response = raw_provider_response
        claim.run.parsed_raw_response = parsed_raw.model_dump(mode="json")
        db.commit()
        publication = ThemeNatalReadingSlotService.publish_accepted_payload(
            db,
            run_id=claim.run.id,
            public_payload=public_payload,
        )
        if request.access_result is not None:
            ThemeNatalReadingSlotService.consume_quota_after_publication(
                db,
                user_id=request.user_id,
                access_result=request.access_result,
                publication=publication,
            )
        return ThemeNatalBasicFullReadingRuntimeResult(
            accepted=True,
            cached=False,
            slot_id=publication.slot.id,
            run_id=publication.run.id,
            provider_mode=request.provider_mode,
            decision=decision,
            generation_contract_key=snapshot.generation_contract_key,
            generation_contract_hash=snapshot.generation_contract_hash,
            generation_contract_snapshot_id=snapshot.generation_contract_snapshot_id,
            data_hash=data_hash,
            prompt_payload=prompt_payload,
            public_payload=dict(publication.slot.public_payload or {}),
            rejection_reason=None,
        )


def build_contractual_theme_natal_free_preview() -> dict[str, object]:
    """Construit la preview Free fake contractuelle sans route generative legacy."""
    raw = ThemeNatalFreeRawProviderResponse.model_validate(
        {
            "schema_version": _FREE_PROVIDER_SCHEMA_VERSION,
            "preview_title": "Un aperçu symbolique de votre thème",
            "preview_summary": (
                "Cette preview met en avant quelques repères publics et ouvre la porte "
                "à une lecture complète sans exposer de trace technique de génération."
            ),
            "highlights": (
                {
                    "title": "Fil conducteur",
                    "narrative": "Une dynamique centrale ressort avec nuance et progressivité.",
                    "evidence_refs": (
                        {
                            "source_id": "free-preview-source-1",
                            "source_kind": "safety_rule",
                            "relevance": "Repere public non technique.",
                        },
                    ),
                },
                {
                    "title": "Point d'attention",
                    "narrative": "La lecture complète précisera les ressources et les tensions.",
                    "evidence_refs": (
                        {
                            "source_id": "free-preview-source-2",
                            "source_kind": "safety_rule",
                            "relevance": "Repere public non technique.",
                        },
                    ),
                },
            ),
            "safety_notes": ("Lecture symbolique sans conseil medical, juridique ou financier.",),
        }
    )
    public = ThemeNatalFreePublicReading(
        schema_version="theme_natal_free_preview_public_v1",
        title=raw.preview_title,
        summary=raw.preview_summary,
        highlights=tuple(highlight.title for highlight in raw.highlights),
        call_to_action="Débloquez la lecture Basic complète pour obtenir les chapitres détaillés.",
    )
    return public.model_dump(mode="json")


def _resolve_basic_generation_decision(
    request: ThemeNatalBasicFullReadingRuntimeRequest,
) -> ThemeNatalReadingProductDecision:
    """Selectionne le contrat produit Basic via le resolver canonique CS-427."""
    return resolve_theme_natal_reading_action(
        ThemeNatalReadingActionRequest(
            user_id=request.user_id,
            chart_id=request.chart_numeric_id,
            action=ThemeNatalReadingAction.GENERATE_FULL,
            entitlement=ThemeNatalReadingProductEntitlement(
                tier=ThemeNatalEntitlementTier.BASIC,
                granted=True,
                reason_code="basic_fake_provider_runtime",
            ),
            locale=request.locale,
        )
    )


def _fake_basic_provider_response(
    *,
    mode: ThemeNatalFakeProviderMode,
    prompt_payload: dict[str, object],
) -> str:
    """Retourne une reponse provider deterministe pour chaque mode contractuel."""
    if mode is ThemeNatalFakeProviderMode.INVALID_JSON:
        return '{"schema_version":'

    response = _valid_basic_provider_payload(prompt_payload)
    if mode is ThemeNatalFakeProviderMode.UNKNOWN_FIELD:
        response["debug_trace"] = "trace technique interdite"
    elif mode is ThemeNatalFakeProviderMode.EMPTY_SOURCE:
        response["sections"][0]["source_refs"][0]["source_id"] = ""
    elif mode is ThemeNatalFakeProviderMode.INVENTED_FACT:
        response["sections"][0]["source_refs"][0]["source_id"] = "invented-vulcan-factor"
    elif mode is ThemeNatalFakeProviderMode.TECHNICAL_LEAK:
        response["sections"][0]["narrative"] += " raw_provider_response={secret}"
    elif mode is ThemeNatalFakeProviderMode.MECHANICAL_PHRASE:
        response["sections"][0]["narrative"] = "En tant qu'IA, " + str(
            response["sections"][0]["narrative"]
        )
    elif mode is ThemeNatalFakeProviderMode.SHORT_SECTION:
        response["sections"][0]["narrative"] = "Section trop courte."

    return json.dumps(response, ensure_ascii=False, sort_keys=True)


def _valid_basic_provider_payload(prompt_payload: dict[str, object]) -> dict[str, Any]:
    evidence_ids = _allowed_source_ids(prompt_payload)
    source_cycle = evidence_ids or ("basic-plan-source",)
    sections: list[dict[str, object]] = []
    for index, section_key in enumerate(_BASIC_SECTION_KEYS):
        sections.append(
            {
                "key": section_key,
                "heading": _heading_for_section(section_key),
                "narrative": _section_narrative(section_key),
                "source_refs": (
                    {
                        "source_id": source_cycle[index % len(source_cycle)],
                        "source_kind": "reading_plan",
                        "relevance": "Repere public issu du BasicNatalReadingPlan.",
                    },
                ),
                "limitations": (),
            }
        )
    return {
        "schema_version": _BASIC_PROVIDER_SCHEMA_VERSION,
        "title": "Lecture Basic complète du thème natal",
        "introduction": _long_text(
            "Cette lecture relie les repères publics du plan Basic pour proposer une "
            "synthèse claire, prudente et exploitable sans exposer de donnée technique."
        ),
        "sections": tuple(sections),
        "conclusion": _long_text(
            "La synthèse finale rassemble les thèmes dominants en gardant une lecture "
            "symbolique et nuancée, centrée sur les ressources déjà validées."
        ),
        "safety_notes": ("Lecture symbolique sans conseil medical, juridique ou financier.",),
    }


def _parse_and_validate_basic_provider_response(
    *,
    raw_provider_text: str,
    prompt_payload: dict[str, object],
) -> tuple[ThemeNatalBasicRawProviderResponse | None, list[dict[str, object]] | None]:
    try:
        decoded = json.loads(raw_provider_text)
    except json.JSONDecodeError as exc:
        return None, [{"code": "invalid_json", "message": exc.msg}]
    try:
        raw = ThemeNatalBasicRawProviderResponse.model_validate(decoded)
    except ValidationError as exc:
        return None, [
            {
                "code": "schema_validation",
                "location": [str(item) for item in error["loc"]],
                "message": str(error["msg"]),
            }
            for error in exc.errors()
        ]

    semantic_errors = _semantic_validation_errors(raw, prompt_payload)
    if semantic_errors:
        return None, semantic_errors
    return raw, None


def _semantic_validation_errors(
    raw: ThemeNatalBasicRawProviderResponse,
    prompt_payload: dict[str, object],
) -> list[dict[str, object]]:
    allowed_sources = set(_allowed_source_ids(prompt_payload))
    errors: list[dict[str, object]] = []
    for section in raw.sections:
        for source_ref in section.source_refs:
            if source_ref.source_id not in allowed_sources:
                errors.append(
                    {
                        "code": "source_not_in_basic_plan",
                        "source_id": source_ref.source_id,
                        "section": section.key,
                    }
                )
        section_text = " ".join(
            (section.heading, section.narrative, *(ref.relevance for ref in section.source_refs))
        )
        errors.extend(_text_guard_errors(section_text, section=section.key))
    full_text = " ".join((raw.title, raw.introduction, raw.conclusion, *raw.safety_notes))
    errors.extend(_text_guard_errors(full_text, section="document"))
    return errors


def _text_guard_errors(text: str, *, section: str) -> list[dict[str, object]]:
    normalized = text.casefold()
    errors = [
        {"code": "technical_leak", "section": section, "token": token}
        for token in _TECHNICAL_LEAK_TOKENS
        if token in normalized
    ]
    errors.extend(
        {"code": "mechanical_phrase", "section": section, "phrase": phrase}
        for phrase in _MECHANICAL_PHRASES
        if phrase in normalized
    )
    return errors


def _project_basic_public_payload(
    raw: ThemeNatalBasicRawProviderResponse,
) -> ThemeNatalBasicPublicReading:
    """Projette le raw provider en payload public sans trace provider."""
    return ThemeNatalBasicPublicReading(
        schema_version="theme_natal_basic_full_public_v1",
        title=raw.title,
        introduction=raw.introduction,
        chapters=tuple(
            ThemeNatalBasicPublicChapter(
                key=section.key,
                title=section.heading,
                text=section.narrative,
                source_annex=tuple(ref.relevance for ref in section.source_refs),
            )
            for section in raw.sections
        ),
        conclusion=raw.conclusion,
        disclaimers=("Lecture symbolique a replacer dans votre contexte personnel.",),
    )


def _allowed_source_ids(prompt_payload: dict[str, object]) -> tuple[str, ...]:
    evidence = prompt_payload.get("editorial_evidence")
    if not isinstance(evidence, list):
        return ()
    source_ids = []
    for index, item in enumerate(evidence, start=1):
        if isinstance(item, dict):
            label = item.get("label")
            if isinstance(label, str) and label.strip():
                source_ids.append(f"plan-evidence-{index}")
    return tuple(source_ids)


def _raw_provider_evidence(
    raw_provider_text: str,
    parsed_raw: ThemeNatalBasicRawProviderResponse | None,
) -> dict[str, object]:
    raw_hash = hashlib.sha256(raw_provider_text.encode("utf-8")).hexdigest()
    return {
        "provider": "fake_provider",
        "raw_response_hash": raw_hash,
        "raw_response": raw_provider_text,
        "schema_version": (
            parsed_raw.schema_version if parsed_raw is not None else _BASIC_PROVIDER_SCHEMA_VERSION
        ),
    }


def _stable_hash(payload: object) -> str:
    serialized = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _heading_for_section(section_key: str) -> str:
    return {
        "identity": "Identité et fil conducteur",
        "resources": "Ressources disponibles",
        "relationships": "Lien aux autres",
        "growth": "Pistes de croissance",
    }[section_key]


def _section_narrative(section_key: str) -> str:
    return _long_text(
        {
            "identity": (
                "Le fil identitaire se construit autour d'une présence claire, capable "
                "d'organiser les élans personnels sans perdre la nuance."
            ),
            "resources": (
                "Les ressources principales invitent à transformer les appuis stables "
                "en choix concrets, avec une attention particulière au rythme intérieur."
            ),
            "relationships": (
                "La relation aux autres gagne en qualité lorsque l'expression reste "
                "lisible, progressive et reliée aux besoins déjà reconnus."
            ),
            "growth": (
                "La croissance personnelle se nourrit d'un équilibre entre initiative, "
                "écoute et intégration patiente des tensions utiles."
            ),
        }[section_key]
    )


def _long_text(seed: str) -> str:
    return " ".join((seed, seed, seed))


__all__ = [
    "ThemeNatalBasicFullReadingRuntime",
    "ThemeNatalBasicFullReadingRuntimeRequest",
    "ThemeNatalBasicFullReadingRuntimeResult",
    "ThemeNatalFakeProviderMode",
    "build_contractual_theme_natal_free_preview",
]
