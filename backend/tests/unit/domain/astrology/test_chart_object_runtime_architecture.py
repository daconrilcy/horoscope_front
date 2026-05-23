"""Tests d'architecture du runtime chart-object unifie."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
NEW_MODULES = (
    REPO_ROOT / "app/domain/astrology/runtime/chart_object_runtime_data.py",
    REPO_ROOT / "app/domain/astrology/builders/chart_object_runtime_builder.py",
    REPO_ROOT / "app/domain/astrology/builders/chart_object_house_runtime_enricher.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/contracts.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_selectors.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_enricher.py",
    REPO_ROOT / "app/domain/astrology/dignities/chart_object_inputs.py",
    REPO_ROOT / "app/domain/astrology/dominance/chart_object_inputs.py",
)
CHART_OBJECT_BUILDER = REPO_ROOT / "app/domain/astrology/builders/chart_object_runtime_builder.py"
CHART_OBJECT_HOUSE_ENRICHER = (
    REPO_ROOT / "app/domain/astrology/builders/chart_object_house_runtime_enricher.py"
)
CHART_OBJECT_RUNTIME = REPO_ROOT / "app/domain/astrology/runtime/chart_object_runtime_data.py"
CALCULATOR_ROOTS = (
    REPO_ROOT / "app/domain/astrology/calculators",
    REPO_ROOT / "app/domain/astrology/fixed_stars",
    REPO_ROOT / "app/domain/astrology/dignities",
    REPO_ROOT / "app/domain/astrology/dominance",
    REPO_ROOT / "app/domain/astrology/advanced_conditions",
    REPO_ROOT / "app/domain/astrology/planetary_conditions",
    REPO_ROOT / "app/domain/astrology/interpretation",
    REPO_ROOT / "app/domain/astrology/interpretation_adapters",
)
ASPECT_ENGINE_MODULES = (
    REPO_ROOT / "app/domain/astrology/calculators/aspects.py",
    REPO_ROOT / "app/domain/astrology/calculators/aspect_inputs.py",
)
FORBIDDEN_ASPECT_BUILDERS = (
    "PlanetAspectBodyBuilder",
    "AngleAspectBodyBuilder",
    "AstralPointAspectBodyBuilder",
    "FixedStarAspectBodyBuilder",
)
FORBIDDEN_ASPECT_COLLECTION_NAMES = (
    "planet_positions",
    "astral_points",
    "angles",
    "fixed_stars",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "app.api",
    "app.infra",
    "app." + "infrastructure",
    "app.services",
    "sqlalchemy",
    "fastapi",
    "pydantic",
)
FORBIDDEN_CONDITION_CALCULATOR_CALLS = (
    "calculate_solar_proximity",
    "calculate_planetary_motion",
    "calculate_solar_phase",
    "calculate_planet_visibility",
)
FORBIDDEN_LOCAL_THRESHOLDS = ("8.5", "17", "17.0", "0.2833", "0.01")
CAPABILITY_INPUT_MODULES = (
    REPO_ROOT / "app/domain/astrology/dignities/chart_object_inputs.py",
    REPO_ROOT / "app/domain/astrology/dominance/chart_object_inputs.py",
)
FORBIDDEN_CAPABILITY_INPUT_NAMES = (
    "object_type",
    "ChartObjectType",
    "TRADITIONAL_PLANETS",
    "planet_positions",
)
FORBIDDEN_RULERSHIP_BUILDERS = (
    "HouseRulershipPayloadBuilder",
    "MarsRulershipPayloadBuilder",
)
FORBIDDEN_RULERSHIP_TABLE_NAMES = (
    "SIGN_RULERS",
    "TRADITIONAL_SIGN_RULERS",
)
FIXED_STAR_MODULES = (
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_selectors.py",
    REPO_ROOT / "app/domain/astrology/fixed_stars/fixed_star_enricher.py",
)
FORBIDDEN_FIXED_STAR_BUILDERS = (
    "FixedStar" + "ConjunctionBuilder",
    "PlanetFixedStar" + "ConjunctionBuilder",
)


def test_new_chart_object_modules_keep_domain_pure_dependencies() -> None:
    """Les nouveaux modules restent hors API, DB, services et Pydantic."""
    for module_path in NEW_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_names = (node.module,)
            else:
                continue
            assert not any(
                imported_name == prefix or imported_name.startswith(f"{prefix}.")
                for imported_name in imported_names
                for prefix in FORBIDDEN_IMPORT_PREFIXES
            ), f"{module_path} imports forbidden dependency {imported_names}"


def test_business_calculators_do_not_branch_on_chart_object_type() -> None:
    """Les calculateurs metier ne selectionnent pas par `object_type`."""
    offenders: list[str] = []
    for root in CALCULATOR_ROOTS:
        if not root.exists():
            continue
        for module_path in root.rglob("*.py"):
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if _branches_on_object_type(node):
                    offenders.append(f"{module_path}:{getattr(node, 'lineno', '?')}")

    assert offenders == []


def test_aspect_engine_does_not_reintroduce_specialized_inputs() -> None:
    """Le moteur d'aspects ne revient pas aux collections ou builders specialises."""
    offenders: list[str] = []
    for module_path in ASPECT_ENGINE_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        source = module_path.read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if _uses_forbidden_aspect_collection(node):
                offenders.append(f"{module_path}:{getattr(node, 'lineno', '?')}")
        for builder_name in FORBIDDEN_ASPECT_BUILDERS:
            if builder_name in source:
                offenders.append(f"{module_path}:builder:{builder_name}")

    assert offenders == []


