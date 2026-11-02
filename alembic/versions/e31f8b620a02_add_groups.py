"""Add groups table.

Revision ID: e31f8b620a02
Revises: e31f8b620a01
"""
from alembic import op
import sqlalchemy as sa

revision = "e31f8b620a02"
down_revision = "e31f8b620a01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("rejalashtirilgan", "faol", "tugagan", "bekor_qilingan", name="groupstatus"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("max_students", sa.SmallInteger(), nullable=False),
        sa.Column("current_students", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("price", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("max_students > 0", name="ck_group_max_students"),
        sa.CheckConstraint("current_students >= 0 AND current_students <= max_students", name="ck_group_current_students"),
        sa.CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_group_dates"),
        sa.CheckConstraint("price IS NULL OR price >= 0", name="ck_group_price"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"]),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["teacher_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_id", "name", name="uq_group_branch_name"),
    )


def downgrade() -> None:
    op.drop_table("groups")
