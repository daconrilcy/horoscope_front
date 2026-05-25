# Commentaire global: ces tests verrouillent le contrat interne de la projection
# technique expert sans creer de surface runtime publique.
"""Tests de contrat pour expert_technical_projection_v1."""

from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPO_ROOT / "docs" / "architecture" / "expert-technical-projection-v1-contract.md"
REGISTRY_PATH = (
    REPO_ROOT / "docs" / "architecture" / "official-product-primitives-public-projections.md"
)
CURRENT_STATE_PATH = (
    REPO_ROOT / "docs" / "architecture" / "product-architecture-current-state-2026-05-24.md"
)
RBAC_PATH = REPO_ROOT / "backend" / "app" / "core" / "rbac.py"


def _contract_content() -> str:
    """Charge le contrat canonique de projection technique expert."""
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _registry_row() -> str:
    """Retourne la ligne de registre associee a la projection technique expert."""
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    return next(
        line
        for line in registry.splitlines()
        if line.startswith("| `expert_technical_projection` |")
    )


def test_contract_document_defines_internal_projection_shape() -> None:
    """Valide les champs obligatoires et la classification interne du contrat."""
    content = _contract_content()

    assert content.startswith("<!-- Commentaire global:")
    for expected in (
        "expert_technical_projection_v1",
        "interne",
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


def test_contract_lists_allowed_astrology_families_and_evidence_links() -> None:
    """Controle les familles de donnees et les liens de preuve autorises."""
    content = _contract_content()

    for family in ("dignity", "conditions", "dominance", "aspects", "houses"):
        assert family in content
    for source in ("structured_facts_v1", "structured signals", "evidence_refs"):
        assert source in content


def test_contract_excludes_b2c_and_raw_technical_payloads() -> None:
    """Empeche la confusion avec une surface client ou debug brute."""
    content = _contract_content()

    for denied in (
        "Clients B2C",
        "raw runtime traces",
        "prompt internals",
        "replay payloads",
        "provider debug dumps",
        "unrestricted technical diagnostics",
        "ChartObjectRuntimeData",
    ):
        assert denied in content
    assert "fallback silencieux" in content


def test_registry_reclassifies_expert_projection_as_internal_only() -> None:
    """Verifie que le registre ne presente plus cette projection comme publique."""
    row = _registry_row()

    assert "internal-only" in row
    assert "non client" in row
    assert "expert_technical_projection_v1" in row
    assert "none for public API" in row
    assert "none for public frontend client" in row
    assert "| public |" not in row
    assert "futur contrat public expert" not in row


def test_current_state_reclassifies_expert_projection_as_internal_only() -> None:
    """Verifie que la synthese d'architecture ne ravive pas l'ambiguite publique."""
    content = CURRENT_STATE_PATH.read_text(encoding="utf-8")
    expert_lines = "\n".join(
        line for line in content.splitlines() if "expert_technical_projection" in line
    )

    for required in (
        "expert_technical_projection` est reclassifie interne, non client",
        "Expert internal projection",
        "internal admin/expert only; no B2C frontend",
        "`expert_technical_projection` is internal-only",
        "no B2C expert projection",
    ):
        assert required in content
    for forbidden in (
        "Expert public projection",
        "Public expert projection needs field selection",
        "Define expert technical public projection contract",
        "public_api future, frontend future",
    ):
        assert forbidden not in expert_lines


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


def test_runtime_surfaces_do_not_expose_internal_projection() -> None:
    """Prouve que la story reste neutre pour routes, OpenAPI et roles actifs."""
    serialized_openapi = str(app.openapi())
    route_paths = {route.path for route in app.routes}
    rbac_source = RBAC_PATH.read_text(encoding="utf-8")

    assert "expert_technical_projection_v1" not in serialized_openapi
    assert not any("expert-technical-projection" in path for path in route_paths)
    assert "ASTRO_EXPERT" not in rbac_source
