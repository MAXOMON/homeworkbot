from pydantic import BaseModel

from model.pydantic.students_group import StudentsGroup
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.teacher import Teacher


class DbStartData(BaseModel):
    groups: list[StudentsGroup]
    disciplines: list[DisciplineWorksConfig]
    teachers: list[Teacher]
    chats: list[int]
