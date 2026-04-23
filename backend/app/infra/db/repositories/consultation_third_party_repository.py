from __future__ import annotations

from datetime import date

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.consultation_third_party import (
    ConsultationThirdPartyProfileModel,
    ConsultationThirdPartyUsageModel,
)


class ConsultationThirdPartyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_external_id(self, external_id: str) -> ConsultationThirdPartyProfileModel | None:
        return self.db.scalar(
            select(ConsultationThirdPartyProfileModel).where(
                ConsultationThirdPartyProfileModel.external_id == external_id
            )
        )

    def list_for_user(self, user_id: int) -> list[ConsultationThirdPartyProfileModel]:
        return list(
            self.db.scalars(
                select(ConsultationThirdPartyProfileModel)
                .where(ConsultationThirdPartyProfileModel.user_id == user_id)
                .order_by(desc(ConsultationThirdPartyProfileModel.updated_at))
            ).all()
        )

    def create_profile(
        self,
        user_id: int,
        nickname: str,
        birth_date: date,
        birth_place: str,
        birth_timezone: str,
        birth_time: str | None = None,
        birth_time_known: bool = True,
        birth_city: str | None = None,
        birth_country: str | None = None,
        birth_lat: float | None = None,
        birth_lon: float | None = None,
        birth_place_resolved_id: int | None = None,
    ) -> ConsultationThirdPartyProfileModel:
        model = ConsultationThirdPartyProfileModel(
            user_id=user_id,
            nickname=nickname,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_time_known=birth_time_known,
            birth_place=birth_place,
            birth_timezone=birth_timezone,
            birth_city=birth_city,
            birth_country=birth_country,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            birth_place_resolved_id=birth_place_resolved_id,
        )
        self.db.add(model)
        self.db.flush()
        return model

    def record_usage(
        self,
        third_party_profile_id: int,
        consultation_id: str,
        consultation_type: str,
        context_summary: str,
    ) -> ConsultationThirdPartyUsageModel:
        model = ConsultationThirdPartyUsageModel(
            third_party_profile_id=third_party_profile_id,
            consultation_id=consultation_id,
            consultation_type=consultation_type,
            context_summary=context_summary,
        )
        self.db.add(model)
        self.db.flush()

        # Also update the updated_at of the profile
        profile = self.db.get(ConsultationThirdPartyProfileModel, third_party_profile_id)
        if profile:
            profile.updated_at = datetime_provider.utcnow()
            self.db.flush()

        return model

    def list_usages(self, third_party_profile_id: int) -> list[ConsultationThirdPartyUsageModel]:
        return list(
            self.db.scalars(
                select(ConsultationThirdPartyUsageModel)
                .where(
                    ConsultationThirdPartyUsageModel.third_party_profile_id
                    == third_party_profile_id
                )
                .order_by(desc(ConsultationThirdPartyUsageModel.created_at))
            ).all()
        )
