# Validation locale des exemples JSON CS-371.
"""Controle les livrables JSON et Markdown produits pour la story."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = (
    REPO_ROOT
    / "_condamad/examples/prompt-generation-cartography/"
    / "1973-04-24-1100-paris-theme-astral-v1"
)
EVIDENCE_DIR = (
    REPO_ROOT
    / "_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence"
)
EXPECTED_FILES = {
    "README.md",
    "intermediate-data.json",
    "free-provider-payload.json",
    "basic-provider-payload.json",
    "premium-provider-payload.json",
    "structure-comparison.md",
}
PLANS = ("free", "basic", "premium")
FORBIDDEN_STRINGS = {
    "TODO",
    "TBD",
    "PLACEHOLDER",
    "{{",
    "YYYY-MM-DD",
    "HH:MM",
}
COMMERCIAL_LABELS = {"plan", "free", "basic", "premium"}
TABLE_SOURCE_OWNERS = {
    "astral_planet_interpretation_profiles",
    "astral_house_interpretation_profiles",
    "astral_aspect_interpretation_profiles",
}


def main() -> None:
    """Leve une AssertionError si un critere story n'est pas respecte."""
    _assert_expected_files()
    intermediate = _read_json("intermediate-data.json")
    payloads = {plan: _read_json(f"{plan}-provider-payload.json") for plan in PLANS}

    _assert_birth_context(intermediate, payloads)
    _assert_common_skeleton(payloads)
    _assert_required_blocks(payloads)
    _assert_table_material_sources(intermediate, payloads)
    _assert_density_increases(payloads)
    _assert_no_forbidden_tokens(payloads)
    _assert_commercial_labels_outside_payload_values(payloads)
    _assert_persistent_evidence()

    print("PASS: expected deliverables present")
    print("PASS: four JSON files parse successfully")
    print("PASS: birth scenario 1973-04-24 11:00 Paris is present")
    print("PASS: provider payload skeleton is shared by free/basic/premium")
    print("PASS: interpretation_material and required blocks are non-empty")
    print("PASS: interpretation_material includes DB-profile source refs")
    print("PASS: density increases across provider profiles")
    print("PASS: provider payload values are resolved and contain no placeholders")
    print("PASS: commercial labels are absent from provider payload values")
    print("PASS: persistent evidence files exist")


def _assert_expected_files() -> None:
    """Verifie les six livrables attendus."""
    existing = {path.name for path in EXAMPLE_DIR.iterdir() if path.is_file()}
    assert EXPECTED_FILES <= existing, EXPECTED_FILES - existing


def _read_json(name: str) -> dict[str, Any]:
    """Charge un JSON exemple."""
    return json.loads((EXAMPLE_DIR / name).read_text(encoding="utf-8"))


def _assert_birth_context(
    intermediate: dict[str, Any], payloads: dict[str, dict[str, Any]]
) -> None:
    """Verifie que le scenario de naissance est visible et auditable."""
    birth_input = intermediate["birth_input"]
    assert birth_input["date"] == "1973-04-24"
    assert birth_input["time"] == "11:00"
    assert birth_input["place"] == "Paris"
    for payload in payloads.values():
        serialized_birth_context = json.dumps(
            payload["input_data"]["birth_context"], ensure_ascii=False
        )
        assert "1973-04-24" in serialized_birth_context
        assert "11:00" in serialized_birth_context
        assert "Paris" in serialized_birth_context


def _assert_common_skeleton(payloads: dict[str, dict[str, Any]]) -> None:
    """Compare les squelettes recursifs des trois payloads provider."""
    skeletons = {_skeleton(payload) for payload in payloads.values()}
    assert len(skeletons) == 1


