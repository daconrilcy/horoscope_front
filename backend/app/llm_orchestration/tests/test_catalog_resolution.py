from __future__ import annotations

import os
from unittest.mock import patch

from app.prompts.catalog import PROMPT_CATALOG, resolve_model


def test_resolve_model_granular_override():
    """Verify that OPENAI_ENGINE_{UC} takes precedence."""
    use_case = "guidance_daily"
    granular_key = "OPENAI_ENGINE_GUIDANCE_DAILY"
    override_model = "gpt-granular-model"

    with patch.dict(os.environ, {granular_key: override_model}):
        resolved = resolve_model(use_case)
        assert resolved == override_model


def test_resolve_model_priority_granular_vs_legacy():
    """Verify Granular > Legacy."""
    use_case = "guidance_daily"
    granular_key = "OPENAI_ENGINE_GUIDANCE_DAILY"
    legacy_key = "LLM_MODEL_OVERRIDE_GUIDANCE_DAILY"

    granular_model = "gpt-granular"
    legacy_model = "gpt-legacy"

    with patch.dict(os.environ, {granular_key: granular_model, legacy_key: legacy_model}):
        resolved = resolve_model(use_case)
        assert resolved == granular_model


def test_resolve_model_fallback_to_legacy():
    """Verify fallback to Legacy if Granular is missing."""
    use_case = "guidance_daily"
    legacy_key = "LLM_MODEL_OVERRIDE_GUIDANCE_DAILY"
    legacy_model = "gpt-legacy"

    # Ensure granular key is NOT in env
    granular_key = PROMPT_CATALOG[use_case].engine_env_key

    with patch.dict(os.environ, {legacy_key: legacy_model}):
        if granular_key in os.environ:
            del os.environ[granular_key]
        resolved = resolve_model(use_case)
        assert resolved == legacy_model


def test_resolve_model_fallback_to_provided_fallback():
    """Verify fallback to provided fallback_model."""
    use_case = "guidance_daily"
    fallback_model = "gpt-fallback-from-db"

    # Ensure no env overrides
    with patch.dict(os.environ, {}, clear=True):
        resolved = resolve_model(use_case, fallback_model=fallback_model)
        assert resolved == fallback_model


def test_resolve_model_default():
    """Verify fallback to settings default."""
    use_case = "guidance_daily"

    with patch.dict(os.environ, {}, clear=True):
        # We don't mock settings here but we expect it to return something
        # (either from .env or gpt-4o-mini)
        resolved = resolve_model(use_case, fallback_model=None)
        assert resolved is not None
        assert isinstance(resolved, str)
