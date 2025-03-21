"""
This module contains various checking functions that are specific to teachers.
"""
from sqlalchemy import and_, select
from database.main_db.database import Session
from model.main_db.admin import Admin
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student import Student
from model.main_db.teacher import Teacher


def is_teacher(telegram_id: int) -> bool:
    """
    Check if the user is a teacher

    :param telegram_id: user Telegram_ID

    :return bool: True IF is a theacher ELSE False
    """
    with Session() as session:
        teacher = session.query(Teacher).filter(
            Teacher.telegram_id == telegram_id
        ).first()
        return teacher is not None

def get_assign_group_discipline(
        teacher_tg_id: int, group_id: int) -> list[Discipline]:
    """
    Get a list of disciplines that are assigned to a teacher
    for a specific group

    :param teacher_tg_id: teacher Telegram ID
    :param group_id: group ID

    :return list[Discipline]: list of objects of class Discipline
    """
    with Session() as session:
        teacher = session.query(Teacher).filter(
            Teacher.telegram_id == teacher_tg_id
        ).first()

        teacher_disciplines = {it.short_name for it in teacher.disciplines}

        group = session.query(Group).filter(
            Group.id == group_id
        ).first()

        group_disciplines = {it.short_name for it in group.disciplines}

        return [it for it in teacher.disciplines
                if it.short_name in teacher_disciplines.intersection(
                    group_disciplines)]

def switch_teacher_mode_to_admin(teacher_tg_id: int) -> None:
    """
    Switch from teacher mode to administrator mode
    
    :param teacher_tg_id: teacher Тelegram ID

    :return None:
    """
    with Session() as session:
        admin = session.get(Admin, teacher_tg_id)
        admin.teacher_mode = False
        session.commit()

def get_assign_groups(teacher_tg_id: int) -> list[Group]:
    """
    Get a list of groups taught by this teacher

    :param teacher_tg_id: teacher Telegram ID

    :return list[Group]: list of objects of class Group
    """
    with Session() as session:
        smt = select(Teacher).where(
            Teacher.telegram_id == teacher_tg_id
        )
        teacher = session.scalars(smt).first()
        return teacher.groups

def get_teacher_disciplines(teacher_tg_id: int) -> list[Discipline]:
    """
    Get a list of disciplines assigned to a teacher

    :param teacher_tg_id: teacher Telegram ID

    :return list[Discipline]: list of objects of class Discipline
    """
    with Session() as session:
        smt = select(Teacher).where(
            Teacher.telegram_id == teacher_tg_id
        )
        teacher = session.scalars(smt).first()
        return teacher.disciplines

def get_auth_students(group_id: int) -> list[Student]:
    """
    Return the list of authenticated students

    :param group_id: students GROUP ID

    :return list[Student]: list of objects of class Student
    """
    with Session() as session:
        students = session.query(Student).filter(
            and_(
                Student.group_id == group_id,
                Student.telegram_id.is_not(None)
            )
        ).all()
        return students
