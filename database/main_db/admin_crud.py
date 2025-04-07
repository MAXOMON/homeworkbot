"""
Contains functions for adding, reading, 
changing and deleting data from the database, 
intended for the administrator of this system.
"""
import os
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import DisciplineNotFoundException,\
    GroupAlreadyExistException, DisciplineAlreadyExistException,\
    GroupNotFoundException
from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student
from model.pydantic.db_start_data import DbStartData
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup
from utils.disciplines_utils import disciplines_works_from_json,\
      disciplines_works_to_json, counting_tasks
from utils.homeworks_utils import create_homeworks, homeworks_to_json


def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
    Check if this administrator has teacher functions disabled

    :param telegram_id: admin Telegram ID

    :return bool: True, if this administrator has teacher functions disabled
    """
    with Session() as session:
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return not admin.teacher_mode

def is_admin_with_teacher_mode(telegram_id: int) -> bool:
    """
    Check if this administrator has teacher privileges

    :param telegram_id: admin Telegram ID

    :return bool: True, if this administrator has teacher privileges
    """
    with Session() as session:
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return admin.teacher_mode

def is_admin(telegram_id: int) -> bool:
    """
    Check if this user is an administrator

    :param telegram_id: user Telegram ID

    :return bool: True if the user is an administrator
    """
    with Session() as session:
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
        return admin is not None

def is_admin_and_teacher(telegram_id: int) -> bool:
    """
    Check if this user is an administrator and a teacher

    :param telegram_id: user Telegram ID

    :return bool: True if the USER is an administrator and a teacher
    """
    _is_admin = is_admin(telegram_id)
    _is_teacher = is_teacher(telegram_id)
    return _is_admin and _is_teacher

def add_chat(chat_id: int) -> None:
    """
    Add chat to database

    :param chat_id: chat Telegram ID

    :return None:
    """
    with Session() as session:
        session.add(Chat(chat_id=chat_id))
        session.commit()

def add_teacher(full_name: str, tg_id: int) -> None:
    """
    Add the teacher to the database

    :param full_name: teacher full name
    :param tg_id: teacher Telegram ID

    :return None:
    """
    with Session() as session:
        session.add(Teacher(full_name=full_name, telegram_id=tg_id))
        session.commit()

def get_teachers() -> list[Teacher]:
    """
    Return the list of teachers

    :param None:

    :return list[Teacher]: list of teachers
    """
    with Session() as session:
        return session.query(Teacher).all()

def get_not_assign_teacher_groups(teacher_id: int) -> list[Group]:
    """
    Return the list of groups that are not assigned to the teacher

    :param teacher_id: teacher Telegram ID

    :return list[Group]: list of groups
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        ids_assigned_groups = [it.id for it in teacher.groups]
        query = select(Group).where(
            Group.id.not_in(ids_assigned_groups)
        )
        return session.scalars(query).all()

