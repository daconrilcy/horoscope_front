from pathlib import Path

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
    check_block_marker = "Dernière vérification manuelle contre le pipeline réel du gateway"
    assert check_block_marker in content
    
    # Extraire le bloc de vérification finale
    verification_block = content.split(check_block_marker)[-1].split("Si le code diverge")[0]
    
    # AC1, AC9 : Format stable et répétable (Date + Référence stable)
    assert "- **Date** :" in verification_block
    assert "- **Référence stable (Commit SHA)** :" in verification_block
    
    # AC1, AC6 : Pas de HEAD dans le bloc de vérification
    assert "HEAD" not in verification_block, \
        "Le bloc de vérification finale ne doit plus accepter 'HEAD' comme référence stable."

    # AC2, AC7 : Obligation explicite
    assert "Maintenance de cette documentation" in content
    assert "obligatoire" in content.lower()
    assert "traçable" in content.lower()
    justif_ok = ("justifier explicitement" in content or 
                 "justification d'absence de changement" in content)
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
        "ExecutionProfile"
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
        "ExecutionProfile"
    ]
    
    for zone in required_zones_in_pr:
        assert zone in content, f"Le template PR doit mentionner la zone '{zone}'."
        
    # AC5 : Deux issues (MAJ ou Justification)
    assert "J'ai mis à jour" in content
    assert "JUSTIFICATION" in content
    
    # Vérification bonus : liens relatifs sans slash initial pour GitHub
    assert "(/docs/" not in content, "Les liens ne doivent pas commencer par un slash initial."
    assert "](docs/" in content, "Les liens doivent être relatifs au repo."
