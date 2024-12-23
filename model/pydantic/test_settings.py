from pydantic import BaseModel


class TestLocalSettings(BaseModel):
    """
    Локальные политики конкретной задачи
    """
    lab_number: int
    prohibition: list[str] | None  #  запрет
    restriction: list[str] | None  #  ограничение
    resolve_import: list[str] | None  # разрешённые импорты


class TestGlobalSettings(BaseModel):
    """
    Глобальные политики всей лабораторной (домашней) работы
    """
    prohibition: list[str] | None  # запрет
    restriction: list[str] | None  # ограничение


class TestSettings(BaseModel):
    """
    Агрегация политик лабораторной (домашней) работы
    с зависимостями от внешних пакетов
    """
    dependencies: list[str] | None  # зависимости
    global_level: TestGlobalSettings
    local_level: list[TestLocalSettings]
