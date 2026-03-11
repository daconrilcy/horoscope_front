from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.prediction_reference import PredictionCategoryModel
    from app.infra.db.models.prediction_ruleset import (
        PredictionRulesetModel,
        RulesetEventTypeModel,
    )
    from app.infra.db.models.reference import ReferenceVersionModel
    from app.infra.db.models.user import UserModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DailyPredictionRunModel(Base):
    __tablename__ = "daily_prediction_runs"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "local_date",
            "reference_version_id",
            "ruleset_id",
            "engine_mode",
            name="uq_daily_prediction_runs_user_date_ruleset",
        ),
        Index("ix_daily_prediction_runs_user_id_local_date", "user_id", "local_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    local_date: Mapped[date] = mapped_column(nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id", ondelete="RESTRICT"), nullable=False
    )
    ruleset_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_rulesets.id", ondelete="RESTRICT"), nullable=False
    )
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    engine_mode: Mapped[str] = mapped_column(String(16), nullable=False, default="v2")
    engine_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    snapshot_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    evidence_pack_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    v3_metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    house_system_effective: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_provisional_calibration: Mapped[bool | None] = mapped_column(nullable=True)
    calibration_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    overall_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_tone: Mapped[str | None] = mapped_column(String(16), nullable=True)
    main_turning_point_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["UserModel"] = relationship()
    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    ruleset: Mapped["PredictionRulesetModel"] = relationship()

    category_scores: Mapped[list["DailyPredictionCategoryScoreModel"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    turning_points: Mapped[list["DailyPredictionTurningPointModel"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    time_blocks: Mapped[list["DailyPredictionTimeBlockModel"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )

    # Transient flag (not in DB) — ClassVar prevents ORM mapping
    needs_recompute: ClassVar[bool] = False


class DailyPredictionCategoryScoreModel(Base):
    __tablename__ = "daily_prediction_category_scores"
    __table_args__ = (UniqueConstraint("run_id", "category_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("daily_prediction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    raw_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    normalized_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    note_20: Mapped[int | None] = mapped_column(Integer, nullable=True)
    power: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    intensity_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    rarity_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    level_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    dominance_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    stability_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    intensity_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_provisional: Mapped[bool | None] = mapped_column(nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    contributors_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["DailyPredictionRunModel"] = relationship(back_populates="category_scores")
    category: Mapped["PredictionCategoryModel"] = relationship()


class DailyPredictionTurningPointModel(Base):
    __tablename__ = "daily_prediction_turning_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("daily_prediction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    occurred_at_local: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    event_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("ruleset_event_types.id", ondelete="SET NULL"), nullable=True
    )
    severity: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["DailyPredictionRunModel"] = relationship(back_populates="turning_points")
    event_type: Mapped["RulesetEventTypeModel | None"] = relationship()


class DailyPredictionTimeBlockModel(Base):
    __tablename__ = "daily_prediction_time_blocks"
    __table_args__ = (UniqueConstraint("run_id", "block_index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("daily_prediction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    block_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_at_local: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_at_local: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tone_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    dominant_categories_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["DailyPredictionRunModel"] = relationship(back_populates="time_blocks")
