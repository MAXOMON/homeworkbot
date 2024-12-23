import os
from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import DisciplineNotFoundException, GroupAlreadyExistException, \
    DisciplineAlreadyExistException, GroupNotFoundException

from sqlalchemy.exc import IntegrityError

from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.teacher_group import TeacherGroup
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student
from utils.disciplines_utils import disciplines_works_from_json, disciplines_works_to_json, counting_tasks
from utils.homeworks_utils import create_homeworks, homeworks_to_json
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup
from model.main_db.teacher_discipline import TeacherDiscipline
from model.pydantic.db_start_data import DbStartData


def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
    Функция проверяет, не имеет ли администратор
    привилегии преподавателя

    :param telegram_id: Telegram ID пользователя

    :return: True, если администратор не имеет привилегии преподавателя
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return not admin.teacher_mode


def is_admin_with_teacher_mode(telegram_id: int) -> bool:
    """
    Функция проверяет, имеет ли администратор
    привилегии преподавателя

    :param telegram_id: Telegram ID пользователя

    :return: True, если администратор имеет привилегии преподавателя
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        if admin is None:
            return False
        return admin.teacher_mode
    

def is_admin(telegram_id: int) -> bool:
    """
    Функция проверяет, является ли пользователь администратором

    :param telegram_id: Telegram ID пользователя

    :return: True, если пользователь является администратором
    """
    with Session() as session:
        admin = session.query(Admin).get(telegram_id)
        return admin is not None


def is_admin_and_teacher(telegram_id: int) -> bool:
    """
    Функция проверяет, является ли пользователь администратором и преподавателем

    :param telegram_id: Telegram ID пользователя

    :return: True, если пользователь является администратором и преподавателем
    """
    _is_admin = is_admin(telegram_id)
    _is_teacher = is_teacher(telegram_id)
    return _is_admin and _is_teacher


def add_chat(chat_id: int) -> None:
    """
    Функция добавляет чат в базу данных

    :param chat_id: Telegram ID чата
    """
    with Session() as session:
        session.add(Chat(chat_id=chat_id))
        session.commit()


def add_teacher(full_name: str, tg_id: int) -> None:
    """
    Функция добавляет преподавателя в базу данных

    :param full_name: ФИО преподавателя
    :param tg_id: Telegram ID преподавателя

    :return: None
    """
    with Session() as session:
        session.add(Teacher(full_name=full_name, telegram_id=tg_id))
        session.commit()


def get_teachers() -> list[Teacher]:
    """
    Функция возвращает список преподавателей

    :return: Список преподавателей
    """
    with Session() as session:
        return session.query(Teacher).all()
    

def get_not_assign_teacher_groups(teacher_id: int) -> list[Group]:
    """
    Функция возвращает список групп, которые не назначены преподавателю

    :param teacher_id: Telegram ID преподавателя

    :return: Список групп, не назначенных преподавателю
    """
    with Session() as session:
        assign_group = session.query(TeacherGroup).filter(
            TeacherGroup.teacher_id == teacher_id
        )
        assign_group = [it.group_id for it in assign_group]
        not_assign_group = session.query(Group).filter(
            Group.id.not_in(assign_group)
        ).all()
        return not_assign_group
    

def assign_teacher_to_group(teacher_id: int, group_id: int) -> None:
    """
    Функция добавляет преподавателя и группу в таблицу teacher_group в базу данных

    :param teacher_id: Telegram ID преподавателя
    :param group_id: Telegram ID группы

    :return: None
    """
    with Session() as session:
        session.add(TeacherGroup(teacher_id=teacher_id, group_id=group_id))
        session.commit()


def get_all_groups() -> list[Group]:
    """
    Функция возвращает список всех групп

    :return: Список всех групп
    """
    with Session() as session:
        return session.query(Group).all()
    

def add_student(full_name: str, group_id: int, discipline_id: int):
    """
    Функция добавляет студента в базу данных

    :param full_name: ФИО студента
    :param group_id: Telegram ID группы
    :param discipline_id: Telegram ID дисциплины

    :return: None
    """
    session = Session()
    student = Student(full_name=full_name, group=group_id)
    session.add(student)
    session.flush()
    discipline: Discipline = session.query(Discipline).get(discipline_id)
    empty_homework = create_homeworks(
        disciplines_works_from_json(discipline.works)
    )
    session.add(
        AssignedDiscipline(
            student_id=student.id,
            discipline_id=discipline_id,
            home_work=homeworks_to_json(empty_homework)
        )
    )
    session.commit()
    session.close()


def add_discipline(discipline: DisciplineWorksConfig) -> None:
    """
        Функция добавляет дисциплину в БД

        :param discipline: Дисциплина

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
    Функция добавляет группы студентов

    :param student_groups: Список с параментрами групп

    :raises DisciplineNotFoundException: Если дисциплина не найдена
    :raises GroupAlreadyExistException: Если такая группа уже существует

    :return: None
    """
    session = Session()
    session.begin()
    try:
        for it in student_groups:
            group = Group(group_name=it.group_name)
            session.add(group)
            session.flush()
            students = [Student(full_name=student_raw, group=group.id) for student_raw in it.students]
            session.add_all(students)
            session.flush()
            for discipline in it.disciplines_short_name:
                current_discipline = session.query(Discipline).filter(
                    Discipline.short_name.ilike(f"%{discipline}%")
                ).first()
                if current_discipline is None:
                    raise DisciplineNotFoundException(f"{discipline} нет в БД")
                
                empty_homework = create_homeworks(
                    disciplines_works_from_json(current_discipline.works)
                )
                session.add_all(
                    [
                        AssignedDiscipline(
                            student_id=student.id,
                            discipline_id=current_discipline.id,
                            home_work=homeworks_to_json(empty_homework)
                    ) for student in students]
                )
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
    Функция назначает преподавателю дисциплину

    :param teacher_id: Telegram ID преподавателя
    :param discipline_id: ID дисциплины

    :return: None
    """
    with Session() as session:
        session.add(TeacherDiscipline(teacher_id=teacher_id, discipline_id=discipline_id))
        session.commit()


