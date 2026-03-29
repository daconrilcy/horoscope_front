from __future__ import annotations

import logging
import os
import secrets
import sys
from enum import Enum
from hashlib import sha256
from pathlib import Path

from dotenv import load_dotenv

from app.core.versions import ACTIVE_REFERENCE_VERSION, ACTIVE_RULESET_VERSION

backend_root = Path(__file__).parent.parent.parent
env_path = backend_root / ".env"
logger = logging.getLogger(__name__)


def _should_load_backend_dotenv() -> bool:
    if os.getenv("APP_DISABLE_BACKEND_DOTENV", "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    # Test suites must control their own env explicitly and should not inherit local dev .env.
    return "pytest" not in sys.modules


# Load .env file from backend root if it exists and the current runtime allows it.
if env_path.exists() and _should_load_backend_dotenv():
    load_dotenv(dotenv_path=env_path)


class ZodiacType(str, Enum):
    TROPICAL = "tropical"
    SIDEREAL = "sidereal"


class FrameType(str, Enum):
    GEOCENTRIC = "geocentric"
    TOPOCENTRIC = "topocentric"


class HouseSystemType(str, Enum):
    PLACIDUS = "placidus"
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"


class AspectSchoolType(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    STRICT = "strict"


class DailyEngineMode(str, Enum):
    V2 = "v2"
    V3 = "v3"
    DUAL = "dual"


class Settings:
    @staticmethod
    def _parse_canonical_db_validation_mode() -> str:
        raw_mode = os.getenv("CANONICAL_DB_VALIDATION_MODE", "strict").strip().lower()
        if raw_mode in {"strict", "warn", "off"}:
            return raw_mode
        logger.warning(
            "canonical_db_startup_validation_invalid_mode mode=%s fallback=strict",
            raw_mode,
        )
        return "strict"

    @staticmethod
    def _parse_feature_scope_validation_mode() -> str:
        raw_mode = os.getenv("FEATURE_SCOPE_VALIDATION_MODE", "strict").strip().lower()
        if raw_mode in {"strict", "warn", "off"}:
            return raw_mode
        logger.warning(
            "feature_scope_registry_startup_validation_invalid_mode mode=%s fallback=strict",
            raw_mode,
        )
        return "strict"

    @staticmethod
    def _normalize_database_url(database_url: str) -> str:
        # Prevent cwd-dependent sqlite DB selection.
        # Example: root/horoscope.db vs backend/horoscope.db.
        if database_url.startswith("sqlite:///./"):
            rel = database_url.removeprefix("sqlite:///./")
            abs_path = (backend_root / rel).resolve()
            return f"sqlite:///{abs_path.as_posix()}"
        return database_url

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
        # SQLite URLs are always local filesystem or in-memory databases.
        return normalized.startswith("sqlite:///")

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

    @staticmethod
    def _parse_daily_engine_mode(raw_value: str | DailyEngineMode | None) -> DailyEngineMode:
        if isinstance(raw_value, DailyEngineMode):
            return raw_value
        if raw_value is None:
            return DailyEngineMode.V2
        normalized = str(raw_value).strip().lower()
        try:
            return DailyEngineMode(normalized)
        except ValueError:
            return DailyEngineMode.V2

    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development").strip().lower()
        self.database_url = self._normalize_database_url(
            os.getenv("DATABASE_URL", "sqlite:///./horoscope.db")
        )
        self.active_reference_version = os.getenv(
            "ACTIVE_REFERENCE_VERSION", ACTIVE_REFERENCE_VERSION
        )
        self._ruleset_version = os.getenv("RULESET_VERSION", ACTIVE_RULESET_VERSION)

        default_zodiac = (
            os.getenv("NATAL_RULESET_DEFAULT_ZODIAC", ZodiacType.TROPICAL).strip().lower()
        )
        try:
            self.natal_ruleset_default_zodiac = ZodiacType(default_zodiac)
        except ValueError:
            self.natal_ruleset_default_zodiac = ZodiacType.TROPICAL

        default_ayanamsa_raw = os.getenv("NATAL_RULESET_DEFAULT_AYANAMSA", "").strip().lower()
        self.natal_ruleset_default_ayanamsa = default_ayanamsa_raw or None

        default_frame = (
            os.getenv("NATAL_RULESET_DEFAULT_FRAME", FrameType.GEOCENTRIC).strip().lower()
        )
        try:
            self.natal_ruleset_default_frame = FrameType(default_frame)
        except ValueError:
            self.natal_ruleset_default_frame = FrameType.GEOCENTRIC

        default_house_system = (
            os.getenv("NATAL_RULESET_DEFAULT_HOUSE_SYSTEM", HouseSystemType.PLACIDUS)
            .strip()
            .lower()
        )
        try:
            self.natal_ruleset_default_house_system = HouseSystemType(default_house_system)
        except ValueError:
            self.natal_ruleset_default_house_system = HouseSystemType.PLACIDUS

        default_aspect_school = (
            os.getenv("NATAL_RULESET_DEFAULT_ASPECT_SCHOOL", AspectSchoolType.MODERN)
            .strip()
            .lower()
        )
        try:
            self.natal_ruleset_default_aspect_school = AspectSchoolType(default_aspect_school)
        except ValueError:
            self.natal_ruleset_default_aspect_school = AspectSchoolType.MODERN

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
        # pricing experiment settings
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
        self.nominatim_user_agent = os.getenv("NOMINATIM_USER_AGENT", "horoscope-app/1.0").strip()
        self.nominatim_contact = os.getenv("NOMINATIM_CONTACT", "admin@horoscope.app").strip()
        self.nominatim_timeout_seconds = self._parse_int_env(
            "NOMINATIM_TIMEOUT_SECONDS", default=10, minimum=1
        )
        self.geocoding_cache_ttl_seconds = self._parse_int_env(
            "GEOCODING_CACHE_TTL_SECONDS", default=3600, minimum=1
        )
        self.swisseph_enabled = self._parse_bool_env("SWISSEPH_ENABLED", default=False)
        self.swisseph_pro_mode = self._parse_bool_env("SWISSEPH_PRO_MODE", default=False)
        # Story 26.1: offline timezone derivation from lat/lon (SWISSEPH_PRO_MODE phase 3).
        self.timezone_derived_enabled = self._parse_bool_env(
            "TIMEZONE_DERIVED_ENABLED", default=False
        )
        self.ephemeris_path = os.getenv(
            "SWISSEPH_DATA_PATH", os.getenv("EPHEMERIS_PATH", "")
        ).strip()
        self.ephemeris_path_version = os.getenv(
            "SWISSEPH_PATH_VERSION", os.getenv("EPHEMERIS_PATH_VERSION", "")
        ).strip()
        self.ephemeris_path_hash = os.getenv("EPHEMERIS_PATH_HASH", "").strip()
        self.ephemeris_required_files = self._parse_secret_list("EPHEMERIS_REQUIRED_FILES")
        # Backward-compatible aliases from previous stories.
        self.swisseph_data_path = self.ephemeris_path
        self.swisseph_path_version = self.ephemeris_path_version
        natal_engine_default = os.getenv("NATAL_ENGINE_DEFAULT", "swisseph").strip().lower()
        if natal_engine_default not in {"swisseph", "simplified"}:
            natal_engine_default = "swisseph"
        self.natal_engine_default = natal_engine_default
        self.natal_engine_simplified_enabled = self._parse_bool_env(
            "NATAL_ENGINE_SIMPLIFIED_ENABLED", default=False
        )
        self.natal_engine_compare_enabled = self._parse_bool_env(
            "NATAL_ENGINE_COMPARE_ENABLED", default=False
        )
        self.llm_narrator_enabled = self._parse_bool_env("LLM_NARRATOR_ENABLED", default=False)
        self.daily_engine_mode = self._parse_daily_engine_mode(os.getenv("DAILY_ENGINE_MODE"))

        # Review Queue Alerting (Story 61.39)
        self.ops_review_queue_alerts_enabled = self._parse_bool_env(
            "OPS_REVIEW_QUEUE_ALERTS_ENABLED", default=False
        )
        self.ops_review_queue_alert_webhook_url = os.getenv(
            "OPS_REVIEW_QUEUE_ALERT_WEBHOOK_URL"
        )
        self.ops_review_queue_alert_base_url = os.getenv(
            "OPS_REVIEW_QUEUE_ALERT_BASE_URL"
        )
        self.ops_review_queue_alert_max_candidates = self._parse_int_env(
            "OPS_REVIEW_QUEUE_ALERT_MAX_CANDIDATES", default=100, minimum=1
        )

        # Feature Scope Validation Mode (Story 61.29)
        self.feature_scope_validation_mode = self._parse_feature_scope_validation_mode()

        # Story 61.30
        self.canonical_db_validation_mode = self._parse_canonical_db_validation_mode()

        # Stripe Configuration
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip() or None
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip() or None
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip() or None
        self.stripe_price_basic = os.getenv("STRIPE_PRICE_BASIC", "").strip() or None
        self.stripe_price_premium = os.getenv("STRIPE_PRICE_PREMIUM", "").strip() or None
        self.stripe_api_version = os.getenv("STRIPE_API_VERSION", "2024-12-18.acacia").strip()
        self.stripe_checkout_success_url = os.getenv(
            "STRIPE_CHECKOUT_SUCCESS_URL",
            "http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}",
        ).strip()
        self.stripe_checkout_cancel_url = os.getenv(
            "STRIPE_CHECKOUT_CANCEL_URL",
            "http://localhost:5173/billing/cancel",
        ).strip()
        self.stripe_portal_return_url = os.getenv(
            "STRIPE_PORTAL_RETURN_URL",
            "http://localhost:5173/settings/subscription",
        ).strip()
        self.stripe_portal_configuration_id = os.getenv(
            "STRIPE_PORTAL_CONFIGURATION_ID", ""
        ).strip() or None

        # LLM Engine Configuration
        self.openai_model_default = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini").strip()

        # V3 Engine Conventions (AC4)
        self.v3_engine_version = os.getenv("V3_ENGINE_VERSION", "v3.0.0-alpha").strip()
        self.v3_snapshot_version = os.getenv("V3_SNAPSHOT_VERSION", "1.0").strip()
        self.v3_evidence_pack_version = os.getenv("V3_EVIDENCE_PACK_VERSION", "1.0").strip()

        self.natal_schema_version = os.getenv("NATAL_SCHEMA_VERSION", "v3").strip().lower()
        self.llm_replay_encryption_key = os.getenv("LLM_REPLAY_ENCRYPTION_KEY", "").strip()
        if self.app_env == "production" and not self.llm_replay_encryption_key:
            raise RuntimeError("LLM_REPLAY_ENCRYPTION_KEY must be set in production")
        if not self.llm_replay_encryption_key:
            from cryptography.fernet import Fernet

            self.llm_replay_encryption_key = Fernet.generate_key().decode()

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
    def active_ruleset_version(self) -> str:
        return self._ruleset_version

    @active_ruleset_version.setter
    def active_ruleset_version(self, value: str) -> None:
        self._ruleset_version = value

    @property
    def ruleset_version(self) -> str:
        """Alias for active_ruleset_version (backwards compatibility)."""
        return self._ruleset_version

    @ruleset_version.setter
    def ruleset_version(self, value: str) -> None:
        """Alias for active_ruleset_version (backwards compatibility)."""
        self._ruleset_version = value

    @property
    def jwt_verification_secret_keys(self) -> list[str]:
        return [self.jwt_secret_key, *self.jwt_previous_secret_keys]


settings = Settings()
