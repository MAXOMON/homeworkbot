from sqlalchemy import Column, Integer, String

from database.main_db.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Group [ID: {self.id}, name: {self.group_name}]"
    