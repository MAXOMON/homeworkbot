import asyncio

from pathlib import Path
from database.queue_db import queue_in_crud, rejected_crud
from testing_tools.checker.folder_builder import FolderBuilder
from model.queue_db.queue_in import QueueIn
from model.pydantic.test_rejected_files import TestRejectedFiles, RejectedType



class TaskProcessing:
    """
    Главный класс подсистемы проверки
    """
    def __init__(
            self,
            temp_folder_path: Path,
            docker_amount_restriction: int = 1):
        """
        :param temp_folder: путь до временной директории, где будут формироваться
        каталоги для создания docker-контейнеров
        :param docker_amount_restriction: ограничение на количество одновременно
        работающих контейнеров
        """
        self.temp_folder_path = temp_folder_path
        self.docker_amount_restriction = docker_amount_restriction

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            for it in range(self.docker_amount_restriction):
                tg.create_task(self.__task_processing())

    async def __task_processing(self):
        while True:
            await asyncio.sleep(2)
            if queue_in_crud.is_not_empty():
                record = queue_in_crud.get_first_record()
                await asyncio.gather(
                    asyncio.to_thread(
                        _run_prepare_docker,
                        record,
                        self.temp_folder_path
                    )
                )


def _run_prepare_docker(record: QueueIn, temp_folder_path: Path) -> None:
    """
    Функция подготовки файлов для контейнера и его последующего запуска

    :param record: запись из промежуточной БД, с данными по загруженным ответам студента
    :param temp_folder_path: путь до временной директории, где будут формироваться
    каталоги для создания docker-контейнеров

    :return: None
    """
    folder_builder = FolderBuilder(temp_folder_path, record)
    docker_folder_path = folder_builder.build()
    if folder_builder.has_rejected_files():
        rejected_crud.add_record(
            record.telegram_id,
            record.chat_id,
            TestRejectedFiles(
                type=RejectedType.TemplateError,
                description='Имя файла(-ов) не соответствует шаблону для тестирования',
                files=folder_builder.get_rejected_file_names()
            )
        )
    if not folder_builder.has_file_for_test():
        return None
