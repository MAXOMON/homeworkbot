"""This module is intended for initial filling of the database"""
from database.main_db.first_run_configurator import FirstRunConfigurator
from database.main_db.database import create_tables, Session
from model.pydantic.db_creator_settings import DbCreatorSettings
from model.main_db.group import Group
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.discipline import Discipline
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.admin import Admin


async def create_main_tables(settings: DbCreatorSettings) -> None:
    """
    create all the main tables

    :param settings: formatted data structure
    
    :return None:
    """
    await create_tables()

    if not settings.remote_configuration:
        await fill_db_from_files(
            settings.disciplines_path,
            settings.excel_data_path
        )
    else:
        async with Session() as session:
            session.add(Admin(telegram_id=settings.default_admin))
            await session.commit()

async def fill_db_from_files(disciplines_path: str,
                       excel_data_path: str) -> None:
    """
    Fill the database with primary data 
    from the local configuration

    :param disciplines_path: path to the discipline configuration file
    :param excel_data_path: path to file
        with data on teachers and students
    """
    configurator = FirstRunConfigurator(disciplines_path, excel_data_path)
    disciplines: dict[str, Discipline] = {}
    groups: dict[str, Group] = {}

    async with Session() as session:
        async with session.begin():
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

            temp_students: dict[str, list[Student]] = {}
            for it, _ in configurator.students_config.items():
                for group_name, students_raw_list \
                    in configurator.students_config[it].items():
                    temp_students[it] = [
                        Student(full_name=it.full_name) for it in students_raw_list
                    ]
                    groups[group_name] = Group(
                        group_name=group_name,
                        students=temp_students[it]
                    )
                    disciplines_groups = await getattr(disciplines[it].awaitable_attrs, 'groups')
                    disciplines_groups.append(groups[group_name])
                    #disciplines[it].groups.append(groups[group_name])

            for dis, teacher_group in configurator.teachers_config.items():
                for group_name, teachers_raw_list in teacher_group.items():

                    for teachers_raw in teachers_raw_list:
                        teacher = Teacher(
                            full_name=teachers_raw.full_name,
                            telegram_id=teachers_raw.telegram_id,
                        )
                        teacher_groups = await getattr(teacher.awaitable_attrs, 'groups')
                        teacher_groups.append(groups[group_name])
                        
                        disciplines_teachers = await getattr(disciplines[dis].awaitable_attrs, 'teachers')
                        disciplines_teachers.append(teacher)

                        if teachers_raw.is_admin:
                            session.add(Admin(telegram_id=teachers_raw.telegram_id))

            session.add_all(disciplines.values())
            await session.flush()

            for dis, student_list in temp_students.items():
                for student in student_list:
                    student.homeworks.append(
                        AssignedDiscipline(
                            discipline_id=disciplines[dis].id,
                            home_work=configurator.create_empty_homework_json(dis)
                        )
                    )

            await session.commit()