def _assert_required_blocks(payloads: dict[str, dict[str, Any]]) -> None:
    """Controle les blocs imposes par le contrat theme_astral."""
    for payload in payloads.values():
        assert payload["delivery_profile"]
        assert payload["astrologer_voice"]
        assert payload["safety_contract"]
        assert payload["feature_context"]
        input_data = payload["input_data"]
        for key in (
            "birth_context",
            "astrological_facts",
            "interpretation_material",
            "selected_themes",
            "limits",
        ):
            assert key in input_data
        assert any(input_data["interpretation_material"].values())
        assert payload["output_contract"]["response_contract_id"] == (
            "theme_astral_response_contract_v1"
        )


def _assert_table_material_sources(
    intermediate: dict[str, Any], payloads: dict[str, dict[str, Any]]
) -> None:
    """Verifie que les sources principales proviennent du repository DB."""
    source_coverage = intermediate["source_coverage"]
    assert source_coverage["table_source_count"] > 0
    assert TABLE_SOURCE_OWNERS <= set(source_coverage["source_owners"])
    for payload in payloads.values():
        material = payload["input_data"]["interpretation_material"]
        source_refs = {
            item["source_ref"] for section_items in material.values() for item in section_items
        }
        assert any(ref.startswith("astral_planet_interpretation_profiles:") for ref in source_refs)
        assert any(ref.startswith("astral_house_interpretation_profiles:") for ref in source_refs)
        assert any(ref.startswith("astral_aspect_interpretation_profiles:") for ref in source_refs)


def _assert_density_increases(payloads: dict[str, dict[str, Any]]) -> None:
    """Verifie que les volumes augmentent avec le profil."""
    objects = [len(payloads[plan]["input_data"]["astrological_facts"]["objects"]) for plan in PLANS]
    aspects = [len(payloads[plan]["input_data"]["astrological_facts"]["aspects"]) for plan in PLANS]
    sections = [
        len(payloads[plan]["input_data"]["selected_themes"]["section_keys"]) for plan in PLANS
    ]
    output_sections = [payloads[plan]["output_contract"]["max_sections"] for plan in PLANS]
    material_budget = [
        payloads[plan]["delivery_profile"]["material_budget"]["max_source_items"] for plan in PLANS
    ]
    assert objects[0] < objects[1] <= objects[2]
    assert aspects[0] < aspects[1] < aspects[2]
    assert sections[0] < sections[1] < sections[2]
    assert output_sections[0] < output_sections[1] < output_sections[2]
    assert material_budget[0] < material_budget[1] < material_budget[2]


def _assert_no_forbidden_tokens(payloads: dict[str, dict[str, Any]]) -> None:
    """Rejette les placeholders et formats non resolus."""
    for payload in payloads.values():
        serialized = json.dumps(payload, ensure_ascii=False)
        for token in FORBIDDEN_STRINGS:
            assert token not in serialized


def _assert_commercial_labels_outside_payload_values(payloads: dict[str, dict[str, Any]]) -> None:
    """Interdit les labels commerciaux comme valeurs prompt-visibles."""
    for payload in payloads.values():
        assert COMMERCIAL_LABELS.isdisjoint(_json_strings(payload))
        assert '"plan"' not in json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _assert_persistent_evidence() -> None:
    """Controle les preuves persistantes attendues par la story."""
    for name in (
        "examples-baseline.txt",
        "examples-after.txt",
        "guardrails.txt",
        "source-coverage.md",
        "json-validation.txt",
        "no-provider-proof.txt",
        "validation.txt",
    ):
        assert (EVIDENCE_DIR / name).exists(), name


def _skeleton(value: Any) -> str:
    """Retourne un squelette recursif serialisable."""
    if isinstance(value, dict):
        return json.dumps({key: _skeleton(value[key]) for key in value}, sort_keys=True)
    if isinstance(value, list):
        return "list:" + (_skeleton(value[0]) if value else "empty")
    return type(value).__name__


def _json_strings(value: Any) -> set[str]:
    """Collecte toutes les chaines de caracteres d'une structure JSON."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for nested in value.values() for item in _json_strings(nested)}
    if isinstance(value, list):
        return {item for nested in value for item in _json_strings(nested)}
    return set()


if __name__ == "__main__":
    main()
