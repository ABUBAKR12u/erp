"""Register the existing courses table in migration history.

Revision ID: e31f8b620a01
Revises: 7d164b4f562b
"""
from alembic import op
import sqlalchemy as sa

revision = "e31f8b620a01"
down_revision = "7d164b4f562b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_months", sa.SmallInteger(), nullable=True),
        sa.Column("lessons_count", sa.SmallInteger(), nullable=True),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("min_age", sa.SmallInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    # This baseline adopts a table that may predate Alembic; keep its data.
    pass
