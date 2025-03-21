"""
This module contains a configurator that loads data on disciplines, students,
teachers, from a file and thus prepares the data for subsequent processing,
for example, the initial filling of the database
"""
from pathlib import Path
from utils.disciplines_utils import disciplines_works_to_json,\
    load_disciplines_config, counting_tasks
from utils.homeworks_utils import DisciplineWorksConfig, create_homeworks,\
    homeworks_to_json
from utils.excel_parser import ExcelDataParser
from model.pydantic.db_start_data import StudentRaw, TeacherRaw
from database.main_db.crud_exceptions import DisciplineNotFoundException


class FirstRunConfigurator:
    """To download data on subjects, students, teachers from files"""
    def __init__(self, disciplines_path: str, excel_path: str):
        """
        The constructor accepts two paths: to the file with disciplines
        and to the excel file with information about students and pupils.
        Processes the presented information and saves it
        in a more convenient format for subsequent processing

        :param disciplines_path: path to the prepared file with disciplines
        :param excel_path: path to the prepared excel_file 
            with teachers-students data
        """
        excel_init_data = ExcelDataParser(excel_path)

        self.__disciplines = load_disciplines_config(disciplines_path)
        self.__students = excel_init_data.students
        self.__teachers = excel_init_data.teachers
        self.__create_directory()

    def __create_directory(self) -> None:
        """
        Create directories for the discipline and its tasks/answers 
        according to the system parameters

        :param None:

        :return None:
        """
        path = Path.cwd()
        for it in self.__disciplines.disciplines:
            Path(
                path.joinpath(it.path_to_test)
                ).mkdir(parents=True, exist_ok=True)
            Path(
                path.joinpath(it.path_to_answer)
                ).mkdir(parents=True, exist_ok=True)

    def counting_tasks(self, discipline: DisciplineWorksConfig) -> int:
        """
        Return the total number of tasks for this subject

        :param discipline: discipline passed in the format of the model
            pydantic DisciplineWorksConfig

        :return int: total count tasks on work of current discipline
        """
        return counting_tasks(discipline)

    @property
    def disciplines(self) -> list[DisciplineWorksConfig]:
        """
        Get disciplines data

        :param None:

        :return list[DisciplineWorksConfig]: a list containing data 
            on disciplines (full name, short name, path to tests,
            path to answers, language, list of works on this discipline)
        """
        return self.__disciplines.disciplines

    @property
    def students_config(self) -> dict[str, dict[str, list[StudentRaw]]]:
        """
        Get students data

        :param None:

        :return dict[str, dict[str, list[StudentRaw]]]:
            {discipline: {group_id: [students]}}
        """
        return self.__students

    @property
    def teachers_config(self) -> dict[str, dict[str, list[TeacherRaw]]]:
        """
        Get teachers data

        :param None:

        :return dict[str, dict[str, list[TeacherRaw]]]:
            {discipline: {group_id: [teachers]}}
        """
        return self.__teachers

    def create_empty_homework_json(self, discipline_short_name: str) -> str:
        """
        Сreate empty (not yet completed) homework

        :param discipline_short_name: eg "PTM" ...

        :return str: output format string (result json.dumps function)       
        """
        discipline = None
        for it in self.disciplines:
            if it.short_name == discipline_short_name:
                discipline = it

        if discipline is None:
            raise DisciplineNotFoundException(f"Discipline with short name \
                            {discipline_short_name} not found")

        empty_homework = create_homeworks(discipline)
        return homeworks_to_json(empty_homework)

    def disciplines_works_to_json(
            self, discipline: DisciplineWorksConfig
            ) -> str:
        """
        Convert discipline to json-like string format

        :param discipline: discipline containing parameters such as
            full name, short name, path to tests, path to answers, language,
            and a list of works on this discipline

        :return str: output format string (result json.dumps function)
        """
        return disciplines_works_to_json(discipline)
