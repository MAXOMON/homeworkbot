from pydantic import BaseModel


class StudentsGroup(BaseModel):
    group_name: str
    disciplines_short_name: list[str]
    students: list[str]