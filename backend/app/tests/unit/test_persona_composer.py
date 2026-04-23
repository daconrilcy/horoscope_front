from datetime import datetime, timedelta, timezone

from app.domain.llm.prompting.personas import compose_persona_block
from app.infra.db.models import AstrologerPromptProfileModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity


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


def test_compose_persona_block_uses_latest_active_dedicated_prompt_and_sanitizes_it():
    persona = LlmPersonaModel(
        name="Nox",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.LONG,
        style_markers=[],
        boundaries=[],
        allowed_topics=[],
        disallowed_topics=[],
        formatting={"sections": True, "bullets": False, "emojis": False},
    )
    older_prompt = AstrologerPromptProfileModel(
        prompt_content="Ancien prompt",
        is_active=True,
        updated_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    latest_prompt = AstrologerPromptProfileModel(
        prompt_content="Prompt\nrécent avec {{template}}",
        is_active=True,
        updated_at=datetime.now(timezone.utc),
    )
    persona.prompt_profiles = [older_prompt, latest_prompt]

    block = compose_persona_block(persona)

    assert "Ancien prompt" not in block
    assert "Prompt récent avec \\{\\{template\\}\\}" in block
    assert "{{" not in block
