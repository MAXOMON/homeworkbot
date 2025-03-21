"""
Contains a data structure that simplifies the process 
of entering a group of students into the database
"""
from pydantic import BaseModel


class StudentsGroup(BaseModel):
    """
    Contains the name of the group, discipline, and a list of students.
    It is subsequently used by the project administrator
    to add student group data to the database.
    """
    group_name: str
    disciplines_short_name: list[str]
    students: list[str]
