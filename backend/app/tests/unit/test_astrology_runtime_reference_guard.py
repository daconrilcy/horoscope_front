"""Gardes anti-retour du runtime reference astrologique."""

from __future__ import annotations

import ast
import re
from pathlib import Path

FORBIDDEN_NATAL_FLOW_PATTERNS = (
    r"ReferenceDataService\.get_active_reference_data",
    r"reference_data\s*:\s*dict",
    r"\bPLANET_KEYWORDS\b",
    r"\bSIGN_RULERS\b",
    r"\bDEFAULT_ORB\b",
    r"\bASPECT_WEIGHTS\b",
    r"\bHOUSE_MEANINGS\b",
    r"\bUNKNOWN_SIGN\b",
    r"\bZODIAC_SIGNS\b",
    r"\bELEMENT_BY_SIGN\b",
    r"\bMODALITY_BY_SIGN\b",
    r"\bPOLARITY_BY_SIGN\b",
    r"\bSEASONAL_QUADRANT_BY_SIGN\b",
    r"\bFERTILITY_BY_SIGN\b",
    r"\bVOICE_BY_SIGN\b",
    r"\bFORM_BY_SIGN\b",
    r"\bHUMANE_BY_SIGN\b",
    r"\bBESTIAL_BY_SIGN\b",
    r"\bSIGN_PROFILE_DATA\b",
    r"\bASTRAL_POINTS\s*=",
    r"\bPOINT_VARIANTS\s*=",
    r"\bNODE_VARIANTS\s*=",
    r"\bLILITH_VARIANTS\s*=",
    r"\btrue_node\b",
    r"\bmean_node\b",
    r"\bEXACT_ORB_DEG\b",
    r"\bTIGHT_RATIO\b",
    r"\bMODERATE_RATIO\b",
    r"_allows_simplified_fallback",
    r"if\s+engine\s*==\s*[\"']swisseph[\"'][\s\S]{0,500}engine\s*=\s*[\"']simplified[\"']",
    r"SwissEph\s+bootstrap[\s\S]{0,300}engine\s*=\s*[\"']simplified[\"']",
    r"calculation_engine\s*=\s*[\"']simplified[\"']",
)

BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _source(path: str) -> str:
    """Retourne le contenu source d'un fichier backend."""
    return (BACKEND_ROOT / path).read_text(encoding="utf-8")


def test_natal_flow_does_not_use_legacy_reference_service_or_symbols() -> None:
    """Le flux natal ne depend plus des donnees reference legacy."""
    files = [
        *(BACKEND_ROOT / "app/domain/astrology").rglob("*.py"),
        *(BACKEND_ROOT / "app/services/natal").rglob("*.py"),
    ]
    hits: list[str] = []

    for pattern in FORBIDDEN_NATAL_FLOW_PATTERNS:
        compiled = re.compile(pattern)
        for path in files:
            if compiled.search(path.read_text(encoding="utf-8")):
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_runtime_sign_profile_fixtures_do_not_import_seed_mappings() -> None:
    """Les fixtures runtime ne doivent pas masquer la source DB par un mapping seed."""
    factory = BACKEND_ROOT / "tests/factories/astrology_runtime_reference_factory.py"
    content = factory.read_text(encoding="utf-8")

    assert "SIGN_PROFILE_DATA" not in content


def test_build_natal_result_signature_uses_runtime_reference_not_dict() -> None:
    """La fonction publique de calcul consomme le contrat runtime type."""
    tree = ast.parse(_source("app/domain/astrology/natal_calculation.py"))
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "build_natal_result"
    )
    annotations = {
        arg.arg: ast.unparse(arg.annotation) if arg.annotation is not None else ""
        for arg in function.args.args
    }

    assert annotations["runtime_reference"] == "AstrologyRuntimeReference"
    assert "reference_data" not in annotations
    assert all("dict" not in annotation for annotation in annotations.values())


def test_astrology_domain_does_not_import_prediction_or_llm_runtime() -> None:
    """Le domaine astrology reste separe de prediction et du runtime LLM."""
    forbidden = ("app.domain.prediction", "app.services.prediction", "AIEngineAdapter", "OpenAI")
    hits: list[str] = []
    for path in (BACKEND_ROOT / "app/domain/astrology").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_natal_result_exposes_points_collection_without_flat_point_fields() -> None:
    """Le contrat natal conserve uniquement la collection `astral_points[]`."""
    tree = ast.parse(_source("app/domain/astrology/natal_calculation.py"))
    natal_result = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "NatalResult"
    )
    field_names = {
        node.target.id
        for node in natal_result.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }

    assert "astral_points" in field_names
    assert "points" not in field_names
    assert "true_node" not in field_names
    assert "mean_node" not in field_names
    assert "lilith" not in field_names
    assert "summary" not in field_names
    assert "keywords" not in field_names
    assert "micro_note" not in field_names
    assert "prompt_hints" not in field_names


