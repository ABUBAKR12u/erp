from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base

class TeacherProfiles(Base):
    __tablename__ = "teacher_profiles"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True
    )
    bio: Mapped[str | None] = mapped_column(Text)
    specialization: Mapped[str | None] = mapped_column(String(255))
    experience_years: Mapped[int | None] = mapped_column()
    max_groups: Mapped[int | None] = mapped_column()

    employee: Mapped["Employees"] = relationship(
        "Employees", back_populates="teacher_profile"
    )