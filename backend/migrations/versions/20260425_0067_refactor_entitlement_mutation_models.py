"""refactor entitlement mutation models

Revision ID: 20260425_0067
Revises: 20260402_0066
Create Date: 2026-04-25 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20260425_0067"
down_revision = "20260402_0066"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column("review_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column("request_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_audit_reviews_created_at"),
        "canonical_entitlement_mutation_audit_reviews",
        ["created_at"],
        unique=False,
    )

    op.add_column(
        "canonical_entitlement_mutation_audit_review_events",
        sa.Column("event_type", sa.String(length=32), nullable=False, server_default="updated"),
    )

    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("alert_status", sa.String(length=32), nullable=False, server_default="open"),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("first_delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("delivery_attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("is_suppressed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("suppressed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("suppression_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_updated_at"),
        "canonical_entitlement_mutation_alert_events",
        ["updated_at"],
        unique=False,
    )
    op.execute(
        """
        UPDATE canonical_entitlement_mutation_alert_events
        SET
            delivery_attempt_count = CASE
                WHEN delivery_status IS NULL OR delivery_status = '' THEN 0
                ELSE 1
            END,
            first_delivered_at = delivered_at,
            updated_at = created_at
        """
    )

    op.add_column(
        "canonical_entitlement_mutation_alert_delivery_attempts",
        sa.Column("response_code", sa.Integer(), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_delivery_attempts",
        sa.Column("is_retryable", sa.Boolean(), nullable=True),
    )

    op.create_table(
        "canonical_entitlement_mutation_alert_suppression_applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_event_id", sa.Integer(), nullable=False),
        sa.Column("suppression_rule_id", sa.Integer(), nullable=True),
        sa.Column("suppression_key", sa.String(length=64), nullable=True),
        sa.Column("application_mode", sa.String(length=32), nullable=False),
        sa.Column("application_reason", sa.Text(), nullable=True),
        sa.Column("applied_by_user_id", sa.Integer(), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "applied_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["alert_event_id"], ["canonical_entitlement_mutation_alert_events.id"]
        ),
        sa.ForeignKeyConstraint(
            ["suppression_rule_id"],
            ["canonical_entitlement_mutation_alert_suppression_rules.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_suppression_applications_alert_event_id"),
        "canonical_entitlement_mutation_alert_suppression_applications",
        ["alert_event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_suppression_applications_applied_at"),
        "canonical_entitlement_mutation_alert_suppression_applications",
        ["applied_at"],
        unique=False,
    )
    op.create_index(
        op.f(
            "ix_canonical_entitlement_mutation_alert_suppression_applications_suppression_rule_id"
        ),
        "canonical_entitlement_mutation_alert_suppression_applications",
        ["suppression_rule_id"],
        unique=False,
    )

    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("resolution_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("incident_key", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("requires_followup", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("followup_due_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("suppression_application_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("handling_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column("request_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handlings",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    if op.get_bind().dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_cemah_suppression_application_id",
            "canonical_entitlement_mutation_alert_event_handlings",
            "canonical_entitlement_mutation_alert_suppression_applications",
            ["suppression_application_id"],
            ["id"],
        )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_event_handlings_created_at"),
        "canonical_entitlement_mutation_alert_event_handlings",
        ["created_at"],
        unique=False,
    )

    op.add_column(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("event_type", sa.String(length=32), nullable=False, server_default="updated"),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("resolution_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("incident_key", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("requires_followup", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("followup_due_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "canonical_entitlement_mutation_alert_suppression_rules",
        sa.Column("rule_status", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("canonical_entitlement_mutation_alert_suppression_rules", "rule_status")

    op.drop_column("canonical_entitlement_mutation_alert_event_handling_events", "followup_due_at")
    op.drop_column(
        "canonical_entitlement_mutation_alert_event_handling_events", "requires_followup"
    )
    op.drop_column("canonical_entitlement_mutation_alert_event_handling_events", "incident_key")
    op.drop_column("canonical_entitlement_mutation_alert_event_handling_events", "resolution_code")
    op.drop_column("canonical_entitlement_mutation_alert_event_handling_events", "event_type")

    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_event_handlings_created_at"),
        table_name="canonical_entitlement_mutation_alert_event_handlings",
    )
    if op.get_bind().dialect.name != "sqlite":
        op.drop_constraint(
            "fk_cemah_suppression_application_id",
            "canonical_entitlement_mutation_alert_event_handlings",
            type_="foreignkey",
        )
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "updated_at")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "created_at")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "request_id")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "handling_version")
    op.drop_column(
        "canonical_entitlement_mutation_alert_event_handlings", "suppression_application_id"
    )
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "followup_due_at")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "requires_followup")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "incident_key")
    op.drop_column("canonical_entitlement_mutation_alert_event_handlings", "resolution_code")

    op.drop_index(
        op.f(
            "ix_canonical_entitlement_mutation_alert_suppression_applications_suppression_rule_id"
        ),
        table_name="canonical_entitlement_mutation_alert_suppression_applications",
    )
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_suppression_applications_applied_at"),
        table_name="canonical_entitlement_mutation_alert_suppression_applications",
    )
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_suppression_applications_alert_event_id"),
        table_name="canonical_entitlement_mutation_alert_suppression_applications",
    )
    op.drop_table("canonical_entitlement_mutation_alert_suppression_applications")

    op.drop_column("canonical_entitlement_mutation_alert_delivery_attempts", "is_retryable")
    op.drop_column("canonical_entitlement_mutation_alert_delivery_attempts", "response_code")

    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_updated_at"),
        table_name="canonical_entitlement_mutation_alert_events",
    )
    op.drop_column("canonical_entitlement_mutation_alert_events", "closed_at")
    op.drop_column("canonical_entitlement_mutation_alert_events", "suppression_reason")
    op.drop_column("canonical_entitlement_mutation_alert_events", "suppressed_at")
    op.drop_column("canonical_entitlement_mutation_alert_events", "is_suppressed")
    op.drop_column("canonical_entitlement_mutation_alert_events", "delivery_attempt_count")
    op.drop_column("canonical_entitlement_mutation_alert_events", "first_delivered_at")
    op.drop_column("canonical_entitlement_mutation_alert_events", "updated_at")
    op.drop_column("canonical_entitlement_mutation_alert_events", "alert_status")

    op.drop_column("canonical_entitlement_mutation_audit_review_events", "event_type")

    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_audit_reviews_created_at"),
        table_name="canonical_entitlement_mutation_audit_reviews",
    )
    op.drop_column("canonical_entitlement_mutation_audit_reviews", "request_id")
    op.drop_column("canonical_entitlement_mutation_audit_reviews", "updated_at")
    op.drop_column("canonical_entitlement_mutation_audit_reviews", "created_at")
    op.drop_column("canonical_entitlement_mutation_audit_reviews", "review_version")
