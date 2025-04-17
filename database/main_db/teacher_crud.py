"""
This module contains various checking functions that are specific to teachers.
"""
from sqlalchemy.future import select
from database.main_db.database import Session
from model.main_db.admin import Admin
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student import Student
from model.main_db.teacher import Teacher


async def is_teacher(telegram_id: int) -> bool:
    """
    Check if the user is a teacher

    :param telegram_id: user Telegram_ID

    :return bool: True IF is a theacher ELSE False
    """
    async with Session() as session:
        teacher = await session.scalar(
            select(Teacher).where(
                Teacher.telegram_id == telegram_id
            )
        )
        return teacher is not None

async def get_assign_group_discipline(
        teacher_tg_id: int, group_id: int) -> list[Discipline]:
    """
    Get a list of disciplines that are assigned to a teacher
    for a specific group

    :param teacher_tg_id: teacher Telegram ID
    :param group_id: group ID

    :return list[Discipline]: list of objects of class Discipline
    """
    async with Session() as session:
        teacher = await session.scalar(
            select(Teacher).where(
                Teacher.telegram_id == teacher_tg_id
            )
        )
        disciplines_from_teacher = await getattr(teacher.awaitable_attrs, 'disciplines')
        teacher_disciplines = {it.short_name for it in disciplines_from_teacher}

        group = await session.get(Group, group_id)
        disciplines_from_group = await getattr(group.awaitable_attrs, 'disciplines')
        group_disciplines = {it.short_name for it in disciplines_from_group}

        return [it for it in disciplines_from_teacher
                if it.short_name in teacher_disciplines.intersection(
                    group_disciplines)]

async def switch_teacher_mode_to_admin(teacher_tg_id: int) -> None:
    """
    Switch from teacher mode to administrator mode
    
    :param teacher_tg_id: teacher Тelegram ID

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            admin = await session.get(Admin, teacher_tg_id)
            admin.teacher_mode = False
            await session.commit()

async def get_assign_groups(teacher_tg_id: int) -> list[Group]:
    """
    Get a list of groups taught by this teacher

    :param teacher_tg_id: teacher Telegram ID

    :return list[Group]: list of objects of class Group
    """
    async with Session() as session:
        smt = select(Teacher).where(
            Teacher.telegram_id == teacher_tg_id
        )
        teacher = await session.scalar(smt)
        groups = await getattr(teacher.awaitable_attrs, 'groups')
        return groups

async def get_teacher_disciplines(teacher_tg_id: int) -> list[Discipline]:
    """
    Get a list of disciplines assigned to a teacher

    :param teacher_tg_id: teacher Telegram ID

    :return list[Discipline]: list of objects of class Discipline
    """
    async with Session() as session:
        smt = select(Teacher).where(
            Teacher.telegram_id == teacher_tg_id
        )
        teacher = await session.scalar(smt)
        disciplines = await getattr(teacher.awaitable_attrs, 'disciplines')
        return disciplines

async def get_auth_students(group_id: int) -> list[Student]:
    """
    Return the list of authenticated students

    :param group_id: students GROUP ID

    :return list[Student]: list of objects of class Student
    """
    async with Session() as session:
        students = await session.scalars(
            select(Student).where(
                Student.group_id == group_id,
                Student.telegram_id.is_not(None)
            )
        )
        return students.all()
