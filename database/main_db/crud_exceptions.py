"""
The module contains announcements of possible exclusions 
when the bot is running
"""


class GroupNotFoundException(Exception):
    """No such group found"""
    ...


class DisciplineNotFoundException(Exception):
    """No such discipline found"""
    ...


class StudentNotFoundException(Exception):
    """No such student found"""
    ...


class TeacherNotFoundException(Exception):
    """No such teacher found"""
    ...


class GroupAlreadyExistException(Exception):
    """Such a group already exists"""
    ...


class DisciplineAlreadyExistException(Exception):
    """Such a discipline already exists"""
    ...


class StudentAlreadyExistException(Exception):
    """This student already exists in the database"""
    ...


class TeacherAlreadyExistException(Exception):
    """This teacher already exists in the database"""
    ...
