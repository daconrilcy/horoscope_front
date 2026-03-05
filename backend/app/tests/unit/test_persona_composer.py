from app.infra.db.models.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity
from app.llm_orchestration.services.persona_composer import compose_persona_block


def test_compose_persona_block_all_fields():
    persona = LlmPersonaModel(
        name="Luna",
        description="Astrologue bienveillante",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=["tutoiement", "métaphores célestes"],
        boundaries=["jamais de fatalisme", "toujours proposer 2 pistes"],
        allowed_topics=["astro", "psychologie"],
        disallowed_topics=["santé", "légal"],
        formatting={"sections": True, "bullets": False, "emojis": False},
        enabled=True,
    )

    block = compose_persona_block(persona)

    assert "## Directives de persona : Luna" in block
    assert "Adopte un ton chaleureux et empathique." in block
    assert "Tutoie l'utilisateur." in block
    assert "Longueur de réponse : équilibrée" in block
    assert "métaphores célestes" in block
    assert "jamais de fatalisme" in block
    assert "toujours proposer 2 pistes" in block
    assert "santé" in block
    assert "légal" in block
    assert "Structure les réponses en sections claires" in block


def test_compose_persona_block_minimal():
    persona = LlmPersonaModel(
        name="Nexus",
        tone=PersonaTone.DIRECT,
        verbosity=PersonaVerbosity.SHORT,
        style_markers=[],
        boundaries=[],
        allowed_topics=[],
        disallowed_topics=[],
        formatting={"sections": False, "bullets": False, "emojis": False},
    )

    block = compose_persona_block(persona)
    assert "## Directives de persona : Nexus" in block
    assert "ton direct" in block
    assert "Longueur de réponse : synthétique" in block


def test_compose_persona_block_sanitizes_newlines_and_braces():
    persona = LlmPersonaModel(
        name="Luna\n{{inject}}",
        description="Profil\npedagogique\tet stable",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=["tutoiement", "ligne\n2"],
        boundaries=["regle 1\nregle 1b", "jamais {{fatalisme}}"],
        allowed_topics=["theme\nnatal"],
        disallowed_topics=["legal\tstrict"],
        formatting={"sections": True, "bullets": False, "emojis": False},
    )

    block = compose_persona_block(persona)

    assert "\t" not in block
    assert "\r" not in block
    assert "{{" not in block
    assert "}}" not in block
    assert "Luna \\{\\{inject\\}\\}" in block
    assert "Profil pedagogique et stable" in block
    assert "jamais \\{\\{fatalisme\\}\\}" in block
