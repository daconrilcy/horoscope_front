# Commentaire global: verrouille les contrats de generation theme natal et leurs schemas.
"""Tests unitaires des contrats stricts de generation theme natal."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_output_schema_definition,
    get_canonical_use_case_contract,
)
from app.domain.theme_natal.generation_contracts import (
    THEME_NATAL_GENERATION_CONTRACTS,
    THEME_NATAL_GENERATION_CONTRACTS_BY_KEY,
    THEME_NATAL_SNAPSHOT_FIELDS,
    calculate_theme_natal_generation_contract_hash,
    resolve_theme_natal_generation_contract,
)
from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalOutputVariant,
)


def test_generation_contract_keys_are_distinct_and_complete() -> None:
    """Verifie que Free, Basic et Premium ont chacun leur contrat cible."""

    assert set(THEME_NATAL_GENERATION_CONTRACTS_BY_KEY) == {
        "theme_natal.reading.free_preview.v1",
        "theme_natal.reading.basic_full_reading.v1",
        "theme_natal.reading.premium_full_reading.v1",
    }
    assert {contract.output_variant for contract in THEME_NATAL_GENERATION_CONTRACTS} == set(
        ThemeNatalOutputVariant
    )
    assert {
        variant: contract.generation_contract_key
        for variant, contract in (
            (contract.output_variant, contract) for contract in THEME_NATAL_GENERATION_CONTRACTS
        )
    } == THEME_NATAL_READING_CONTRACT_KEYS


def test_contract_sections_are_versioned_and_store_ready() -> None:
    """Verifie les sections obligatoires et les champs de snapshot persistables."""

    for contract in THEME_NATAL_GENERATION_CONTRACTS:
        assert contract.generation_contract_version == "1.0.0"
        assert contract.engine_profile.version.startswith("theme_natal.engine.")
        assert contract.data_contract.version.startswith("theme_natal.data.")
        assert contract.prompt_contract.version.startswith("theme_natal.prompt.")
        assert contract.output_contract.version == "theme_natal.output_contract.v1"
        assert contract.persistence_contract.version == "theme_natal.persistence_contract.v1"
        assert contract.persistence_contract.snapshot_fields == THEME_NATAL_SNAPSHOT_FIELDS
        assert contract.persistence_contract.mutable_registry_reference_allowed is False
        assert contract.data_contract.prompt_visible
        assert contract.data_contract.validation_only
        assert contract.data_contract.audit_only


def test_raw_and_public_schemas_are_distinct_and_recursively_closed() -> None:
    """Verifie la separation raw/public et le refus recursif des champs inconnus."""

    public_schemas = []
    for contract in THEME_NATAL_GENERATION_CONTRACTS:
        raw_schema = contract.output_contract.raw_provider_schema
        public_schema = contract.output_contract.public_projected_schema

        assert raw_schema != public_schema
        assert raw_schema["$id"] == contract.output_contract.raw_schema_name
        assert public_schema["$id"] == contract.output_contract.public_schema_name
        assert _object_schemas_without_additional_properties(raw_schema) == []
        assert _object_schemas_without_additional_properties(public_schema) == []
        public_schemas.append(public_schema)

    assert public_schemas[1] != public_schemas[2]


def test_snapshot_metadata_and_hash_are_deterministic() -> None:
    """Verifie les metadonnees de snapshot et le hash du contenu resolu."""

    snapshot = resolve_theme_natal_generation_contract("theme_natal.reading.basic_full_reading.v1")

    assert snapshot.generation_contract_snapshot_id.startswith(
        "theme_natal.reading.basic_full_reading.v1@"
    )
    assert snapshot.generation_contract_hash == calculate_theme_natal_generation_contract_hash(
        snapshot.contract
    )
    assert snapshot.prompt_contract_version == snapshot.contract.prompt_contract.version
    assert snapshot.output_schema_version == snapshot.contract.output_contract.version
    assert snapshot.data_contract_version == snapshot.contract.data_contract.version
    assert snapshot.engine_profile_version == snapshot.contract.engine_profile.version


def test_public_schemas_do_not_expose_generation_trace_fields() -> None:
    """Verifie que la projection publique ne contient pas les champs techniques de snapshot."""

    forbidden_public_fields = {
        "generation_contract_key",
        "generation_contract_version",
        "generation_contract_snapshot_id",
        "generation_contract_hash",
        "prompt_contract_version",
        "output_schema_version",
        "data_contract_version",
        "engine_profile_version",
    }
    for contract in THEME_NATAL_GENERATION_CONTRACTS:
        serialized_public_schema = json.dumps(
            contract.output_contract.public_projected_schema,
            sort_keys=True,
        )
        for field_name in forbidden_public_fields:
            assert field_name not in serialized_public_schema


def test_canonical_registry_exposes_theme_natal_generation_contracts() -> None:
    """Verifie que le registre canonique reference les contrats et schemas publics."""

    for contract in THEME_NATAL_GENERATION_CONTRACTS:
        registered = get_canonical_use_case_contract(contract.generation_contract_key)
        schema = get_canonical_output_schema_definition(contract.output_contract.public_schema_name)

        assert registered is not None
        assert registered.output_schema_name == contract.output_contract.public_schema_name
        assert registered.fallback_target_key is None
        assert schema is not None
        assert schema.json_schema == contract.output_contract.public_projected_schema


def test_theme_natal_contract_modules_keep_pure_domain_imports() -> None:
    """Analyse les imports pour bloquer framework, DB, provider et frontend."""

    backend_root = Path(__file__).resolve().parents[4]
    domain_root = backend_root / "app" / "domain" / "theme_natal"
    forbidden_roots = (
        "fastapi",
        "sqlalchemy",
        "frontend",
        "app.api",
        "app.infra",
        "app.services",
    )
    forbidden_fragments = (".llm_generation", ".runtime.provider", ".responses_client")

    violations: list[str] = []
    for source_path in sorted(domain_root.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            for module_name in _imported_module_names(node):
                if module_name.startswith(forbidden_roots) or any(
                    fragment in module_name for fragment in forbidden_fragments
                ):
                    violations.append(f"{source_path.name}: {module_name}")

    assert violations == []


def _object_schemas_without_additional_properties(schema: dict[str, object]) -> list[str]:
    """Retourne les chemins objet qui n'ont pas additionalProperties=false."""

    missing: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                missing.append(path)
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(schema, "$")
    return missing


def _imported_module_names(node: ast.AST) -> tuple[str, ...]:
    """Retourne les noms de modules importes pour l'AST guard."""

    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return (node.module,) if node.module is not None else ()
    return ()
