"""This module contains a file directory builder with answers and tests"""
import glob
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from pydantic.json import pydantic_encoder
from database.main_db import common_crud
from model.pydantic.queue_in_raw import QueueInRaw
from model.queue_db.queue_in import QueueIn
from testing_tools.logger.report_model import TestLogInit


class FolderBuilder:
    """
    Class for creating a directory with test files, uploaded student answers
    and testing policy settings and rejecting answer files
    for which there are no tests.
    """
    def __init__(self, temp_path: Path, raw_data: QueueIn):
        """
        :param temp_path: path to temporary directory
        :param raw_data: data on the assignments and the work number 
            that the student sent
        """
        self.temp_path = temp_path
        self.student_id = raw_data.telegram_id
        self.answer = QueueInRaw(**json.loads(raw_data.data))
        self.docker_folder: Path | None = None
        self.rejected_files = []
        self.is_test_available = False

    def get_lab_number(self) -> int:
        """
        Obtain the lab work number from the submitted work.

        :return int: lab number
        """
        return self.answer.lab_number

    async def build(self) -> Path:
        """
        Forms a path in a pre-defined directory where the student's 
            answers will be located. And copies his files with the work there.

        :return Path: group_name/answers/student_full_name--uuid/...
        """
        discipline = await common_crud.get_discipline(self.answer.discipline_id)
        test_path = Path.cwd().joinpath(
            discipline.path_to_test
        ).joinpath(str(self.answer.lab_number))
        original_test_files = glob.glob(f"{test_path}/*")

        answers = {Path(file).name for file in self.answer.files_path}
        tests = {
            Path(file).name.split("_", 1)[1]
            for file in original_test_files
            if 'settings.json' not in file
        }

        self.rejected_files = list(answers.difference(tests))

        temp_test_files = []
        for test_file in answers.intersection(tests):
            temp_test_files.append(test_path.joinpath(f"test_{test_file}"))

        temp_test_files.append(
            test_path.joinpath('settings.json')
        )

        current_time = datetime.now()

        self.docker_folder = self.temp_path.joinpath(
            discipline.short_name
        ).joinpath(
            str(self.answer.lab_number)
        ).joinpath(
            f'{self.student_id}_{uuid.uuid4()}'
        )
        Path(self.docker_folder).mkdir(parents=True, exist_ok=True)

        for answer_file in self.answer.files_path:
            if Path(answer_file).name not in self.rejected_files:
                shutil.copy(answer_file, self.docker_folder)

        for test_file in temp_test_files:
            shutil.copy(test_file, self.docker_folder)

        formatted_current_time = current_time.replace(microsecond=0)

        log_init_data = TestLogInit(
            student_id=self.student_id,
            lab_id=self.answer.lab_number,
            run_time=formatted_current_time
        )

        with open(
            f"{self.docker_folder.joinpath('log_init.json')}",
            'w', encoding='utf-8') as file:
            json.dump(
                log_init_data,
                file,
                sort_keys=False,
                indent=0,
                ensure_ascii=False,
                separators=(',', ':'),
                default=pydantic_encoder
            )

        self.is_test_available = len(self.rejected_files) <= len(answers)

        return self.docker_folder

    def get_rejected_file_names(self) -> list[str]:
        """
        Get files that were rejected (failed to pass verification).

        :return list[str]: list of file names
        """
        return self.rejected_files

    def has_rejected_files(self) -> bool:
        """
        Check if there are any rejected files

        :return bool: True IF has rej files ELSE False
        """
        return len(self.rejected_files) > 0

    def has_file_for_test(self) -> bool:
        """
        Check if there are files available for testing.

        :return bool: True IF has files ELSE False
        """
        return self.is_test_available

    def add_file(self, path_to_file: Path) -> None:
        """
        Add the selected file to an existing directory.

        :param path_to_file: Path to the file to be added.

        :return None:
        """
        shutil.copy(path_to_file, self.docker_folder)

    def add_dir(self, path_to_dir: Path) -> None:
        """
        Add the selected directory to an existing directory.

        :param path_to_dir: Path to the directory to be added.

        :return None:
        """
        shutil.copytree(
            path_to_dir,
            self.docker_folder.joinpath(path_to_dir.name)
        )
