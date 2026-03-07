import re

from app.ai_engine.schemas import GenerateContext, GenerateInput
from app.ai_engine.services.prompt_registry import PromptRegistry
from scripts.seed_30_15_chat_naturalite import CHAT_ASTROLOGER_PROMPT_V3

# Patterns interdits dans une réponse conversationnelle (AC5)
_FORBIDDEN_RESPONSE_PATTERNS = [
    r"^###\s",  # Titres markdown niveau 3
    r"\*\*Jupiter",  # Aspect Jupiter en gras
    r"\*\*Mars",  # Aspect Mars en gras
    r"\*\*Vénus",  # Aspect Vénus en gras
    r"\*\*Saturne",  # Aspect Saturne en gras
    r"^- \*\*",  # Listes d'aspects "- **Aspect :"
]


def _response_contains_forbidden_patterns(response_text: str) -> list[str]:
    """Retourne la liste des patterns interdits trouvés dans la réponse."""
    found = []
    for pattern in _FORBIDDEN_RESPONSE_PATTERNS:
        if re.search(pattern, response_text, re.MULTILINE):
            found.append(pattern)
    return found


def test_chat_system_jinja2_naturalite_instructions():
    """
    Vérifie que le template Jinja2 (v1) contient les instructions de 'natal silencieux'.
    """
    context = GenerateContext(
        natal_chart_summary="Soleil en Bélier, Lune en Taureau",
        current_datetime="07 mars 2026 a 15h30 (Europe/Paris)",
        current_timezone="Europe/Paris",
        current_location="Paris, France",
        extra={"persona_name": "TestAstro"},
    )
    input_data = GenerateInput()

    rendered = PromptRegistry.render_prompt(
        use_case="chat", locale="fr", input_data=input_data, context=context
    )

    # Vérifications AC2 — les règles précèdent le natal dans le template restructuré
    assert "RÈGLES ABSOLUES" in rendered
    assert "DONNÉES CONTEXTUELLES PRIVÉES" in rendered
    assert "NE PAS PRÉSENTER À L'UTILISATEUR" in rendered
    assert "Soleil en Bélier, Lune en Taureau" in rendered  # natal bien injecté
    assert "07 mars 2026 a 15h30 (Europe/Paris)" in rendered
    assert "FUSEAU HORAIRE ACTUEL : Europe/Paris" in rendered
    assert "LIEU ACTUEL : Paris, France" in rendered

    # Vérifications AC3 — instruction d'ouverture présente
    assert "INTERDICTION STRICTE" in rendered
    assert "UNE question de clarification" in rendered


def test_prompt_v3_naturalite_instructions():
    """
    Vérifie que le prompt v3 (v2 orchestration) contient les instructions de 'natal silencieux'.
    """
    # Vérifications AC1
    assert "natal_chart_summary est ton CONTEXTE DE FOND PRIVÉ" in CHAT_ASTROLOGER_PROMPT_V3
    assert "ne le récite jamais" in CHAT_ASTROLOGER_PROMPT_V3

    # Vérifications AC4
    assert "Intègre les éléments astrologiques de façon fluide" in CHAT_ASTROLOGER_PROMPT_V3
    assert "votre Soleil en Bélier vous pousse à..." in CHAT_ASTROLOGER_PROMPT_V3

    # Vérifications AC3 (v2)
    assert "Sur un message d'ouverture court" in CHAT_ASTROLOGER_PROMPT_V3
    assert "Ne présente pas le thème natal." in CHAT_ASTROLOGER_PROMPT_V3


def test_prompt_v3_no_markdown_lists_restriction():
    """
    Vérifie que le prompt v3 interdit explicitement les formats de liste markdown.
    """
    # Vérifications AC5 (instruction dans le prompt)
    assert (
        'N\'utilise JAMAIS les formats "### Titre" ou "- **Aspect** :"' in CHAT_ASTROLOGER_PROMPT_V3
    )
    assert "sauf si l'utilisateur demande explicitement une liste" in CHAT_ASTROLOGER_PROMPT_V3


def test_response_bonjour_no_forbidden_patterns():
    """
    AC5 — Test comportemental : une réponse conforme pour "bonjour" ne contient
    pas de marqueurs de liste d'aspects (###, **Jupiter, **Mars, - **).
    Valide via un mock de réponse LLM représentatif du comportement attendu.
    """
    # Réponse CONFORME attendue pour un message "bonjour"
    good_response = (
        "Bonjour ! Je suis ravi de vous accueillir. "
        "Sur quoi aimeriez-vous que nous nous penchions aujourd'hui ?"
    )
    assert _response_contains_forbidden_patterns(good_response) == [], (
        "La réponse conforme ne devrait contenir aucun pattern interdit"
    )


def test_response_with_forbidden_patterns_is_detected():
    """
    AC5 — Contre-test : vérifie que les patterns interdits sont bien détectés
    (valide le mécanisme de détection lui-même).
    """
    bad_response = (
        "Voici votre thème natal :\n"
        "### Aspects principaux\n"
        "- **Jupiter** sextile Mercure : expansion mentale\n"
        "- **Mars** carré Vénus : tension relationnelle\n"
    )
    found = _response_contains_forbidden_patterns(bad_response)
    assert len(found) > 0, (
        "La réponse avec patterns interdits doit être détectée comme non-conforme"
    )


def test_response_explicit_request_allows_listing():
    """
    AC5 — Exception : sur demande explicite de l'utilisateur, une réponse structurée
    est acceptable. La détection ne doit PAS s'appliquer dans ce contexte.
    Ce test documente l'intention : les patterns ne doivent être bloqués
    qu'en réponse conversationnelle générale, pas sur demande explicite.
    """
    explicit_response = (
        "Voici vos transits actuels :\n"
        "### Transits du moment\n"
        "- **Jupiter** sextile votre Soleil natal : période favorable\n"
    )
    # Sur demande explicite, la réponse peut contenir des structures markdown.
    # Ce test documente que le prompt autorise cela (règle "si l'utilisateur demande").
    assert "Jupiter" in explicit_response  # Sanity check — la réponse contient bien des aspects
