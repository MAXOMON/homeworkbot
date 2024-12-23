from pydantic import BaseModel
from datetime import datetime




class TestLogInit(BaseModel):
    student_id: int
    lab_id: int
    run_time: datetime


class TaskReport(BaseModel):
    task_id: int
    time: datetime
    status: bool
    description: set[str] = []


class LabReport(BaseModel):
    lab_id: int
    tasks: list[TaskReport] = []
