"""Describes 'banlist' table - banned students"""
from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base


class StudentBan(Base):
    """
    :param telegram_id: Telegram ID student who was banned
    """
    __tablename__ = "banlist"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def __repr__(self) -> str:
        return f"Ban [ID: {self.telegram_id}]"
