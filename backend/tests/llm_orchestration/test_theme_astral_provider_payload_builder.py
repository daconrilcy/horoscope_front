"""Tests du builder canonique de payload provider theme astral."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.domain.astrology.interpretation.interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
)
from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode
from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_DELIVERY_PROFILES,
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
)
from app.domain.llm.runtime.theme_astral_provider_payload_builder import (
    ThemeAstralProviderPayloadBuilder,
)
from app.ops.llm.bootstrap.seed_30_8_v3_prompts import NATAL_COMPLETE_PROMPT_V3
from tests.unit.domain.astrology.basic_natal_reading_plan_helpers import (
    build_plan,
    fact,
    theme,
)
from tests.unit.domain.astrology.interpretation.test_interpretation_material_builder import (
    _build_chart_input,
    _prepared_paris_birth,
    _sources_for,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = REPO_ROOT / "app/domain/llm/runtime"
TOP_LEVEL_KEYS = (
    "runtime_contract",
    "safety_contract",
    "astrologer_voice",
    "feature_context",
    "delivery_profile",
    "input_data",
    "output_contract",
)
INPUT_DATA_KEYS = (
    "birth_context",
    "astrological_facts",
    "interpretation_material",
    "selected_themes",
    "limits",
)
BASIC_INPUT_DATA_KEYS = ("basic_natal_prompt_payload",)
COMMERCIAL_LABELS = {"plan", "free", "basic", "premium"}


def test_provider_payload_builder_has_one_canonical_owner() -> None:
    """AST guard: un seul owner construit le payload provider theme astral."""
    builder_source = (RUNTIME_DIR / "theme_astral_provider_payload_builder.py").read_text(
        encoding="utf-8"
    )
    owner_files = [
        path
        for path in RUNTIME_DIR.glob("*.py")
        if "class ThemeAstralProviderPayloadBuilder" in path.read_text(encoding="utf-8")
    ]
    tree = ast.parse(builder_source)
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    assert owner_files == [RUNTIME_DIR / "theme_astral_provider_payload_builder.py"]
    assert class_names == {"ThemeAstralProviderPayloadBuilder"}
    assert not (
        REPO_ROOT / "app/domain/astrology/interpretation/theme_astral_llm_input_v1_builder.py"
    ).exists()
    assert "resolve_theme_astral_provider_delivery_profile" in builder_source
    assert "_DELIVERY_PROFILES" not in builder_source


def test_provider_payload_skeleton_is_stable_for_all_commercial_plans() -> None:
    """Les plans backend changent les valeurs mais jamais les cles provider."""
    payloads = _payloads_by_commercial_plan()

    assert {tuple(payload) for payload in payloads.values()} == {TOP_LEVEL_KEYS}
    assert tuple(payloads["basic"]["input_data"]) == BASIC_INPUT_DATA_KEYS
    assert {
        tuple(payload["input_data"]) for key, payload in payloads.items() if key != "basic"
    } == {INPUT_DATA_KEYS}
    assert {
        tuple(payload["input_data"]["interpretation_material"])
        for payload in payloads.values()
        if "interpretation_material" in payload["input_data"]
    } == {INTERPRETATION_MATERIAL_KEYS}


def test_commercial_labels_stay_out_of_provider_payload() -> None:
    """Le payload ne contient aucun libelle commercial prompt-visible."""
    for payload in _payloads_by_commercial_plan().values():
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        assert COMMERCIAL_LABELS.isdisjoint(_json_strings(payload))
        assert '"plan"' not in serialized


def test_delivery_material_voice_and_output_contract_are_emitted() -> None:
    """Les blocs obligatoires portent profil, matiere, voix et contrat versionne."""
    payload = _payloads_by_commercial_plan()["premium"]

    assert payload["runtime_contract"]["contract_id"] == THEME_ASTRAL_INPUT_CONTRACT_ID
    assert payload["delivery_profile"]["depth"] == "complete"
    assert payload["astrologer_voice"] == {
        "tone": "calme",
        "vocabulary": ["symbolique"],
        "emphases": ["integration"],
    }
    assert payload["input_data"]["interpretation_material"]["planet_sign_interpretations"]
    assert payload["input_data"]["selected_themes"]["selection_owner"] == (
        "InterpretationMaterialBuilder"
    )
    assert set(payload["input_data"]["selected_themes"]["section_keys"]).issubset(
        set(INTERPRETATION_MATERIAL_KEYS)
    )
    assert not payload["input_data"]["limits"]["missing_data"]["birth_context"]
    assert not payload["input_data"]["limits"]["missing_data"]["empty_fact_groups"]
    assert payload["output_contract"]["response_contract_id"] == THEME_ASTRAL_RESPONSE_CONTRACT_ID
    assert payload["output_contract"]["response_contract_version"] == "v1"


def test_basic_payload_exposes_private_narrative_source_family_metrics() -> None:
    """Le payload Premium garde les metriques privees hors contrat Basic."""
    payload = _payloads_by_commercial_plan()["premium"]
    selected_themes = payload["input_data"]["selected_themes"]
    family_metrics = selected_themes["narrative_source_families"]

    assert selected_themes["selected_source_count"] <= selected_themes["max_source_items"] == 48
    assert selected_themes["section_keys"] == list(INTERPRETATION_MATERIAL_KEYS[:8])
    assert {item["family"] for item in family_metrics} == {
        "personnalite",
        "emotions",
        "relations",
        "vocation",
        "evolution",
    }
    assert all(item["covered"] for item in family_metrics)
    assert all(item["source_count"] > 0 for item in family_metrics)


def test_basic_payload_uses_reading_plan_contract_only() -> None:
    """Le payload Basic expose uniquement le contrat prompt issu du plan."""
    payload = _payloads_by_commercial_plan()["basic"]
    prompt_payload = payload["input_data"]["basic_natal_prompt_payload"]

    assert tuple(prompt_payload) == (
        "sections",
        "resolved_syntheses",
        "editorial_evidence",
        "limitations",
        "disclaimers",
        "style_constraints",
    )
    assert prompt_payload["sections"]
    assert prompt_payload["resolved_syntheses"]
    assert prompt_payload["editorial_evidence"]
    assert prompt_payload["style_constraints"] == {
        "word_count": {"minimum": 900, "maximum": 1300},
        "section_count": {"minimum": 6, "maximum": 8},
        "tone": "vous",
        "prediction_policy": "no_firm_prediction",
        "advice_policy": "no_prescriptive_advice",
        "plan_constraints": [
            "Employer un ton clair, nuance et non fataliste.",
            "Ne pas ajouter de fait astrologique absent du plan.",
            "Garder les preuves publiques lisibles sans scores ni traces techniques.",
        ],
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    assert "BasicNatalReadingPlan" not in serialized


def test_nominal_natal_prompt_requests_five_source_families() -> None:
    """Le prompt complet nominal demande les cinq familles sources narratives."""
    prompt = NATAL_COMPLETE_PROMPT_V3.casefold()

    assert "familles sources narratives" in prompt
    for family in ("personnalite", "emotions", "relations", "vocation", "evolution"):
        assert family in prompt
    assert "chart_json" not in prompt
    assert "natal_data" not in prompt


def test_birth_context_exposes_structured_birth_data() -> None:
    """Le provider recoit les champs de naissance normalises du runtime."""
    payload = _payloads_by_commercial_plan()["premium"]

    assert payload["input_data"]["birth_context"] == {
        "chart_id": "chart-1",
        "birth_date": "1973-04-24",
        "birth_time_local": "11:00",
        "birth_place": {
            "city": "Paris",
            "country": "France",
            "timezone": "Europe/Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
        },
        "precision": {
            "birth_time_known": True,
            "coordinates_known": True,
        },
        "locale": "fr-FR",
        "chart_type": "natal",
    }


def test_basic_payload_excludes_birth_context_and_internal_prompt_tokens() -> None:
    """Le payload prompt Basic ne transporte ni donnees personnelles ni IDs bruts."""
    payload = _payloads_by_commercial_plan()["basic"]
    prompt_payload = payload["input_data"]["basic_natal_prompt_payload"]
    serialized = json.dumps(prompt_payload, ensure_ascii=False, sort_keys=True)

    forbidden_tokens = {
        "birth_context",
        "astrological_facts",
        "interpretation_material",
        "selected_themes",
        "chart_json",
        "natal_data",
        "email",
        "user_id",
        "place_id",
        "latitude",
        "longitude",
        "audit_input",
        "ranking_score",
        "weighted_score",
        "score_profile",
        "condition_axis",
        "prompt_hint",
        "required_fact_ids",
        "forbidden_fact_ids",
        "supporting_evidence_ids",
        "runtime.fact",
    }

    assert forbidden_tokens.isdisjoint(_json_strings(prompt_payload))
    assert all(token not in serialized for token in forbidden_tokens)


def test_birth_context_marks_missing_precision_without_reconstructing_values() -> None:
    """Les donnees absentes restent nulles et signalees dans les limites."""
    chart_input = _build_chart_input_without_birth_time_or_coordinates()
    payload = ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan="free",
    )

    birth_context = payload["input_data"]["birth_context"]

    assert birth_context["birth_time_local"] is None
    assert birth_context["birth_place"]["latitude"] is None
    assert birth_context["birth_place"]["longitude"] is None
    assert birth_context["precision"] == {
        "birth_time_known": False,
        "coordinates_known": False,
    }
    assert payload["input_data"]["limits"]["missing_data"]["birth_context"] == ["birth_time_local"]


def test_birth_context_does_not_parse_chart_id() -> None:
    """AST guard: `chart_id` reste un identifiant technique non parse."""
    builder_source = (RUNTIME_DIR / "theme_astral_provider_payload_builder.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(builder_source)
    birth_context_function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_birth_context"
    )
    call_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(birth_context_function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute | ast.Name)
    }

    assert {"split", "fromisoformat"}.isdisjoint(call_names)


def test_profile_quantities_vary_without_skeleton_drift() -> None:
    """Les budgets resolus varient par profil sans creer de cles specifiques."""
    payloads = _payloads_by_commercial_plan()
    provider_depths = {payload["delivery_profile"]["depth"] for payload in payloads.values()}
    budgets = {
        key: payload["delivery_profile"]["material_budget"]["max_source_items"]
        for key, payload in payloads.items()
    }
    aspect_counts = {
        key: len(payload["input_data"]["interpretation_material"]["aspect_interpretations"])
        for key, payload in payloads.items()
    }
    fact_aspect_counts = {
        key: len(payload["input_data"]["astrological_facts"]["aspects"])
        for key, payload in payloads.items()
    }
    selected_section_counts = {
        key: len(payload["input_data"]["selected_themes"]["section_keys"])
        for key, payload in payloads.items()
    }
    output_section_limits = {
        key: payload["output_contract"]["max_sections"] for key, payload in payloads.items()
    }

    assert provider_depths == set(THEME_ASTRAL_DELIVERY_PROFILES)
    assert budgets["free"] < budgets["basic"] < budgets["premium"]
    assert aspect_counts == {"free": 1, "basic": 3, "premium": 6}
    assert fact_aspect_counts == {"free": 1, "basic": 3, "premium": 6}
    assert selected_section_counts == {"free": 4, "basic": 6, "premium": 8}
    assert output_section_limits == {"free": 4, "basic": 6, "premium": 8}


def test_voice_changes_style_fields_only_and_truth_stays_engine_owned() -> None:
    """La voix reste hors faits astrologiques et des sources de verite."""
    payload = _payloads_by_commercial_plan()["premium"]

    assert payload["input_data"]["astrological_facts"]["source_owner"] == (
        "ChartInterpretationInputBuilder"
    )
    facts_as_text = json.dumps(payload["input_data"]["astrological_facts"], sort_keys=True)
    assert "calme" not in facts_as_text
    assert "symbolique" not in facts_as_text
    assert payload["safety_contract"]["voice_policy"] == "style_only_no_fact_mutation"


def test_prompt_data_is_carried_once_in_user_payload_block() -> None:
    """Le builder ne produit pas de bloc developer prompt dupliquant la matiere."""
    payload = _payloads_by_commercial_plan()["premium"]

    assert "developer_prompt" not in payload
    assert "messages" not in payload
    assert "interpretation_material" in payload["input_data"]


def _payloads_by_commercial_plan() -> dict[str, dict[str, object]]:
    """Construit les trois payloads representatifs depuis les memes sources."""
    chart_input = _build_chart_input(
        aspect_codes=("trine", "square", "opposition", "conjunction", "sextile", "quincunx")
    )
    sources = _sources_for(chart_input)
    builder = ThemeAstralProviderPayloadBuilder()
    return {
        plan: builder.build(
            chart_input=chart_input,
            interpretation_sources=sources,
            commercial_plan=plan,
            astrologer_voice={
                "tone": "calme",
                "vocabulary": ["symbolique"],
                "emphases": ["integration"],
            },
            basic_reading_plan=_basic_reading_plan() if plan == "basic" else None,
        )
        for plan in ("free", "basic", "premium")
    }


def _build_chart_input_without_birth_time_or_coordinates() -> object:
    """Construit un input sans precision horaire ni coordonnees canoniques."""
    return _build_chart_input(
        aspect_codes=("trine",),
        prepared_input=_prepared_paris_birth(birth_time_local=None).model_copy(
            update={"birth_lat": None, "birth_lon": None}
        ),
    )


def _json_strings(value: object) -> set[str]:
    """Collecte les chaines JSON pour detecter les labels interdits."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for nested in value.values() for item in _json_strings(nested)}
    if isinstance(value, list):
        return {item for nested in value for item in _json_strings(nested)}
    return set()


