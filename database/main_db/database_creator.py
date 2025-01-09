from database.main_db.first_run_configurator import FirstRunConfigurator
from model.pydantic.db_creator_settings import DbCreatorSettings
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.chat import Chat
from model.main_db.admin import Admin
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.student_ban import StudentBan
from model.main_db.teacher_discipline import TeacherDiscipline
from model.main_db.teacher_group import TeacherGroup

from database.main_db.database import create_tables, Session


def create_main_tables(settings: DbCreatorSettings) -> None:
    create_tables()

    if not settings.remote_configuration:
        fill_db_from_files(
            settings.disciplines_path,
            settings.excel_data_path
        )
    else:
        session = Session()
        session.add(Admin(telegram_id=settings.default_admin))
        session.commit()
        session.close()
        

def fill_db_from_files(disciplines_path: str,
                       excel_data_path: str) -> None:
    configurator = FirstRunConfigurator(disciplines_path, excel_data_path)
    disciplines: dict[str, Discipline] = {}
    groups: dict[str, Group] = {}

    session = Session()
    start_disciplines = configurator.disciplines

    for it in start_disciplines:
        disciplines[it.short_name] = Discipline(
            full_name=it.full_name,
            short_name=it.short_name,
            path_to_test=it.path_to_test,
            path_to_answer=it.path_to_answer,
            language=it.language,
            max_tasks=configurator.counting_tasks(it),
            works=configurator.disciplines_works_to_json(it),
            max_home_works=len(it.works)
        )
        session.add(disciplines[it.short_name])
    
    temp_students: dict[str, list[Student]] = {}
    for it in configurator.students_config:
        for group_name, students_raw_list in configurator.students_config[it].items():
            temp_students[it] = []
            groups[group_name] = Group(group_name=group_name)
            session.add(groups[group_name])
            session.flush()

            for student_raw in students_raw_list:
                student = Student(
                    full_name=student_raw.full_name,
                    group=groups[group_name].id
                )

                temp_students[it].append(student)
                session.add(student)
    
    for dis, teacher_group in configurator.teachers_config.items():
        for group_name, teachers_raw_list in teacher_group.items():
            if group_name not in groups:
                groups[group_name] = Group(group_name=group_name)
                session.add(groups[group_name])
                session.flush()

            for teachers_raw in teachers_raw_list:
                teacher = Teacher(
                    full_name=teachers_raw.full_name,
                    telegram_id=teachers_raw.telegram_id,
                )
                if teachers_raw.is_admin:
                    session.add(Admin(telegram_id=teachers_raw.telegram_id))
                session.add(teacher)
                session.flush()
                session.add(
                    TeacherGroup(
                        group_id=groups[group_name].id,
                        teacher_id=teacher.id
                    )
                )
                session.add(
                    TeacherDiscipline(
                        discipline_id=disciplines[dis].id,
                        teacher_id=teacher.id
                    )
                )

    session.flush()

    for dis, student_list in temp_students.items():
        for student in student_list:
            discipline = disciplines[dis]
            assigned_discipline = AssignedDiscipline(
                discipline_id=discipline.id,
                student_id=student.id,
                home_work=configurator.create_empty_homework_json(dis)
            )
            session.add(assigned_discipline)

    session.commit()
    session.close()
