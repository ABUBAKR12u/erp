from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.Base import Base


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    employee_id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"))