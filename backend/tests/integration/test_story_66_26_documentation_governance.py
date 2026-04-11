import re
from pathlib import Path


def _extract_verification_block(content: str) -> str:
    marker = "Dernière vérification manuelle contre le pipeline réel du gateway"
    assert marker in content
    return content.split(marker, maxsplit=1)[1].split("Si le code diverge", maxsplit=1)[0]


def _find_line(block: str, prefix: str) -> str:
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line
    raise AssertionError(f"Ligne attendue introuvable dans le bloc de vérification: {prefix}")


def test_llm_pipeline_documentation_governance_rules():
    """
    Vérifie que le document d'architecture LLM respecte les règles de gouvernance 66.26.
    (AC1, AC2, AC3, AC6, AC7, AC9)
    """
    root = Path(__file__).parent.parent.parent.parent
    doc_path = root / "docs" / "llm-prompt-generation-by-feature.md"

    assert doc_path.exists(), f"Le document {doc_path} doit exister."

    content = doc_path.read_text(encoding="utf-8")

    # AC1, AC6, AC9 : Référence stable et format normatif
    verification_block = _extract_verification_block(content)

    date_line = _find_line(verification_block, "- **Date** :")
    reference_line = _find_line(verification_block, "- **Référence stable")

    # AC1, AC9 : Format stable et répétable avec valeurs auditables
    assert re.fullmatch(r"- \*\*Date\*\* : `\d{4}-\d{2}-\d{2}`", date_line), (
        "La ligne de date doit utiliser un format stable ISO `YYYY-MM-DD`."
    )
    assert re.fullmatch(
        r"- \*\*Référence stable(?: \(Commit SHA\))?\*\* : `(?:[0-9a-f]{7,40}|v[0-9A-Za-z._-]+)`",
        reference_line,
    ), "La référence stable doit être un SHA git ou un tag explicite dans un format répétable."

    # AC1, AC6 : Pas de référence flottante dans le bloc de vérification
    assert "HEAD" not in verification_block, (
        "Le bloc de vérification finale ne doit plus accepter 'HEAD' comme référence stable."
    )
    forbidden_floating_refs = ["main", "master", "branche courante", "current branch"]
    lowered_block = verification_block.lower()
    for floating_ref in forbidden_floating_refs:
        assert floating_ref not in lowered_block, (
            f"Le bloc de vérification ne doit pas contenir la référence flottante '{floating_ref}'."
        )

    # AC2, AC7 : Obligation explicite
    assert "Maintenance de cette documentation" in content
    assert "obligatoire" in content.lower()
    assert "traçable" in content.lower()
    justif_ok = (
        "justifier explicitement" in content or "justification d'absence de changement" in content
    )
    assert justif_ok, "La justification doit être mentionnée."

    # AC3 : Zones à impact obligatoire bornées (incluant context_quality)
    required_zones = [
        "_resolve_plan()",
        "execute_request()",
        "_call_provider()",
        "_build_messages()",
        "PromptRenderer",
        "PromptAssemblyConfig",
        "context_quality",
        "ContextQualityInjector",
        "ProviderParameterMapper",
        "FallbackGovernanceRegistry",
        "feature/subfeature/plan",
        "ExecutionProfile",
    ]

    for zone in required_zones:
        assert zone in content, f"La zone '{zone}' doit être listée."


def test_pull_request_template_governance_rules():
    """
    Vérifie que le template PR contient les règles de gouvernance LLM.
    (AC4, AC5)
    """
    root = Path(__file__).parent.parent.parent.parent
    template_path = root / ".github" / "pull_request_template.md"

    assert template_path.exists(), f"Le template PR {template_path} doit exister."

    content = template_path.read_text(encoding="utf-8")

    # AC4 : Règle PR présente
    assert "Maintenance du Pipeline LLM" in content
    assert "Gouvernance obligatoire" in content

    # AC5 : Cohérence des zones (incluant context_quality)
    required_zones_in_pr = [
        "_resolve_plan()",
        "execute_request()",
        "_call_provider()",
        "_build_messages()",
        "PromptRenderer",
        "PromptAssemblyConfig",
        "context_quality",
        "ContextQualityInjector",
        "ProviderParameterMapper",
        "FallbackGovernanceRegistry",
        "feature/subfeature/plan",
        "ExecutionProfile",
    ]

    for zone in required_zones_in_pr:
        assert zone in content, f"Le template PR doit mentionner la zone '{zone}'."

    # AC5 : Deux issues (MAJ ou Justification)
    assert "J'ai mis à jour" in content
    assert "JUSTIFICATION" in content

    # Vérification bonus : liens relatifs sans slash initial pour GitHub
    assert "(/docs/" not in content, "Les liens ne doivent pas commencer par un slash initial."
    assert "](docs/" in content, "Les liens doivent être relatifs au repo."
