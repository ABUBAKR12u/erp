from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.Base import Base


class LeadSource(Base):
    __tablename__ = "lead_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    monthly_budget: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")