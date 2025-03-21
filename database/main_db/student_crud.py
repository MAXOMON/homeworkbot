"""
This module contains various checking functions that are specific to students.
"""
from database.main_db.database import Session

from model.main_db.student import Student
from model.main_db.discipline import Discipline
#from model.main_db.assigned_discipline import AssignedDiscipline


def has_student(full_name: str) -> bool:
    """
    Check if a student already exists in the database.

    :param full_name: student Telegram ID

    :return bool: True IF already exists ELSE False
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).first()
        return student is not None

def is_student(telegram_id: int) -> bool:
    """
    Check if the user is a student.

    :param telegram_id: user Telegram ID

    :return bool: True IF user a student ELSE False
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        return student is not None

def set_telegram_id(full_name: str, telegram_id: int) -> None:
    """
    Set this telegram ID for this student

    :param full_name: student full name
    :param telegram_id: student Telegram ID

    :return None:
    """
    with Session() as session:
        session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).update(
            {Student.telegram_id: telegram_id}, synchronize_session="fetch"
        )
        session.commit()

def get_student_by_tg_id(telegram_id: int) -> Student:
    """
    Return the Student object by his telegram ID

    :param telegram_id: student Telegram ID

    :return: object of class Student
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        return student

def get_assign_disciplines(student_tg_id: int) -> list[Discipline]:
    """
    Get all the disciplines assigned to the student.

    :param student_tg_id: student Telegram ID

    :return list[Discipline]: list of objects of class Discipline
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == student_tg_id
        ).first()
        return student.group.disciplines
