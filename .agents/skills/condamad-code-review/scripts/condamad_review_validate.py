#!/usr/bin/env python3
"""Valide la structure minimale du skill CONDAMAD Code Review.

Ce script garde la maintenance du skill explicite: il verifie les fichiers
obligatoires, les marqueurs de doctrine et les valeurs de verdict attendues.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "workflow.md",
    "agents/openai.yaml",
    "references/review-doctrine.md",
    "references/finding-taxonomy.md",
    "references/codex-modern-review-guidance.md",
    "steps/step-01-target-and-context.md",
    "steps/step-02-adversarial-review.md",
    "steps/step-03-triage-and-evidence.md",
    "steps/step-04-report-and-next-action.md",
]

SEVERITIES = ["Critical", "High", "Medium", "Low"]
VERDICTS = [
    "BLOCKING",
    "CHANGES_REQUESTED",
    "ACCEPTABLE_WITH_LIMITATIONS",
    "CLEAN",
]
FORBIDDEN_PATH_PARTS = {"__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def read_text(path: Path) -> str:
    """Lit un fichier UTF-8 et renvoie une chaine vide si le fichier manque."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def has_frontmatter_field(content: str, field: str) -> bool:
    """Verifie qu'un champ existe dans le frontmatter YAML du skill."""
    match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    return bool(match and re.search(rf"^{re.escape(field)}:", match.group(1), re.M))


def validate(skill_dir: Path) -> list[str]:
    """Retourne la liste des erreurs structurelles detectees."""
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        path = skill_dir / relative
        if not path.exists():
            errors.append(f"Missing required file: {relative}")
            continue
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"Required file is empty: {relative}")

    skill_content = read_text(skill_dir / "SKILL.md")
    for field in ["name", "description"]:
        if not has_frontmatter_field(skill_content, field):
            errors.append(f"SKILL.md missing frontmatter field: {field}")

    openai_yaml = read_text(skill_dir / "agents" / "openai.yaml")
    if "allow_implicit_invocation: false" not in openai_yaml:
        errors.append("agents/openai.yaml must set allow_implicit_invocation: false")
    if "$condamad-code-review" not in openai_yaml:
        errors.append(
            "agents/openai.yaml default_prompt must mention $condamad-code-review"
        )

    taxonomy = read_text(skill_dir / "references" / "finding-taxonomy.md")
    for severity in SEVERITIES:
        if severity not in taxonomy:
            errors.append(f"finding-taxonomy.md missing severity: {severity}")

    workflow = read_text(skill_dir / "workflow.md")
    for verdict in VERDICTS:
        if verdict not in workflow:
            errors.append(f"workflow.md missing verdict: {verdict}")

    doctrine = read_text(skill_dir / "references" / "review-doctrine.md")
    if "False CLEAN Prevention" not in doctrine:
        errors.append("review-doctrine.md missing False CLEAN Prevention section")

    step_one = read_text(skill_dir / "steps" / "step-01-target-and-context.md")
    if "git ls-files --others --exclude-standard" not in step_one:
        errors.append("step-01-target-and-context.md does not require untracked scan")

    for path in skill_dir.rglob("*"):
        relative = path.relative_to(skill_dir)
        if any(part in FORBIDDEN_PATH_PARTS for part in relative.parts):
            errors.append(f"Forbidden cache path in skill: {relative.as_posix()}")
        if path.suffix in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden bytecode file in skill: {relative.as_posix()}")

    return errors


def main() -> int:
    """Point d'entree CLI du validateur de skill."""
    parser = argparse.ArgumentParser(
        description="Validate the CONDAMAD code-review skill structure."
    )
    parser.add_argument(
        "skill_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to condamad-code-review skill directory.",
    )
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    errors = validate(skill_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {skill_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
