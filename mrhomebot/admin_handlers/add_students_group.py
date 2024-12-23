import json

from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message

from database.main_db.crud_exceptions import DisciplineNotFoundException, GroupAlreadyExistException
from mrhomebot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message
from mrhomebot.configuration import bot
from database.main_db import admin_crud
from model.pydantic.students_group import StudentsGroup


class AdminStates(StatesGroup):
    upload_students_group = State()


@bot.message_handler(is_admin=True, commands=["addstudentsgroup"])
async def handle_add_students_group(message: Message):
    await _handle_add_students_group(message)


@bot.message_handler(is_admin=False, commands=["addstudentsgroup"])
async def handle_no_add_students_group(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


async def _handle_add_students_group(message: Message):
    await bot.set_state(message.from_user.id, AdminStates.upload_students_group, message.chat.id)
    await bot.send_message(
        message.chat.id,
        "Загрузите json-файл с конфигурацией новой группы и" \
        "назначенной ей дисциплины, которая уже существует в системе:"
    )

@bot.message_handler(state=AdminStates.upload_students_group, content_types=["document"])
async def handle_upload_discipline(message: Message):
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name
    if file_name[-4:] == "json":
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        group_data = json.loads(downloaded_file)
        groups_list = [StudentsGroup(**it) for it in group_data]
        try:
            admin_crud.add_students_group(groups_list)
            await finish_upload_file_message(
                message,
                result_message,
                f"<i>Группа(ы) студентов успешно добавлена(ы)!</i>"
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
        except DisciplineNotFoundException as dnf_ex:
            await bot.reply_to(message, dnf_ex)
        except GroupAlreadyExistException as gae_ex:
            await bot.reply_to(message, gae_ex)
    else:
        await bot.reply_to(message, "Неверный тип файла")
