# docker_logger.py
"""
The module is copied to the directory from which the container 
will be launched.
"""
import json
import os
from threading import Lock
#from pydantic.json import pydantic_encoder
from pydantic_core import to_jsonable_python
from .report_model import LabReport, TestLogInit, TaskReport


class _SingletonBaseClass(type):
    """For correct operation in multi-threaded verification systems"""
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DockerLogger(metaclass=_SingletonBaseClass):
    """Class for logging results"""
    def __init__(self):
        path_to_volume: str = 'data'  # TODO: Docker env
        with open('log_init.json', encoding='utf-8') as file:
            data = json.load(file)

        self.test_settings = TestLogInit(**data)
        self.path_to_volume = path_to_volume
        self.path_to_log = f'{self.test_settings.student_id}-\
            {self.test_settings.lab_id}-' \
            f'{self.test_settings.run_time:%Y-%m-%d_%H-%M-%S%z}.json'

        if os.path.isfile(self.path_to_log):
            with open(self.path_to_log, encoding='utf-8') as file:
                data = json.load(file)
                self.lab_report = LabReport(**data)
        else:
            self.lab_report = LabReport(
                lab_id=self.test_settings.lab_id
            )

    def get_logfile_name(self) -> str:
        """
        :return str: path to logging result
        """
        return self.path_to_log

    def add_successful_task(self, task_id: int) -> None:
        """
        Method for adding a task whose test completed successfully

        :param task_id: task number (identifier)

        :return None:
        """
        self.__add_task_report(task_id, True)

    def add_fail_task(self, task_id: int, description: str) -> None:
        """
        Method for adding a task whose test failed

        :param task_id: task number (identifier)
        :param description: description of the reason for failure

        :return None:
        """
        self.__add_task_report(task_id, False, description)

    def __add_task_report(self,
                          task_id: int,
                          status: bool,
                          description: str | None = None) -> None:
        """
        Method of adding a record to the test result log file

        :param task_id: task number (identifier)
        :param status: True IF - the test is passed, ELSE - False
        :param description: description of the reason for failure or success

        :return None:
        """
        task = None
        for it in self.lab_report.tasks:
            if task_id == it.task_id:
                task = it
                break

        if task is None:
            self.lab_report.tasks.append(
                TaskReport(
                    task_id=task_id,
                    time=self.test_settings.run_time,
                    status=status,
                    description=[description] if description is not None else []
                )
            )
        else:
            if not (task.status and status):
                if task.status:
                    task.status = False
                    task.description.add(description)
                else:
                    if description is not None:
                        task.description.add(description)

    def save(self) -> None:
        """
        Saves the log to the previously specified directory

        :return None:
        """
        with open(self.path_to_log, 'w', encoding='utf-8') as file:
            json.dump(
                self.lab_report,
                file,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
                separators=(',', ': '),
                default=to_jsonable_python
                #default=pydantic_encoder
            )

    def to_json(self) -> str:
        """
        Method for converting a data structure storing test results 
        into json format

        :return: test result in json format
        """
        return json.dumps(
                self.lab_report,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
                separators=(',', ': '),
                default=to_jsonable_python
                #default=pydantic_encoder
            )
