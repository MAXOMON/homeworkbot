from enum import IntEnum

from pydantic import BaseModel


class RejectedType(IntEnum):
    TemplateError = 0  # не вышел названием
    KeyWordsError = 1  # запрещённые или отсутствующие ключевые слова


class TestRejectedFiles(BaseModel):
    type: RejectedType
    description: str
    files: list[str]
