import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Integer, Date, DateTime, Numeric, Enum, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base


class EnrollmentStatus(str, enum.Enum):
    faol = "faol"
    muzlatilgan = "muzlatilgan"
    bitirgan = "bitirgan"
    ketgan = "ketgan"


OPEN_ENROLLMENTS = (EnrollmentStatus.faol, EnrollmentStatus.muzlatilgan)


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "group_id", "joined_at", name="uq_enrollment_student_group_joined"),
        CheckConstraint("price >= 0", name="ck_enrollment_price"),
        CheckConstraint("left_at IS NULL OR left_at >= joined_at", name="ck_enrollment_dates"),
        CheckConstraint("(status IN ('faol', 'muzlatilgan') AND left_at IS NULL) OR (status IN ('bitirgan', 'ketgan') AND left_at IS NOT NULL)", name="ck_enrollment_status_dates"),
        Index("ix_enrollment_group_status", "group_id", "status"),
        Index("ix_enrollment_student", "student_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    status: Mapped[EnrollmentStatus] = mapped_column(Enum(EnrollmentStatus), default=EnrollmentStatus.faol)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    joined_at: Mapped[date] = mapped_column(Date)
    left_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", lazy="selectin")
    group = relationship("Group", lazy="selectin")
