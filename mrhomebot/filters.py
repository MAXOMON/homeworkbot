"""
Contains filters that check the user's status and, 
in accordance with it, configure the system's behavior 
for different interactions with the user.
"""
import asyncio
import telebot
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import Message, CallbackQuery
from database.main_db import admin_crud, teacher_crud, student_crud


add_student_factory = CallbackData(
    "group_id",
    "next_step",
    prefix="StudentADD_"
)


class IsAdmin(telebot.asyncio_filters.SimpleCustomFilter):
    """
    This class is used to check the user status, i.e. 
    whether he is an Administrator.
    """
    key = "is_admin"

    @staticmethod
    async def check(message: Message):
        """
        Check if this is an administrator without a teacher mode.

        :param message: the object containing information about
        an incoming message from the user
        """
        result = await admin_crud.is_admin_no_teacher_mode(message.from_user.id)
        return result


class IsStudent(telebot.asyncio_filters.SimpleCustomFilter):
    """
    This class is used to check the user status, i.e. 
    whether he is an Student.
    """
    key = "is_student"

    @staticmethod
    async def check(message: Message):
        """
        Check if this is a student.

        :param message: the object containing information about
        an incoming message from the user
        """
        result = await student_crud.is_student(message.from_user.id)
        return result


class IsTeacher(telebot.asyncio_filters.SimpleCustomFilter):
    """
    This class is used to check the user status, i.e. 
    whether he is an Teacher.
    """
    key = "is_teacher"

    @staticmethod
    async def check(message: Message):
        """
        Check, it's a teacher.

        :param message: the object containing information about
        an incoming message from the user
        """
        result = await admin_crud.is_admin_and_teacher(message.from_user.id)
        if result:
            return await admin_crud.is_admin_with_teacher_mode(message.from_user.id)
        return await teacher_crud.is_teacher(message.from_user.id)


class AddStudentCallbackFilter(AdvancedCustomFilter):
    """
    This class is needed to check the passed factory,
    to add a student to the database.
    """
    key = "addst_config"

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        """
        Check if such config exists or not

        :param call: an object that extends a standard message.
        :param config: add_student_factory
        """
        await asyncio.sleep(0.0001)
        return config.check(query=call)
