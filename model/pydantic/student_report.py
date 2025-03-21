"""
For simplified processing of data on work completed by a student.
For subsequent use in interactive reports.
"""
from pydantic import BaseModel


class StudentReport(BaseModel):
    """
    Stores data in the form of a report on the work done by the student. 
    Necessary for subsequent interactive reporting.
    """
    full_name: str = ""
    points: float = 0
    lab_completed: int = 0
    deadlines_fails: int = 0
    task_completed: int = 0
    task_ratio: int = 0
