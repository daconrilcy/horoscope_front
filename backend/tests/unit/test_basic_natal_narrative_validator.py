# Commentaire global: tests du validateur narratif Basic adosse au BasicNatalReadingPlan.
"""Verifie la validation, la reparation et le fallback des brouillons narratifs Basic."""

from __future__ import annotations

import inspect

from app.domain.astrology.interpretation.basic_natal_reading_plan import (
    BasicNatalPlanSection,
    BasicNatalPublicEvidence,
    BasicNatalReadingPlan,
)
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.services.llm_generation.natal import interpretation_service
from app.services.llm_generation.natal.interpretation_service import (
    _basic_natal_contract_from_draft,
    _validate_basic_natal_draft_output,
)
from app.services.llm_generation.natal.narrative_natal_reading_validator import (
    build_basic_natal_rejection_outcome,
    validate_basic_natal_draft_against_plan,
    validate_repair_or_fallback_basic_natal_draft,
)


def _date_only_plan() -> BasicNatalReadingPlan:
    """Construit un plan date-only minimal sans surfaces horaires."""
    return BasicNatalReadingPlan(
        level="basic",
        locale="fr-FR",
        engine_version="basic-natal-reading-v1",
        sections=(
            BasicNatalPlanSection(
                section_code="identity",
                heading_intent="Identite et elan central",
                target_length_words=120,
                theme_codes=("core_identity",),
                required_fact_ids=("sun_balance",),
                forbidden_fact_ids=("asc_lion",),
                forbidden_fact_families=("angle", "house_emphasis", "rulership"),
                supporting_evidence_ids=("ev_sun",),
            ),
            BasicNatalPlanSection(
                section_code="values",
                heading_intent="Valeurs et ressources",
                target_length_words=120,
                theme_codes=("resources_and_values",),
                required_fact_ids=("moon_taurus",),
                forbidden_fact_ids=(),
                forbidden_fact_families=("angle", "house_emphasis", "rulership"),
                supporting_evidence_ids=("ev_moon",),
            ),
        ),
        public_evidence=(
            BasicNatalPublicEvidence(
                id="ev_sun",
                label="Soleil en Balance",
                explanation="Elan relationnel nuance",
                source_section_codes=("identity",),
            ),
            BasicNatalPublicEvidence(
                id="ev_moon",
                label="Lune en Taureau",
                explanation="Besoin de stabilite",
                source_section_codes=("values",),
            ),
        ),
        style_constraints=("Rester en vous.",),
        limitations=("Lecture sans heure de naissance: surfaces horaires exclues.",),
        disclaimers=("Lecture symbolique sans prediction certaine.",),
    )


def _valid_draft(plan: BasicNatalReadingPlan | None = None) -> dict[str, object]:
    """Retourne un brouillon conforme au plan de test."""
    plan = plan or _date_only_plan()
    return {
        "sections": [
            {
                "section_code": "identity",
                "heading": "Identite",
                "content": (
                    "Vous avancez avec un elan relationnel nuance et lisible. "
                    "Cette dynamique peut aider a choisir des liens plus equilibres."
                ),
                "evidence_ids": ["ev_sun"],
                "fact_ids": ["sun_balance"],
            },
            {
                "section_code": "values",
                "heading": "Valeurs",
                "content": (
                    "Votre besoin de stabilite soutient des choix progressifs. "
                    "Il peut se manifester par une recherche de rythme simple et fiable."
                ),
                "evidence_ids": ["ev_moon"],
                "fact_ids": ["moon_taurus"],
            },
        ],
        "limitations": list(plan.limitations),
        "disclaimers": list(plan.disclaimers),
        "public_evidence_ids": ["ev_sun", "ev_moon"],
        "public_sources": ["Soleil en Balance", "Lune en Taureau"],
    }


def _plan_with_synthesis() -> BasicNatalReadingPlan:
    """Ajoute un fil conducteur pour tester la projection publique dedupliquee."""
    base = _date_only_plan()
    synthesis = BasicNatalPlanSection(
        section_code="synthesis",
        heading_intent="Fil conducteur",
        target_length_words=120,
        theme_codes=("synthesis",),
        required_fact_ids=("sun_balance",),
        forbidden_fact_ids=(),
        forbidden_fact_families=(),
        supporting_evidence_ids=("ev_sun",),
    )
    return BasicNatalReadingPlan(
        level=base.level,
        locale=base.locale,
        engine_version=base.engine_version,
        sections=(synthesis, *base.sections),
        public_evidence=base.public_evidence,
        style_constraints=base.style_constraints,
        limitations=base.limitations,
        disclaimers=base.disclaimers,
    )


