import telebot
from telebot.types import Message
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import Message, CallbackQuery

from database.main_db import admin_crud, teacher_crud, student_crud


add_student_factory = CallbackData(
    #"full_name",
    "group_id",
    "next_step",
    prefix="StudentADD_"
)


class IsAdmin(telebot.asyncio_filters.SimpleCustomFilter):
    key = "is_admin"

    @staticmethod
    async def check(message: Message):
        return admin_crud.is_admin_no_teacher_mode(message.from_user.id)


class IsStudent(telebot.asyncio_filters.SimpleCustomFilter):
    key = "is_student"

    @staticmethod
    async def check(message: Message):
        return student_crud.is_student(message.from_user.id)
    

class IsTeacher(telebot.asyncio_filters.SimpleCustomFilter):
    key = "is_teacher"

    @staticmethod
    async def check(message: Message):
        if admin_crud.is_admin_and_teacher(message.from_user.id):
            return admin_crud.is_admin_with_teacher_mode(message.from_user.id)
        return teacher_crud.is_teacher(message.from_user.id)


class AddStudentCallbackFilter(AdvancedCustomFilter):
    key = "addst_config"

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
