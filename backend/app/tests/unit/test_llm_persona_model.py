import uuid

from app.infra.db.models.llm.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity


def test_llm_persona_model_init():
    persona_id = uuid.uuid4()
    persona = LlmPersonaModel(
        id=persona_id,
        name="Luna",
        description="Astrologue bienveillante",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=["tutoiement", "métaphores célestes"],
        boundaries=["jamais de fatalisme"],
        allowed_topics=["astro", "psychologie"],
        disallowed_topics=["santé", "légal"],
        formatting={"sections": True, "bullets": False, "emojis": False},
        enabled=True,
    )

    assert persona.id == persona_id
    assert persona.name == "Luna"
    assert persona.tone == PersonaTone.WARM
    assert persona.verbosity == PersonaVerbosity.MEDIUM
    assert "tutoiement" in persona.style_markers
    assert persona.formatting["sections"] is True
    assert persona.enabled is True
