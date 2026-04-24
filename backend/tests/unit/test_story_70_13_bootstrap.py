from unittest.mock import Mock, patch

from app import main


def test_story_70_13_legacy_llm_seed_disabled_by_default(monkeypatch) -> None:
    """Story 70.13: legacy LLM reseed must not run without explicit opt-in."""

    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(main.settings, "dev_allow_legacy_seed", False)

    with patch("app.main.logger.info") as mock_info:
        main._ensure_llm_registry_seeded()

    mock_info.assert_any_call("llm_registry_legacy_seed_disabled")


class _FakeQuery:
    def __init__(self, count: int) -> None:
        self._count = count

    def filter(self, *_args, **_kwargs):
        return self

    def count(self) -> int:
        return self._count


class _FakeSession:
    def __init__(self, counts: dict[str, int]) -> None:
        self._counts = counts

    def query(self, model):
        return _FakeQuery(self._counts.get(model.__name__, 0))


class _FakeSessionLocal:
    def __init__(self, counts: dict[str, int]) -> None:
        self._counts = counts

    def __call__(self):
        return self

    def __enter__(self):
        return _FakeSession(self._counts)

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_canonical_llm_bootstrap_seeds_blank_local_db(monkeypatch) -> None:
    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(
        "app.infra.db.session.SessionLocal",
        _FakeSessionLocal(
            {
                "LlmOutputSchemaModel": 0,
                "LlmPromptVersionModel": 0,
                "LlmPersonaModel": 0,
                "PromptAssemblyConfigModel": 0,
                "LlmExecutionProfileModel": 0,
            }
        ),
    )
    monkeypatch.setattr(
        "app.domain.llm.configuration.prompt_version_lookup.get_active_prompt_version",
        lambda *_args, **_kwargs: None,
    )

    seed_astrologers = Mock()
    seed_bootstrap_contracts = Mock()
    seed_prompts = Mock()
    seed_natal_v3_prompts = Mock()
    seed_chat_prompt_v2 = Mock()
    seed_guidance_prompts = Mock()
    seed_horoscope_narrator_assembly = Mock()
    seed_66_20_taxonomy = Mock()

    monkeypatch.setattr("scripts.seed_astrologers_6_profiles.seed_astrologers", seed_astrologers)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.use_cases_seed.seed_bootstrap_contracts",
        seed_bootstrap_contracts,
    )
    monkeypatch.setattr("app.ops.llm.bootstrap.seed_29_prompts.seed_prompts", seed_prompts)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_8_v3_prompts.seed",
        seed_natal_v3_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_14_chat_prompt.seed",
        seed_chat_prompt_v2,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_guidance_prompts.seed_guidance_prompts",
        seed_guidance_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_horoscope_narrator_assembly.seed_horoscope_narrator_assembly",
        seed_horoscope_narrator_assembly,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_66_20_taxonomy.seed_66_20_taxonomy",
        seed_66_20_taxonomy,
    )

    main._ensure_canonical_llm_bootstrap_seeded()

    seed_astrologers.assert_called_once()
    seed_bootstrap_contracts.assert_called_once()
    seed_prompts.assert_called_once()
    seed_natal_v3_prompts.assert_called_once()
    seed_chat_prompt_v2.assert_called_once()
    seed_guidance_prompts.assert_called_once()
    seed_horoscope_narrator_assembly.assert_called_once()
    seed_66_20_taxonomy.assert_called_once()


def test_canonical_llm_bootstrap_only_seeds_canonical_use_case_registry(monkeypatch) -> None:
    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(
        "app.infra.db.session.SessionLocal",
        _FakeSessionLocal(
            {
                "LlmOutputSchemaModel": 0,
                "LlmPromptVersionModel": 0,
                "LlmPersonaModel": 0,
                "PromptAssemblyConfigModel": 0,
                "LlmExecutionProfileModel": 0,
            }
        ),
    )
    monkeypatch.setattr(
        "app.domain.llm.configuration.prompt_version_lookup.get_active_prompt_version",
        lambda *_args, **_kwargs: None,
    )

    seed_astrologers = Mock()
    seed_prompts = Mock()
    seed_natal_v3_prompts = Mock()
    seed_chat_prompt_v2 = Mock()
    seed_guidance_prompts = Mock()
    seed_horoscope_narrator_assembly = Mock()
    seed_66_20_taxonomy = Mock()
    legacy_seed_use_cases = Mock()
    canonical_bootstrap_contracts = Mock()
    monkeypatch.setattr("scripts.seed_astrologers_6_profiles.seed_astrologers", seed_astrologers)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.use_cases_seed.seed_use_cases",
        legacy_seed_use_cases,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.use_cases_seed.seed_bootstrap_contracts",
        canonical_bootstrap_contracts,
    )
    monkeypatch.setattr("app.ops.llm.bootstrap.seed_29_prompts.seed_prompts", seed_prompts)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_8_v3_prompts.seed",
        seed_natal_v3_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_14_chat_prompt.seed",
        seed_chat_prompt_v2,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_guidance_prompts.seed_guidance_prompts",
        seed_guidance_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_horoscope_narrator_assembly.seed_horoscope_narrator_assembly",
        seed_horoscope_narrator_assembly,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_66_20_taxonomy.seed_66_20_taxonomy",
        seed_66_20_taxonomy,
    )

    main._ensure_canonical_llm_bootstrap_seeded()

    legacy_seed_use_cases.assert_not_called()
    canonical_bootstrap_contracts.assert_called_once()


