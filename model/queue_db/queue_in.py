"""
Contains an input intermediate table with data 
for the incoming data (homework/lab) from the student
"""
from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column, Mapped
from database.queue_db.database import Base


class QueueIn(Base):
    """
    :param telegram_id: user Telegram ID, eg message.from_user.id
    :param chat_id: chat ID, eg message.chat.id
    :param data: student answers
    """
    __tablename__ = "input"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"Q(input) [ID: {self.id}, TG: {self.telegram_id}, " \
              f"chat: {self.chat_id}, \ndata: {self.data}\n]"
