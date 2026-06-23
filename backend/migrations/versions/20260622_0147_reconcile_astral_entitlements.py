"""Réconcilie les entitlements après externalisation Astral.

Revision ID: 20260622_0147
Revises: 20260622_0146
Create Date: 2026-06-22 22:35:00
"""

from __future__ import annotations

from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "20260622_0147"
down_revision = "20260622_0146"
branch_labels = None
depends_on = None

_ACTIVE_FEATURES = ("horoscope_daily", "b2b_api_access")
_LEGACY_FEATURES = (
    "natal_chart_short",
    "natal_chart_long",
    "astrologer_chat",
    "thematic_consultation",
    "transit_client_projection",
)
_B2C_PLAN_LIMITS = {
    "free": 1,
    "trial": 7,
    "basic": 30,
    "premium": 120,
}


def _now() -> datetime:
    """Retourne un timestamp UTC naïf compatible avec les colonnes existantes."""
    return datetime.now(UTC).replace(tzinfo=None)


def upgrade() -> None:
    """Supprime les bindings legacy et garantit les quotas horoscope_daily."""
    conn = op.get_bind()
    now = _now()

    legacy_feature_ids = [
        row.id
        for row in conn.execute(
            sa.text("SELECT id FROM feature_catalog WHERE feature_code IN :codes").bindparams(
                sa.bindparam("codes", expanding=True)
            ),
            {"codes": _LEGACY_FEATURES},
        )
    ]
    if legacy_feature_ids:
        legacy_binding_ids = [
            row.id
            for row in conn.execute(
                sa.text("SELECT id FROM plan_feature_bindings WHERE feature_id IN :ids").bindparams(
                    sa.bindparam("ids", expanding=True)
                ),
                {"ids": legacy_feature_ids},
            )
        ]
        if legacy_binding_ids:
            conn.execute(
                sa.text(
                    "DELETE FROM plan_feature_quotas WHERE plan_feature_binding_id IN :binding_ids"
                ).bindparams(sa.bindparam("binding_ids", expanding=True)),
                {"binding_ids": legacy_binding_ids},
            )
            conn.execute(
                sa.text("DELETE FROM plan_feature_bindings WHERE id IN :binding_ids").bindparams(
                    sa.bindparam("binding_ids", expanding=True)
                ),
                {"binding_ids": legacy_binding_ids},
            )
        conn.execute(
            sa.text(
                "UPDATE feature_catalog SET is_active = 0, updated_at = :now WHERE id IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": legacy_feature_ids, "now": now},
        )

    horoscope_feature_id = conn.execute(
        sa.text("SELECT id FROM feature_catalog WHERE feature_code = 'horoscope_daily'")
    ).scalar_one_or_none()
    if horoscope_feature_id is None:
        conn.execute(
            sa.text(
                "INSERT INTO feature_catalog "
                "(feature_code, feature_name, description, is_metered, "
                "is_active, created_at, updated_at) "
                "VALUES "
                "('horoscope_daily', 'Horoscope Daily', NULL, 1, 1, :now, :now)"
            ),
            {"now": now},
        )
        horoscope_feature_id = conn.execute(
            sa.text("SELECT id FROM feature_catalog WHERE feature_code = 'horoscope_daily'")
        ).scalar_one()
    else:
        conn.execute(
            sa.text(
                "UPDATE feature_catalog "
                "SET is_metered = 1, is_active = 1, updated_at = :now "
                "WHERE id = :id"
            ),
            {"id": horoscope_feature_id, "now": now},
        )

    for plan_code, quota_limit in _B2C_PLAN_LIMITS.items():
        plan_id = conn.execute(
            sa.text(
                "SELECT id FROM plan_catalog WHERE plan_code = :plan_code AND audience = 'B2C'"
            ),
            {"plan_code": plan_code},
        ).scalar_one_or_none()
        if plan_id is None:
            continue

        binding_id = conn.execute(
            sa.text(
                "SELECT id FROM plan_feature_bindings "
                "WHERE plan_id = :plan_id AND feature_id = :feature_id"
            ),
            {"plan_id": plan_id, "feature_id": horoscope_feature_id},
        ).scalar_one_or_none()
        if binding_id is None:
            conn.execute(
                sa.text(
                    "INSERT INTO plan_feature_bindings "
                    "(plan_id, feature_id, is_enabled, access_mode, variant_code, "
                    "source_origin, created_at, updated_at) "
                    "VALUES (:plan_id, :feature_id, 1, 'QUOTA', :variant_code, "
                    "'MANUAL', :now, :now)"
                ),
                {
                    "plan_id": plan_id,
                    "feature_id": horoscope_feature_id,
                    "variant_code": f"{plan_code}_daily",
                    "now": now,
                },
            )
            binding_id = conn.execute(
                sa.text(
                    "SELECT id FROM plan_feature_bindings "
                    "WHERE plan_id = :plan_id AND feature_id = :feature_id"
                ),
                {"plan_id": plan_id, "feature_id": horoscope_feature_id},
            ).scalar_one()
        else:
            conn.execute(
                sa.text(
                    "UPDATE plan_feature_bindings "
                    "SET is_enabled = 1, access_mode = 'QUOTA', "
                    "variant_code = :variant_code, updated_at = :now "
                    "WHERE id = :id"
                ),
                {"id": binding_id, "variant_code": f"{plan_code}_daily", "now": now},
            )

        conn.execute(
            sa.text("DELETE FROM plan_feature_quotas WHERE plan_feature_binding_id = :id"),
            {"id": binding_id},
        )
        conn.execute(
            sa.text(
                "INSERT INTO plan_feature_quotas "
                "(plan_feature_binding_id, quota_key, quota_limit, period_unit, "
                "period_value, reset_mode, source_origin, created_at, updated_at) "
                "VALUES (:binding_id, 'runs', :quota_limit, 'DAY', 1, "
                "'CALENDAR', 'MANUAL', :now, :now)"
            ),
            {"binding_id": binding_id, "quota_limit": quota_limit, "now": now},
        )


def downgrade() -> None:
    """Ne restaure pas les anciens entitlements supprimés du registre applicatif."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM plan_feature_quotas "
            "WHERE plan_feature_binding_id IN ("
            "SELECT b.id FROM plan_feature_bindings b "
            "JOIN feature_catalog f ON f.id = b.feature_id "
            "WHERE f.feature_code = 'horoscope_daily'"
            ")"
        )
    )
    conn.execute(
        sa.text(
            "DELETE FROM plan_feature_bindings "
            "WHERE feature_id IN ("
            "SELECT id FROM feature_catalog WHERE feature_code = 'horoscope_daily'"
            ")"
        )
    )
