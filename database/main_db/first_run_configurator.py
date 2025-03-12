from pathlib import Path

from utils.disciplines_utils import *
from utils.homeworks_utils import *
from utils.excel_parser import ExcelDataParser
from model.pydantic.db_start_data import StudentRaw, TeacherRaw


class FirstRunConfigurator:
    
    def __init__(self, disciplines_path: str, excel_path: str):
        excel_init_data = ExcelDataParser(excel_path)

        self.__disciplines = load_disciplines_config(disciplines_path)
        self.__students = excel_init_data.students
        self.__teachers = excel_init_data.teachers
        self.__create_directory()

    def __create_directory(self):
        path = Path.cwd()
        for it in self.__disciplines.disciplines:
            Path(path.joinpath(it.path_to_test)).mkdir(parents=True, exist_ok=True)
            Path(path.joinpath(it.path_to_answer)).mkdir(parents=True, exist_ok=True)

    def counting_tasks(self, discipline: DisciplineWorksConfig) -> int:
        return counting_tasks(discipline)
    
    @property
    def disciplines(self) -> list[DisciplineWorksConfig]:
        return self.__disciplines.disciplines
    
    @property
    def students_config(self) -> dict[str, dict[str, list[StudentRaw]]]:
        return self.__students
    
    @property
    def teachers_config(self) -> dict[str, dict[str, list[TeacherRaw]]]:
        return self.__teachers
    
    def create_empty_homework_json(self, discipline_short_name: str) -> str:
        discipline = None
        for it in self.disciplines:
            if it.short_name == discipline_short_name:
                discipline = it
            
        if discipline is None:
            raise Exception(f"Discipline with short name {discipline_short_name} not found")

        empty_homework = create_homeworks(discipline)
        return homeworks_to_json(empty_homework)
    
    def disciplines_works_to_json(self, discipline: DisciplineWorksConfig) -> str:
        return disciplines_works_to_json(discipline)
