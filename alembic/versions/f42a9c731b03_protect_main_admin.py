"""Protect the main administrator and grant full application access.

Revision ID: f42a9c731b03
Revises: e31f8b620a02
"""
from alembic import op
import sqlalchemy as sa

revision = "f42a9c731b03"
down_revision = "e31f8b620a02"
branch_labels = None
depends_on = None

DELETE_TRIGGER = """
CREATE TRIGGER protect_main_admin_delete
BEFORE DELETE ON employees FOR EACH ROW
BEGIN
    IF OLD.is_superadmin = 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Main administrator cannot be deleted';
    END IF;
END
"""

UPDATE_TRIGGER = """
CREATE TRIGGER protect_main_admin_update
BEFORE UPDATE ON employees FOR EACH ROW
BEGIN
    IF OLD.is_superadmin = 1 AND
       (NEW.is_superadmin = 0 OR NEW.is_active = 0 OR NEW.fired_at IS NOT NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Main administrator cannot be deactivated or demoted';
    END IF;
END
"""


def upgrade() -> None:
    op.add_column("employees", sa.Column("is_superadmin", sa.Boolean(), nullable=False, server_default="0"))
    op.execute("""
        UPDATE employees SET is_superadmin = 1 WHERE id = (
            SELECT candidate.id FROM (
                SELECT e.id FROM employees e
                JOIN employee_roles er ON er.employee_id = e.id
                JOIN roles r ON r.id = er.role_id
                WHERE e.is_active = 1 AND e.fired_at IS NULL AND r.code IN ('boss', 'admin')
                ORDER BY CASE WHEN r.code = 'boss' THEN 0 ELSE 1 END, e.id
                LIMIT 1
            ) AS candidate
        )
    """)
    op.create_check_constraint("ck_employees_superadmin_active", "employees", "NOT is_superadmin OR (is_active AND fired_at IS NULL)")
    op.execute(DELETE_TRIGGER)
    op.execute(UPDATE_TRIGGER)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS protect_main_admin_update")
    op.execute("DROP TRIGGER IF EXISTS protect_main_admin_delete")
    op.drop_constraint("ck_employees_superadmin_active", "employees", type_="check")
    op.drop_column("employees", "is_superadmin")
