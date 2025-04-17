"""
Contains functions for adding, reading, 
changing and deleting data from the database,
intended for the normal purposes of this system
"""
import json
from datetime import datetime
from enum import Enum
from sqlalchemy import exists, and_
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from database.main_db import admin_crud
from database.main_db.database import Session
from model.main_db.admin import Admin
from model.main_db.student import Student
from model.main_db.teacher import Teacher
from model.main_db.teacher_group import association_teacher_to_group
from model.main_db.chat import Chat
from model.main_db.group import Group
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student_ban import StudentBan
from model.pydantic.queue_in_raw import QueueInRaw
from model.queue_db.queue_in import QueueIn
from testing_tools.logger.report_model import LabReport
import utils.homeworks_utils as utils


class UserEnum(Enum):
    """For simplified user classification and verification"""
    ADMIN = 0
    TEACHER = 1
    STUDENT = 2
    UNKNOWN = 3


async def user_verification(telegram_id: int) -> UserEnum:
    """
    Check who this user is

    :param telegram_id: user Telegram ID

    :return UserEnum: value represented by the UserEnum class (Enum)
    """
    async with Session() as session:
        user = await session.get(Admin, telegram_id)
        if user is not None:
            return UserEnum.ADMIN
        user = await session.scalar(
            select(Teacher).where(Teacher.telegram_id == telegram_id)
        )
        if user is not None:
            return UserEnum.TEACHER
        user = await session.scalar(
            select(Student).where(Student.telegram_id == telegram_id)
        )
        if user is not None:
            return UserEnum.STUDENT
        return UserEnum.UNKNOWN

async def get_chats() -> list[int]:
    """
    Return the list of chats in which the bot will be available

    :param None:

    :return list[int]: list of chats from DB in integer list format
    
    """
    async with Session() as session:
        chats = await session.scalars(
            select(Chat)
        )
        return [it.chat_id for it in chats.all()]

async def get_group_disciplines(group_id: int) -> list[Discipline]:
    """
    Return all disciplines of the selected group

    :param group_id: group ID from DB

    :return list[Discipline]: list of all disciplines assigned to the selected
        group from the database, 
        in the format of a list of objects of the Discipline class
    """
    async with Session() as session:
        group = await session.get(Group, group_id)
        disciplines = await getattr(group.awaitable_attrs, 'disciplines')
        return disciplines

async def ban_student(telegram_id: int) -> None:
    """
    Ban this student
    
    :param telegram_id: student Telegram ID

    :return: None
    """
    async with Session() as session:
        session.add(StudentBan(telegram_id=telegram_id))
        await session.commit()

async def unban_student(telegram_id: int) -> None:
    """
    Remove this student from the ban list

    :param telegram_id: student Telegram ID

    :return None:
    """
    async with Session() as session:
        student = await session.scalar(
            select(StudentBan).where(StudentBan.telegram_id == telegram_id)
        )
        await session.delete(student)
        await session.commit()

async def is_ban(telegram_id: int) -> bool:
    """
    Check if this student is on the ban list

    :param telegram_id: student Telegram ID

    :return bool: True IF student is banned ELSE False
    """
    async with Session() as session:
        tg_id = await session.scalar(
            select(StudentBan).where(
                StudentBan.telegram_id == telegram_id
            )
        )
        return tg_id is not None

async def get_ban_students(teacher_telegram_id: int) -> list[Student]:
    """
    Return all banned students of the selected teacher.
    Request is executed by administrator.

    :param teacher_telegram_id: teacher Telegram ID

    :return list[Student]: list of banned students from group selected teacher
        from database in the format list of objects of the class Student
    """
    async with Session() as session:
        if await admin_crud.is_admin_no_teacher_mode(teacher_telegram_id):
            result = await session.scalars(
                select(Student).where(
                    exists().where(
                        StudentBan.telegram_id == Student.telegram_id)
            ))
            return result.all()
        else:
            query = select(Student).where(
                exists().where(StudentBan.telegram_id == Student.telegram_id)
            ).join(
                Group,
                Student.group_id == Group.id
            ).join(
                association_teacher_to_group,
                association_teacher_to_group.c.group_id == Group.id
            ).join(
                Teacher,
                association_teacher_to_group.c.teacher_id == Teacher.id
            ).where(
                Teacher.telegram_id == teacher_telegram_id
            )
            result = await session.scalars(query)
            return result.all()

