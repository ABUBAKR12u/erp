from sqlalchemy import BigInteger, Boolean, CheckConstraint, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base


class LeadStatus(Base):
    __tablename__ = "lead_statuses"
    __table_args__ = (CheckConstraint("NOT (is_won AND is_lost)", name="ck_lead_status_won_lost"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    is_won: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    is_lost: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    # leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="status")