"""
Describes the 'admin' table - bot administrators
"""
from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base


class Admin(Base):
    """
    :param telegram_id: Telegram_ID admin
    :param teacher_mode: access to teacher functions IF TRUE
    """
    __tablename__ = "admin"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    teacher_mode: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Admin [ID: {self.telegram_id}, mode: {self.teacher_mode}]"
    