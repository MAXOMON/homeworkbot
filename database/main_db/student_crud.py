"""
This module contains various checking functions that are specific to students.
"""
from database.main_db.database import Session
from model.main_db.discipline import Discipline
from model.main_db.group import Group
from model.main_db.student import Student




def has_student(full_name: str) -> bool:
    """
    Check if a student already exists in the database.

    :param full_name: student full name

    :return bool: True IF already exists ELSE False
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).first()
        return student is not None

def has_more_students(full_name: str) -> bool:
    """
    Check if there are such students in the database with the same full name.

    :param full_name: student full name

    :return bool: True IF already exists ELSE False
    """
    with Session() as session:
        students = session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).all()
        students = [student.telegram_id for student in students 
                    if student.telegram_id is None]
        return len(students) > 1

def get_groups_of_students_with_same_name(full_name: str) -> list[Group]:
    """
    Return a list of groups from the database in which students 
    with the same full name study

    :param full_name: student full name

    :return list[Group]: list of groups in which students 
        with the same full name study
    """
    with Session() as session:
        students = session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).all()
        return [student.group for student in students]

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
        ).where(
            Student.telegram_id.is_(None)
        ).update(
            {Student.telegram_id: telegram_id}, synchronize_session="fetch"
        )
        session.commit()

def set_telegram_id_on_group_id(full_name: str,
                                group_id: int,
                                telegram_id: int):
    """
    Set a telegram ID for a selected student of a specific group.

    :param full_name: student full name
    :param group_id: ID of the group in which the student studies
    :param telegram_id: student Telegram ID
    
    :return None:
    """
    with Session() as session:
        session.query(Student).filter(
            Student.full_name == full_name,
            Student.group_id == group_id
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
