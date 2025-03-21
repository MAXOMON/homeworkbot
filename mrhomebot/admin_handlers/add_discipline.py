"""
This module contains all the necessary functionality to 
add an academic discipline to the database.
"""
from pathlib import Path
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message
from mrhomebot.admin_handlers.utils import start_upload_file_message,\
    finish_upload_file_message
from mrhomebot.configuration import bot
from database.main_db import admin_crud
from utils.disciplines_utils import load_discipline


class AdminStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg add an academic discipline.
    """
    upload_discipline = State()


@bot.message_handler(is_admin=True, commands=["adddiscipline"])
async def handle_add_discipline(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "add discipline"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await _handle_add_discipline(message)


@bot.message_handler(is_admin=False, commands=["adddiscipline"])
async def handle_no_add_discipline(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


async def _handle_add_discipline(message: Message):
    """
    Sets the user to a special state that 
    grants access to the admin function of adding an academic discipline.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id,
                           "Загрузите json-файл с конфигурацией дисциплины")
    await bot.set_state(
        message.from_user.id, AdminStates.upload_discipline, message.chat.id)


@bot.message_handler(state=AdminStates.upload_discipline,
                     content_types=["document"])
async def handle_upload_discipline(message: Message):
    """
    Add discipline to the DB if the transferred data is correct.

    :param message: the object containing information about
        an incoming message from the user.
    """
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name
    if file_name[-4:] == "json":
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        discipline = load_discipline(downloaded_file)
        admin_crud.add_discipline(discipline)
        path = Path.cwd()
        Path(path.joinpath(discipline.path_to_test)).mkdir(parents=True,
                                                           exist_ok=True)
        Path(path.joinpath(discipline.path_to_answer)).mkdir(parents=True,
                                                             exist_ok=True)
        await finish_upload_file_message(
            message,
            result_message,
            f"<i>Дисциплина {discipline.short_name} добавлена!</i>"
        )
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.reply_to(message, "Неверный тип файла")
