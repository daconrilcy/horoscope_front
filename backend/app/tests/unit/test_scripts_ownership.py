# Garde d'ownership des scripts racine.
"""Verifie que chaque script racine possede une decision d'ownership."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
OWNERSHIP_REGISTRY_PATH = SCRIPTS_ROOT / "ownership-index.md"
BASELINE_INVENTORY_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "formalize-scripts-ownership"
    / "scripts-inventory-baseline.txt"
)
AFTER_INVENTORY_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "formalize-scripts-ownership"
    / "scripts-inventory-after.txt"
)
REQUIRED_ROW_FIELDS = (
    "script",
    "family",
    "owner",
    "usage",
    "validation_command",
    "support_status",
    "decision",
)
EXPECTED_REGISTRY_HEADER = "| " + " | ".join(REQUIRED_ROW_FIELDS) + " |"
ALLOWED_FAMILIES = {"quality", "security", "db", "perf", "llm", "dev", "story-tools"}
ALLOWED_SUPPORT_STATUSES = {
    "supported",
    "supported-with-follow-up",
    "dev-only",
    "needs-user-decision",
}


def _current_script_inventory() -> set[str]:
    """Retourne les fichiers racine `scripts/` dans un format stable."""
    return {
        path.relative_to(REPO_ROOT).as_posix() for path in SCRIPTS_ROOT.iterdir() if path.is_file()
    }


def _ownership_registry_lines() -> list[str]:
    """Retourne les lignes du registre d'ownership sans alterer le Markdown."""
    return OWNERSHIP_REGISTRY_PATH.read_text(encoding="utf-8").splitlines()


def _snapshot_inventory(path: Path) -> set[str]:
    """Parse un snapshot `rg --files scripts` en chemins normalises."""
    return {
        line.strip().replace("\\", "/")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _ownership_rows() -> dict[str, dict[str, str]]:
    """Parse le registre Markdown des scripts et refuse les doublons."""
    rows: dict[str, dict[str, str]] = {}
    duplicate_scripts: list[str] = []
    for line in _ownership_registry_lines():
        if not line.startswith("| `scripts/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(REQUIRED_ROW_FIELDS):
            raise AssertionError(f"ligne d'ownership invalide: {line}")

        values = dict(zip(REQUIRED_ROW_FIELDS, cells, strict=True))
        script_path = values["script"].strip("`")
        values["script"] = script_path
        values["validation_command"] = values["validation_command"].strip("`")
        if script_path in rows:
            duplicate_scripts.append(script_path)
        rows[script_path] = values

    if duplicate_scripts:
        raise AssertionError(
            "lignes d'ownership dupliquees: " + ", ".join(sorted(set(duplicate_scripts)))
        )
    return rows


def test_route_removal_audit_validator_is_not_root_script() -> None:
    """Le validateur ponctuel de suppression des routes reste absent de `scripts/`."""
    forbidden_name = "validate_route_removal_audit" + ".py"
    forbidden_script = REPO_ROOT / "scripts" / forbidden_name

    assert not forbidden_script.exists()


def test_scripts_ownership_registry_covers_current_inventory() -> None:
    """Chaque script racine doit avoir une ligne d'ownership unique."""
    registry_rows = _ownership_rows()
    current_scripts = _current_script_inventory()

    assert sorted(current_scripts - set(registry_rows)) == []
    assert sorted(set(registry_rows) - current_scripts) == []


def test_scripts_ownership_registry_exposes_required_header() -> None:
    """Le tableau Markdown conserve son contrat de colonnes visible."""
    assert EXPECTED_REGISTRY_HEADER in _ownership_registry_lines()


def test_scripts_ownership_rows_are_actionable() -> None:
    """Le registre expose les colonnes et decisions obligatoires."""
    offenders: list[str] = []
    for script_path, row in _ownership_rows().items():
        real_path = REPO_ROOT / script_path
        if not real_path.exists():
            offenders.append(f"{script_path}: missing file")
        if row["family"] not in ALLOWED_FAMILIES:
            offenders.append(f"{script_path}: unsupported family {row['family']}")
        if not row["owner"]:
            offenders.append(f"{script_path}: missing owner")
        if not row["usage"]:
            offenders.append(f"{script_path}: missing usage")
        if not row["validation_command"]:
            offenders.append(f"{script_path}: missing validation command")
        if row["support_status"] not in ALLOWED_SUPPORT_STATUSES:
            offenders.append(f"{script_path}: unsupported support status {row['support_status']}")
        if not row["decision"]:
            offenders.append(f"{script_path}: missing decision")

    assert offenders == []


def test_scripts_inventory_snapshots_prove_no_path_was_moved() -> None:
    """Les snapshots avant/apres prouvent que seul le registre a ete ajoute."""
    baseline_scripts = _snapshot_inventory(BASELINE_INVENTORY_PATH)
    after_scripts = _snapshot_inventory(AFTER_INVENTORY_PATH)

    assert "scripts/ownership-index.md" not in baseline_scripts
    assert after_scripts == baseline_scripts | {"scripts/ownership-index.md"}


def test_stripe_shell_listener_keeps_blocked_support_decision() -> None:
    """Le listener shell Stripe reste bloque en attente de decision utilisateur."""
    stripe_shell = _ownership_rows()["scripts/stripe-listen-webhook.sh"]

    assert stripe_shell["support_status"] == "needs-user-decision"
    assert stripe_shell["decision"] == "blocked-support-decision"
