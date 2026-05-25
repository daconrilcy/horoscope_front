# Commentaire global: ces tests verrouillent le modele documentaire des roles internes
# sans activer de nouveaux acces.
"""Tests de contrat du vocabulaire cible des roles internes."""

from pathlib import Path

from app.core.rbac import VALID_ROLES

REPO_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = REPO_ROOT / "docs" / "architecture" / "internal-role-model.md"
RBAC_PATH = REPO_ROOT / "backend" / "app" / "core" / "rbac.py"
ADMIN_DOC_PATH = REPO_ROOT / "docs" / "admin-implementation-overview.md"

INTERNAL_ROLES = {"ADMIN", "MARKETER", "TECHNO", "ASTRO_EXPERT"}
FUTURE_INTERNAL_ROLES = INTERNAL_ROLES - {"ADMIN"}
OUT_OF_MODEL_RUNTIME_ROLES = {"user", "support", "ops", "enterprise_admin"}
REQUIRED_ADMIN_SURFACES = {
    "admin dashboard",
    "audit",
    "content",
    "logs",
    "support",
}
ADMIN_DOC_SURFACE_MARKERS = {
    "admin dashboard": ("admindashboardpage", "/admin/dashboard"),
    "audit": ("/v1/admin/audit",),
    "content": ("admincontentpage", "/admin/content"),
    "logs": ("adminlogspage", "/admin/logs"),
    "support": ("adminsupportpage", "/admin/support"),
}


def _role_model_content() -> str:
    """Charge le document canonique des roles internes."""
    return DOC_PATH.read_text(encoding="utf-8")


def _role_block(content: str, role: str) -> str:
    """Isole la fiche documentaire d'un role interne."""
    start = content.index(f"### `{role}`")
    next_section = content.find("\n### `", start + 1)
    if next_section == -1:
        next_section = content.find("\n## ", start + 1)
    if next_section == -1:
        next_section = len(content)
    return content[start:next_section]


def test_internal_role_model_document_defines_required_roles_and_boundaries() -> None:
    """Valide la forme minimale du contrat documentaire des roles internes."""
    content = _role_model_content()

    assert content.startswith("<!-- Commentaire global:")
    for role in INTERNAL_ROLES:
        assert f"`{role}`" in content
    assert "`ADMIN` est le seul role interne operationnel aujourd'hui" in content
    for runtime_role in OUT_OF_MODEL_RUNTIME_ROLES:
        assert f"`{runtime_role}`" in content
    assert "ne sont pas des alias" in content
    assert "clients B2C" in content
    assert "comptes B2B" in content
    assert "CS-271" in content
    assert "matrice" in content or "permissions" in content
    for surface in REQUIRED_ADMIN_SURFACES:
        assert surface in content


def test_future_internal_roles_are_target_only_without_current_access() -> None:
    """Empeche une documentation qui accorderait implicitement les futurs roles."""
    content = _role_model_content()

    for role in FUTURE_INTERNAL_ROLES:
        role_section = _role_block(content, role)
        assert "`target-only`" in role_section
        assert "Aucun acces courant" in role_section
        assert "CS-271" in role_section


def test_runtime_rbac_does_not_activate_future_internal_roles() -> None:
    """Verifie que le registre RBAC actif ne contient pas les roles cibles."""
    normalized_roles = {role.lower() for role in VALID_ROLES}
    forbidden_runtime_roles = {role.lower() for role in FUTURE_INTERNAL_ROLES}

    assert "admin" in normalized_roles
    assert OUT_OF_MODEL_RUNTIME_ROLES.issubset(normalized_roles)
    assert forbidden_runtime_roles.isdisjoint(normalized_roles)
    assert all(role not in RBAC_PATH.read_text(encoding="utf-8") for role in FUTURE_INTERNAL_ROLES)


def test_role_model_reuses_existing_admin_surface_documentation() -> None:
    """Controle que les surfaces listees existent deja dans la documentation admin."""
    role_model = _role_model_content()
    admin_doc = ADMIN_DOC_PATH.read_text(encoding="utf-8").lower()

    for surface in REQUIRED_ADMIN_SURFACES:
        assert surface in role_model
        assert any(marker in admin_doc for marker in ADMIN_DOC_SURFACE_MARKERS[surface])
