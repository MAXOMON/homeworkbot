"""
This model contains a system for checking 
answers directly from the student
"""
import asyncio
import json
from pathlib import Path
from database.main_db import common_crud
from database.queue_db import queue_in_crud, rejected_crud, queue_out_crud
from model.pydantic.queue_in_raw import QueueInRaw
from model.pydantic.queue_out_raw import TaskResult, TestResult
from model.pydantic.test_rejected_files import TestRejectedFiles, RejectedType
from model.queue_db.queue_in import QueueIn
from testing_tools.checker.docker_builder import DockerBuilder
from testing_tools.checker.folder_builder import FolderBuilder
from testing_tools.checker.keywords_controller import KeyWordsController
from testing_tools.logger.report_model import LabReport, LabReportException


class TaskProcessing:
    """Main class of the verification subsystem"""
    def __init__(
            self,
            temp_folder_path: Path,
            docker_amount_restriction: int = 1):
        """
        :param temp_folder: path to the temporary directory 
            where directories for creating docker containers will be formed
        :param docker_amount_restriction: limit on the number 
            of simultaneously running containers
        """
        self.temp_folder_path = temp_folder_path
        self.docker_amount_restriction = docker_amount_restriction

    async def run(self):
        """
        Run creating task groups according to the allowed number 
        of containers to be launched at a time.
        """
        async with asyncio.TaskGroup() as tg:
            for _ in range(self.docker_amount_restriction):
                tg.create_task(self.__task_processing())

    async def __task_processing(self):
        """
        Take the first record from the input table of the intermediate DB 
        and send it for verification in a separate docker container, 
        in a separate thread.
        """
        while True:
            await asyncio.sleep(3)
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
    The function of preparing files for a container and its subsequent launch

    :param record: record from the intermediate database, 
        with data on the student's uploaded answers
    :param temp_folder_path: path to the temporary directory where directories
        for creating docker containers will be formed
    """
    folder_builder = FolderBuilder(temp_folder_path, record)
    docker_folder_path = folder_builder.build()
    if folder_builder.has_rejected_files():
        rejected_crud.add_record(
            record.telegram_id,
            record.chat_id,
            TestRejectedFiles(
                type=RejectedType.TemplateError,
                description='Имя файла(-ов) не соответствует \
                    шаблону для тестирования',
                files=folder_builder.get_rejected_file_names()
            )
        )
    if not folder_builder.has_file_for_test():
        return None

    keywords_controller = KeyWordsController(docker_folder_path)
    keywords_controller.run()
    if keywords_controller.has_rejected_files():
        rejected_crud.add_record(
            record.telegram_id,
            record.chat_id,
            TestRejectedFiles(
                type=RejectedType.KeyWordsError,
                description="В файле(-ах) имеются запрещенные \
                    ключевые слова, " +
                    "либо не используются необходимые для решения задачи",
                files=keywords_controller.get_rejected_file_names()
            )
        )

    if not keywords_controller.has_file_for_test():
        return None

    module_path = Path.cwd().joinpath('testing_tools')

    folder_builder.add_file(module_path.joinpath('conftest.py'))
    folder_builder.add_file(module_path.joinpath('docker_output.py'))
    folder_builder.add_dir(module_path.joinpath('logger'))

    docker_builder = DockerBuilder(
        docker_folder_path,
        record.telegram_id,
        folder_builder.get_lab_number()
    )
    docker_builder.run_docker()

    result = docker_builder.get_run_result()
    try:
        lab_report = LabReport(**json.loads(result))
    except LabReportException:
        print("Произошла ошибка, при чтении docker.logs(output)")

    common_crud.write_test_result(lab_report, record)
    _send_test_result_to_bot(lab_report, record)


def _send_test_result_to_bot(lab_report: LabReport, record: QueueIn) -> None:
    """
    Function of sending the test result to the intermediate database

    :param lab_report: data structure with the results of the container 
        in which the testing was run
    :param record: record from the intermediate database, 
        with data on the student's uploaded answers
    """
    straw = QueueInRaw(**json.loads(record.data))
    result_report = TestResult(
        discipline_id=straw.discipline_id,
        lab_number=straw.lab_number
    )
    for it in lab_report.tasks:
        if it.status:
            result_report.successful_task.append(
                TaskResult(
                    task_id=it.task_id,
                    file_name=f'lab{straw.lab_number}-{it.task_id}.py'
                )
            )
        else:
            result_report.failed_task.append(
                TaskResult(
                    task_id=it.task_id,
                    file_name=f'lab{straw.lab_number}-{it.task_id}.py',
                    description=it.description
                )
            )
    queue_out_crud.add_record(
        record.telegram_id,
        record.chat_id,
        result_report
    )
