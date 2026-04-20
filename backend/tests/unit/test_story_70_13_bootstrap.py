from unittest.mock import patch

from app import main


def test_story_70_13_legacy_llm_seed_disabled_by_default(monkeypatch) -> None:
    """Story 70.13: legacy LLM reseed must not run without explicit opt-in."""

    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(main.settings, "dev_allow_legacy_seed", False)

    with patch("app.main.logger.info") as mock_info:
        main._ensure_llm_registry_seeded()

    mock_info.assert_any_call("llm_registry_legacy_seed_disabled")
