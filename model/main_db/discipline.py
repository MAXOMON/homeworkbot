"""Describes 'disciplines' table (academic disciplines)"""
from typing import List

from sqlalchemy import JSON, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.main_db.database import Base
from model.main_db.discipline_group import association_discipline_to_group
from model.main_db.teacher_discipline import association_teacher_to_discipline


class Discipline(Base):
    """
    :param full_name: full name of the discipline, for example
        "Programming Technologies and Methods"
    :param short_name: abbreviated name of the discipline (abbreviation),
        for example "PTM"
    :param path_to_test: path where tests should be located,
        to this discipline, for example "_disciplines/tmp/test"
    :param path_to_answer: the path where the students' answers should 
        be located, to the selected discipline,
        for example "_disciplines/tmp/answer"
    :param language: programming language used in training/testing, eg "python"
    :param max_tasks: how many learning tasks does this discipline contain,
        for example 169
    :param max_home_works: how many lab assignments does it contain, 
        i.e. the number of max_tasks, divided into conditional subgroups,
        for example 10
    :param works: field, in JSON format, contains data for configuring
        another model, namely DisciplineWorksConfig

    :param groups: set the connection with the 'groups' table 
        for the correct work associative table
    :param teachers: set the connection with the 'teachers' table 
        for the correct work associative table
    """
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    path_to_test: Mapped[str] = mapped_column(String(200), nullable=False)
    path_to_answer: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    max_tasks: Mapped[int] = mapped_column(nullable=False)
    max_home_works: Mapped[int] = mapped_column(nullable=False)
    # DisciplineWorksConfig
    works: Mapped[str] = mapped_column(JSON, nullable=False)

    groups: Mapped[List['Group']] = relationship(
        secondary=association_discipline_to_group,
        back_populates="disciplines",
        cascade="all, delete, delete-orphan",
        single_parent=True
    )

    teachers: Mapped[List['Teacher']] = relationship(
        secondary=association_teacher_to_discipline,
        back_populates="disciplines"
    )

    def __repr__(self) -> str:
        info: str = f"Дисциплина {self.short_name}, " \
            f"max_tasks: {self.max_tasks}, " \
            f"works: {self.works}"
        return info
