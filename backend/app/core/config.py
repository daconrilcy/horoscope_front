from __future__ import annotations

import os
import secrets
from hashlib import sha256


class Settings:
    @staticmethod
    def _parse_secret_list(env_name: str) -> list[str]:
        raw = os.getenv(env_name, "")
        values = [item.strip() for item in raw.split(",")]
        return [item for item in values if item]

    @staticmethod
    def _derive_non_prod_seed_admin_token(app_env: str, database_url: str) -> str:
        fingerprint = sha256(f"{app_env}:{database_url}".encode("utf-8")).hexdigest()[:32]
        return f"dev-seed-{fingerprint}"

    @staticmethod
    def _allows_implicit_seed_admin_token(app_env: str) -> bool:
        return app_env in {"development", "dev", "local", "test", "testing"}

    @staticmethod
    def _is_local_sqlite_database_url(database_url: str) -> bool:
        normalized = database_url.strip().lower()
        return normalized.startswith("sqlite:///./") or normalized.startswith("sqlite:///:memory:")

    @staticmethod
    def _parse_bool_env(env_name: str, default: bool = False) -> bool:
        raw = os.getenv(env_name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _parse_int_env(
        env_name: str,
        *,
        default: int,
        minimum: int | None = None,
    ) -> int:
        raw = os.getenv(env_name)
        if raw is None or not raw.strip():
            return default
        try:
            parsed = int(raw.strip())
        except ValueError:
            return default
        if minimum is not None and parsed < minimum:
            return minimum
        return parsed

    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development").strip().lower()
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./horoscope.db")
        self.active_reference_version = os.getenv("ACTIVE_REFERENCE_VERSION", "1.0.0")
        self.ruleset_version = os.getenv("RULESET_VERSION", "1.0.0")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
        if self.app_env == "production" and not self.jwt_secret_key:
            raise RuntimeError("JWT_SECRET_KEY must be set in production")
        if not self.jwt_secret_key:
            self.jwt_secret_key = secrets.token_hex(32)
        self.jwt_previous_secret_keys = self._parse_secret_list("JWT_PREVIOUS_SECRET_KEYS")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_minutes = int(os.getenv("JWT_ACCESS_MINUTES", "15"))
        self.jwt_refresh_minutes = int(os.getenv("JWT_REFRESH_MINUTES", str(60 * 24 * 7)))
        self.api_credentials_secret_key = os.getenv("API_CREDENTIALS_SECRET_KEY", "").strip()
        if self.app_env == "production" and not self.api_credentials_secret_key:
            raise RuntimeError("API_CREDENTIALS_SECRET_KEY must be set in production")
        if not self.api_credentials_secret_key:
            self.api_credentials_secret_key = secrets.token_hex(32)
        self.api_credentials_previous_secret_keys = self._parse_secret_list(
            "API_CREDENTIALS_PREVIOUS_SECRET_KEYS"
        )
        self.natal_generation_timeout_seconds = int(
            os.getenv("NATAL_GENERATION_TIMEOUT_SECONDS", "150")
        )
        self.chat_llm_timeout_seconds = int(os.getenv("CHAT_LLM_TIMEOUT_SECONDS", "20"))
        self.chat_llm_retry_count = int(os.getenv("CHAT_LLM_RETRY_COUNT", "1"))
        self.chat_llm_retry_backoff_seconds = float(
            os.getenv("CHAT_LLM_RETRY_BACKOFF_SECONDS", "0")
        )
        self.chat_llm_retry_backoff_max_seconds = float(
            os.getenv("CHAT_LLM_RETRY_BACKOFF_MAX_SECONDS", "1.5")
        )
        self.chat_llm_retry_jitter_seconds = float(os.getenv("CHAT_LLM_RETRY_JITTER_SECONDS", "0"))
        self.chat_context_window_messages = int(os.getenv("CHAT_CONTEXT_WINDOW_MESSAGES", "12"))
        self.chat_context_max_characters = int(os.getenv("CHAT_CONTEXT_MAX_CHARACTERS", "4000"))
        self.chat_prompt_version = os.getenv("CHAT_PROMPT_VERSION", "chat-v1").strip() or "chat-v1"
        self.billing_subscription_cache_ttl_seconds = float(
            os.getenv("BILLING_SUBSCRIPTION_CACHE_TTL_SECONDS", "5")
        )
        self.llm_anonymization_salt = os.getenv("LLM_ANONYMIZATION_SALT", "").strip()
        if self.app_env == "production" and not self.llm_anonymization_salt:
            raise RuntimeError("LLM_ANONYMIZATION_SALT must be set in production")
        if not self.llm_anonymization_salt:
            self.llm_anonymization_salt = secrets.token_hex(32)
        self.enable_reference_seed_admin_fallback = self._parse_bool_env(
            "ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", default=False
        )
        self.b2b_daily_usage_limit = int(os.getenv("B2B_DAILY_USAGE_LIMIT", "500"))
        self.b2b_monthly_usage_limit = int(os.getenv("B2B_MONTHLY_USAGE_LIMIT", "10000"))
        self.b2b_usage_limit_mode = os.getenv("B2B_USAGE_LIMIT_MODE", "block").strip().lower()
        if self.b2b_usage_limit_mode not in {"block", "overage"}:
            self.b2b_usage_limit_mode = "block"
        self.pricing_experiment_enabled = self._parse_bool_env(
            "PRICING_EXPERIMENT_ENABLED",
            default=True,
        )
        self.pricing_experiment_min_sample_size = self._parse_int_env(
            "PRICING_EXPERIMENT_MIN_SAMPLE_SIZE",
            default=50,
            minimum=1,
        )
        self.nominatim_url = os.getenv(
            "NOMINATIM_URL", "https://nominatim.openstreetmap.org/search"
        ).strip()
        self.nominatim_user_agent = os.getenv(
            "NOMINATIM_USER_AGENT", "horoscope-app/1.0"
        ).strip()
        self.nominatim_contact = os.getenv(
            "NOMINATIM_CONTACT", "admin@horoscope.app"
        ).strip()
        self.nominatim_timeout_seconds = self._parse_int_env(
            "NOMINATIM_TIMEOUT_SECONDS", default=10, minimum=1
        )
        self.geocoding_cache_ttl_seconds = self._parse_int_env(
            "GEOCODING_CACHE_TTL_SECONDS", default=3600, minimum=1
        )
        token = os.getenv("REFERENCE_SEED_ADMIN_TOKEN", "").strip()
        if token:
            self.reference_seed_admin_token = token
        elif self._allows_implicit_seed_admin_token(
            self.app_env
        ) and self._is_local_sqlite_database_url(self.database_url):
            if self.enable_reference_seed_admin_fallback:
                self.reference_seed_admin_token = self._derive_non_prod_seed_admin_token(
                    self.app_env, self.database_url
                )
            else:
                self.reference_seed_admin_token = secrets.token_hex(32)
        else:
            raise RuntimeError(
                "REFERENCE_SEED_ADMIN_TOKEN must be set outside local/test environments"
            )

    @property
    def jwt_verification_secret_keys(self) -> list[str]:
        return [self.jwt_secret_key, *self.jwt_previous_secret_keys]


settings = Settings()
