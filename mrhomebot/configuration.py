import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage

from mrhomebot.filters import IsAdmin, IsStudent, IsTeacher
from mrhomebot.filters import AddStudentCallbackFilter

from mrhomebot.middlewares import BanMiddleware, StudentFloodMiddleware


load_dotenv()

bot = AsyncTeleBot(os.getenv("BOT_TOKEN"), state_storage=StateMemoryStorage())

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsStudent())
bot.add_custom_filter(IsTeacher())
bot.add_custom_filter(AddStudentCallbackFilter())

bot.setup_middleware(BanMiddleware(bot))

if bool(os.getenv("FLOOD_MIDDLEWARE")):
    bot.setup_middleware((
        StudentFloodMiddleware(
            bot,
            int(os.getenv("STUDENT_UPLOAD_LIMIT")),
            int(os.getenv("STUDENT_COMMAND_LIMIT"))
        )
    ))
