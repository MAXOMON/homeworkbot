from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base


class Chat(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    

    def __repr__(self) -> str:
        return f"Chat [ID: {self.chat_id}]"
    