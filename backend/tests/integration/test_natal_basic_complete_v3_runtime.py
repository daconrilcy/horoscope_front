# Commentaire global: preuves runtime Basic complete pour le pipeline natal V3.
"""Valide le parcours Basic complete avec un gateway controle et sans provider reel."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy import text

from app.domain.astrology.reading import BASIC_NATAL_PUBLIC_SCHEMA_VERSION
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import (
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    NatalExecutionInput,
    UsageInfo,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.main import app
from app.services.entitlement.entitlement_types import EffectiveEntitlementsSnapshot
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.natal.stored_interpretation_payload import (
    BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY,
)
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.tests.helpers.natal_result_factory import make_natal_result
from tests.integration.basic_natal_v2_helpers import (
    basic_runtime_plan,
    gateway_result_from_draft,
    valid_basic_draft,
)


def _long_text(label: str, count: int) -> str:
    """Construit un texte V3 valide sans padding mono-mot."""
    return " ".join(
        f"{label} porte une nuance narrative distincte et verifiable numero {index}."
        for index in range(count)
    )


def _basic_v3_payload() -> dict[str, object]:
    """Retourne une fixture AstroResponse_v3 compatible lecture Basic complete."""
    return {
        "title": "Lecture Basic complete V3",
        "summary": _long_text("La synthese Basic V3", 28),
        "sections": [
            {
                "key": "overall",
                "heading": "Votre personnalite",
                "content": _long_text("La personnalite", 34),
            },
            {
                "key": "inner_life",
                "heading": "Votre monde emotionnel",
                "content": _long_text("Le monde emotionnel", 34),
            },
            {
                "key": "relationships",
                "heading": "Vos relations",
                "content": _long_text("Les relations", 34),
            },
            {
                "key": "career",
                "heading": "Votre vocation",
                "content": _long_text("La vocation", 34),
            },
            {
                "key": "growth_direction",
                "heading": "Votre chemin d evolution",
                "content": _long_text("Le chemin d evolution", 34),
            },
        ],
        "highlights": [
            "Elan personnel valorise",
            "Rythme interieur mobilise",
            "Presence relationnelle structuree",
            "Cap professionnel visible",
            "Dynamique harmonieuse active",
        ],
        "advice": [
            "Rester concret",
            "Ecouter le rythme interieur",
            "Clarifier les attentes",
            "Choisir une priorite",
            "Transformer les tensions en cap",
        ],
        "evidence": ["SUN", "MOON", "HOUSE_10", "TRINE", "HOUSE_1"],
    }


def _birth_profile() -> UserBirthProfileData:
    """Cree un profil de naissance minimal pour le service natal."""
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )


def _entitlement_snapshot() -> EffectiveEntitlementsSnapshot:
    """Fournit un plan Basic controle pour la resolution runtime."""
    return EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=408,
        plan_code="basic",
        billing_status="active",
        entitlements={},
    )


def _llm_astrology_input_v1() -> dict[str, object]:
    """Expose les seules preuves internes requises par le validateur narratif."""
    return {
        "contract_version": "llm_astrology_input_v1.contract.v1",
        "provenance": {
            "llm_input_hash": "a" * 64,
            "projection_hash": "b" * 64,
        },
        "evidence": {
            "grounding_status": "grounded",
            "evidence_refs": [
                {
                    "section_id": "llm_astrology_input_v1",
                    "source_type": "projection_version",
                    "source_id": "projection",
                    "source_version": "structured_facts_v1.contract.v1",
                    "source_hash": "b" * 64,
                }
            ],
        },
        "shaping": {
            "support_elements": [
                {"code": "source_label", "value": "Soleil en Gemeaux"},
                {"code": "highlight", "value": "Maison dix active"},
                {"code": "personalization_note", "value": "Lecture Basic issue du theme natal."},
            ]
        },
        "facts": {
            "positions": [
                {"planet_code": "sun", "code": "SUN"},
                {"planet_code": "moon", "code": "MOON"},
            ],
            "houses": [{"house_number": 10}, {"house_number": 1}],
            "major_aspects": [
                {
                    "code": "TRINE",
                    "aspect_code": "trine",
                    "participant_codes": ["SUN", "MOON"],
                }
            ],
            "dominants": [],
        },
        "signals": {"interpretive_signal_codes": {}},
        "limits": {"missing_data": {"empty_collections": []}},
    }


def _gateway_result(natal_input: NatalExecutionInput) -> GatewayResult:
    """Fabrique une reponse gateway V3 acceptee pour Basic complete."""
    payload = _basic_v3_payload()
    return GatewayResult(
        use_case=natal_input.use_case_key,
        request_id=natal_input.request_id,
        trace_id=natal_input.trace_id,
        raw_output=json.dumps(payload),
        structured_output=payload,
        usage=UsageInfo(input_tokens=120, output_tokens=480, total_tokens=600),
        meta=GatewayMeta(
            latency_ms=20,
            cached=False,
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            model="fake-basic-v3",
            output_schema_id="AstroResponse_v3",
            validation_status="valid",
            repair_attempted=False,
            fallback_triggered=False,
        ),
    )


@pytest.mark.asyncio
async def test_basic_complete_runtime_uses_basic_v2_and_persists_contract(db) -> None:
    """Prouve le use_case, les metas V2 et la persistance contractuelle acceptee."""
    captured_inputs: list[NatalExecutionInput] = []
    plan = basic_runtime_plan(chart_id="chart-basic-v3")
    provider_draft = valid_basic_draft(plan)

    async def fake_generate_natal_interpretation(
        natal_input: NatalExecutionInput, db: Any | None = None
    ) -> GatewayResult:
        captured_inputs.append(natal_input)
        return gateway_result_from_draft(natal_input, provider_draft)

    with (
        patch.object(
            AIEngineAdapter,
            "generate_natal_interpretation",
            side_effect=fake_generate_natal_interpretation,
        ),
        patch(
            "app.services.entitlement.effective_entitlement_resolver_service."
            "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
            return_value=_entitlement_snapshot(),
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "LlmTokenUsageService.record_usage"
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "_build_llm_astrology_input_v1",
            return_value=_llm_astrology_input_v1(),
        ),
        patch.object(type(db), "refresh", lambda self, instance: None),
    ):
        response = await NatalInterpretationService.interpret(
            db=db,
            user_id=408,
            chart_id="chart-basic-v3",
            natal_result=make_natal_result(),
            birth_profile=_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-v3",
            trace_id="trace-basic-v3",
            force_refresh=True,
            variant_code="single_astrologer",
        )

    assert len(captured_inputs) == 1
    natal_input = captured_inputs[0]
    assert natal_input.use_case_key == "natal_interpretation"
    assert natal_input.plan == "basic"
    assert natal_input.validation_strict is True

    assert response.data.use_case == "natal_interpretation"
    assert response.data.meta.schema_version == BASIC_NATAL_PUBLIC_SCHEMA_VERSION
    assert response.data.meta.validation_status == "valid"
    assert response.data.meta.repair_attempted is False
    assert response.data.meta.fallback_triggered is False
    assert response.data.basic_natal_interpretation_v2 is not None
    assert response.data.basic_natal_interpretation_v2.schema_version == (
        BASIC_NATAL_PUBLIC_SCHEMA_VERSION
    )
    assert response.data.basic_natal_interpretation_v2.public_evidence

    persisted = (
        db.execute(
            text(
                "SELECT use_case, grounding_status, interpretation_payload "
                "FROM user_natal_interpretations WHERE id = :id"
            ),
            {"id": response.data.meta.id},
        )
        .mappings()
        .one()
    )
    assert persisted["use_case"] == "natal_interpretation"
    assert persisted["grounding_status"] == "grounded"
    persisted_payload = json.loads(persisted["interpretation_payload"])
    persisted_reading = persisted_payload[BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY]
    assert persisted_reading["schema_version"] == BASIC_NATAL_PUBLIC_SCHEMA_VERSION
    assert persisted_reading["public_evidence"]


@pytest.mark.asyncio
async def test_adapter_maps_basic_complete_to_natal_interpretation_assembly(monkeypatch) -> None:
    """Prouve la cible runtime natal/interpretation/basic/fr-FR avant provider."""
    captured_requests = []

    async def fake_execute_request(
        self: LLMGateway, request: LLMExecutionRequest, db: Any | None = None
    ) -> GatewayResult:
        captured_requests.append(request)
        return _gateway_result(
            NatalExecutionInput(
                use_case_key=request.user_input.use_case,
                locale=request.user_input.locale,
                level="complete",
                llm_astrology_input_v1={},
                plan=request.user_input.plan,
                user_id=request.user_id or 0,
                request_id=request.request_id,
                trace_id=request.trace_id,
            )
        )

    monkeypatch.setattr(LLMGateway, "execute_request", fake_execute_request)

    await AIEngineAdapter.generate_natal_interpretation(
        natal_input=NatalExecutionInput(
            use_case_key="natal_interpretation",
            locale="fr-FR",
            level="complete",
            llm_astrology_input_v1={"contract_version": "llm_astrology_input_v1.contract.v1"},
            plan="basic",
            validation_strict=True,
            user_id=408,
            request_id="req-assembly-basic",
            trace_id="trace-assembly-basic",
        )
    )

    assert len(captured_requests) == 1
    request = captured_requests[0]
    assert request.user_input.use_case == "natal_interpretation"
    assert request.user_input.feature == "natal"
    assert request.user_input.subfeature == "interpretation"
    assert request.user_input.plan == "basic"
    assert request.user_input.locale == "fr-FR"
    assert request.flags.validation_strict is True
    assembly_target = (
        f"{request.user_input.feature}/"
        f"{request.user_input.subfeature}/"
        f"{request.user_input.plan}/"
        f"{request.user_input.locale}"
    )
    assert assembly_target == "natal/interpretation/basic/fr-FR"
    assert (
        LLMGateway()._normalize_plan_for_assembly(
            "basic",
            feature="natal",
            subfeature="interpretation",
            use_case="natal_interpretation",
        )
        == "basic"
    )
    assert (
        LLMGateway()._normalize_plan_for_assembly(
            "basic",
            feature="natal",
            subfeature="interpretation",
            use_case="natal_interpretation_short",
        )
        == "free"
    )


def test_public_natal_routes_and_openapi_remain_loadable() -> None:
    """Verifie les routes publiques et l'ancien POST documente en endpoint gone."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    openapi = app.openapi()

    assert "/v1/natal/interpretation" in route_paths
    assert "/v1/natal/interpretations/{interpretation_id}" in route_paths
    assert "paths" in openapi
    assert "/v1/natal/interpretation" in openapi["paths"]
    operation = openapi["paths"]["/v1/natal/interpretation"]["post"]
    assert "200" not in operation["responses"]
    assert "410" in operation["responses"]