def get_not_assign_teacher_discipline(teacher_id: int) -> list[Discipline]:
    """
    Функция возвращает не присвоенные преподавателю дисциплины

    :param teacher_id: Telegram ID преподавателя

    :return: Список не присвоенных преподавателю дисциплин
    """
    with Session() as session:
        assign_discipline = session.query(TeacherDiscipline).filter(
            TeacherDiscipline.teacher_id == teacher_id
        )
        assign_discipline_id = [it.discipline_id for it in assign_discipline]
        not_assign_discipline = session.query(Discipline).filter(
            Discipline.id.not_in(assign_discipline_id)
        ).all()

        return not_assign_discipline


def delete_group(group_id: int) -> None:
    """
    Функция удаляет группу из БД

    :param group_id: ID группы

    :return: None
    """
    with Session() as session:
        session.query(Group).filter(
            Group.id == group_id
        ).delete(synchronize_session="fetch")
        session.query(TeacherGroup).filter(
            TeacherGroup.group_id == group_id
        ).delete(synchronize_session="fetch")

        students = session.query(Student).filter(Student.group == group_id).all()

        if not students:
            session.commit()
            return
        students_id = [it.id for it in students]
        session.query(AssignedDiscipline).filter(
            AssignedDiscipline.student_id.in_(students_id)
        ).delete(synchronize_session="fetch")
        session.query(Student).filter(
            Student.group == group_id
        ).delete(synchronize_session="fetch")
        session.commit()


def delete_student(student_id: int) -> None:
    """
    Функция удаляет студента из БД
    
    :param student_id: ID студента

    :return: None
    """
    with Session() as session:
        session.query(Student).filter(
            Student.id == student_id
        ).delete(synchronize_session="fetch")
        session.query(AssignedDiscipline).filter(
            AssignedDiscipline.student_id == student_id
        ).delete(synchronize_session="fetch")
        session.commit()


def delete_teacher(teacher_id: int) -> None:
    """
    Функция удаляет преподавателя из БД

    :param teacher_id: ID преподавателя

    :return: None
    """
    with Session() as session:
        session.query(Teacher).filter(
            Teacher.id == teacher_id
        ).delete(synchronize_session="fetch")

        session.query(TeacherGroup).filter(
            TeacherGroup.teacher_id == teacher_id
        ).delete(synchronize_session="fetch")

        session.query(TeacherDiscipline).filter(
            TeacherDiscipline.teacher_id == teacher_id
        ).delete(synchronize_session="fetch")
        
        session.commit()