def assign_teacher_to_group(teacher_id: int, group_id: int) -> None:
    """
    Assign the teacher and group to the teacher_group table in the database

    :param teacher_id: teacher Telegram ID
    :param group_id: group ID

    :return None:
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        teacher.groups.append(
            session.get(Group, group_id)
        )
        session.commit()

def get_all_groups() -> list[Group]:
    """
    Return the list of all groups

    :param None:

    :return list[Group]: List of all groups
    """
    with Session() as session:
        return session.query(Group).all()

def add_student(full_name: str, group_id: int) -> None:
    """
    Add the student to the database

    :param full_name: student full name
    :param group_id: group ID

    :return None:
    """
    session = Session()
    group: Group = session.get(Group, group_id)

    student = Student(
        full_name=full_name,
        group_id=group_id
    )
    group.students.append(student)
    for discipline in group.disciplines:
        empty_homework = create_homeworks(
            disciplines_works_from_json(discipline.works)
        )
        student.homeworks.append(
            AssignedDiscipline(
                discipline_id=discipline.id,
                home_work=homeworks_to_json(empty_homework)
            )
        )
    session.commit()
    session.close()

def add_discipline(discipline: DisciplineWorksConfig) -> None:
    """
    Add discipline to the DB

    :param discipline: formatted data (pydantic-obj) DisciplineWorksConfig

    :return: None
    """
    with Session() as session:
        session.add(
            Discipline(
                full_name=discipline.full_name,
                short_name=discipline.short_name,
                path_to_test=discipline.path_to_test,
                path_to_answer=discipline.path_to_answer,
                works=disciplines_works_to_json(discipline),
                language=discipline.language,
                max_tasks=counting_tasks(discipline),
                max_home_works=len(discipline.works)
            )
        )
        session.commit()

def add_students_group(student_groups: list[StudentsGroup]) -> None:
    """
    Add student groups

    :param student_groups: list formatted data (pydantic-obj) StudentsGroup

    :return None:

    :raises DisciplineNotFoundException: If discipline is not found
    :raises GroupAlreadyExistException: If such a group already exists
    """
    session = Session()
    session.begin()
    try:
        for it in student_groups:
            group = Group(
                group_name=it.group_name,
                students = [Student(full_name=student_raw) 
                            for student_raw in it.students]
                )
            session.add(group)

            for discipline in it.disciplines_short_name:
                query = select(Discipline).where(
                    Discipline.short_name.ilike(f"%{discipline}%")
                )
                current_discipline = session.scalars(query).first()
                if current_discipline is None:
                    raise DisciplineNotFoundException(f"{discipline} нет в БД")

                empty_homework = create_homeworks(
                    disciplines_works_from_json(current_discipline.works)
                )
                for student in group.students:
                    student.homeworks.append(
                        AssignedDiscipline(
                            discipline_id=current_discipline.id,
                            home_work=homeworks_to_json(empty_homework)
                        )
                    )
                group.disciplines.append(current_discipline)
        session.commit()
    except DisciplineNotFoundException as ex:
        session.rollback()
        raise ex
    except IntegrityError as ex:
        session.rollback()
        raise GroupAlreadyExistException(f"{ex.params[0]} уже существует")
    finally:
        session.close()

def assign_teacher_to_discipline(teacher_id: int, discipline_id: int) -> None:
    """
    Assign the discipline to the teacher

    :param teacher_id: teacher Telegram ID
    :param discipline_id: discipline ID

    :return None:
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        teacher.disciplines.append(
            session.get(Discipline, discipline_id)
        )
        session.commit()

def get_not_assign_teacher_discipline(teacher_id: int) -> list[Discipline]:
    """
    Return all disciplines not assigned to the teacher

    :param teacher_id: teacher Telegram ID

    :return list[Discipline]: List of 'Discipline`s' not assigned to the teacher
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        ids_assigned_disciplines = [it.id for it in teacher.disciplines]
        query = select(Discipline).where(
            Discipline.id.not_in(ids_assigned_disciplines)
        )
        return session.scalars(query).all()

def delete_group(group_id: int) -> None:
    """
    Delete group from DB

    :param group_id: group ID

    :return None:
    """
    with Session() as session:
        group = session.get(Group, group_id)
        session.delete(group)
        session.commit()

def delete_discipline(discipline_id: int) -> None:
    """
    Delete discipline from DB

    :param discipline_id: discipline ID on DB

    :return None:
    """
    with Session() as session:
        discipline = session.get(Discipline, discipline_id)
        session.delete(discipline)
        session.commit()

def delete_student(student_id: int) -> None:
    """
    Delete student from DB
    
    :param student_id: student ID

    :return None:
    """
    with Session() as session:
        student = session.get(Student, student_id)
        session.delete(student)
        session.commit()

def delete_teacher(teacher_id: int) -> None:
    """
    Remove the teacher from the database

    :param teacher_id: teacher ID

    :return None:
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        session.delete(teacher)
        session.commit()

def delete_teacher_on_tg_id(teacher_telegram_id: int) -> None:
    """
    Remove the teacher from the database

    :param teacher_id: teacher Telegram ID

    :return None:
    """
    with Session() as session:
        query = delete(Teacher).where(Teacher.telegram_id == teacher_telegram_id)
        session.execute(query)
        session.commit()

def delete_chat(chat_id: int) -> None:
    """
    Delete chat from database

    :param chat_id: chat Telegram ID

    :return None:
    """
    with Session() as session:
        chat = session.get(Chat, chat_id)
        session.delete(chat)
        session.commit()

def get_all_disciplines() -> list[Discipline]:
    """
    Return the list of all disciplines

    :param: None

    :return list[Discipline]: list of disciplines (objects of 'Discipline' - class)
    """
    with Session() as session:
        return session.query(Discipline).all()

