from pydantic import BaseModel


class StudentReport(BaseModel):
    full_name: str = ""
    points: float = 0
    lab_completed: int = 0
    deadlines_fails: int = 0
    task_completed: int = 0
    task_ratio: int = 0
