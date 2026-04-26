from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.v1.schemas.routers.public.consultation import (
    ConsultationThirdPartyProfile,
    ConsultationThirdPartyProfileCreate,
    ConsultationThirdPartyUsage,
)
from app.infra.db.repositories.consultation_third_party_repository import (
    ConsultationThirdPartyRepository,
)


class ConsultationThirdPartyService:
    @staticmethod
    def list_third_parties(db: Session, user_id: int) -> list[ConsultationThirdPartyProfile]:
        repo = ConsultationThirdPartyRepository(db)
        models = repo.list_for_user(user_id)

        results = []
        for m in models:
            usages = repo.list_usages(m.id)
            results.append(
                ConsultationThirdPartyProfile(
                    external_id=m.external_id,
                    nickname=m.nickname,
                    birth_date=m.birth_date,
                    birth_time=m.birth_time,
                    birth_time_known=m.birth_time_known,
                    birth_place=m.birth_place,
                    birth_city=m.birth_city,
                    birth_country=m.birth_country,
                    birth_lat=m.birth_lat,
                    birth_lon=m.birth_lon,
                    place_resolved_id=m.birth_place_resolved_id,
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                    usage_history=[
                        ConsultationThirdPartyUsage(
                            consultation_id=u.consultation_id,
                            consultation_type=u.consultation_type,
                            context_summary=u.context_summary,
                            created_at=u.created_at,
                        )
                        for u in usages
                    ],
                )
            )
        return results

    @staticmethod
    def create_third_party(
        db: Session, user_id: int, payload: ConsultationThirdPartyProfileCreate
    ) -> ConsultationThirdPartyProfile:
        repo = ConsultationThirdPartyRepository(db)

        birth_timezone = payload.birth_timezone or "UTC"

        model = repo.create_profile(
            user_id=user_id,
            nickname=payload.nickname,
            birth_date=payload.birth_date,
            birth_place=payload.birth_place,
            birth_timezone=birth_timezone,
            birth_time=payload.birth_time,
            birth_time_known=payload.birth_time_known,
            birth_city=payload.birth_city,
            birth_country=payload.birth_country,
            birth_lat=payload.birth_lat,
            birth_lon=payload.birth_lon,
            birth_place_resolved_id=payload.place_resolved_id,
        )
        db.commit()  # Ensure it's committed in tests too if not using shared session

        return ConsultationThirdPartyProfile(
            external_id=model.external_id,
            nickname=model.nickname,
            birth_date=model.birth_date,
            birth_time=model.birth_time,
            birth_time_known=model.birth_time_known,
            birth_place=model.birth_place,
            birth_city=model.birth_city,
            birth_country=model.birth_country,
            birth_lat=model.birth_lat,
            birth_lon=model.birth_lon,
            place_resolved_id=model.birth_place_resolved_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            usage_history=[],
        )