def test_canonical_llm_bootstrap_skips_when_nominal_tables_exist(monkeypatch) -> None:
    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(
        "app.infra.db.session.SessionLocal",
        _FakeSessionLocal(
            {
                "LlmOutputSchemaModel": 3,
                "LlmPromptVersionModel": 5,
                "LlmPersonaModel": 1,
                "PromptAssemblyConfigModel": 4,
                "LlmExecutionProfileModel": 2,
            }
        ),
    )
    monkeypatch.setattr(
        "app.domain.llm.configuration.prompt_version_lookup.get_active_prompt_version",
        lambda *_args, **_kwargs: object(),
    )

    seed_prompts = Mock()
    seed_66_20_taxonomy = Mock()
    monkeypatch.setattr("app.ops.llm.bootstrap.seed_29_prompts.seed_prompts", seed_prompts)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_66_20_taxonomy.seed_66_20_taxonomy",
        seed_66_20_taxonomy,
    )

    main._ensure_canonical_llm_bootstrap_seeded()

    seed_prompts.assert_not_called()
    seed_66_20_taxonomy.assert_not_called()


def test_canonical_llm_bootstrap_reseeds_when_active_short_prompt_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(
        "app.infra.db.session.SessionLocal",
        _FakeSessionLocal(
            {
                "LlmOutputSchemaModel": 3,
                "LlmPromptVersionModel": 5,
                "LlmPersonaModel": 1,
                "PromptAssemblyConfigModel": 4,
                "LlmExecutionProfileModel": 2,
            }
        ),
    )
    monkeypatch.setattr(
        "app.domain.llm.configuration.prompt_version_lookup.get_active_prompt_version",
        lambda *_args, **_kwargs: None,
    )

    seed_astrologers = Mock()
    seed_bootstrap_contracts = Mock()
    seed_prompts = Mock()
    seed_natal_v3_prompts = Mock()
    seed_chat_prompt_v2 = Mock()
    seed_guidance_prompts = Mock()
    seed_horoscope_narrator_assembly = Mock()
    seed_66_20_taxonomy = Mock()

    monkeypatch.setattr("scripts.seed_astrologers_6_profiles.seed_astrologers", seed_astrologers)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.use_cases_seed.seed_bootstrap_contracts",
        seed_bootstrap_contracts,
    )
    monkeypatch.setattr("app.ops.llm.bootstrap.seed_29_prompts.seed_prompts", seed_prompts)
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_8_v3_prompts.seed",
        seed_natal_v3_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_30_14_chat_prompt.seed",
        seed_chat_prompt_v2,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_guidance_prompts.seed_guidance_prompts",
        seed_guidance_prompts,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_horoscope_narrator_assembly.seed_horoscope_narrator_assembly",
        seed_horoscope_narrator_assembly,
    )
    monkeypatch.setattr(
        "app.ops.llm.bootstrap.seed_66_20_taxonomy.seed_66_20_taxonomy",
        seed_66_20_taxonomy,
    )

    main._ensure_canonical_llm_bootstrap_seeded()

    seed_astrologers.assert_called_once()
    seed_bootstrap_contracts.assert_called_once()
    seed_prompts.assert_called_once()
    seed_natal_v3_prompts.assert_called_once()
    seed_chat_prompt_v2.assert_called_once()
    seed_guidance_prompts.assert_called_once()
    seed_horoscope_narrator_assembly.assert_called_once()
    seed_66_20_taxonomy.assert_called_once()
