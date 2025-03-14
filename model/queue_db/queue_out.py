from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column, Mapped

from database.queue_db.database import Base


class QueueOut(Base):
    __tablename__ = "output"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"Q(output) [ID: {self.id}, TG: {self.telegram_id}, " \
             f"chat: {self.chat_id}, \ndata: {self.data}\n]"