def test_calculation_modules_do_not_import_astral_point_interpretation_services() -> None:
    """Le calcul natal ne doit pas dépendre de l'éditorial des points astraux."""
    forbidden = (
        "astral_point_interpretation_profiles",
        "astral_point_interpretation_keywords",
        "AstralPointInterpretationProfileModel",
        "AstralPointInterpretationKeywordModel",
        "AstralPointInterpretationRepository",
        "AstralPointInterpretationService",
        "InterpretationService",
        "PromptContext",
    )
    roots = [
        BACKEND_ROOT / "app/domain/astrology/calculation",
        BACKEND_ROOT / "app/domain/astrology/calculators",
        BACKEND_ROOT / "app/infra/ephemeris",
        BACKEND_ROOT / "app/services/natal",
    ]
    paths = [
        BACKEND_ROOT / "app/domain/astrology/natal_calculation.py",
        BACKEND_ROOT / "app/domain/astrology/astral_point_calculation_resolver.py",
        BACKEND_ROOT / "app/domain/astrology/ephemeris_provider.py",
    ]
    for root in roots:
        if root.exists():
            paths.extend(root.rglob("*.py"))
    hits: list[str] = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_dignity_calculators_do_not_cross_runtime_boundaries() -> None:
    """Les calculateurs de dignites restent purs et sans scoring local."""
    dignity_root = BACKEND_ROOT / "app/domain/astrology/dignities"
    forbidden_patterns = (
        "Session",
        "select(",
        "from app.infra",
        "from app.services",
        "from app.api",
        "DIGNITY_SCORES",
        "DOMICILE_SCORE",
        "ACCIDENTAL_DIGNITY_SCORES",
        "AIEngineAdapter",
        "OpenAI",
        "chat.completions",
        "prompt",
        "interpretation",
        "micro_note",
    )
    hits: list[str] = []
    for path in dignity_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_condition_profiles_do_not_cross_runtime_boundaries() -> None:
    """La couche condition reste derivee, pure et sans seuil local."""
    condition_root = BACKEND_ROOT / "app/domain/astrology/condition"
    forbidden_patterns = (
        "Session",
        "select(",
        "from app.infra",
        "from app.services",
        "from app.api",
        "from app.domain.prediction",
        "from app.services.prediction",
        "VISIBILITY_" + "WEIGHTS",
        "CONDITION_" + "SCORES",
        "CONDITION_" + "LEVELS",
        "SIGNAL_" + "THRESHOLDS",
        "CONDITION_SIGNAL_" + "RULES",
        "CONDITION_SIGNAL_" + "PROFILES",
        "FUNCTIONAL_STRENGTH_" + "THRESHOLDS",
        "VISIBILITY_SIGNAL_" + "LEVELS",
        "AIEngineAdapter",
        "OpenAI",
        "chat.completions",
        "narration",
        "micro_note",
    )
    hits: list[str] = []
    for path in condition_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_condition_profile_table_is_not_created() -> None:
    """La v1 ne doit pas introduire de persistance dediee aux profils."""
    roots = [BACKEND_ROOT / "app", BACKEND_ROOT / "migrations"]
    hits: list[str] = []
    forbidden_table = "astral_chart_planet_" + "condition_profiles"
    for root in roots:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if forbidden_table in text:
                hits.append(str(path))

    assert hits == []


def test_condition_signals_are_projected_from_natal_result_only() -> None:
    """Le serialiseur public ne recalcule pas les signaux conditionnels."""
    tree = ast.parse(_source("app/services/chart/json_builder.py"))
    serializer = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_serialize_condition_signals"
    )
    comparisons = [node for node in ast.walk(serializer) if isinstance(node, ast.Compare)]
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(serializer)
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name)
    ]

    assert comparisons == []
    assert "PlanetConditionSignalBuilder" not in "".join(calls)


