from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.prediction_reference import PredictionCategoryModel
    from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
    from app.infra.db.models.reference import ReferenceVersionModel
    from app.infra.db.models.user import UserModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserPredictionBaselineModel(Base):
    __tablename__ = "user_prediction_baselines"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category_id",
            "window_start_date",
            "window_end_date",
            "reference_version_id",
            "ruleset_id",
            "house_system_effective",
            name="uq_user_prediction_baseline",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id", ondelete="RESTRICT"), nullable=False
    )
    ruleset_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_rulesets.id", ondelete="RESTRICT"), nullable=False
    )
    house_system_effective: Mapped[str] = mapped_column(String(16), nullable=False)
    window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    window_start_date: Mapped[date] = mapped_column(nullable=False)
    window_end_date: Mapped[date] = mapped_column(nullable=False)

    mean_raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    std_raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    mean_note_20: Mapped[float] = mapped_column(Float, nullable=False)
    std_note_20: Mapped[float] = mapped_column(Float, nullable=False)

    p10: Mapped[float] = mapped_column(Float, nullable=False)
    p50: Mapped[float] = mapped_column(Float, nullable=False)
    p90: Mapped[float] = mapped_column(Float, nullable=False)

    sample_size_days: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    # Relationships
    user: Mapped["UserModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()
    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    ruleset: Mapped["PredictionRulesetModel"] = relationship()
