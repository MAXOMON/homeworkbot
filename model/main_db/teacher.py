from dataclasses import dataclass
from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.main_db.database import Base
from model.main_db.teacher_discipline import association_teacher_to_discipline
from model.main_db.teacher_group import association_teacher_to_group


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    disciplines: Mapped[List["Discipline"]] = relationship(
        secondary=association_teacher_to_discipline,
        back_populates="teachers"
    )

    groups: Mapped[List["Group"]] = relationship(
        secondary=association_teacher_to_group,
        back_populates="teachers"
    )

    def __repr__(self) -> str:
        info: str = f"Преподаватель [ФИО: {self.full_name}, " \
            f"Telegram ID: {self.telegram_id}]"
        return info


@dataclass
class TeacherRaw:
    full_name: str
    telegram_id: int
    is_admin: bool
