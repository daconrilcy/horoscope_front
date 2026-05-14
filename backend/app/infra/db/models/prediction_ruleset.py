from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    false,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.prediction_reference import PredictionCategoryModel
    from app.infra.db.models.reference import AstralHouseSystemModel, ReferenceVersionModel


class PredictionRulesetModel(Base):
    __tablename__ = "prediction_rulesets"
    __table_args__ = (UniqueConstraint("version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    zodiac_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="tropical", server_default="tropical"
    )
    coordinate_mode: Mapped[str] = mapped_column(
        String(16), nullable=False, default="geocentric", server_default="geocentric"
    )
    house_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_house_systems.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    time_step_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, server_default="30"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_locked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    reference_version: Mapped["ReferenceVersionModel"] = relationship()
    house_system_reference: Mapped["AstralHouseSystemModel"] = relationship()

    @property
    def house_system(self) -> str:
        """Retourne le code applicatif du système de maisons référencé."""
        pending_code = getattr(self, "_pending_house_system_code", None)
        if pending_code is not None:
            return str(pending_code)
        return self.house_system_reference.code

    @house_system.setter
    def house_system(self, code: str) -> None:
        """Diffère la résolution SQL du code jusqu'au flush de la session."""
        self._pending_house_system_code = code


class RulesetEventTypeModel(Base):
    __tablename__ = "ruleset_event_types"
    __table_args__ = (UniqueConstraint("ruleset_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ruleset_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_rulesets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    event_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    base_weight: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0, server_default="1.0"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    ruleset: Mapped["PredictionRulesetModel"] = relationship()


class RulesetParameterModel(Base):
    __tablename__ = "ruleset_parameters"
    __table_args__ = (
        UniqueConstraint("ruleset_id", "param_key"),
        CheckConstraint(
            "data_type IN ('string', 'float', 'int', 'bool', 'json')",
            name="ck_ruleset_parameters_data_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ruleset_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_rulesets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    param_key: Mapped[str] = mapped_column(String(64), nullable=False)
    param_value: Mapped[str] = mapped_column(Text, nullable=False)
    data_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="string", server_default="string"
    )

    ruleset: Mapped["PredictionRulesetModel"] = relationship()


class CategoryCalibrationModel(Base):
    __tablename__ = "category_calibrations"
    __table_args__ = (UniqueConstraint("ruleset_id", "category_id", "valid_from"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ruleset_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_rulesets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    p05: Mapped[float | None] = mapped_column(Float, nullable=True)
    p25: Mapped[float | None] = mapped_column(Float, nullable=True)
    p50: Mapped[float | None] = mapped_column(Float, nullable=True)
    p75: Mapped[float | None] = mapped_column(Float, nullable=True)
    p95: Mapped[float | None] = mapped_column(Float, nullable=True)
    calibration_label: Mapped[str] = mapped_column(
        String(64), nullable=False, default="provisional", server_default="provisional"
    )
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    ruleset: Mapped["PredictionRulesetModel"] = relationship()
    category: Mapped["PredictionCategoryModel"] = relationship()
