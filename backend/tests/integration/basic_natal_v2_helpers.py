# Commentaire global: helpers partages pour les preuves d'integration Basic natal V2.
"""Fabriques de test pour le pipeline Basic natal V2 sans appel provider reel."""

from __future__ import annotations

import json
from typing import Any

from app.domain.astrology.interpretation.basic_natal_reading_plan import BasicNatalReadingPlan
from app.domain.llm.runtime.contracts import (
    GatewayMeta,
    GatewayResult,
    NatalExecutionInput,
    UsageInfo,
)
from app.services.entitlement.entitlement_types import EffectiveEntitlementsSnapshot
from app.services.llm_generation.natal.interpretation_service import (
    _basic_natal_contract_from_draft,
    _build_basic_natal_reading_plan_for_runtime,
)
from app.services.llm_generation.natal.narrative_natal_reading_validator import (
    build_basic_natal_deterministic_fallback,
)
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.tests.helpers.natal_result_factory import make_natal_result


def basic_birth_profile() -> UserBirthProfileData:
    """Cree un profil de naissance stable pour les tests Basic V2."""
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )


def basic_entitlement_snapshot(user_id: int = 418) -> EffectiveEntitlementsSnapshot:
    """Retourne un snapshot Basic actif sans dependance au catalogue produit."""
    return EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=user_id,
        plan_code="basic",
        billing_status="active",
        entitlements={},
    )


def basic_runtime_plan(
    chart_id: str = "chart-basic-v2", locale: str = "fr-FR"
) -> BasicNatalReadingPlan:
    """Reconstruit le plan Basic attendu par le service pour une fixture natale."""
    return _build_basic_natal_reading_plan_for_runtime(
        natal_result=make_natal_result(),
        chart_id=chart_id,
        locale=locale,
    )


def valid_basic_draft(plan: BasicNatalReadingPlan) -> dict[str, object]:
    """Produit un brouillon provider valide en suivant strictement le plan."""
    return build_basic_natal_deterministic_fallback(plan)


def gateway_result_from_draft(
    natal_input: NatalExecutionInput,
    draft: dict[str, object],
    *,
    prompt_version_id: str = "11111111-1111-1111-1111-111111111111",
) -> GatewayResult:
    """Emballe un brouillon Basic dans une reponse gateway controlee."""
    return GatewayResult(
        use_case=natal_input.use_case_key,
        request_id=natal_input.request_id,
        trace_id=natal_input.trace_id,
        raw_output=json.dumps(draft),
        structured_output=draft,
        usage=UsageInfo(input_tokens=120, output_tokens=480, total_tokens=600),
        meta=GatewayMeta(
            latency_ms=20,
            cached=False,
            prompt_version_id=prompt_version_id,
            model="fake-basic-v2",
            output_schema_id="basic_natal_draft_v1",
            validation_status="valid",
            repair_attempted=False,
            fallback_triggered=False,
        ),
    )


def persisted_basic_payload(plan: BasicNatalReadingPlan) -> dict[str, Any]:
    """Construit un payload stocke compatible Basic V2 pour les tests de cache."""
    draft = valid_basic_draft(plan)
    contract = _basic_natal_contract_from_draft(accepted_draft=draft, reading_plan=plan)
    return {**draft, "basic_natal_interpretation_v2": contract.model_dump(mode="json")}
