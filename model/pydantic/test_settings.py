"""These policies are used directly in the student lab testing system"""
from pydantic import BaseModel


class TestLocalSettings(BaseModel):
    """
    Local policies for a specific task
    """
    lab_number: int
    prohibition: list[str] | None  #  запрет
    restriction: list[str] | None  #  ограничение
    resolve_import: list[str] | None  # разрешённые импорты


class TestGlobalSettings(BaseModel):
    """
    Global policies for all lab (homework) work
    """
    prohibition: list[str] | None  # запрет
    restriction: list[str] | None  # ограничение


class TestSettings(BaseModel):
    """
    Contains policies for lab (homework) work
    with dependencies on external packages
    """
    dependencies: list[str] | None  # зависимости
    global_level: TestGlobalSettings
    local_level: list[TestLocalSettings]
