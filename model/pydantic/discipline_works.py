from datetime import date

from pydantic import BaseModel


class DisciplineWork(BaseModel):
    number: int
    amount_tasks: int
    deadline: date


class DisciplineWorksConfig(BaseModel):
    full_name: str
    short_name: str
    path_to_test: str
    path_to_answer: str
    language: str
    works: list[DisciplineWork]


class DisciplinesConfig(BaseModel):
    disciplines: list[DisciplineWorksConfig]
