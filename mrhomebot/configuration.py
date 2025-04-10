"""
This module is a configuration file that defines the operation 
of a telegram bot instance.
"""
import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from mrhomebot.filters import AddStudentCallbackFilter, IsAdmin, IsStudent, \
    IsTeacher
from mrhomebot.middlewares import BanMiddleware, StudentFloodMiddleware


load_dotenv()




bot = AsyncTeleBot(os.getenv("BOT_TOKEN"), state_storage=StateMemoryStorage())

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsStudent())
bot.add_custom_filter(IsTeacher())
bot.add_custom_filter(AddStudentCallbackFilter())

bot.setup_middleware(BanMiddleware(bot))


def my_str_to_bool(value: str) -> bool:
    """
    Converts the string representation of a boolean value to a boolean.

    :param value: string value, such as 'True' or 'False'
    """
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        raise ValueError('Правильно заполните .env')


if my_str_to_bool(os.getenv("FLOOD_MIDDLEWARE")):
    bot.setup_middleware((
        StudentFloodMiddleware(
            bot,
            int(os.getenv("STUDENT_UPLOAD_LIMIT")),
            int(os.getenv("STUDENT_COMMAND_LIMIT"))
        )
    ))
