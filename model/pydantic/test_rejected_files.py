"""Contains a data structure for student responses rejected by the system"""
from enum import IntEnum
from pydantic import BaseModel


class RejectedType(IntEnum):
    """Reason, on select, for which answer files may be rejected"""
    TEMPLATEERROR = 0  # не вышел названием
    KEYWORDSERROR = 1  # запрещённые или отсутствующие ключевые слова


class TestRejectedFiles(BaseModel):
    """
    Contains the error type, description, and files that were rejected.
    Will be used in the checker module of the task_processing module.
    """
    type: RejectedType
    description: str
    files: list[str]
