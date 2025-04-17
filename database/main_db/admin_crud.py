"""
Contains functions for adding, reading, 
changing and deleting data from the database, 
intended for the administrator of this system.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from database.main_db import common_crud
from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import DisciplineNotFoundException,\
    GroupAlreadyExistException, DisciplineAlreadyExistException,\
    GroupNotFoundException, ChatAlreadyExistException
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


async def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
    Check if this administrator has teacher functions disabled

    :param telegram_id: admin Telegram ID

    :return bool: True, if this administrator has teacher functions disabled
    """
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin is None:
            return False
        return not admin.teacher_mode

async def is_admin_with_teacher_mode(telegram_id: int) -> bool:
    """
    Check if this administrator has teacher privileges

    :param telegram_id: admin Telegram ID

    :return bool: True, if this administrator has teacher privileges
    """
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin is None:
            return False
        return admin.teacher_mode

async def is_admin(telegram_id: int) -> bool:
    """
    Check if this user is an administrator

    :param telegram_id: user Telegram ID

    :return bool: True if the user is an administrator
    """
    async with Session() as session:
        admin = await session.get(Admin, telegram_id)
        return admin is not None

async def is_admin_and_teacher(telegram_id: int) -> bool:
    """
    Check if this user is an administrator and a teacher

    :param telegram_id: user Telegram ID

    :return bool: True if the USER is an administrator and a teacher
    """
    _is_admin = await is_admin(telegram_id)
    _is_teacher = await is_teacher(telegram_id)
    return _is_admin and _is_teacher

async def add_chat(chat_id: int) -> None:
    """
    Add chat to database

    :param chat_id: chat Telegram ID

    :return None:
    """
    async with Session() as session:
        chats = await common_crud.get_chats()
        try:
            if chat_id in chats:
                raise ChatAlreadyExistException(f"Чат {chat_id} уже существует!")
            session.add(Chat(chat_id=chat_id))
            await session.commit()
        except ChatAlreadyExistException as cex:
            await session.rollback()
            raise cex

async def add_teacher(full_name: str, tg_id: int) -> None:
    """
    Add the teacher to the database

    :param full_name: teacher full name
    :param tg_id: teacher Telegram ID

    :return None:
    """
    async with Session() as session:
        session.add(Teacher(full_name=full_name, telegram_id=tg_id))
        await session.commit()

async def get_teachers() -> list[Teacher]:
    """
    Return the list of teachers

    :param None:

    :return list[Teacher]: list of teachers
    """
    async with Session() as session:
        result = await session.scalars(
            select(Teacher)
        )
        return result.all()

async def get_not_assign_teacher_groups(teacher_id: int) -> list[Group]:
    """
    Return the list of groups that are not assigned to the teacher

    :param teacher_id: teacher Telegram ID

    :return list[Group]: list of groups
    """
    async with Session() as session:
        teacher = await session.get(Teacher, teacher_id)
        teacher_groups = await getattr(teacher.awaitable_attrs, 'groups')
        ids_assigned_groups = [it.id for it in teacher_groups]
        result = await session.scalars(
            select(Group).where(Group.id.not_in(ids_assigned_groups))
            )
        return result.all()

async def assign_teacher_to_group(teacher_id: int, group_id: int) -> None:
    """
    Assign the teacher and group to the teacher_group table in the database

    :param teacher_id: teacher Telegram ID
    :param group_id: group ID

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            teacher = await session.get(Teacher, teacher_id)
            group = await session.get(Group, group_id)
            teacher_groups = await getattr(teacher.awaitable_attrs, 'groups')
            teacher_groups.append(group)
            await session.commit()



async def get_all_groups() -> list[Group]:
    """
    Return the list of all groups

    :param None:

    :return list[Group]: List of all groups
    """
    async with Session() as session:
        groups = await session.scalars(select(Group))
        return groups.all()

async def add_student(full_name: str, group_id: int) -> None:
    """
    Add the student to the database

    :param full_name: student full name
    :param group_id: group ID

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            group: Group = await session.get(Group, group_id)
            student = Student(
                full_name=full_name,
                group_id=group_id
            )
            group_students = await getattr(group.awaitable_attrs, 'students')
            group_students.append(student)
            #group.students.append(student)
            group_disciplines = await getattr(group.awaitable_attrs, 'disciplines')
            #for discipline in group.disciplines:
            for discipline in group_disciplines:
                empty_homework = create_homeworks(
                    disciplines_works_from_json(discipline.works)
                )
                student_homeworks = await getattr(student.awaitable_attrs, 'homeworks')
                #student.homeworks.append(
                student_homeworks.append(
                    AssignedDiscipline(
                        discipline_id=discipline.id,
                        home_work=homeworks_to_json(empty_homework)
                    )
                )
            await session.commit()