def _errors(draft: dict[str, object]) -> list[str]:
    """Valide le brouillon courant et retourne les codes d'erreur."""
    return validate_basic_natal_draft_against_plan(
        draft=draft,
        reading_plan=_date_only_plan(),
        request_id="req-basic-validator",
    ).validation_errors


def _gateway_result(payload: dict[str, object]) -> GatewayResult:
    """Construit une sortie gateway minimale pour les helpers runtime Basic."""
    return GatewayResult(
        use_case="natal_interpretation",
        request_id="req-basic-runtime",
        trace_id="trace-basic-runtime",
        raw_output="{}",
        structured_output=payload,
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=10,
            model="gpt-test",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            plan="basic",
            provider="openai",
        ),
    )


def test_valid_basic_draft_keeps_plan_limitations_disclaimers_and_sources() -> None:
    """Un brouillon complet garde les contraintes et sources publiques du plan."""
    result = validate_basic_natal_draft_against_plan(
        draft=_valid_draft(),
        reading_plan=_date_only_plan(),
        request_id="req-basic-validator",
    )

    assert result.is_valid is True
    assert result.validation_errors == []
    assert result.request_id == "req-basic-validator"
    assert result.engine_version == "basic-natal-reading-v1"
    assert result.schema_version == "basic_natal_interpretation_v2"


def test_missing_and_unauthorized_sections_are_invalid() -> None:
    """Les sections absentes ou non demandees par le plan sont refusees."""
    draft = _valid_draft()
    draft["sections"] = [
        draft["sections"][0],
        {
            "section_code": "vocation",
            "heading": "Vocation",
            "content": "Votre vocation se precise.",
            "evidence_ids": ["ev_sun"],
            "fact_ids": ["sun_balance"],
        },
    ]

    errors = _errors(draft)

    assert "missing_requested_section:values" in errors
    assert "unauthorized_section:vocation" in errors
    assert "unsupported_vocation_section" in errors


def test_malformed_section_entry_is_invalid_even_when_required_sections_exist() -> None:
    """Une entree section brute ne peut pas etre ignoree silencieusement."""
    draft = _valid_draft()
    draft["sections"].append("section brute non auditable")

    errors = _errors(draft)

    assert "invalid_section_entry" in errors


def test_unsupported_fact_and_date_only_time_surface_are_invalid() -> None:
    """Le validateur refuse les faits absents du plan et les marqueurs horaires date-only."""
    draft = _valid_draft()
    draft["sections"][0]["content"] = "Votre Ascendant et Jupiter dominent la maison 10."
    draft["sections"][0]["fact_ids"] = ["sun_balance", "jupiter_dominant"]

    errors = _errors(draft)

    assert "unsupported_generated_fact:jupiter_dominant" in errors
    assert "unsupported_generated_fact:jupiter" in errors
    assert "date_only_time_based_fact" in errors


def test_technical_marker_mixed_person_and_prescriptive_advice_are_invalid() -> None:
    """Les marqueurs techniques, le melange tu/vous et les conseils prescriptifs sont rejetes."""
    draft = _valid_draft()
    draft["sections"][0]["content"] = (
        "Vous devez investir maintenant; tu verras le ranking_score interne."
    )

    errors = _errors(draft)

    assert "technical_or_jargon_marker" in errors
    assert "mixed_grammatical_person" in errors
    assert "prescriptive_advice" in errors


def test_mechanical_source_listing_and_raw_labels_are_invalid() -> None:
    """Les phrases templates et libelles anglais observes sont rejetes."""
    denied_fragments = (
        "Luminaire: moon",
        "Position planetaire: saturn",
        "north node",
        "south node",
        "Ce repere retient un signal descriptif.",
        (
            "cette lecture s'appuie uniquement sur ces sources "
            "avec une confiance editoriale controlee."
        ),
    )

    for fragment in denied_fragments:
        draft = _valid_draft()
        draft["sections"][0]["content"] = fragment
        errors = _errors(draft)

        assert (
            "technical_or_jargon_marker" in errors or "source_listing_as_content:identity" in errors
        )


def test_disclaimer_only_and_single_sentence_theme_are_invalid() -> None:
    """Un disclaimer ou une phrase unique ne remplace pas le contenu editorial."""
    draft = _valid_draft()
    draft["sections"][0]["content"] = "Lecture symbolique sans prediction certaine."

    errors = _errors(draft)

    assert "weak_editorial_section:identity" in errors
    assert "disclaimer_only_section:identity" in errors


def test_missing_limitation_disclaimer_and_public_sources_are_invalid() -> None:
    """Les limitations, disclaimers et sources publiques du plan restent obligatoires."""
    draft = _valid_draft()
    draft["limitations"] = []
    draft["disclaimers"] = []
    draft["public_evidence_ids"] = []
    draft["public_sources"] = []

    errors = _errors(draft)

    assert any(error.startswith("missing_limitation:") for error in errors)
    assert any(error.startswith("missing_disclaimer:") for error in errors)
    assert "missing_public_sources" in errors


