# backend/app/infra/db/models/calibration.py
from datetime import UTC, datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, UniqueConstraint

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CalibrationRawDayModel(Base):
    __tablename__ = "calibration_raw_days"
    __table_args__ = (
        UniqueConstraint(
            "profile_label",
            "local_date",
            "category_code",
            "reference_version",
            "ruleset_version",
            name="uq_calibration_raw_day",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_label = Column(String, nullable=False)
    local_date = Column(Date, nullable=False)
    category_code = Column(String, nullable=False)
    raw_score = Column(Float, nullable=False)
    power = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    pivot_count = Column(Integer, nullable=False, default=0)
    reference_version = Column(String, nullable=False)
    ruleset_version = Column(String, nullable=False)
    computed_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
