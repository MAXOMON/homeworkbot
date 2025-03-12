from database.main_db.database import Session

from model.main_db.student import Student
from model.main_db.discipline import Discipline
#from model.main_db.assigned_discipline import AssignedDiscipline


def has_student(full_name: str) -> bool:
    with Session() as session:
        student = session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).first()
        return student is not None

def is_student(telegram_id: int) -> bool:
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        return student is not None

def set_telegram_id(full_name: str, telegram_id: int) -> None:
    with Session() as session:
        session.query(Student).filter(
            Student.full_name.ilike(f"%{full_name}%")
        ).update(
            {Student.telegram_id: telegram_id}, synchronize_session="fetch"
        )
        session.commit()

def get_student_by_tg_id(telegram_id: int) -> Student:
    """
    Функция запроса студента по Telegram ID

    :param telegram_id: Telegram ID студента

    :return: объект класса Student
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == telegram_id
        ).first()
        return student

def get_assign_disciplines(student_tg_id: int) -> list[Discipline]:
    """
    Функция запрашивает все дисциплины, закреплённые за студентом

    :param student_tg_id: Telegram ID студента

    :return: список оъектов класса Discipline
    """
    with Session() as session:
        student = session.query(Student).filter(
            Student.telegram_id == student_tg_id
        ).first()
        return student.group.disciplines
