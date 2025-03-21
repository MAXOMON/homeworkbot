"""Contains the data structure for the queue database output table"""
from pydantic import BaseModel


class TaskResult(BaseModel):
    """
    A class that stores data about the result of testing a task within 
    a lab or homework assignment, as well as explanations for failed tests
    """
    task_id: int
    file_name: str
    description: set[str] = []


class TestResult(BaseModel):
    """
    A class that stores data on the results of responses that 
    have successfully passed testing or failed during the process.
    Its instance is passed from the verification subsystem to the bot
    via an intermediate database
    """
    discipline_id: int
    lab_number: int
    successful_task: list[TaskResult] = []
    failed_task: list[TaskResult] = []
