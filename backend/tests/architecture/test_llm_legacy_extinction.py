# Garde d'architecture contre les anciens carriers de prompt natal.
"""Verifie que le runtime natal ne reactive pas les surfaces d'injection legacy."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.domain.llm.runtime.contracts import NatalExecutionInput
from app.main import app

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = BACKEND_ROOT / "app"
GATEWAY_PATH = APP_ROOT / "domain/llm/runtime/gateway.py"
ADAPTER_PATH = APP_ROOT / "domain/llm/runtime/adapter.py"
INTERPRETATION_SERVICE_PATH = APP_ROOT / "services/llm_generation/natal/interpretation_service.py"
PUBLIC_ROUTERS_ROOT = APP_ROOT / "api/v1/routers/public"
ASSEMBLY_RESOLVER_PATH = APP_ROOT / "domain/llm/configuration/assembly_resolver.py"
PROMPT_GOVERNANCE_REGISTRY_PATH = (
    APP_ROOT / "domain/llm/governance/data/prompt_governance_registry.json"
)

FORBIDDEN_NATAL_CARRIERS = {
    "basic_natal_prompt_payload",
    "chart_json",
    "natal_data",
    "evidence_catalog",
}
DELETED_PUBLIC_GENERATOR_KEYS = {"natal_interpretation_short", "natal_long_free"}


def _string_constants(path: Path) -> set[str]:
    """Collecte les constantes texte d'un fichier pour inspecter les branches legacy."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def test_natal_execution_input_has_no_legacy_prompt_carrier_fields() -> None:
    """Le DTO runtime natal expose uniquement la cle astrologique canonique."""

    assert FORBIDDEN_NATAL_CARRIERS.isdisjoint(NatalExecutionInput.model_fields)
    assert "llm_astrology_input_v1" in NatalExecutionInput.model_fields


def test_public_routes_do_not_call_legacy_natal_generation_service() -> None:
    """Les routeurs publics ne doivent plus atteindre le service generateur legacy."""

    public_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PUBLIC_ROUTERS_ROOT.glob("*.py")
        if path.name != "__init__.py"
    )

    assert "NatalInterpretationService.interpret(" not in public_sources
    assert "NatalInterpretationService.interpret_chart(" not in public_sources


def test_natal_legacy_service_has_no_free_short_generation_branch() -> None:
    """Le service legacy ne doit plus construire les cles short/free supprimées."""

    source = INTERPRETATION_SERVICE_PATH.read_text(encoding="utf-8")
    interpret_source = source.split("async def interpret(", maxsplit=1)[1]
    interpret_source = interpret_source.split("def list_interpretations(", maxsplit=1)[0]

    assert "async def _generate_free_short(" not in source
    assert '"natal_long_free"' not in interpret_source
    assert '"natal_interpretation_short"' not in interpret_source


def test_public_runtime_contract_excludes_deleted_natal_generator_keys() -> None:
    """Les routes et schemas publics ne republient pas les cles de generation supprimees."""

    routes_blob = "\n".join(getattr(route, "path", "") for route in app.routes)
    openapi_blob = json.dumps(app.openapi(), sort_keys=True)

    for deleted_key in DELETED_PUBLIC_GENERATOR_KEYS:
        assert deleted_key not in routes_blob
        assert deleted_key not in openapi_blob


def test_natal_adapter_does_not_forward_legacy_prompt_carriers() -> None:
    """L'adapter natal ne rehydrate pas les anciens carriers dans ExecutionContext."""

    source = ADAPTER_PATH.read_text(encoding="utf-8")
    natal_method = source.split("async def generate_natal_interpretation", maxsplit=1)[1]
    natal_method = natal_method.split("async def generate_horoscope_narration", maxsplit=1)[0]

    assert "natal_data=" not in natal_method
    assert "chart_json=" not in natal_method
    assert "evidence_catalog=" not in natal_method
    assert "basic_natal_prompt_payload" not in natal_method
    assert "natal_interpretation_short" not in natal_method
    assert "natal_long_free" not in natal_method


def test_gateway_has_no_natal_transition_carrier_registry() -> None:
    """Aucune branche de transition natal ne liste les anciens carriers prompt."""

    constants = _string_constants(GATEWAY_PATH)
    source = GATEWAY_PATH.read_text(encoding="utf-8")

    assert "_NATAL_TRANSITION_PROMPT_CARRIERS" not in source
    assert (
        "Transition legacy: seuls les schemas anciens peuvent encore demander chart_json."
        not in source
    )
    assert "llm_astrology_input_v1" in constants


def test_natal_preview_variables_exclude_legacy_carriers() -> None:
    """La preview des prompts natals ne propose plus d'exemples old-key."""

    source = ASSEMBLY_RESOLVER_PATH.read_text(encoding="utf-8")
    natal_preview_block = source.split('if config.feature == "natal":', maxsplit=1)[1]
    natal_preview_block = natal_preview_block.split(
        "reg = get_prompt_governance_registry()", maxsplit=1
    )[0]

    assert '"llm_astrology_input_v1"' in natal_preview_block
    assert '"chart_json"' not in natal_preview_block
    assert '"natal_data"' not in natal_preview_block


def test_natal_prompt_governance_family_excludes_legacy_carriers() -> None:
    """Le registre de gouvernance natal ne declare plus les anciens carriers."""

    registry = json.loads(PROMPT_GOVERNANCE_REGISTRY_PATH.read_text(encoding="utf-8"))
    natal_placeholders = {
        placeholder["name"] for placeholder in registry["placeholders_by_family"]["natal"]
    }

    assert "llm_astrology_input_v1" in natal_placeholders
    assert natal_placeholders.isdisjoint({"chart_json", "natal_data"})
