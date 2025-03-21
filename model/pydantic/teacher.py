"""
Contains a data structure that simplifies the process 
of entering teacher information into the database
"""
from pydantic import BaseModel


class Teacher(BaseModel):
    """
    Contains comprehensive information about the teacher, namely full name,
    telegram ID, administrator status, assigned courses and assigned groups.
    Will be used later to add to the database
    """
    full_name: str
    telegram_id: int
    is_admin: bool
    assign_disciplines: list[str]
    assign_groups: list[str]
