"""Describes 'teachers' table - teachers of this project"""
from dataclasses import dataclass
from typing import List
from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.main_db.database import Base
from model.main_db.teacher_discipline import association_teacher_to_discipline
from model.main_db.teacher_group import association_teacher_to_group


class Teacher(Base):
    """
    :param full_name: teacher full name
    :param telegram_id: teacher Telegram ID

    :param disciplines: set the connection with the 'disciplines' table 
        for the correct work associative table
    :param groups: set the connection with the 'groups' table 
        for the correct work associative table
    """
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger,
                                             nullable=False,
                                             unique=True)

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
    """
    For simplified data processing in 
    first_run_configurator, module database.main_db...

    :param full_name: teacher full name
    :param telegram_id: teacher Telegram ID
    :param is_admin: 'True' IF has access to admin functions ELSE 'False'
    """
    full_name: str
    telegram_id: int
    is_admin: bool
