# Référentiel courant des règles de suppression d'alertes.
"""Définit les règles de suppression actives du sous-domaine entitlement mutation."""

from __future__ import annotations

from sqlalchemy import Boolean, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.shared.base_mixins import (
    CreatedAtMixin,
    UpdatedAtMixin,
)


class CanonicalEntitlementMutationAlertSuppressionRuleModel(Base, CreatedAtMixin, UpdatedAtMixin):
    """Porte la définition normalisée d'une règle de suppression."""

    __tablename__ = "canonical_entitlement_mutation_alert_suppression_rules"
    __table_args__ = (
        Index("ix_cema_suppression_rules_is_active", "is_active"),
        Index("ix_cema_suppression_rules_is_active_kind", "is_active", "alert_kind"),
        Index(
            "uq_cema_suppression_rules_criteria_normalized",
            "alert_kind",
            text("coalesce(feature_code, '')"),
            text("coalesce(plan_code, '')"),
            text("coalesce(actor_type, '')"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    feature_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actor_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    suppression_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ops_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
