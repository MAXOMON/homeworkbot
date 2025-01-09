from dataclasses import dataclass
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.main_db.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete="CASCADE"), nullable=False)
    telegram_id: Mapped[int] = mapped_column(nullable=True, unique=True)

    group: Mapped["Group"] = relationship(
        back_populates="students"
    )
    homeworks: Mapped[List["AssignedDiscipline"]] = relationship(
        back_populates="student", cascade="all, delete, delete-orphan"
    )

    def __repr__(self) -> str:
        info: str = f"Студент [ФИО: {self.full_name}, " \
            f"ID группы: {self.group}, Telegram ID: {self.telegram_id}]" 

        return info


@dataclass
class StudentRaw:
    full_name: str
