"""Add weekly schedules and dated lesson sessions.

Revision ID: b731c9a42004
Revises: f42a9c731b03
"""
from alembic import op
import sqlalchemy as sa

revision = "b731c9a42004"
down_revision = "f42a9c731b03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "group_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=False),
        sa.CheckConstraint("weekday BETWEEN 1 AND 7", name="ck_schedule_weekday"),
        sa.CheckConstraint("end_time > start_time", name="ck_schedule_times"),
        sa.UniqueConstraint("group_id", "weekday", "start_time", name="uq_schedule_group_slot"),
    )
    op.create_index("ix_schedule_day_time", "group_schedules", ["weekday", "start_time", "end_time"])
    op.create_table(
        "lesson_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("topic", sa.String(200), nullable=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("status", sa.Enum("rejalashtirilgan", "otilgan", "bekor_qilingan", name="sessionstatus"), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("end_time > start_time", name="ck_session_times"),
        sa.UniqueConstraint("group_id", "date", "start_time", name="uq_session_group_slot"),
    )
    op.create_index("ix_session_date_time", "lesson_sessions", ["date", "start_time", "end_time"])


def downgrade() -> None:
    op.drop_table("lesson_sessions")
    op.drop_table("group_schedules")
