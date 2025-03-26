"""
The module contains the necessary models and parameters 
for more convenient testing of student laboratory work.
"""
from datetime import datetime
from pydantic import BaseModel


class LabReportException(Exception):
    """An error occurred while generating a report 
    on the completed laboratory work."""

class TestLogInit(BaseModel):
    """
    Contains information about the student, 
    the lab work being tested, 
    and the testing start time.
    """
    student_id: int
    lab_id: int
    run_time: datetime


class TaskReport(BaseModel):
    """
    Contains information about the task number, test time, 
    status (whether the test was passed or not), and description.
    """
    task_id: int
    time: datetime
    status: bool
    description: set[str] = []


class LabReport(BaseModel):
    """
    A model containing information about the laboratory work and 
    a list of tested tasks."""
    lab_id: int
    tasks: list[TaskReport] = []