def _basic_reading_plan() -> object:
    """Construit un plan Basic representatif avec plusieurs sections publiques."""
    facts = (
        fact("sun.aries", NatalFactFamily.LUMINARY, ("sun",)),
        fact("moon.cancer", NatalFactFamily.LUMINARY, ("moon",)),
        fact("mercury.gemini", NatalFactFamily.PLANET_POSITION, ("mercury",)),
        fact("venus.taurus", NatalFactFamily.PLANET_POSITION, ("venus",)),
        fact("mars.leo", NatalFactFamily.PLANET_POSITION, ("mars",)),
        fact("jupiter.libra", NatalFactFamily.PLANET_POSITION, ("jupiter",)),
        fact("saturn.capricorn", NatalFactFamily.PLANET_POSITION, ("saturn",)),
        fact("node.virgo", NatalFactFamily.NODE, ("north_node",)),
    )
    themes = (
        theme(BasicThemeCode.CORE_IDENTITY, ("sun.aries",), objects=("sun",)),
        theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon.cancer",), objects=("moon",)),
        theme(BasicThemeCode.MENTAL_STYLE, ("mercury.gemini",), objects=("mercury",)),
        theme(BasicThemeCode.RESOURCES_AND_VALUES, ("venus.taurus",), objects=("venus",)),
        theme(BasicThemeCode.ACTION_AND_DRIVE, ("mars.leo",), objects=("mars",)),
        theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("jupiter.libra",), objects=("jupiter",)),
        theme(BasicThemeCode.GROWTH_DIRECTION, ("node.virgo",), objects=("north_node",)),
        theme(BasicThemeCode.TENSION_TO_INTEGRATE, ("saturn.capricorn",), objects=("saturn",)),
    )
    return build_plan(facts, themes)