async def add_discipline(discipline: DisciplineWorksConfig) -> None:
    """
    Add discipline to the DB

    :param discipline: formatted data (pydantic-obj) DisciplineWorksConfig

    :return: None
    """
    async with Session() as session:
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
        await session.commit()

async def add_students_group(student_groups: list[StudentsGroup]) -> None:
    """
    Add student groups

    :param student_groups: list formatted data (pydantic-obj) StudentsGroup

    :return None:

    :raises DisciplineNotFoundException: If discipline is not found
    :raises GroupAlreadyExistException: If such a group already exists
    """
    async with Session() as session:
        async with session.begin():
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
                        current_discipline = await session.scalar(query)
                        if current_discipline is None:
                            raise DisciplineNotFoundException(f"{discipline} нет в БД")

                        empty_homework = create_homeworks(
                            disciplines_works_from_json(current_discipline.works)
                        )
                        group_students = await getattr(group.awaitable_attrs, 'students')
                        #for student in group.students:
                        for student in group_students:
                            student_homeworks = await getattr(student.awaitable_attrs, 'homeworks')
                            #student.homeworks.append(
                            student_homeworks.append(
                                AssignedDiscipline(
                                    discipline_id=current_discipline.id,
                                    home_work=homeworks_to_json(empty_homework)
                                )
                            )
                        group_disciplines = await getattr(group.awaitable_attrs, 'disciplines')
                        group_disciplines.append(current_discipline)
                        #group.disciplines.append(current_discipline)
                await session.commit()
            except DisciplineNotFoundException as ex:
                await session.rollback()
                raise ex
            except IntegrityError as ex:
                await session.rollback()
                raise GroupAlreadyExistException(f"{ex.params[0]} уже существует")

async def assign_teacher_to_discipline(teacher_id: int, discipline_id: int) -> None:
    """
    Assign the discipline to the teacher

    :param teacher_id: teacher Telegram ID
    :param discipline_id: discipline ID

    :return None:
    """
    async with Session() as session:
        teacher = await session.get(Teacher, teacher_id)
        disciplines = await getattr(teacher.awaitable_attrs, 'disciplines')
        discipline = await session.get(Discipline, discipline_id)
        disciplines.append(discipline)
        await session.commit()

async def get_not_assign_teacher_discipline(teacher_id: int) -> list[Discipline]:
    """
    Return all disciplines not assigned to the teacher

    :param teacher_id: teacher Telegram ID

    :return list[Discipline]: List of 'Discipline`s' not assigned to the teacher
    """
    async with Session() as session:
        teacher = await session.get(Teacher, teacher_id)
        disciplines = await getattr(teacher.awaitable_attrs, 'disciplines')
        ids_assigned_disciplines = [it.id for it in disciplines]
        query = select(Discipline).where(
            Discipline.id.not_in(ids_assigned_disciplines)
        )
        result = await session.scalars(query)
        return result.all()

async def delete_group(group_id: int) -> None:
    """
    Delete group from DB

    :param group_id: group ID

    :return None:
    """
    async with Session() as session:
        group = await session.get(Group, group_id)
        await session.delete(group)
        await session.commit()

async def delete_discipline(discipline_id: int) -> None:
    """
    Delete discipline from DB

    :param discipline_id: discipline ID on DB

    :return None:
    """
    async with Session() as session:
        discipline = await session.get(Discipline, discipline_id)
        await session.delete(discipline)
        await session.commit()

