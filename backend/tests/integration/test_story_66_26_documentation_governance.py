from pathlib import Path

def test_llm_pipeline_documentation_governance_rules():
    """
    Vérifie que le document d'architecture LLM respecte les règles de gouvernance 66.26.
    (AC1, AC2, AC3, AC6, AC7)
    """
    # Chemin vers le document d'architecture depuis la racine du repo
    # Le test est lancé depuis backend/, donc on remonte d'un niveau
    root = Path(__file__).parent.parent.parent.parent
    doc_path = root / "docs" / "llm-prompt-generation-by-feature.md"
    
    assert doc_path.exists(), f"Le document {doc_path} doit exister."
    
    content = doc_path.read_text(encoding="utf-8")
    
    # AC1, AC6 : Référence stable (pas de HEAD)
    assert "Commit SHA" in content or "Référence stable" in content
    check_block = "Dernière vérification manuelle contre le pipeline réel du gateway"
    assert "HEAD" not in content.split(check_block)[-1], \
        "Le bloc de vérification finale ne doit plus accepter 'HEAD' comme référence stable."

    # AC2, AC7 : Obligation explicite
    assert "Maintenance de cette documentation" in content
    assert "obligatoire" in content.lower()
    assert "traçable" in content.lower()
    justif_ok = ("justifier explicitement" in content or 
                 "justification d'absence de changement" in content)
    assert justif_ok, "La justification doit être mentionnée."

    # AC3 : Zones à impact obligatoire bornées
    required_zones = [
        "_resolve_plan()",
        "execute_request()",
        "_call_provider()",
        "_build_messages()",
        "PromptRenderer",
        "PromptAssemblyConfig",
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
    # Chemin vers le template PR
    root = Path(__file__).parent.parent.parent.parent
    template_path = root / ".github" / "pull_request_template.md"
    
    assert template_path.exists(), f"Le template PR {template_path} doit exister."
    
    content = template_path.read_text(encoding="utf-8")
    
    # AC4 : Règle PR présente
    assert "Maintenance du Pipeline LLM" in content
    assert "Gouvernance obligatoire" in content
    
    # AC5 : Cohérence des zones
    required_zones_in_pr = [
        "_resolve_plan()",
        "execute_request()",
        "_call_provider()",
        "_build_messages()",
        "PromptRenderer",
        "PromptAssemblyConfig",
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
