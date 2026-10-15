from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.Base import Base


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id") ,primary_key=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"))

    role: Mapped["Roles"]=relationship("Roles" , back_populates="employee_role")
    employee: Mapped["Employees"]=relationship("Employees" , back_populates="employee_role")