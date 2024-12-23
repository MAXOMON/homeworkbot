from sqlalchemy import Column, Integer, JSON

from database.queue_db.database import Base


class Rejected(Base):
    __tablename__ = "rejected"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"Rejected [tID : {self.telegram_id}, chatID: {self.chat_id}, data: {self.data}]"