async def delete_student(student_id: int) -> None:
    """
    Delete student from DB
    
    :param student_id: student ID

    :return None:
    """
    async with Session() as session:
        student = await session.get(Student, student_id)
        await session.delete(student)
        await session.commit()

async def delete_teacher(teacher_id: int) -> None:
    """
    Remove the teacher from the database

    :param teacher_id: teacher ID

    :return None:
    """
    async with Session() as session:
        teacher = await session.get(Teacher, teacher_id)
        await session.delete(teacher)
        await session.commit()

async def delete_teacher_on_tg_id(teacher_telegram_id: int) -> None:
    """
    Remove the teacher from the database

    :param teacher_id: teacher Telegram ID

    :return None:
    """
    async with Session() as session:
        teacher = await session.scalar(
            select(Teacher).where(Teacher.telegram_id == teacher_telegram_id)
        )
        await session.delete(teacher)
        await session.commit()

async def delete_chat(chat_id: int) -> None:
    """
    Delete chat from database

    :param chat_id: chat Telegram ID

    :return None:
    """
    async with Session() as session:
        chat = await session.get(Chat, chat_id)
        await session.delete(chat)
        await session.commit()

async def get_all_disciplines() -> list[Discipline]:
    """
    Return the list of all disciplines

    :param: None

    :return list[Discipline]: list of disciplines (objects of 'Discipline' - class)
    """
    async with Session() as session:
        result = await session.scalars(select(Discipline))
        return result.all()

async def get_discipline(discipline_id: int) -> Discipline:
    """
    Return specific discipline by ID

    :param discipline_id: discipline ID

    :return Discipline: object of 'Discipline'- class
    """
    async with Session() as session:
        return await session.get(Discipline, discipline_id)

