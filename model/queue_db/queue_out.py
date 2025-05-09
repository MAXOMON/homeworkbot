"""
Contains an output intermediate table with output data:
results of checking the student's homework/laboratory work
"""
from sqlalchemy import JSON, BigInteger
from sqlalchemy.orm import mapped_column, Mapped
from database.queue_db.database import Base


class QueueOut(Base):
    """
    :param telegram_id: user Telegram ID, eg message.from_user.id
    :param chat_id: chat ID, eg message.chat.id
    :param data: test result with data 
        on successful/unsuccessful laboratory works
    """
    __tablename__ = "output"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    data: Mapped[str] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"Q(output) [ID: {self.id}, TG: {self.telegram_id}, " \
             f"chat: {self.chat_id}, \ndata: {self.data}\n]"
