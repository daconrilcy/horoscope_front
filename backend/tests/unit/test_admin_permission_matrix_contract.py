# Commentaire global: ces tests verrouillent la matrice cible des permissions admin
# sans activer de nouveaux roles RBAC.
"""Tests de contrat de la matrice cible des permissions admin."""

from pathlib import Path

from app.core.rbac import VALID_ROLES

REPO_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = REPO_ROOT / "docs" / "architecture" / "admin-permission-matrix.md"
RBAC_PATH = REPO_ROOT / "backend" / "app" / "core" / "rbac.py"

INTERNAL_ROLES = {"ADMIN", "MARKETER", "TECHNO", "ASTRO_EXPERT"}
FUTURE_INTERNAL_ROLES = INTERNAL_ROLES - {"ADMIN"}
DATA_DOMAINS = {"business", "technical", "astrology", "debug"}
REQUIRED_ACTIONS = {"read", "search", "export", "replay", "correct"}
DEBUG_CATEGORIES = {"traces", "prompts", "replay"}
OPEN_DECISIONS = {
    "OPEN-ADMIN-PERM-001",
    "OPEN-ADMIN-PERM-002",
    "OPEN-ADMIN-PERM-003",
    "OPEN-ADMIN-PERM-004",
    "OPEN-ADMIN-PERM-005",
}


def _matrix_content() -> str:
    """Charge la matrice canonique des permissions admin."""
    return DOC_PATH.read_text(encoding="utf-8")


def _role_rows(content: str, role: str) -> list[str]:
    """Retourne les lignes de matrice documentant un role donne."""
    return [line for line in content.splitlines() if line.startswith(f"| `{role}` |")]


def test_permission_matrix_document_exists_and_defines_contract_shape() -> None:
    """Valide l'existence et les champs obligatoires de la matrice."""
    content = _matrix_content()

    assert content.startswith("<!-- Commentaire global:")
    for field in (
        "role_code",
        "data_domain",
        "data_category",
        "action",
        "current_access",
        "target_access",
        "masking_rule",
        "decision_status",
        "rbac_activation_state",
    ):
        assert field in content


def test_permission_matrix_covers_roles_domains_and_actions() -> None:
    """Controle que la matrice croise les roles, domaines et actions attendus."""
    content = _matrix_content()

    for role in INTERNAL_ROLES:
        rows = _role_rows(content, role)
        assert rows, role
        for domain in DATA_DOMAINS:
            assert any(f"| `{domain}` |" in row for row in rows), (role, domain)

    for action in REQUIRED_ACTIONS:
        assert f"`{action}`" in content


def test_sensitive_and_debug_data_are_separated() -> None:
    """Verifie les regles de sensibilite, masquage et separation debug."""
    content = _matrix_content()
    lowered = content.lower()

    assert "données de naissance" in content
    assert "donnees sensibles" in lowered
    assert "masquees hors contexte admin explicitement approuve" in lowered
    for category in DEBUG_CATEGORIES:
        assert category in lowered
    assert "surfaces distinctes" in lowered
    assert "une permission sur l'une n'ouvre pas les deux autres" in lowered


def test_future_roles_have_no_current_access_until_rbac() -> None:
    """Empeche la matrice d'accorder un acces courant aux roles cibles."""
    content = _matrix_content()

    for role in FUTURE_INTERNAL_ROLES:
        rows = _role_rows(content, role)
        assert rows, role
        assert all("| refuse |" in row for row in rows)
        assert all("inactive until RBAC" in row for row in rows)

    normalized_roles = {role.lower() for role in VALID_ROLES}
    forbidden_runtime_roles = {role.lower() for role in FUTURE_INTERNAL_ROLES}
    assert forbidden_runtime_roles.isdisjoint(normalized_roles)
    assert all(role not in RBAC_PATH.read_text(encoding="utf-8") for role in FUTURE_INTERNAL_ROLES)


def test_b2c_access_is_excluded_and_open_decisions_are_listed() -> None:
    """Controle l'exclusion B2C et la visibilite des decisions ouvertes."""
    content = _matrix_content()

    assert "Les acces client B2C sont exclus de cette matrice admin" in content
    for marker in OPEN_DECISIONS:
        assert marker in content
    assert "decision ouverte" in content or "decisions ouvertes" in content
