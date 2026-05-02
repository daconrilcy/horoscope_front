# Garde du script de demarrage de la stack locale.
"""Verifie que le script dev local garde Stripe optionnel et explicite."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / "scripts" / "start-dev-stack.ps1"
DOC_PATH = REPO_ROOT / "docs" / "local-dev-stack.md"


def _script_content() -> str:
    """Retourne le contenu PowerShell normalise pour les assertions structurelles."""
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _conditional_stripe_branch(content: str) -> str:
    """Isole la branche qui doit posseder toute dependance Stripe explicite."""
    match = re.search(
        r"if \(\$WithStripe\) \{\s+"
        r"Assert-PathExists -Path \$stripeScriptPath.*?"
        r"Assert-CommandExists -Name \"stripe\".*?"
        r"\}",
        content,
        flags=re.DOTALL,
    )
    assert match is not None
    return match.group(0)


def test_default_dev_stack_does_not_require_or_start_stripe() -> None:
    """Le chemin nominal backend/frontend ne doit pas dependre de Stripe."""
    content = _script_content()

    assert "[switch] $WithStripe" in content
    assert "[switch] $Help" in content
    assert "if ($Help)" in content
    assert "SkipStripe" not in content

    unconditional_preamble = content.split("if ($WithStripe)", maxsplit=1)[0]
    assert "Get-Command $Name" in unconditional_preamble
    assert 'Assert-CommandExists -Name "stripe"' not in unconditional_preamble
    assert 'Assert-PathExists -Path $stripeScriptPath -Label "Script Stripe"' not in (
        unconditional_preamble
    )

    base_wt_arguments = re.search(
        r"\$wtArguments = @\((?P<body>.*?)\)\s+if \(\$WithStripe\)",
        content,
        flags=re.DOTALL,
    )
    assert base_wt_arguments is not None
    assert '"--title", "Backend"' in base_wt_arguments.group("body")
    assert '"--title", "Frontend"' in base_wt_arguments.group("body")
    assert '"--title", "Stripe"' not in base_wt_arguments.group("body")


def test_with_stripe_branch_requires_cli_and_reuses_listener_script() -> None:
    """Le mode Stripe doit echouer explicitement si la CLI Stripe est absente."""
    content = _script_content()
    validation_branch = _conditional_stripe_branch(content)

    assert 'Assert-CommandExists -Name "stripe"' in validation_branch
    assert "relancez sans -WithStripe" in validation_branch
    assert 'Assert-PathExists -Path $stripeScriptPath -Label "Script Stripe"' in validation_branch

    wt_branch = re.search(
        r"if \(\$WithStripe\) \{\s+\$wtArguments \+= @\((?P<body>.*?)\)\s+\}",
        content,
        flags=re.DOTALL,
    )
    assert wt_branch is not None
    assert '"--title", "Stripe"' in wt_branch.group("body")
    assert "$stripeCommand" in wt_branch.group("body")


def test_dev_stack_documentation_names_default_and_stripe_modes() -> None:
    """La documentation doit rendre visible le mode par defaut et le mode Stripe."""
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "scripts/start-dev-stack.ps1" in content
    assert "-WithStripe" in content
    assert "backend et frontend" in content
    assert "Stripe CLI" in content
