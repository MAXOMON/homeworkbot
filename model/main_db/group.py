"""Describes 'groups' table - study groups of students"""
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.main_db.database import Base
from model.main_db.discipline_group import association_discipline_to_group
from model.main_db.teacher_group import association_teacher_to_group


class Group(Base):
    """
    :param group_name: group name eg 'PTM'

    :param students: set the connection with the 'students' table 
        for the correct work associative table
    :param disciplines: set the connection with the 'disciplines' table 
        for the correct work associative table
    :param teachers: set the connection with the 'teachers' table 
        for the correct work associative table
    """
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(String(20), unique=True)

    students: Mapped[List["Student"]] = relationship(
        back_populates="group",
        cascade="all, delete, delete-orphan",
    )

    disciplines: Mapped[List["Discipline"]] = relationship(
        secondary=association_discipline_to_group,
        back_populates="groups"
    )

    teachers: Mapped[List["Teacher"]] = relationship(
        secondary=association_teacher_to_group,
        back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"Группа [ID: {self.id}, Название: {self.group_name}]"
    