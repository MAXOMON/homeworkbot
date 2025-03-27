"""Describes 'students' table - students in this system"""
from dataclasses import dataclass
from typing import List
from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.main_db.database import Base


class Student(Base):
    """
    :param full_name: Full name of the student
    :param group_id: group id to where the student is assigned
    :param telegram_id: student Telegram ID

    :param group: set the connection with the 'groups' table 
        for the correct work associative table
    :param homeworks: set the connection with the 'assigned_discipline' table 
        for the correct work associative table
    """
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int] = mapped_column(
        ForeignKey('groups.id', ondelete="CASCADE"), nullable=False
        )
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=True, unique=True)

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
    """
    For simplified data processing in 
    first_run_configurator, module database.main_db...
    
    :param full_name: student full name
    """
    full_name: str
