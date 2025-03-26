"""
Module for processing the administrator's command 
to download answers for a specific group's discipline
"""
import asyncio
from pathlib import Path
from telebot.types import Message, CallbackQuery, InputFile,\
    InlineKeyboardMarkup, InlineKeyboardButton
from database.main_db import admin_crud
from mrhomebot.admin_handlers.utils import create_discipline_button
from mrhomebot.configuration import bot
from reports.create_answers_archive import create_answers_archive


@bot.message_handler(is_admin=True, commands=['granswer'])
async def handle_download_answers(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "download answers"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await create_discipline_button(message, 'dowAnswersDis')

@bot.message_handler(is_admin=False, commands=['granswer'])
async def handle_no_download_answers(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, 'Нет прав доступа!!!')

__answer_prefix = [
    'dowAnswersDis_',
    'dowAnswersGr_'
]

def __is_answer_prefix_callback(data: str) -> bool:
    """
    Check if the transmitted data contains a prefix for downloading responses!

    :param data: is the object of the call, in the Telegram API, 
        generated when the administrator clicks on 
        the button in the Telegram bot chat.

    :return bool: True IF answer_prefix in data ELSE False
    """
    for it in __answer_prefix:
        if it in data:
            return True
    return False

@bot.callback_query_handler(
    func=lambda call: __is_answer_prefix_callback(call.data)
)
async def callback_download_answers(call: CallbackQuery):
    """
    Transfer the collected necessary information about the discipline 
    and group for which you need to download the archive with answers
    to the next function for downloading answers.

    :param call: an object that extends the standard message.
        contains the discipline and group identifier
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "dowAnswersDis":
            discipline_id = int(call.data.split("_")[1])
            discipline = admin_crud.get_discipline(discipline_id)
            path = Path.cwd().joinpath(discipline.path_to_answer)
            dirs = [it for it in path.iterdir() if it.is_dir()]
            if not dirs:
                await bot.edit_message_text(
                    "Директории для скачивания ответов отсутствуют",
                    call.message.chat.id,
                    call.message.id
                )
            else:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    *[InlineKeyboardButton(
                        it.name,
                        callback_data=f'dowAnswersGr_{it.name}_{discipline_id}'
                    ) for it in dirs]
                )
                await bot.edit_message_text(
                    "Выберите группу:",
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=markup
                )
        case "dowAnswersGr":
            group_name = call.data.split("_")[1]
            discipline_id = int(call.data.split("_")[2])
            discipline = admin_crud.get_discipline(discipline_id)
            path = Path.cwd().joinpath(discipline.path_to_answer)
            path = path.joinpath(group_name)
            await _download_answer(call, path)
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )

async def _download_answer(call: CallbackQuery, path_to_group_folder: Path):
    """
    Run the function of downloading 
    the archive with answers in a separate thread.

    :param call: an object that extends the standard message.
        contains the discipline and group identifier
    :param path_to_group_folder: the path where the answers are located
    """
    await bot.edit_message_text(
        "Начинаем формировать отчёт",
        call.message.chat.id,
        call.message.id
    )
    path_to_archive = await asyncio.gather(
        asyncio.to_thread(create_answers_archive, path_to_group_folder)
    )

    await bot.edit_message_text(
        "Архив успешно сформирован",
        call.message.chat.id,
        call.message.id
    )

    await bot.send_document(
        call.message.chat.id,
        InputFile(path_to_archive[0])
    )
