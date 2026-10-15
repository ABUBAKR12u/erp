from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.Base import Base


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(80))
    is_system: Mapped[bool] = mapped_column(default=False)