async def switch_admin_mode_to_teacher(admin_id: int) -> None:
    """
    Switching admin mode to teacher mode in telegram chat menu
    
    :param admin_id: teacher Telegram ID

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            stmt = select(Admin).where(Admin.telegram_id == admin_id)
            admin = await session.scalar(stmt)
            admin.teacher_mode = True
            await session.commit()

async def remote_start_db_fill(data: DbStartData, session: AsyncSession) -> None:
    """
    Function for initial (starting) configuration of the system,
    by loading a json file, remotely

    :param data: data on subjects, students, groups and teachers, as well 
    as which subjects are assigned to whom and which teacher teaches them
    :param session: AsyncSession object for ACID operations

    :return None:

    :raises DisciplineNotFoundException: discipline not found
    :raises DisciplineAlreadyExistException: discipline already exists
    :raises GroupAlreadyExistException: group with this name already exists
    :raises GroupNotFoundException: group with this name not found
    """
    admin_default_tg = int(os.getenv("DEFAULT_ADMIN"))
    disciplines: dict[str, Discipline] = {}
    groups: dict[str, Group] = {}

    async def add_disciplines(disciplines_data: list[DisciplineWorksConfig],
                                session: AsyncSession,
                                disciplines: dict[str, Discipline]) -> None:
        """
        Add disciplines to the database.

        :param disciplines_data: formatted data (pydantic-obj) DisciplineWorksConfig
        :param session: An instance of AsyncSession, 
            for correct asynchronous operation of adding data to the database.
        :disciplines: Dictionary with names of disciplines 
            and their ORM table objects.
        """
        async with session.begin():
            try:
                for discipline in disciplines_data:
                    if discipline.short_name in disciplines:
                        raise DisciplineAlreadyExistException(
                            f"{discipline.short_name} дублируется")

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
                await session.commit()
            except DisciplineAlreadyExistException as daex:
                await session.rollback()
                raise daex

    async def add_groups(groups_data: list[StudentsGroup],
                            session: AsyncSession,
                            disciplines: dict[str, Discipline],
                            groups: dict[str, Group]) -> None:
        """
        Add groups to the database.

        :param groups_data: List of student groups.
        :param session: An instance of AsyncSession, 
            for correct asynchronous operation of adding data to the database.
        :param disciplines: Dictionary with names of disciplines 
            and their ORM table objects.
        :param groups: Dictionary with names of groups 
            and their ORM table objects.
        """
        async with session.begin():
            try:
                for it in groups_data:
                    group = Group(
                        group_name=it.group_name,
                        students=[Student(full_name=student_raw) 
                                    for student_raw in it.students]
                                    )
                    session.add(group)
                    groups[it.group_name] = group
                    for name in it.disciplines_short_name:
                        if name not in disciplines:
                            raise DisciplineNotFoundException(f"{name} нет в БД")

                        works_ = disciplines[name].works
                        empty_homework = create_homeworks(
                            disciplines_works_from_json(works_)
                        )
                        groups_ = await getattr(disciplines[name].awaitable_attrs, 'groups')
                        groups_.append(group)
                        for student in group.students:
                            homeworks = await getattr(student.awaitable_attrs, 'homeworks')
                            homeworks.append(
                                AssignedDiscipline(
                                    discipline_id=disciplines[name].id,
                                    home_work=homeworks_to_json(empty_homework)
                                )
                            )
                await session.commit()
            except DisciplineNotFoundException as ex:
                await session.rollback()
                raise ex
            except IntegrityError as ex:
                await session.rollback()
                raise GroupAlreadyExistException(f"{ex.params[0]} уже существует")

    async def add_chats(chats_data: list[int], session: AsyncSession) -> None:
        """
        Add chats to the database.

        :param chats_data: list of telegram IDs of added chats.
        :param session: An instance of AsyncSession, 
            for correct asynchronous operation of adding data to the database.
        """
        async with session.begin():
            try:
                chats = await common_crud.get_chats()
                for chat in chats_data:
                    if chat in chats:
                        raise ChatAlreadyExistException(f"Чат {chat} уже существует!")
                    chat_obj = Chat(chat_id=int(chat))
                    session.add(chat_obj)
                await session.commit()
            except ChatAlreadyExistException as cex:
                await session.rollback()
                raise cex

    async def add_teachers(teachers_data: list[Teacher],
                           session: AsyncSession,
                           groups: dict[str, Group],
                           disciplines: dict[str, Discipline],
                           admin_default_tg: int) -> None:
        """
        Add teachers to the database.

        :param teachers_data: list of teachers
        :param session: An instance of AsyncSession, 
            for correct asynchronous operation of adding data to the database.
        :param groups: Dictionary with names of groups 
            and their ORM table objects.
        :param disciplines: Dictionary with names of disciplines
            and their ORM table objects.
        :param admin_default_tg: Admin Telegram ID
        """
        async with session.begin():
            try:
                for it in teachers_data:
                    teacher = Teacher(
                        full_name=it.full_name,
                        telegram_id=it.telegram_id
                    )

                    for tgr in it.assign_groups:
                        if tgr not in groups:
                            raise GroupNotFoundException(f"Группа {tgr} не найдена")
                        teacher_groups = await getattr(teacher.awaitable_attrs, 'groups')
                        teacher_groups.append(groups[tgr])

                    for tdis in it.assign_disciplines:
                        if tdis not in disciplines:
                            raise DisciplineNotFoundException(f"Дисциплина {tdis} не найдена")
                        teacher_disciplines = await getattr(teacher.awaitable_attrs, 'disciplines')
                        teacher_disciplines.append(disciplines[tdis])

                    if it.is_admin and teacher.telegram_id != admin_default_tg:
                        session.add(
                            Admin(
                                telegram_id=teacher.telegram_id
                            )
                        )
                    session.add(teacher)
                await session.commit()
            except GroupNotFoundException as gnfex:
                await session.rollback()
                raise gnfex
            except DisciplineNotFoundException as ex:
                await session.rollback()
                raise ex

    try:
        await add_disciplines(data.disciplines, session, disciplines)
        await add_groups(data.groups, session, disciplines, groups)
        await add_chats(data.chats, session)
        await add_teachers(data.teachers, session, groups, disciplines, admin_default_tg)
    except Exception as e:
        await session.rollback()