def get_discipline(discipline_id: int) -> Discipline:
    """
    Return specific discipline by ID

    :param discipline_id: discipline ID

    :return Discipline: object of 'Discipline'- class
    """
    with Session() as session:
        return session.get(Discipline, discipline_id)

def remote_start_db_fill(data: DbStartData) -> None:
    """
    Function for initial (starting) configuration of the system,
    by loading a json file, remotely

    :param data: data on subjects, students, groups and teachers, as well 
    as which subjects are assigned to whom and which teacher teaches them

    :return None:

    :raises DisciplineNotFoundException: discipline not found
    :raises DisciplineAlreadyExistException: discipline already exists
    :raises GroupAlreadyExistException: group with this name already exists
    :raises GroupNotFoundException: group with this name not found
    """
    session = Session()  # создаём объект сессии
    session.begin()  # начинаем транзакцию
    admin_default_tg = int(os.getenv("DEFAULT_ADMIN"))  # получаем Telegram ID админа
    disciplines: dict[str, Discipline] = {}  # создаём пустой словарь под имена дисциплин
    groups: dict[str, Group] = {}  # создаём пустой словарь под названия групп

    # начинаем процедуру TRY для парсинга json-файла
    try:
        # парсинг дисциплин
        for discipline in data.disciplines:
            if discipline.short_name in disciplines:
                raise DisciplineAlreadyExistException(f"{discipline.short_name} дублируется")
            dis = Discipline(
                full_name=discipline.full_name,
                short_name=discipline.short_name,
                path_to_test=discipline.path_to_test,
                path_to_answer=discipline.path_to_answer,
                works=disciplines_works_to_json(discipline),
                language=discipline.language,
                max_tasks=counting_tasks(discipline),
                max_home_works=len(discipline.works)
            )
            disciplines[discipline.short_name] = dis

        session.add_all(disciplines.values())
        session.flush()

        # парсинг групп
        for it in data.groups:
            group = Group(
                group_name=it.group_name,
                students=[
                    Student(full_name=student_raw)
                    for student_raw in it.students
                ]
            )
            groups[it.group_name] = group

            for name in it.disciplines_short_name:
                if name not in disciplines:
                    raise DisciplineNotFoundException(f"{name} нет в БД")

                empty_homework = create_homeworks(
                    disciplines_works_from_json(disciplines[name].works)
                )
                disciplines[name].groups.append(
                    groups[it.group_name]
                )

                for student in groups[it.group_name].students:
                    student.homeworks.append(
                        AssignedDiscipline(
                            discipline_id=disciplines[name].id,
                            home_work=homeworks_to_json(empty_homework)
                        )
                    )

        # парсинг преподавателей
        for it in data.teachers:
            teacher = Teacher(
                full_name=it.full_name,
                telegram_id=it.telegram_id
            )

            for tgr in it.assign_groups:
                if tgr not in groups:
                    raise GroupNotFoundException(f"Группа {tgr} не найдена")
                teacher.groups.append(groups[tgr])

            for tdis in it.assign_disciplines:
                if tdis not in disciplines:
                    raise DisciplineNotFoundException(f"Дисциплина {tdis} не найдена")
                teacher.disciplines.append(disciplines[tdis])

            if it.is_admin and teacher.telegram_id != admin_default_tg:
                session.add(
                    Admin(
                        telegram_id=teacher.telegram_id
                    )
                )
            session.add(teacher)

        # парсинг чатов
        for chat in data.chats:
            session.add(
                Chat(chat_id=chat)
            )
        session.commit()
    # блоки Except для отлова ошибок парсинга json-файла
    except DisciplineNotFoundException as ex:
        session.rollback()
        raise ex
    except DisciplineAlreadyExistException as daex:
        session.rollback()
        raise daex
    except GroupNotFoundException as gnfex:
        session.rollback()
        raise gnfex
    except IntegrityError as ex:
        session.rollback()
        raise GroupAlreadyExistException(f"{ex.params[0]} уже существует")
    # блок Finally для завершения сессии
    finally:
        session.close()

def switch_admin_mode_to_teacher(admin_id: int) -> None:
    """
    Switching admin mode to teacher mode in telegram chat menu
    
    :param admin_id: teacher Telegram ID

    :return None:
    """
    with Session() as session:
        admin = session.get(Admin, admin_id)
        admin.teacher_mode = True
        session.commit()
