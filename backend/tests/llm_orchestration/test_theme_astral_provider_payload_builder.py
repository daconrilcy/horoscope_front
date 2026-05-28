"""Tests du builder canonique de payload provider theme astral."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.domain.astrology.interpretation.interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
)
from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_DELIVERY_PROFILES,
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
)
from app.domain.llm.runtime.theme_astral_provider_payload_builder import (
    ThemeAstralProviderPayloadBuilder,
)
from tests.unit.domain.astrology.interpretation.test_interpretation_material_builder import (
    _build_chart_input,
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
    assert {tuple(payload["input_data"]) for payload in payloads.values()} == {INPUT_DATA_KEYS}
    assert {
        tuple(payload["input_data"]["interpretation_material"]) for payload in payloads.values()
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
    assert payload["output_contract"]["response_contract_id"] == THEME_ASTRAL_RESPONSE_CONTRACT_ID
    assert payload["output_contract"]["response_contract_version"] == "v1"


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
        )
        for plan in ("free", "basic", "premium")
    }


def _json_strings(value: object) -> set[str]:
    """Collecte les chaines JSON pour detecter les labels interdits."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for nested in value.values() for item in _json_strings(nested)}
    if isinstance(value, list):
        return {item for nested in value for item in _json_strings(nested)}
    return set()
