"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

task_priority = postgresql.ENUM("low", "medium", "high", name="taskpriority")
task_status = postgresql.ENUM("todo", "in_progress", "done", name="taskstatus")

# Column-level references to the SAME types must not try to CREATE TYPE a
# second time -- we create the types explicitly below, so the columns that
# use them are marked create_type=False. Omitting this causes a
# "type already exists" error the moment create_table() runs, because
# SQLAlchemy otherwise emits CREATE TYPE again as part of the table DDL.
task_priority_col = postgresql.ENUM(
    "low", "medium", "high", name="taskpriority", create_type=False
)
task_status_col = postgresql.ENUM(
    "todo", "in_progress", "done", name="taskstatus", create_type=False
)


def upgrade():
    bind = op.get_bind()
    task_priority.create(bind, checkfirst=True)
    task_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("google_id", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_google_id", "users", ["google_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", task_priority_col, nullable=False, server_default="medium"),
        sa.Column("status", task_status_col, nullable=False, server_default="todo"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "task_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
    )

    op.create_table(
        "ai_chats",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("ai_chats")
    op.drop_table("task_sessions")
    op.drop_table("tasks")
    op.drop_table("users")
    task_status.drop(op.get_bind(), checkfirst=True)
    task_priority.drop(op.get_bind(), checkfirst=True)