def test_rejection_audit_contains_structured_basic_metadata() -> None:
    """Le rejet audite request_id, engine_version, schema_version et validation_errors."""
    validation_result = validate_basic_natal_draft_against_plan(
        draft={"sections": []},
        reading_plan=_date_only_plan(),
        request_id="req-audit-basic",
    )

    outcome = build_basic_natal_rejection_outcome(
        answer_id="basic:req-audit-basic",
        raw_answer={"sections": []},
        validation_result=validation_result,
    )

    assert outcome.rejection_reason["request_id"] == "req-audit-basic"
    assert outcome.rejection_reason["engine_version"] == "basic-natal-reading-v1"
    assert outcome.rejection_reason["schema_version"] == "basic_natal_interpretation_v2"
    assert outcome.rejection_reason["validation_errors"] == validation_result.validation_errors
    assert outcome.to_client_payload() == {
        "status": "rejected",
        "message": outcome.client_message,
    }


def test_invalid_draft_triggers_one_repair_attempt() -> None:
    """Un premier brouillon invalide peut etre remplace par une reparation contrainte valide."""
    calls: list[list[str]] = []

    def repair(draft, reading_plan, validation_result):
        calls.append(validation_result.validation_errors)
        return _valid_draft(reading_plan)

    outcome = validate_repair_or_fallback_basic_natal_draft(
        draft={"sections": []},
        reading_plan=_date_only_plan(),
        request_id="req-repair-basic",
        answer_id="basic:req-repair-basic",
        repair_callback=repair,
    )

    assert calls
    assert outcome.repair_attempted is True
    assert outcome.fallback_used is False
    assert outcome.validation_result.is_valid is True
    assert outcome.rejection_outcome is None


def test_second_invalid_draft_uses_valid_editorial_deterministic_fallback() -> None:
    """Deux validations invalides basculent vers un fallback lisible sans template mecanique."""

    def repair(_draft, _reading_plan, _validation_result):
        return {"sections": []}

    outcome = validate_repair_or_fallback_basic_natal_draft(
        draft={"sections": []},
        reading_plan=_date_only_plan(),
        request_id="req-fallback-basic",
        answer_id="basic:req-fallback-basic",
        repair_callback=repair,
    )

    assert outcome.repair_attempted is True
    assert outcome.fallback_used is True
    assert outcome.validation_result.is_valid is True
    assert outcome.validation_result.fallback_used is True
    assert outcome.accepted_draft is not None
    serialized = str(outcome.accepted_draft)
    assert "cette lecture s'appuie uniquement" not in serialized
    assert outcome.rejection_outcome is None


def test_interpretation_service_routes_basic_draft_to_post_generation_validator() -> None:
    """Le service runtime applique le validateur au chemin Basic complet."""
    source = inspect.getsource(interpretation_service.NatalInterpretationService.interpret)

    assert 'user_plan == "basic"' in source
    assert "_validate_basic_natal_draft_output(" in source


def test_basic_draft_runtime_helper_builds_public_v2_contract_after_validation() -> None:
    """Un draft provider valide est converti en contrat public Basic V2 controle."""
    draft = _valid_draft()

    outcome = _validate_basic_natal_draft_output(
        base_output=draft,
        reading_plan=_date_only_plan(),
        gateway_result=_gateway_result(draft),
        request_id="req-basic-runtime",
    )
    assert outcome.accepted_draft is not None

    contract = _basic_natal_contract_from_draft(
        accepted_draft=outcome.accepted_draft,
        reading_plan=_date_only_plan(),
    )

    assert contract.schema_version == "basic_natal_interpretation_v2"
    assert contract.interpretation.themes
    assert contract.public_evidence


def test_basic_public_contract_uses_synthesis_as_introduction_not_duplicate_theme() -> None:
    """Le fil conducteur nourrit l'introduction sans devenir un theme ordinaire."""
    plan = _plan_with_synthesis()
    draft = _valid_draft(plan)
    draft["sections"].insert(
        0,
        {
            "section_code": "synthesis",
            "heading": "Fil conducteur",
            "content": (
                "Le fil conducteur relie les besoins relationnels et les ressources stables. "
                "Il introduit la lecture sans ajouter de chapitre redondant."
            ),
            "evidence_ids": ["ev_sun"],
            "fact_ids": ["sun_balance"],
        },
    )

    contract = _basic_natal_contract_from_draft(accepted_draft=draft, reading_plan=plan)

    assert contract.interpretation.introduction.startswith("Le fil conducteur")
    assert all(theme.title != "Fil conducteur" for theme in contract.interpretation.themes)