async def get_students_from_group_for_ban(group_id: int) -> list[Student]:
    """
    Return the all students from group, available for ban.

    :param group_id: group ID from DB

    :return list[Student]: list of students from group, available for ban
        from database in the format list of objects of the class Student
    """
    async with Session() as session:
        students = await session.scalars(
            select(Student).options(
                joinedload(Student.group)
                ).filter(
                    and_(
                        Student.group_id == group_id,
                        Student.telegram_id.is_not(None),
                        ~exists().where(
                            StudentBan.telegram_id == Student.telegram_id
                            )
            )
        ))
        return students.all()

async def get_students_from_group(group_id: int) -> list[Student]:
    """
    Return all students in this group

    :param group_id: group ID from DB

    :return list[Student]: list of students from group 
        from a database in the format list of objects of the class Student
    """
    async with Session() as session:
        stmt = (
            select(Group)
            .options(selectinload(Group.students))
            .where(Group.id == group_id)
        )
        group = await session.scalar(stmt)
        if group is None:
            return []
        students = await getattr(group.awaitable_attrs, 'students')
        return students

async def get_group(group_id: int) -> Group:
    """
    Return group from database

    :param group_id: group ID from DB

    :return Group: group record from the database in the
        format of the Group class object
    """
    async with Session() as session:
        result = await session.get(Group, group_id)
        return result

async def get_discipline(discipline_id: int) -> Discipline:
    """
    Return the discipline from database

    :param discipline_id: discipline ID from DB

    :return Discipline: discipline record from the database in the
        format of the Discipline class object
    """
    async with Session() as session:
        result = await session.get(Discipline, discipline_id)
        return result

async def get_disciplines_assigned_to_student(
        student_id: int, discipline_id: int
        ) -> AssignedDiscipline:
    """
    Return the discipline assigned to the student

    :param student_id: student ID from DB
    :param discipline_id: discipline ID from DB

    :return AssignedDiscipline: assigned_discipline record from the database
        in the format of the AssignedDiscipline class object
    """
    async with Session() as session:
        stmt = select(AssignedDiscipline).where(
            AssignedDiscipline.discipline_id == discipline_id,
            AssignedDiscipline.student_id == student_id
        )
        assigned_disciplines = await session.scalar(stmt)
        return assigned_disciplines

async def get_student_from_id(student_id: int) -> Student:
    """
    Return the student by his ID
    
    :param student_id: student ID on DB
    
    :return Student: student record from the database 
        in the format of the Student class object
    """
    async with Session() as session:
        student = await session.scalar(
            select(Student).where(Student.id == student_id)
            )
        return student

async def write_test_result(lab_report: LabReport, input_record: QueueIn) -> None:
    """
    Record the test results.

    IF the work is submitted on time, 
    then a full score is recorded ELSE result / 2

    :param lab_report: report on the results of testing the tasks of the work
    :param input_record: source data sent for testing

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            task_raw = QueueInRaw(**json.loads(input_record.data))

            student = await session.scalar(
                select(Student).where(Student.telegram_id == input_record.telegram_id)
            )

            assig_discipline = await session.scalar(
                select(AssignedDiscipline).where(
                    AssignedDiscipline.student_id == student.id,
                    AssignedDiscipline.discipline_id == task_raw.discipline_id
                )
            )

            hwork = utils.homeworks_from_json(assig_discipline.home_work)

            lab = None
            for it in hwork.home_works:
                if lab_report.lab_id == it.number:
                    lab = it
                    break

            task_done = 0
            for task in lab.tasks:
                task_done += 1 if task.is_done else 0
                for task_result in lab_report.tasks:
                    if task.number == task_result.task_id:
                        task.amount_tries += 1
                        task.last_try_time = task_result.time
                        if not task.is_done and task_result.status:
                            task.is_done = True
                            task_done += 1

            lab.tasks_completed = task_done

            too_slow = False
            if (task_done == len(lab.tasks)) and not lab.is_done:
                end_time = datetime.now()
                lab.end_time = end_time
                lab.is_done = True
                if lab.deadline < end_time.date():
                    too_slow = True

                discipline = await session.scalar(
                    select(Discipline).where(Discipline.id == assig_discipline.discipline_id)
                )
                scale_point = 100.0 / discipline.max_tasks
                lab_points = task_done * scale_point
                if too_slow:
                    lab_points *= 0.5

                assig_discipline.point += lab_points
            assig_discipline.home_work = utils.homeworks_to_json(hwork)
            await session.commit()