def get_all_disciplines() -> list[Discipline]:
    """
        Функция возвращает список всех дисциплин

        :param: None

        :return: Список дисциплин (объекты класса 'Discipline')
    """
    with Session() as session:
        return session.query(Discipline).all()


def get_discipline(discipline_id: int) -> Discipline:
    """
        Функция возвращает конкретную дисциплину по ID

        :param discipline_id: ID дисциплины

        :return: Объект класса 'Discipline'
    """
    with Session() as session:
        return session.query(Discipline).get(discipline_id)


def remote_start_db_fill(data: DbStartData) -> None:
    """
        Функция для начальной (стартовой) настройки конфигурации системы, 
        путём загрузки json-файла, удалённо

        :param data: данные по предметам, студентам, группам и преподавателям,
        а также какие дисциплины кому назначены и какой преподаватель их ведёт

        :raises DisciplineNotFoundException: дисциплина не найдена
        :raises DisciplineAlreadyExistException: дисциплина уже существует
        :raises GroupAlreadyExistException: группа с таким названием уже существует
        :raises GroupNotFoundException: группа с таким названием не найдена

        :return: None
    """
    session = Session()  # создаём объект сессии
    session.begin()  # начинаем транзакцию
    admin_default_tg = int(os.getenv("DEFAULT_ADMIN"))  # получаем Telegram ID админа
    dis_short_names = {}  # создаём пустой словарь под имена дисциплин
    groups_name = {}  # создаём пустой словарь под названия групп

    # начинаем процедуру TRY для парсинга json-файла
    try:
        # парсинг дисциплин
        for discipline in data.disciplines:
            if discipline.short_name in dis_short_names:
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
            session.add(dis)
            session.flush()
            dis_short_names[discipline.short_name] = dis.id
        
        # парсинг групп
        for it in data.groups:
            group = Group(group_name=it.group_name)
            session.add(group)
            session.flush()
            groups_name[it.group_name] = group.id

            students = [
                Student(
                    full_name=student_raw,
                    group=group.id
                ) for student_raw in it.students
            ]
            session.add_all(students)
            session.flush()

            for discipline in it.disciplines_short_name:
                current_discipline = session.query(Discipline).filter(
                    Discipline.short_name.ilike(f"%{discipline}%")
                ).first()
                if current_discipline is None:
                    raise DisciplineNotFoundException(f"{discipline} нет в БД")
                
                empty_homework = create_homeworks(
                    disciplines_works_from_json(current_discipline.works)
                )
                session.add_all([
                    AssignedDiscipline(
                        student_id=student.id,
                        discipline_id=current_discipline.id,
                        home_work=homeworks_to_json(empty_homework)
                    ) for student in students]
                ) 
        # парсинг преподавателей
        for it in data.teachers:
            teacher = Teacher(
                full_name=it.full_name,
                telegram_id=it.telegram_id
            )
            session.add(teacher)
            session.flush()
            for tgr in it.assign_groups:
                if tgr not in groups_name:
                    raise GroupNotFoundException(f"Группа {tgr} не найдена")
                session.add(
                    TeacherGroup(
                        teacher_id=teacher.id,
                        group_id=groups_name[tgr]
                    )
                )
            
            for tdis in it.assign_disciplines:
                if tdis not in dis_short_names:
                    raise DisciplineNotFoundException(f"Дисциплина {tdis} не найдена")
                session.add(
                    TeacherDiscipline(
                        teacher_id=teacher.id,
                        discipline_id=dis_short_names[tdis]
                    )
                )
            
            if it.is_admin and teacher.telegram_id != admin_default_tg:
                session.add(
                    Admin(
                        telegram_id=teacher.telegram_id
                    )
                )
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
    with Session() as session:
        session.query(Admin).filter(
            Admin.telegram_id == admin_id
        ).update(
            {"teacher_mode": True}
        )
        session.commit()
