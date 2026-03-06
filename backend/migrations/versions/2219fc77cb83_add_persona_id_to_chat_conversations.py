"""add persona_id to chat_conversations

Revision ID: 2219fc77cb83
Revises: fd1d41d35808
Create Date: 2026-03-05 17:57:51.743853
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2219fc77cb83"
down_revision: Union[str, Sequence[str], None] = "fd1d41d35808"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add persona_id to chat_conversations as nullable
    op.add_column(
        "chat_conversations",
        sa.Column(
            "persona_id",
            sa.UUID(),
            sa.ForeignKey("llm_personas.id", name="fk_chat_conversations_persona"),
            nullable=True,
        ),
    )

    # 2. Backfill existing conversations
    conn = op.get_bind()

    # Try to find a default persona
    # Preference: "Astrologue Standard"
    res = conn.execute(
        sa.text("SELECT id FROM llm_personas WHERE name = 'Astrologue Standard' LIMIT 1")
    ).fetchone()
    if not res:
        # Fallback: any enabled persona
        res = conn.execute(
            sa.text("SELECT id FROM llm_personas WHERE enabled = 1 LIMIT 1")
        ).fetchone()
    if not res:
        # Fallback: any persona
        res = conn.execute(sa.text("SELECT id FROM llm_personas LIMIT 1")).fetchone()

    default_persona_id = res[0] if res else None

    if default_persona_id:
        # Update existing rows
        conn.execute(
            sa.text(
                "UPDATE chat_conversations SET persona_id = :persona_id WHERE persona_id IS NULL"
            ),
            {"persona_id": default_persona_id},
        )
    else:
        # If no persona at all exists, we might need to create a legacy one
        # For now, let's check if there are any conversations
        count = conn.execute(sa.text("SELECT COUNT(*) FROM chat_conversations")).scalar()
        if count > 0:
            # We HAVE conversations but NO personas. This is a problem.
            # Let's create a legacy persona.
            legacy_id = str(uuid.uuid4())
            conn.execute(
                sa.text("""
                    INSERT INTO llm_personas 
                    (id, name, tone, verbosity, style_markers, boundaries, 
                     allowed_topics, disallowed_topics, formatting, enabled, 
                     created_at, updated_at) 
                    VALUES 
                    (:id, :name, 'direct', 'medium', '[]', '[]', '[]', '[]', 
                     '{}', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """),
                {"id": legacy_id, "name": "Legacy Default"},
            )
            conn.execute(
                sa.text(
                    "UPDATE chat_conversations SET persona_id = :persona_id "
                    "WHERE persona_id IS NULL"
                ),
                {"persona_id": legacy_id},
            )

    # 3. Make persona_id NOT NULL and add unique partial index
    with op.batch_alter_table("chat_conversations", schema=None) as batch_op:
        batch_op.alter_column("persona_id", existing_type=sa.UUID(), nullable=False)
        batch_op.create_index(
            "ix_chat_conversations_user_persona_active",
            ["user_id", "persona_id"],
            unique=True,
            sqlite_where=sa.text("status = 'active'"),
            postgresql_where=sa.text("status = 'active'"),
        )


def downgrade() -> None:
    with op.batch_alter_table("chat_conversations", schema=None) as batch_op:
        batch_op.drop_index("ix_chat_conversations_user_persona_active")
        batch_op.drop_constraint("fk_chat_conversations_persona", type_="foreignkey")
        batch_op.drop_column("persona_id")
