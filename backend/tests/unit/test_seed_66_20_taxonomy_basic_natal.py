# Les tests du seed garantissent la publication Basic natale sans dependance au runtime HTTP.
from __future__ import annotations

import ast
import inspect

from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_use_case_contract,
)
from app.ops.llm.bootstrap import seed_66_20_taxonomy


def _target_assembly_tuples() -> set[tuple[str, str, str, str]]:
    """Extrait les tuples cibles du seed via l'AST pour eviter un scan texte fragile."""

    source = inspect.getsource(seed_66_20_taxonomy.seed_66_20_taxonomy)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "target_assemblies":
                    return {tuple(item) for item in ast.literal_eval(node.value)}
    raise AssertionError("target_assemblies introuvable dans le seed")


def test_basic_natal_assembly_tuple_uses_complete_v3_use_case() -> None:
    """Le seed publie Basic natal sur le use case complet V3."""

    assemblies = _target_assembly_tuples()
    assert (
        "natal",
        "interpretation",
        "basic",
        "natal_interpretation",
    ) in assemblies

    contract = get_canonical_use_case_contract("natal_interpretation")
    assert contract is not None
    assert contract.output_schema_name == "AstroResponse_v3"


def test_basic_natal_profile_defaults_are_explicit_and_not_free_defaults() -> None:
    """Le profil Basic natal a un budget et une verbosite dedies."""

    free_defaults = seed_66_20_taxonomy._profile_defaults_for_target("natal", "free")
    basic_defaults = seed_66_20_taxonomy._profile_defaults_for_target("natal", "basic")

    assert basic_defaults["model"] == "gpt-4o-mini"
    assert basic_defaults["output_mode"] == "structured_json"
    assert basic_defaults["verbosity_profile"] == "detailed"
    assert basic_defaults["max_output_tokens"] == 2400
    assert basic_defaults != free_defaults
