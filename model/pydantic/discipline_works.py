"""
The module contains the necessary models and parameters for processing
and checking data in the configuration file (discipline_config.json)
"""
from datetime import date
from pydantic import BaseModel


class DisciplineWork(BaseModel):
    """Process a specific work in detail"""
    number: int
    amount_tasks: int
    deadline: date


class DisciplineWorksConfig(BaseModel):
    """To process a specific discipline in more detail"""
    full_name: str
    short_name: str
    path_to_test: str
    path_to_answer: str
    language: str
    works: list[DisciplineWork]


class DisciplinesConfig(BaseModel):
    """Process the list of disciplines"""
    disciplines: list[DisciplineWorksConfig]
