"""
Модуль с объявлениями возможных исключений при работе бота
"""


class GroupNotFoundException(Exception):
    ...


class DisciplineNotFoundException(Exception):
    ...


class StudentNotFoundException(Exception):
    ...


class TeacherNotFoundException(Exception):
    ...


class GroupAlreadyExistException(Exception):
    ...


class DisciplineAlreadyExistException(Exception):
    ...


class StudentAlreadyExistException(Exception):
    ...


class TeacherAlreadyExistException(Exception):
    ...
