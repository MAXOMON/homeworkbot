import os

from sqlalchemy import delete, select
from database.main_db.database import Session
from database.main_db.teacher_crud import is_teacher
from database.main_db.crud_exceptions import DisciplineNotFoundException, GroupAlreadyExistException, \
    DisciplineAlreadyExistException, GroupNotFoundException

from sqlalchemy.exc import IntegrityError

from model.main_db.admin import Admin
from model.main_db.chat import Chat
from model.main_db.teacher import Teacher
from model.main_db.group import Group
from model.main_db.assigned_discipline import AssignedDiscipline
from model.main_db.discipline import Discipline
from model.main_db.student import Student
from utils.disciplines_utils import disciplines_works_from_json, disciplines_works_to_json, counting_tasks
from utils.homeworks_utils import create_homeworks, homeworks_to_json
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup
from model.pydantic.db_start_data import DbStartData


def is_admin_no_teacher_mode(telegram_id: int) -> bool:
    """
    Функция проверяет, не имеет ли администратор
    привилегии преподавателя

    :param telegram_id: Telegram ID пользователя

    :return: True, если администратор не имеет привилегии преподавателя
    """
    with Session() as session:
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
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
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
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
        admin = session.get(Admin, telegram_id)
        #admin = session.query(Admin).get(telegram_id)
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
    Функция добавляет преподавателя и группу в таблицу teacher_group в базу данных

    :param teacher_id: Telegram ID преподавателя
    :param group_id: Telegram ID группы
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        teacher.groups.append(
            session.get(Group, group_id)
        )
        session.commit()


def get_all_groups() -> list[Group]:
    """
    Функция возвращает список всех групп

    :return: Список всех групп
    """
    with Session() as session:
        return session.query(Group).all()
    

def add_student(full_name: str, group_id: int) -> None:
    """
    Функция добавляет студента в базу данных

    :param full_name: ФИО студента
    :param group_id: Telegram ID группы
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
    """
    session = Session()
    session.begin()
    try:
        for it in student_groups:
            group = Group(
                group_name=it.group_name,
                students = [Student(full_name=student_raw) for student_raw in it.students]
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
    Функция назначает преподавателю дисциплину

    :param teacher_id: Telegram ID преподавателя
    :param discipline_id: ID дисциплины
    """
    with Session() as session:
        teacher = session.get(Teacher, teacher_id)
        teacher.disciplines.append(
            session.get(Discipline, discipline_id)
        )
        session.commit()


def get_not_assign_teacher_discipline(teacher_id: int) -> list[Discipline]:
    """
    Функция возвращает не присвоенные преподавателю дисциплины

    :param teacher_id: Telegram ID преподавателя

    :return: Список не присвоенных преподавателю дисциплин
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
    Функция удаляет группу из БД

    :param group_id: ID группы
    """
    with Session() as session:
        query = delete(Group).where(Group.id == group_id)
        session.execute(query)
        session.commit()


def delete_student(student_id: int) -> None:
    """
    Функция удаляет студента из БД
    
    :param student_id: ID студента
    """
    with Session() as session:
        query = delete(Student).where(Student.id == student_id)
        session.execute(query)
        session.commit()


def delete_teacher(teacher_id: int) -> None:
    """
    Функция удаляет преподавателя из БД

    :param teacher_id: ID преподавателя
    """
    with Session() as session:
        query = delete(Teacher).where(Teacher.id == teacher_id)
        session.execute(query)
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
        return session.get(Discipline, discipline_id)
        #return session.query(Discipline).get(discipline_id)


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
    Переключение режима администратора в режим преподавателя
    
    :param admin_id: Telegram ID преподавателя
    """
    with Session() as session:
        admin = session.get(Admin, admin_id)
        admin.teacher_mode = True
        session.commit()
