from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey

from app.database.Base import Base


class Lead(Base):
    __tablename__ = "leads"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id:   Mapped[int]        = mapped_column(Integer)
    first_name:  Mapped[str]        = mapped_column(String(60))
    last_name:   Mapped[str | None] = mapped_column(String(60), nullable=True)
    phone:       Mapped[str]        = mapped_column(String(20))
    source_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    course_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    lost_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    student_id:  Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    comment:     Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by:  Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at:  Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at:  Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    branch:   Mapped[Optional["Branch"]]     = relationship("Branch",      primaryjoin="Lead.branch_id == Branch.id",         foreign_keys=[branch_id],   lazy="noload")
    source:   Mapped[Optional["LeadSource"]] = relationship("LeadSource",  primaryjoin="Lead.source_id == LeadSource.id",     foreign_keys=[source_id],   lazy="noload")
    status:   Mapped[Optional["LeadStatus"]] = relationship("LeadStatus",  primaryjoin="Lead.status_id == LeadStatus.id",     foreign_keys=[status_id],   lazy="noload")
    course:   Mapped[Optional["Course"]]     = relationship("Course",      primaryjoin="Lead.course_id == Course.id",         foreign_keys=[course_id],   lazy="noload")
    assignee: Mapped[Optional["Employees"]]  = relationship("Employees",   primaryjoin="Lead.assigned_to == Employees.id",    foreign_keys=[assigned_to], lazy="noload")
    creator:  Mapped[Optional["Employees"]]  = relationship("Employees",   primaryjoin="Lead.created_by == Employees.id",     foreign_keys=[created_by],  lazy="noload")
    student:  Mapped[Optional["Student"]]    = relationship("Student",     primaryjoin="Lead.student_id == Student.id",       foreign_keys=[student_id],  lazy="noload")