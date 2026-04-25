"""
Tests d'intégration AC5 : différentiation de prompts par persona.

Valide que :
- Le contexte persona (tone, verbosity, style_markers, boundaries) est correctement
  injecté dans le contexte transmis au générateur LLM.
- Un persona "Mystique Verbeux" produit un prompt substantiellement différent d'un
  persona "Analytique Concis".
- L'isolation de contexte est assurée : le prompt d'un astrologue ne contient aucune
  trace du style de l'autre (AC3).
- Le fallback legacy fonctionne si persona_id est None (AC4).
"""

import uuid
from typing import Any

import pytest

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_persona import LlmPersonaModel, PersonaTone, PersonaVerbosity
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.llm_generation.chat.chat_guidance_service import ChatGuidanceService
from app.tests.helpers.llm_adapter_stub import reset_test_generators, set_test_chat_generator


def _cleanup_tables() -> None:
    ChatGuidanceService.reset_quality_kpis()
    reset_test_generators()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_user(email: str) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        db.commit()
        return auth.user.id


def _create_persona(
    name: str,
    tone: PersonaTone,
    verbosity: PersonaVerbosity,
    style_markers: list[str],
    boundaries: list[str],
) -> uuid.UUID:
    with SessionLocal() as db:
        persona = LlmPersonaModel(
            name=name,
            enabled=True,
            tone=tone,
            verbosity=verbosity,
            style_markers=style_markers,
            boundaries=boundaries,
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(persona)
        db.commit()
        return persona.id


class ContextCapturingGenerator:
    """Capture les appels au générateur LLM pour inspection du contexte."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str,
    ) -> str:
        self.calls.append({"messages": messages, "context": dict(context)})
        return "Réponse test."


def test_persona_context_fields_injected_for_mystical_persona() -> None:
    """AC1+AC2 : Les champs du LlmPersonaModel sont injectés dans le contexte LLM."""
    _cleanup_tables()
    user_id = _create_user("mystique@example.com")
    persona_id = _create_persona(
        name="Astrologue Mystique",
        tone=PersonaTone.MYSTICAL,
        verbosity=PersonaVerbosity.LONG,
        style_markers=["symbolique", "poétique", "métaphorique"],
        boundaries=["Ne pas interpréter les rêves", "Éviter les prédictions précises"],
    )

    generator = ContextCapturingGenerator()
    set_test_chat_generator(generator)

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Quel est mon destin ?",
            persona_id=str(persona_id),
        )
        db.commit()

    assert len(generator.calls) == 1
    ctx = generator.calls[0]["context"]
    assert ctx.get("persona_name") == "Astrologue Mystique"
    assert ctx.get("persona_tone") == "mystical"
    assert ctx.get("persona_verbosity") == "long"
    assert "symbolique" in (ctx.get("persona_style_markers") or "")
    assert "poétique" in (ctx.get("persona_style_markers") or "")
    assert "Ne pas interpréter les rêves" in (ctx.get("persona_boundaries") or "")


def test_persona_context_differs_between_contrasted_personas() -> None:
    """AC5 : Deux personas contrastés produisent des contextes substantiellement différents."""
    _cleanup_tables()
    user_id_a = _create_user("mystique-a@example.com")
    user_id_b = _create_user("analytique-b@example.com")

    persona_mystique_id = _create_persona(
        name="Mystique Verbeux",
        tone=PersonaTone.MYSTICAL,
        verbosity=PersonaVerbosity.LONG,
        style_markers=["symbolique", "poétique", "ésotérique"],
        boundaries=["Éviter le rationalisme"],
    )
    persona_analytique_id = _create_persona(
        name="Analytique Concis",
        tone=PersonaTone.RATIONAL,
        verbosity=PersonaVerbosity.SHORT,
        style_markers=["factuel", "direct", "précis"],
        boundaries=["Pas de métaphores florales"],
    )

    generator = ContextCapturingGenerator()
    set_test_chat_generator(generator)

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id_a,
            message="Quel est mon avenir ?",
            persona_id=str(persona_mystique_id),
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id_b,
            message="Quel est mon avenir ?",
            persona_id=str(persona_analytique_id),
        )
        db.commit()

    assert len(generator.calls) == 2
    ctx_mystique = generator.calls[0]["context"]
    ctx_analytique = generator.calls[1]["context"]

    # Les noms sont différents
    assert ctx_mystique.get("persona_name") != ctx_analytique.get("persona_name")

    # Les tons sont différents
    assert ctx_mystique.get("persona_tone") == "mystical"
    assert ctx_analytique.get("persona_tone") == "rational"

    # Les verbosités sont différentes
    assert ctx_mystique.get("persona_verbosity") == "long"
    assert ctx_analytique.get("persona_verbosity") == "short"

    # Les style_markers sont différents
    assert "symbolique" in (ctx_mystique.get("persona_style_markers") or "")
    assert "factuel" in (ctx_analytique.get("persona_style_markers") or "")
    assert "symbolique" not in (ctx_analytique.get("persona_style_markers") or "")
    assert "factuel" not in (ctx_mystique.get("persona_style_markers") or "")


def test_persona_context_isolation_no_cross_contamination() -> None:
    """AC3 : Le contexte d'un astrologue A ne contient aucune trace de l'astrologue B."""
    _cleanup_tables()
    user_id = _create_user("isolation@example.com")

    persona_a_id = _create_persona(
        name="Persona Alpha",
        tone=PersonaTone.WARM,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=["chaleureux", "bienveillant"],
        boundaries=["Limite Alpha unique"],
    )
    persona_b_id = _create_persona(
        name="Persona Beta",
        tone=PersonaTone.DIRECT,
        verbosity=PersonaVerbosity.SHORT,
        style_markers=["direct", "factuel"],
        boundaries=["Limite Beta unique"],
    )

    generator = ContextCapturingGenerator()
    set_test_chat_generator(generator)

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Test isolation A",
            persona_id=str(persona_a_id),
        )
        db.commit()

    # Nouvelle session pour Persona B
    user_id_b = _create_user("isolation-b@example.com")
    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id_b,
            message="Test isolation B",
            persona_id=str(persona_b_id),
        )
        db.commit()

    assert len(generator.calls) == 2
    ctx_a = generator.calls[0]["context"]
    ctx_b = generator.calls[1]["context"]

    # A ne contient rien de B
    assert ctx_a.get("persona_name") == "Persona Alpha"
    assert "Beta" not in str(ctx_a)
    assert "Limite Beta" not in str(ctx_a)
    assert "direct" not in (ctx_a.get("persona_style_markers") or "")

    # B ne contient rien de A
    assert ctx_b.get("persona_name") == "Persona Beta"
    assert "Alpha" not in str(ctx_b)
    assert "Limite Alpha" not in str(ctx_b)
    assert "chaleureux" not in (ctx_b.get("persona_style_markers") or "")


def test_persona_fallback_on_none_persona_id_returns_default(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """AC4 : _load_persona_sync logue un warning et retourne le persona par défaut."""
    _cleanup_tables()

    # Créer le persona par défaut en DB
    _create_persona(
        name="Astrologue Standard",
        tone=PersonaTone.DIRECT,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=[],
        boundaries=[],
    )

    with caplog.at_level(
        "WARNING", logger="app.services.llm_generation.chat.chat_guidance_service"
    ):
        with SessionLocal() as db:
            persona = ChatGuidanceService._load_persona_sync(db, None)

    # Un warning doit avoir été loggé mentionnant le backfill
    assert any(
        "chat_persona_missing" in record.message or "backfill" in record.message
        for record in caplog.records
    )

    # Le persona par défaut doit être retourné
    assert persona.name == "Astrologue Standard"


def test_persona_fallback_on_unknown_persona_id_returns_default(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """AC4 : _load_persona_sync retourne le persona par défaut si persona_id inconnu."""
    _cleanup_tables()

    _create_persona(
        name="Astrologue Standard",
        tone=PersonaTone.DIRECT,
        verbosity=PersonaVerbosity.MEDIUM,
        style_markers=[],
        boundaries=[],
    )

    unknown_id = uuid.uuid4()
    with caplog.at_level(
        "WARNING", logger="app.services.llm_generation.chat.chat_guidance_service"
    ):
        with SessionLocal() as db:
            persona = ChatGuidanceService._load_persona_sync(db, unknown_id)

    assert any("chat_persona_not_found" in record.message for record in caplog.records)
    assert persona.name == "Astrologue Standard"
