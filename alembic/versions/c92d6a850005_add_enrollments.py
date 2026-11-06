"""Add student group membership history.

Revision ID: c92d6a850005
Revises: b731c9a42004
"""
from alembic import op
import sqlalchemy as sa

revision = "c92d6a850005"
down_revision = "b731c9a42004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("status", sa.Enum("faol", "muzlatilgan", "bitirgan", "ketgan", name="enrollmentstatus"), nullable=False),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("joined_at", sa.Date(), nullable=False),
        sa.Column("left_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("student_id", "group_id", "joined_at", name="uq_enrollment_student_group_joined"),
        sa.CheckConstraint("price >= 0", name="ck_enrollment_price"),
        sa.CheckConstraint("left_at IS NULL OR left_at >= joined_at", name="ck_enrollment_dates"),
        sa.CheckConstraint("(status IN ('faol', 'muzlatilgan') AND left_at IS NULL) OR (status IN ('bitirgan', 'ketgan') AND left_at IS NOT NULL)", name="ck_enrollment_status_dates"),
    )
    op.create_index("ix_enrollment_group_status", "enrollments", ["group_id", "status"])
    op.create_index("ix_enrollment_student", "enrollments", ["student_id"])


def downgrade() -> None:
    op.drop_table("enrollments")
