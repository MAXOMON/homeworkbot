"""
The module contains the necessary models and parameters for processing
and checking data "home_works.json" for their subsequent addition
to the table  'assigned_discipline'
"""
from datetime import datetime, date
from pydantic import BaseModel


class HomeTask(BaseModel):
    """Process each task in detail"""
    number: int
    is_done: bool = False
    last_try_time: datetime | None = None
    amount_tries: int = 0


class HomeWork(BaseModel):
    """Review each homework assignment in detail."""
    number: int
    deadline: date
    tasks: list[HomeTask]
    is_done: bool = False
    tasks_completed: int = 0
    end_time: datetime | None = None


class DisciplineHomeWorks(BaseModel):
    """Process the list of homework"""
    home_works: list[HomeWork]
