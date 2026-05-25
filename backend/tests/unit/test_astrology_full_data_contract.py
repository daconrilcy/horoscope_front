# Commentaire global: ces tests verrouillent le contrat interne
# astrology_full_data_v1 sans ouvrir de surface runtime publique.
"""Tests de contrat pour astrology_full_data_v1."""

from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPO_ROOT / "docs" / "architecture" / "astrology-full-data-v1-contract.md"
REGISTRY_PATH = (
    REPO_ROOT / "docs" / "architecture" / "official-product-primitives-public-projections.md"
)
RBAC_PATH = REPO_ROOT / "backend" / "app" / "core" / "rbac.py"


def _contract_content() -> str:
    """Charge le contrat canonique de projection astrologique complete."""
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _registry_row() -> str:
    """Retourne la ligne du registre associee a la projection complete."""
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    return next(
        line for line in registry.splitlines() if line.startswith("| `astrology_full_data` |")
    )


def test_contract_document_defines_internal_expert_projection_shape() -> None:
    """Valide l'identite, l'audience et la classification interne."""
    content = _contract_content()

    assert content.startswith("<!-- Commentaire global:")
    for expected in (
        "astrology_full_data_v1",
        "interne",
        "protected",
        "expert-oriented",
        "non client",
        "not client-safe",
        "ADMIN",
        "ASTRO_EXPERT",
        "target-only",
        "B2C",
        "CS-271",
        "admin-permission-matrix.md",
    ):
        assert expected in content


def test_contract_lists_full_astrology_families_and_source_dependencies() -> None:
    """Controle les familles astrologiques completes et les sources exigees."""
    content = _contract_content()

    for family in (
        "chart_objects_summary",
        "positions",
        "houses",
        "dignities",
        "conditions",
        "aspects",
        "dominance",
        "fixed-star policy",
        "sources",
    ):
        assert family in content
    for source in (
        "structured_facts_v1",
        "source versions",
        "doctrine",
        "school metadata",
        "evidence_refs",
    ):
        assert source in content


def test_contract_separates_business_astrology_from_technical_diagnostics() -> None:
    """Empeche la fusion avec les diagnostics et payloads debug bruts."""
    content = _contract_content()

    for denied in (
        "admin_chart_diagnostics_v1",
        "raw runtime traces",
        "calculation debug payloads",
        "replay payloads",
        "provider debug dumps",
        "unrestricted technical diagnostics",
        "ChartObjectRuntimeData",
        "fallback silencieux",
    ):
        assert denied in content
    assert "ne deviennent pas une famille de donnees" in content


def test_fixed_star_policy_denies_client_exposure() -> None:
    """Verifie que les etoiles fixes restent internes et policy-bound."""
    content = _contract_content()
    fixed_star_section = content.split("`fixed-star policy`", maxsplit=1)[1]

    assert "policy-bound" in fixed_star_section
    assert "aucune client exposure" in fixed_star_section
    assert "raw fixed-star catalog data" in fixed_star_section


def test_privacy_masking_rules_cover_birth_and_identifier_fields() -> None:
    """Controle le masquage des champs personnels sensibles."""
    content = _contract_content()

    for sensitive_field in (
        "birth date",
        "birth time",
        "birth place",
        "user id",
        "chart id",
        "masking",
        "justifiee",
    ):
        assert sensitive_field in content


def test_access_log_fields_are_required_by_contract() -> None:
    """Controle les champs minimaux attendus pour les decisions d'acces."""
    content = _contract_content()

    for field in (
        "actor",
        "role",
        "projection id",
        "chart_or_answer_reference",
        "action",
        "decision",
        "timestamp",
        "correlation_id",
    ):
        assert field in content


def test_registry_marks_projection_as_internal_and_non_public() -> None:
    """Verifie que le registre existant reste le seul point d'alignement."""
    row = _registry_row()

    assert "internal-only" in row
    assert "non client" in row
    assert "astrology_full_data_v1" in row
    assert "none for public API" in row
    assert "none for public frontend client" in row
    assert "| public |" not in row


def test_runtime_surfaces_do_not_expose_full_astrology_projection() -> None:
    """Prouve la neutralite routes, OpenAPI et roles actifs."""
    serialized_openapi = str(app.openapi())
    route_paths = {route.path for route in app.routes}
    rbac_source = RBAC_PATH.read_text(encoding="utf-8")

    assert "astrology_full_data_v1" not in serialized_openapi
    assert "astrology_full_data" not in serialized_openapi
    assert not any("astrology-full-data" in path for path in route_paths)
    assert not any("astrology_full_data" in path for path in route_paths)
    assert "ASTRO_EXPERT" not in rbac_source
