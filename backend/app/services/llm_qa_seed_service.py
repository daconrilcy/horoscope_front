from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.geo_place_resolved_repository import (
    GeoPlaceResolvedCreateData,
    GeoPlaceResolvedRepository,
)
from app.infra.db.repositories.user_repository import UserRepository
from app.services.chart_result_service import ChartResultService
from app.services.geocoding_service import GeocodingService
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.user_natal_chart_service import UserNatalChartService

logger = logging.getLogger(__name__)

LLM_QA_TEST_USER_EMAIL = "cyril-test@test.com"
LLM_QA_TEST_USER_PASSWORD = "admin123"
LLM_QA_TEST_BIRTH_PLACE = "Paris, France"
LLM_QA_TEST_BIRTH_DATE = date(1973, 4, 24)
LLM_QA_TEST_BIRTH_TIME = "11:00"
LLM_QA_ALLOWED_ENVIRONMENTS = {"development", "dev", "local", "test", "testing", "staging"}


class LlmQaSeedServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class LlmQaSeedResult:
    user_id: int
    email: str
    birth_place_resolved_id: int
    birth_timezone: str
    chart_id: str
    chart_reused: bool


class LlmQaSeedService:
    @staticmethod
    def _prune_legacy_charts(db: Session, *, user_id: int, keep_chart_id: str) -> None:
        deleted = ChartResultRepository(db).delete_for_user_except_chart_id(
            user_id=user_id,
            keep_chart_id=keep_chart_id,
        )
        if deleted:
            logger.info(
                "llm_qa_seed_pruned_charts user_id=%s keep_chart_id=%s deleted=%s",
                user_id,
                keep_chart_id,
                deleted,
            )

    @staticmethod
    def environment_allows_seed() -> bool:
        if settings.app_env in LLM_QA_ALLOWED_ENVIRONMENTS:
            return True
        return settings.llm_qa_seed_user_allow_production

    @staticmethod
    def _require_allowed_environment() -> None:
        if LlmQaSeedService.environment_allows_seed():
            return
        raise LlmQaSeedServiceError(
            code="llm_qa_seed_not_allowed",
            message="llm qa seed is not allowed in this environment",
            details={"app_env": settings.app_env},
        )

    @staticmethod
    def _find_or_create_user(db: Session) -> UserModel:
        repo = UserRepository(db)
        user = repo.get_by_email(LLM_QA_TEST_USER_EMAIL)
        if user is None:
            return repo.create(
                email=LLM_QA_TEST_USER_EMAIL,
                password_hash=hash_password(LLM_QA_TEST_USER_PASSWORD),
                role="user",
            )

        user.password_hash = hash_password(LLM_QA_TEST_USER_PASSWORD)
        user.role = "user"
        user.email_unsubscribed = False
        user.is_suspended = False
        user.is_locked = False
        user.default_astrologer_id = None
        return user

    @staticmethod
    def _resolve_birth_place(db: Session) -> tuple[int, str, float, float, str | None, str | None]:
        results = GeocodingService.search_with_cache(
            db,
            LLM_QA_TEST_BIRTH_PLACE,
            1,
            country_code="fr",
            lang="fr",
        )
        if not results:
            raise LlmQaSeedServiceError(
                code="llm_qa_seed_place_not_found",
                message="canonical qa place could not be resolved",
                details={"query": LLM_QA_TEST_BIRTH_PLACE},
            )

        best_match = results[0]
        timezone_iana = GeocodingService.derive_timezone(lat=best_match.lat, lon=best_match.lon)
        if not timezone_iana:
            raise LlmQaSeedServiceError(
                code="llm_qa_seed_timezone_not_found",
                message="canonical qa timezone could not be derived",
                details={"query": LLM_QA_TEST_BIRTH_PLACE},
            )

        place, _ = GeoPlaceResolvedRepository(db).find_or_create(
            GeoPlaceResolvedCreateData(
                provider=best_match.provider,
                provider_place_id=best_match.provider_place_id,
                display_name=best_match.display_name,
                latitude=best_match.lat,
                longitude=best_match.lon,
                osm_type=best_match.osm_type,
                osm_id=best_match.osm_id,
                place_type=best_match.type,
                place_class=best_match.class_,
                importance=best_match.importance,
                place_rank=best_match.place_rank,
                country_code=best_match.address.country_code,
                country=best_match.address.country,
                state=best_match.address.state,
                county=best_match.address.county,
                city=best_match.address.city,
                postcode=best_match.address.postcode,
                timezone_iana=timezone_iana,
                timezone_source="timezonefinder",
                timezone_confidence=1.0,
                normalized_query=LLM_QA_TEST_BIRTH_PLACE,
                query_language="fr",
                query_country_code="fr",
                raw_payload=best_match.model_dump(mode="json", by_alias=True),
            )
        )
        if not place.timezone_iana:
            place.timezone_iana = timezone_iana
            place.timezone_source = "timezonefinder"
            place.timezone_confidence = 1.0
            db.flush()

        return (
            place.id,
            place.timezone_iana or timezone_iana,
            float(place.latitude),
            float(place.longitude),
            place.city,
            place.country,
        )

    @staticmethod
    def _upsert_birth_profile(
        db: Session,
        *,
        user_id: int,
        place_resolved_id: int,
        timezone_iana: str,
        birth_lat: float,
        birth_lon: float,
        birth_city: str | None,
        birth_country: str | None,
    ) -> BirthInput:
        birth_input = BirthInput(
            birth_date=LLM_QA_TEST_BIRTH_DATE,
            birth_time=LLM_QA_TEST_BIRTH_TIME,
            birth_place=LLM_QA_TEST_BIRTH_PLACE,
            birth_timezone=timezone_iana,
            place_resolved_id=place_resolved_id,
            birth_city=birth_city,
            birth_country=birth_country,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
        )
        UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=birth_input)
        return birth_input

    @staticmethod
    def _ensure_chart(db: Session, *, user_id: int, birth_input: BirthInput) -> tuple[str, bool]:
        expected_hash = ChartResultService.compute_input_hash(
            birth_input=birth_input,
            reference_version=settings.active_reference_version,
            ruleset_version=settings.ruleset_version,
        )
        latest = ChartResultRepository(db).get_latest_by_user_id(user_id)
        if (
            latest is not None
            and latest.reference_version == settings.active_reference_version
            and latest.ruleset_version == settings.ruleset_version
            and latest.input_hash == expected_hash
        ):
            LlmQaSeedService._prune_legacy_charts(
                db,
                user_id=user_id,
                keep_chart_id=latest.chart_id,
            )
            return latest.chart_id, True

        generated = UserNatalChartService.generate_for_user(db, user_id=user_id)
        LlmQaSeedService._prune_legacy_charts(
            db,
            user_id=user_id,
            keep_chart_id=generated.chart_id,
        )
        return generated.chart_id, False

    @staticmethod
    def ensure_canonical_test_user(db: Session) -> LlmQaSeedResult:
        LlmQaSeedService._require_allowed_environment()

        user = LlmQaSeedService._find_or_create_user(db)
        (
            place_resolved_id,
            timezone_iana,
            birth_lat,
            birth_lon,
            birth_city,
            birth_country,
        ) = LlmQaSeedService._resolve_birth_place(db)
        birth_input = LlmQaSeedService._upsert_birth_profile(
            db,
            user_id=user.id,
            place_resolved_id=place_resolved_id,
            timezone_iana=timezone_iana,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            birth_city=birth_city,
            birth_country=birth_country,
        )
        chart_id, chart_reused = LlmQaSeedService._ensure_chart(
            db,
            user_id=user.id,
            birth_input=birth_input,
        )
        db.commit()

        logger.info(
            "llm_qa_seed_ready user_id=%s email=%s place_resolved_id=%s chart_id=%s reused=%s",
            user.id,
            user.email,
            place_resolved_id,
            chart_id,
            chart_reused,
        )
        return LlmQaSeedResult(
            user_id=user.id,
            email=user.email,
            birth_place_resolved_id=place_resolved_id,
            birth_timezone=timezone_iana,
            chart_id=chart_id,
            chart_reused=chart_reused,
        )


def build_llm_qa_seed_chart_payload(user_id: int) -> dict[str, object]:
    return {
        "chart_id": str(uuid.uuid4()),
        "user_id": user_id,
        "kind": "llm-qa-seed",
    }