def test_chart_object_builder_does_not_call_condition_calculators() -> None:
    """Le mapping chart-object consomme les conditions sans les recalculer."""
    source = CHART_OBJECT_BUILDER.read_text(encoding="utf-8")

    assert not any(call_name in source for call_name in FORBIDDEN_CONDITION_CALCULATOR_CALLS)


def test_chart_object_mapping_does_not_define_magic_thresholds() -> None:
    """Les seuils solaires ou motion restent dans les calculateurs canoniques."""
    sources = (
        CHART_OBJECT_BUILDER.read_text(encoding="utf-8"),
        CHART_OBJECT_RUNTIME.read_text(encoding="utf-8"),
    )

    assert not any(
        threshold in source for source in sources for threshold in FORBIDDEN_LOCAL_THRESHOLDS
    )


def test_dignity_and_dominance_inputs_do_not_use_type_or_collection_eligibility() -> None:
    """Les projectors CS-220 restent pilotes par capacites et chart objects."""
    offenders: list[str] = []
    for module_path in CAPABILITY_INPUT_MODULES:
        source = module_path.read_text(encoding="utf-8")
        for forbidden_name in FORBIDDEN_CAPABILITY_INPUT_NAMES:
            if forbidden_name in source:
                offenders.append(f"{module_path}:{forbidden_name}")

    assert offenders == []


def test_dignity_and_dominance_inputs_do_not_branch_on_nominal_codes() -> None:
    """Les modules CS-220 ne selectionnent pas par code planetaire nominal."""
    offenders: list[str] = []
    for module_path in CAPABILITY_INPUT_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and _compares_nominal_code(node):
                offenders.append(f"{module_path}:{node.lineno}")

    assert offenders == []


def test_house_rulership_enricher_reuses_runtime_sources_without_local_tables() -> None:
    """La projection rulership ne cree pas de second resolver ou table de rulers."""
    source = CHART_OBJECT_HOUSE_ENRICHER.read_text(encoding="utf-8")

    assert "HouseRulerResolver" not in source
    assert not any(builder_name in source for builder_name in FORBIDDEN_RULERSHIP_BUILDERS)
    assert not any(table_name in source for table_name in FORBIDDEN_RULERSHIP_TABLE_NAMES)


def test_house_rulership_enricher_does_not_branch_on_object_type() -> None:
    """La projection house/rulership reste pilotee par les capacites."""
    tree = ast.parse(CHART_OBJECT_HOUSE_ENRICHER.read_text(encoding="utf-8"))

    assert not any(_branches_on_object_type(node) for node in ast.walk(tree))


def test_fixed_star_runtime_consumers_do_not_branch_on_object_type() -> None:
    """Les consommateurs fixed star utilisent payloads et capacites."""
    offenders: list[str] = []
    for module_path in FIXED_STAR_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if _branches_on_object_type(node):
                offenders.append(f"{module_path}:{getattr(node, 'lineno', '?')}")

    assert offenders == []


def test_fixed_star_runtime_does_not_reintroduce_parallel_builders() -> None:
    """Le flux fixed star ne cree pas de moteur parallele actif."""
    offenders: list[str] = []
    for module_path in FIXED_STAR_MODULES:
        source = module_path.read_text(encoding="utf-8")
        for builder_name in FORBIDDEN_FIXED_STAR_BUILDERS:
            if builder_name in source:
                offenders.append(f"{module_path}:{builder_name}")

    assert offenders == []


def _branches_on_object_type(node: ast.AST) -> bool:
    """Detecte les comparaisons et match explicites sur `object_type`."""
    if isinstance(node, ast.Compare):
        return _is_object_type_reference(node.left) or any(
            _is_object_type_reference(comparator) for comparator in node.comparators
        )
    if isinstance(node, ast.Match):
        return _is_object_type_reference(node.subject)
    return False


def _is_object_type_reference(node: ast.AST) -> bool:
    """Reconnait `object_type` et `obj.object_type` dans un AST."""
    return (
        isinstance(node, ast.Name)
        and node.id == "object_type"
        or isinstance(node, ast.Attribute)
        and node.attr == "object_type"
    )


def _uses_forbidden_aspect_collection(node: ast.AST) -> bool:
    """Detecte les anciens noms de collections dans les modules d'aspects."""
    return isinstance(node, ast.Name) and node.id in FORBIDDEN_ASPECT_COLLECTION_NAMES


def _compares_nominal_code(node: ast.Compare) -> bool:
    """Detecte les comparaisons ou appartenances sur codes nominaux."""
    compared_nodes = (node.left, *node.comparators)
    return any(_is_code_reference(item) for item in compared_nodes) and any(
        isinstance(operator, ast.Eq | ast.NotEq | ast.In | ast.NotIn) for operator in node.ops
    )


def _is_code_reference(node: ast.AST) -> bool:
    """Reconnait les champs de code qui ne doivent pas piloter l'eligibilite."""
    if isinstance(node, ast.Name):
        return node.id in {"code", "planet_code"}
    if isinstance(node, ast.Attribute):
        return node.attr in {"code", "planet_code"}
    return False
