"""Tests for Prompt Registry."""

import pytest

from app.ai_engine.exceptions import UnknownUseCaseError
from app.ai_engine.schemas import GenerateContext, GenerateInput
from app.ai_engine.services.prompt_registry import PromptRegistry


class TestPromptRegistry:
    """Tests for PromptRegistry class."""

    def test_list_use_cases_returns_registered_cases(self) -> None:
        """List use cases returns all registered use cases."""
        use_cases = PromptRegistry.list_use_cases()
        assert "chat" in use_cases
        assert "natal_chart_interpretation" in use_cases
        assert "card_reading" in use_cases
        assert "guidance_daily" in use_cases
        assert "guidance_weekly" in use_cases
        assert "guidance_contextual" in use_cases

    def test_get_config_returns_config_for_valid_use_case(self) -> None:
        """Get config returns PromptConfig for valid use case."""
        config = PromptRegistry.get_config("chat")
        assert config.template_name == "chat_system.jinja2"
        assert config.max_tokens > 0
        assert 0 <= config.temperature <= 2

    def test_get_config_raises_for_unknown_use_case(self) -> None:
        """Get config raises UnknownUseCaseError for unknown use case."""
        with pytest.raises(UnknownUseCaseError) as exc_info:
            PromptRegistry.get_config("unknown_use_case")
        assert exc_info.value.status_code == 400
        assert "unknown_use_case" in str(exc_info.value.message)

    def test_render_prompt_chat_french(self) -> None:
        """Render prompt for chat use case in French."""
        input_data = GenerateInput()
        context = GenerateContext(natal_chart_summary="Soleil en Bélier")

        prompt = PromptRegistry.render_prompt(
            use_case="chat",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "français" in prompt
        assert "Soleil en Bélier" in prompt
        assert "bienveillant" in prompt.lower()

    def test_render_prompt_chat_english(self) -> None:
        """Render prompt for chat use case in English."""
        input_data = GenerateInput()
        context = GenerateContext()

        prompt = PromptRegistry.render_prompt(
            use_case="chat",
            locale="en-US",
            input_data=input_data,
            context=context,
        )

        assert "English" in prompt

    def test_render_prompt_chat_spanish(self) -> None:
        """Render prompt for chat use case in Spanish."""
        input_data = GenerateInput()
        context = GenerateContext()

        prompt = PromptRegistry.render_prompt(
            use_case="chat",
            locale="es-ES",
            input_data=input_data,
            context=context,
        )

        assert "español" in prompt

    def test_render_prompt_natal_chart_interpretation(self) -> None:
        """Render prompt for natal chart interpretation use case."""
        input_data = GenerateInput(
            question="Que dit mon thème sur ma carrière ?",
            tone="warm",
        )
        context = GenerateContext(
            natal_chart_summary="Soleil en Bélier, Lune en Cancer",
            birth_data={"date": "1990-02-02", "time": "08:15", "place": "Paris"},
        )

        prompt = PromptRegistry.render_prompt(
            use_case="natal_chart_interpretation",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "carrière" in prompt
        assert "Soleil en Bélier" in prompt
        assert "1990-02-02" in prompt
        assert "Paris" in prompt

    def test_render_prompt_card_reading(self) -> None:
        """Render prompt for card reading use case."""
        input_data = GenerateInput(question="Que me réserve cette semaine ?")
        context = GenerateContext(extra={"cards": "L'Étoile, Le Soleil, La Roue de Fortune"})

        prompt = PromptRegistry.render_prompt(
            use_case="card_reading",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "semaine" in prompt
        assert "Étoile" in prompt or "cartes" in prompt.lower()

    def test_render_prompt_raises_for_unknown_use_case(self) -> None:
        """Render prompt raises UnknownUseCaseError for unknown use case."""
        input_data = GenerateInput()
        context = GenerateContext()

        with pytest.raises(UnknownUseCaseError):
            PromptRegistry.render_prompt(
                use_case="nonexistent",
                locale="fr-FR",
                input_data=input_data,
                context=context,
            )

    def test_render_prompt_injects_input_constraints(self) -> None:
        """Render prompt injects input constraints when provided."""
        from app.ai_engine.schemas import InputConstraints

        input_data = GenerateInput(
            question="Test question",
            tone="formal",
            constraints=InputConstraints(max_chars=500),
        )
        context = GenerateContext()

        prompt = PromptRegistry.render_prompt(
            use_case="natal_chart_interpretation",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "500" in prompt

    def test_extract_language_default_fallback(self) -> None:
        """Extract language returns locale itself for unknown languages."""
        result = PromptRegistry._extract_language("xx-XX")
        assert result == "xx-XX"

    def test_get_config_guidance_daily(self) -> None:
        """Get config for guidance_daily returns expected config."""
        config = PromptRegistry.get_config("guidance_daily")
        assert config.template_name == "guidance_daily_v1.jinja2"
        assert config.max_tokens == 1200
        assert config.temperature == 0.7

    def test_get_config_guidance_weekly(self) -> None:
        """Get config for guidance_weekly returns expected config."""
        config = PromptRegistry.get_config("guidance_weekly")
        assert config.template_name == "guidance_weekly_v1.jinja2"
        assert config.max_tokens == 1500
        assert config.temperature == 0.7

    def test_get_config_guidance_contextual(self) -> None:
        """Get config for guidance_contextual returns expected config."""
        config = PromptRegistry.get_config("guidance_contextual")
        assert config.template_name == "guidance_contextual_v1.jinja2"
        assert config.max_tokens == 1200
        assert config.temperature == 0.7

    def test_render_prompt_guidance_daily(self) -> None:
        """Render prompt for guidance_daily use case."""
        input_data = GenerateInput()
        context = GenerateContext(
            birth_data={
                "birth_date": "1985-03-21",
                "birth_time": "10:30",
                "birth_timezone": "Europe/Paris",
            },
            extra={"persona_line": "Persona prudent et bienveillant"},
        )

        prompt = PromptRegistry.render_prompt(
            use_case="guidance_daily",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "français" in prompt
        assert "guidance" in prompt.lower() or "quotidienne" in prompt.lower()
        assert "1985-03-21" in prompt
        assert "10:30" in prompt
        assert "sécurité" in prompt.lower() or "médical" in prompt.lower()
        assert "Persona prudent et bienveillant" in prompt

    def test_render_prompt_guidance_weekly(self) -> None:
        """Render prompt for guidance_weekly use case."""
        input_data = GenerateInput()
        context = GenerateContext(
            birth_data={
                "birth_date": "1990-07-15",
                "birth_time": "14:00",
                "birth_timezone": "UTC",
            },
        )

        prompt = PromptRegistry.render_prompt(
            use_case="guidance_weekly",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "français" in prompt
        assert "hebdomadaire" in prompt.lower() or "semaine" in prompt.lower()
        assert "1990-07-15" in prompt

    def test_render_prompt_guidance_contextual(self) -> None:
        """Render prompt for guidance_contextual use case."""
        input_data = GenerateInput()
        context = GenerateContext(
            birth_data={
                "birth_date": "1988-12-01",
                "birth_time": "08:45",
                "birth_timezone": "America/New_York",
            },
            extra={
                "situation": "Changement de carrière prévu",
                "objective": "Trouver le bon timing",
                "time_horizon": "3 mois",
            },
        )

        prompt = PromptRegistry.render_prompt(
            use_case="guidance_contextual",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "français" in prompt
        assert "contextuell" in prompt.lower() or "situation" in prompt.lower()
        assert "Changement de carrière" in prompt
        assert "Trouver le bon timing" in prompt
        assert "3 mois" in prompt

    def test_render_prompt_guidance_daily_missing_birth_data(self) -> None:
        """Render prompt for guidance_daily without birth data."""
        input_data = GenerateInput()
        context = GenerateContext()

        prompt = PromptRegistry.render_prompt(
            use_case="guidance_daily",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "français" in prompt
        assert len(prompt) > 100

    def test_render_prompt_guidance_contextual_with_context_lines(self) -> None:
        """Render prompt for guidance_contextual with context lines."""
        input_data = GenerateInput()
        context = GenerateContext(
            extra={
                "context_lines": "user: Bonjour\nassistant: Bonjour!",
                "situation": "Test situation",
                "objective": "Test objectif",
            },
        )

        prompt = PromptRegistry.render_prompt(
            use_case="guidance_contextual",
            locale="fr-FR",
            input_data=input_data,
            context=context,
        )

        assert "Bonjour" in prompt
        assert "Test situation" in prompt

    def test_render_prompt_template_not_found_raises_validation_error(self) -> None:
        """Render prompt raises ValidationError when template file is missing."""
        from app.ai_engine.exceptions import ValidationError
        from app.ai_engine.services.prompt_registry import USE_CASE_REGISTRY, PromptConfig

        original_config = USE_CASE_REGISTRY.get("chat")
        try:
            USE_CASE_REGISTRY["chat"] = PromptConfig(
                template_name="nonexistent_template.jinja2",
                max_tokens=1000,
                temperature=0.8,
            )

            input_data = GenerateInput()
            context = GenerateContext()

            with pytest.raises(ValidationError) as exc_info:
                PromptRegistry.render_prompt(
                    use_case="chat",
                    locale="fr-FR",
                    input_data=input_data,
                    context=context,
                )

            assert "template not found" in exc_info.value.message
            assert exc_info.value.details["use_case"] == "chat"
        finally:
            if original_config:
                USE_CASE_REGISTRY["chat"] = original_config