def test_planet_dominance_domain_does_not_cross_runtime_boundaries() -> None:
    """Le moteur de dominance reste pur et sans poids locaux."""
    dominance_root = BACKEND_ROOT / "app/domain/astrology/dominance"
    forbidden_patterns = (
        "Session",
        "select(",
        "from app.infra",
        "from app.services",
        "from app.api",
        "from app.domain.prediction",
        "from app.services.prediction",
        "DOMINANCE_" + "FACTORS",
        "DOMINANCE_" + "WEIGHTS",
        "CHART_RULER_" + "WEIGHT",
        "ANGULARITY_" + "WEIGHT",
        "SIGN_" + "RULERS",
        "PLANET_" + "RULERS",
        "AIEngineAdapter",
        "OpenAI",
        "chat.completions",
        "prompt",
        "narration",
        "micro_note",
    )
    hits: list[str] = []
    for path in dominance_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_advanced_condition_domain_does_not_cross_runtime_boundaries() -> None:
    """Le moteur avance reste pur et sans poids ou vocabulaires locaux."""
    advanced_root = BACKEND_ROOT / "app/domain/astrology/advanced_conditions"
    forbidden_patterns = (
        "Session",
        "select(",
        "from app.infra",
        "from app.services",
        "from app.api",
        "from app.domain.prediction",
        "from app.services.prediction",
        "ADVANCED_" + "CONDITION_TYPES",
        "ADVANCED_" + "CONDITION_WEIGHTS",
        "HAYZ_" + "RULES",
        "MUTUAL_" + "RECEPTION_RULES",
        "PLANET_" + "SPEED_THRESHOLDS",
        "HELIACAL_" + "PHASES",
        "BENEFIC_" + "PLANETS",
        "MALEFIC_" + "PLANETS",
        "AIEngineAdapter",
        "OpenAI",
        "chat.completions",
        "prompt",
        "narration",
        "micro_note",
    )
    hits: list[str] = []
    for path in advanced_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_advanced_condition_domain_does_not_recreate_planet_nature_sets() -> None:
    """Les natures benefique/malefique doivent venir du runtime DB-backed."""
    advanced_root = BACKEND_ROOT / "app/domain/astrology/advanced_conditions"
    forbidden_sets = {
        frozenset({"venus", "jupiter"}),
        frozenset({"mars", "saturn"}),
    }
    hits: list[str] = []
    for path in advanced_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Set, ast.Tuple, ast.List)):
                continue
            values = {
                element.value
                for element in node.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            }
            if frozenset(values) in forbidden_sets:
                hits.append(f"{path}:{sorted(values)}")

    assert hits == []


def test_advanced_conditions_are_projected_from_natal_result_only() -> None:
    """Le serialiseur public ne recalcule pas les conditions avancees."""
    tree = ast.parse(_source("app/services/chart/json_builder.py"))
    serializer = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_serialize_advanced_conditions"
    )
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(serializer)
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name)
    ]

    assert "AdvancedConditionEngine" not in "".join(calls)


def test_interpretation_adapter_domain_does_not_cross_runtime_boundaries() -> None:
    """La couche d'adaptation reste pure et sans vocabulaire local non versionne."""
    adapter_root = BACKEND_ROOT / "app/domain/astrology/interpretation_adapters"
    forbidden_patterns = (
        "Session",
        "select(",
        "from app.infra",
        "from app.services",
        "from app.api",
        "from app.domain.prediction",
        "from app.services.prediction",
        "INTERPRETATION_" + "RULES",
        "SIGNAL_" + "TYPES",
        "THEME_" + "CODES",
        "PRIORITY_" + "ORDER",
        "ADAPTER_" + "RULES",
        "AIEngineAdapter",
        "OpenAI",
        "chat.completions",
        "prompt",
        "narration",
        "persona",
        "horoscope",
        "matching",
        "micro_note",
    )
    hits: list[str] = []
    for path in adapter_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_interpretation_adapter_is_projected_from_natal_result_only() -> None:
    """Le serialiseur public ne recalcule pas l'adaptation interpretative."""
    tree = ast.parse(_source("app/services/chart/json_builder.py"))
    serializer = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_serialize_interpretation_adapter"
    )
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(serializer)
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name)
    ]

    assert "InterpretationAdapterEngine" not in "".join(calls)


def test_dominant_planets_are_projected_from_natal_result_only() -> None:
    """Le serialiseur public ne recalcule pas les planetes dominantes."""
    tree = ast.parse(_source("app/services/chart/json_builder.py"))
    serializer = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_serialize_dominant_planets"
    )
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(serializer)
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name)
    ]

    assert "PlanetDominanceEngine" not in "".join(calls)


def test_chart_balance_projection_does_not_map_sign_profile_codes() -> None:
    """Le serialiseur public projette les profils calcules sans mapping local."""
    tree = ast.parse(_source("app/services/chart/json_builder.py"))
    serializer = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_serialize_chart_balance"
    )
    source = ast.unparse(serializer)

    assert "SignRuntimeData" not in source
    assert "signs_runtime" not in source
    for forbidden in (
        "FERTILITY_BY_SIGN",
        "VOICE_BY_SIGN",
        "FORM_BY_SIGN",
        "SEASONAL_QUADRANT_BY_SIGN",
        "POLARITY_BY_SIGN",
    ):
        assert forbidden not in source


def test_chart_signature_planets_remain_structural_balance_not_canonical_dominance() -> None:
    """La balance conserve son ancien rang structurel sans remplacer CS-194."""
    chart_signature_source = _source("app/domain/astrology/interpretation/chart_signature.py")
    natal_source = _source("app/domain/astrology/natal_calculation.py")

    assert "PlanetDominanceEngine" not in chart_signature_source
    assert '"sign_runtime"' in chart_signature_source
    assert "dominant_planets=dominant_planets" in chart_signature_source
    assert "dominant_planets=dominant_planets" in natal_source
