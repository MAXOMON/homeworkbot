"""
A module for processing teacher commands, in this case, 
downloading responses from a group of students on a specific subject.
"""
import asyncio
from pathlib import Path
from telebot.types import CallbackQuery, InputFile, InlineKeyboardMarkup,\
    InlineKeyboardButton
from database.main_db import teacher_crud, common_crud
from mrhomebot.configuration import bot
from reports.create_answers_archive import create_answers_archive


__answer_prefix = [
    'dowTAnswersDis_',
    'dowTAnswersGr_'
]


def __is_answer_prefix_callback(data: str) -> bool:
    """
    Check if such a team is on the list of teacher commands.

    :param data: eg message.text

    :return bool: True IF is a command ELSE False
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
    Create a keyboard in the Telegram bot chat, 
    with a choice of discipline and group, 
    to download the answers of students in that group.

    :param call: contains a prefix of the teacher's permitted 
        commands for downloading answers
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "dowTAnswersDis":
            discipline_id = int(call.data.split("_")[1])
            discipline = common_crud.get_discipline(discipline_id)
            path = Path.cwd().joinpath(discipline.path_to_answer)
            dirs = [it for it in path.iterdir() if it.is_dir()]
            if not dirs:
                await bot.edit_message_text(
                    'Директории для скачивания ответов отсутствуют',
                    call.message.chat.id,
                    call.message.id
                )
            else:
                teacher_groups = teacher_crud.get_assign_groups(
                    call.from_user.id
                    )
                dirs = [
                    it for it in dirs if it.name in
                        [tg.group_name for tg in teacher_groups]
                ]
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    *[InlineKeyboardButton(
                        it.name,
                        callback_data=f"dowTAnswersGr_{it.name}_\
                            {discipline_id}"
                    ) for it in dirs]
                )
                await bot.edit_message_text(
                    'Выберите группу:',
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=markup
                )
        case "dowTAnswersGr":
            group_name = call.data.split("_")[1]
            discipline_id = int(call.data.split("_")[2])
            discipline = common_crud.get_discipline(discipline_id)
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
    Run the function of creating and downloading answers from a student 
    of a specific discipline and group in a separate thread.

    :param call: an object that extends a standard message.

    :param path_to_group_folder: The path where the answers 
        of this group are located
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
