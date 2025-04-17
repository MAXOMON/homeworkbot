"""
Module for processing the administrator's command to upload start configuration
"""
import json
from pathlib import Path
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message
from database.main_db import admin_crud
from database.main_db.crud_exceptions import DisciplineNotFoundException,\
    GroupAlreadyExistException, DisciplineAlreadyExistException,\
    GroupNotFoundException
from database.main_db.database import Session
from model.pydantic.db_start_data import DbStartData
from mrhomebot.admin_handlers.utils import start_upload_file_message,\
    finish_upload_file_message
from mrhomebot.configuration import bot


class AdminStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg upload start configuration.
    """
    upload_config = State()


@bot.message_handler(is_admin=True, commands=["upconfig"])
async def handle_upload_start_configuration(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "upload start configuration"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await _handle_upload_start_configuration(message)

@bot.message_handler(is_admin=False, commands=["upconfig"])
async def handle_no_upload_start_configuration(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")

async def _handle_upload_start_configuration(message: Message):
    """
    Sets the user to a special state that 
    grants access to the admin function of upload start configuration

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id,
                           "Загрузите json-файл для наполнения БД")
    await bot.set_state(message.from_user.id,
                        AdminStates.upload_config,
                        message.chat.id)

@bot.message_handler(
        state=AdminStates.upload_config, content_types=["document"]
        )
async def handle_upload_discipline(message: Message):
    """
    Fill the database with data from the configuration file 
    if the configuration file sent by the user has been checked 
    for compliance with certain requirements.

    :param message: the object containing information about an incoming 
        message from a user. In this case, the initial DB configuration file.
    """
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name
    if file_name[-5:] == ".json":
        try:
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            data = json.loads(downloaded_file)
            db_start_data = DbStartData(**data)
            async with Session() as session:
                await admin_crud.remote_start_db_fill(db_start_data, session)
                await session.commit()
            path = Path.cwd()
            for discipline in db_start_data.disciplines:
                Path(path.joinpath(
                    discipline.path_to_test
                    )).mkdir(parents=True, exist_ok=True)
                Path(path.joinpath(
                    discipline.path_to_answer
                    )).mkdir(parents=True, exist_ok=True)
            await finish_upload_file_message(
                message,
                result_message,
                "<i>Стартовое заполнение БД завершено!</i>"
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
        except DisciplineNotFoundException as dnf_ex:
            await bot.reply_to(message, dnf_ex)
        except GroupAlreadyExistException as gae_ex:
            await bot.reply_to(message, gae_ex)
        except DisciplineAlreadyExistException as da_ex:
            await bot.reply_to(message, da_ex)
        except GroupNotFoundException as gnf_ex:
            await bot.reply_to(message, gnf_ex)
    else:
        await bot.reply_to(message, "Неверный тип файла")
