from pydantic import BaseModel


class TaskResult(BaseModel):
    """
    Класс, хранящий данные о результате тестирования задания
    в рамках л/р или д/р, а также пояснения при проваленных тестах
    """
    task_id: int
    file_name: str
    description: set[str] = []


class TestResult(BaseModel):
    """
    Класс, хранящий данные о результатах ответов, которые
    успешно прошли тестирование или завалились в процессе.
    Его экземпляр передаётся из подсистемы проверки к боту
    через промежуточную базу данных
    """
    discipline_id: int
    lab_number: int
    successful_task: list[TaskResult] = []
    failed_task: list[TaskResult] = []
