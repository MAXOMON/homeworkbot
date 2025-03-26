"""
This module contains the necessary functionality to check the student's 
answers (solution files) to global and local policies.
"""
import glob
import json
import os
import re
from pathlib import Path
from model.pydantic.test_settings import TestSettings, TestLocalSettings,\
    TestGlobalSettings


class KeyWordsController:
    """
    A class that applies work testing policies to submitted student answers 
    and rejects answer files that do not meet the conditions 
    (presence of imports, presence or absence of keywords)
    """
    def __init__(self, path_to_folder: Path) -> None:
        """
        :param path_to_folder: The path where the policy file for testing 
            a specific lab is located.
        """
        self.test_dir = path_to_folder
        self.file_path = path_to_folder.joinpath('settings.json')
        with open(self.file_path, encoding='utf-8') as file:
            data = json.load(file)
        self.test_settings = TestSettings(**data)
        self.rejected_files: list[str] = []
        self.is_test_available = False

    def run(self) -> None:
        """
        Call the functionality that checks the submitted tests 
        for global and local policies (permissions and prohibitions).
        """
        glv = self.test_settings.global_level
        llv = self.test_settings.local_level
        filter_test_dir = Path(self.test_dir)
        filter_test_dir = filter_test_dir.joinpath('lab*.py')
        answer_files = glob.glob(f"{filter_test_dir}")

        if self.__has_global_keywords(answer_files, glv):
            answer_files = glob.glob(f"{filter_test_dir}")

        self.__delete_local_settings(answer_files)
        self.__has_local_keywords(answer_files, llv)

        answer_files = glob.glob(f"{filter_test_dir}")
        if answer_files:
            self.is_test_available = True

    def has_file_for_test(self) -> bool:
        """
        Checking if there are files available for testing.

        :return bool:
        """
        return self.is_test_available

    def has_rejected_files(self) -> bool:
        """
        Check if there are any files rejected by testing.

        :return bool:
        """
        return len(self.rejected_files) > 0

    def get_rejected_file_names(self) -> list[str]:
        """
        Get a list of file names that were rejected during testing.

        :return list[str]: list of file names
        """
        return self.rejected_files

    def __delete_local_settings(self, lab_files: list[str]) -> None:
        """
        Method for cleaning local policies from rejected student responses

        :param lab_files: list of remaining answer files
        """
        lab_numbers = [self.get_lab_number(file) for file in lab_files]
        del_local_settings = []
        for it in self.test_settings.local_level:
            if it.lab_number not in lab_numbers:
                del_local_settings.append(it)

        for it in del_local_settings:
            self.test_settings.local_level.remove(it)

        del del_local_settings

    def __has_global_keywords(
            self,
            lab_files: list[str],
            global_level: TestGlobalSettings
    ) -> bool:
        """
        Method for testing global testing policies on student responses

        :param lab_files: list of remaining answer files
        :param global_level: structure containing data
            about global testing policies

        :return: True IF there are rejected files for review, ELSE False
        """
        rejected: set[str] = set()
        if global_level.prohibition is not None:
            rejected.update(
                self.__search_keywords(
                    lab_files,
                    global_level.prohibition
                )
            )
        if global_level.restriction is not None:
            rejected.update(
                self.__search_keywords(
                    lab_files,
                    global_level.restriction,
                    is_restriction=True
                )
            )

        if len(rejected) > 0:
            for it in rejected:
                self.__delete_answer_and_test(it)
            return True
        return False

    def __delete_answer_and_test(self, answer_file_name: str) -> None:
        """
        Method for deleting a student's answer file and the test to it

        :param answer_file_name: student's answer to be deleted

        :return None:
        """
        del_file = Path(answer_file_name)
        self.rejected_files.append(del_file.name)
        os.remove(self.test_dir.joinpath(f'test_{del_file.name}'))
        os.remove(del_file)

    def __has_local_keywords(
            self,
            lab_files: list[str],
            local_level: list[TestLocalSettings]) -> None:
        """
        Method for testing local testing policies on student responses

        :param lab_files: list of remaining answer files
        :param local_level: structure containing data
            about local testing policies
            for each assignment uploaded by the student

        :return None:
        """
        rejected: set[str] = set()
        for locset in local_level:
            for file in lab_files:
                if locset.lab_number == self.get_lab_number(file):
                    if locset.prohibition is not None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                locset.prohibition
                            )
                        )

                    if locset.restriction is not None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                locset.restriction,
                                is_restriction=True
                            )
                        )

                    if locset.resolve_import is None:
                        rejected.update(
                            self.__search_keywords(
                                [file],
                                ['import']
                            )
                        )
                    else:
                        with open(file, 'r') as lab:
                            for line in lab:
                                if re.match(r'^from\s+[\w.]+\s+\
                                            import\s+[\w, ]+', line) or \
                                        re.match(r'^\
                                                 import\s+[\w.]+[\s,]+', line):

                                    is_use = False
                                    for rx in locset.resolve_import:
                                        if re.search('^from ' + rx, line) or \
                                                re.search('^import ' \
                                                          + rx, line):
                                            if not re.search('^import ' \
                                                             + rx+',', line):
                                                is_use = True
                                            break

                                    if not is_use:
                                        rejected.add(file)
        if len(rejected) > 0:
            for it in rejected:
                self.__delete_answer_and_test(it)

    def __search_keywords(
            self,
            lab_files: list[str],
            keywords: list[str],
            is_restriction=False
    ) -> set[str]:
        """
        Method of searching for prohibited or allowed keywords 
        in student responses

        :param lab_files: list of paths to student answers
        :param lab_files: list of searched keywords
        :param is_restriction: Search mode. False -
            to prohibit keywords,
            otherwise to their mandatory presence

        :return: a set of rejected student answers for further checking
        """
        rejected: set[str] = set()
        for file in lab_files:
            for it in keywords:
                with open(file, 'r') as lab:
                    content = lab.read()
                    regex = re.compile(it)
                    if bool(regex.search(content)):
                        if is_restriction:
                            continue
                        else:
                            rejected.add(file)
                            break
                    else:
                        if is_restriction:
                            rejected.add(file)
                            break
        return rejected

    def get_lab_number(self, file: str) -> int:
        """
        Function to extract task number from string to it

        :param file: path to the file with the answer

        :return: task number
        """
        name = Path(file).name
        value = name.split("_")[-1]
        value = value.split('.')[0]
        return int(value)
