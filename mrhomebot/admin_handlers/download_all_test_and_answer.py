"""Contains the necessary functionality to download all tests and answers"""
import asyncio
import os
import shutil
import pathlib
from datetime import datetime
from telebot.types import Message, InputFile
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["dowall"])
async def handle_download_all_test_and_answer(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "download all tests and answers"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await _handle_download_all_test_and_answer(message)

@bot.message_handler(is_admin=False, commands=["dowall"])
async def handle_no_download_all_test_and_answer(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")

async def _handle_download_all_test_and_answer(message: Message):
    """
    Run the function to download all tests and answers in a separate thread.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(
        message.chat.id,
        "Начинаем формировать отчёт"
    )
    path_to_archive = await asyncio.gather(
        asyncio.to_thread(create_archive_all_data)
    )
    await bot.send_message(
        message.chat.id,
        "Архив успешно сформирован"
    )
    await bot.send_document(
        message.chat.id,
        InputFile(path_to_archive[0])
    )

def create_archive_all_data():
    """
    Create an archive from the directory with disciplines,
    where the data on answers and tests are stored.

    :return: Path to the generated archive
    """
    path = pathlib.Path(pathlib.Path.cwd().joinpath(os.getenv('TEMP_REPORT_DIR')))
    file_name = f'data_{datetime.now().date()}'

    shutil.make_archive(
        str(path.joinpath(f'{file_name}')),
        'zip', pathlib.Path.cwd().joinpath('_disciplines')
    )
    return path.joinpath(f'{file_name}.zip')
