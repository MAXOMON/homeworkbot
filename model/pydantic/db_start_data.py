"""
Data structure for processing data on students,
teachers and initial filling of the database
"""
from dataclasses import dataclass
from pydantic import BaseModel
from model.pydantic.students_group import StudentsGroup
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.teacher import Teacher


class DbStartData(BaseModel):
    """
    For simplified processing of data on groups, disciplines,
    teachers and chats
    """
    groups: list[StudentsGroup]
    disciplines: list[DisciplineWorksConfig]
    teachers: list[Teacher]
    chats: list[int]


@dataclass
class StudentRaw:
    """For simplified processing of student data"""
    full_name: str


@dataclass
class TeacherRaw:
    """For simplified processing of teacher data"""
    full_name: str
    telegram_id: int
    is_admin: bool
