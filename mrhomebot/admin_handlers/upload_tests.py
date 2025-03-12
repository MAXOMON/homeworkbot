"""
Модуль обработки команды администратора на загрузку тестов к выбранной дисциплине
"""
from telebot.asyncio_handler_backends import StatesGroup, State
from telebot.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from mrhomebot.admin_handlers.utils import start_upload_file_message, finish_upload_file_message
from mrhomebot.configuration import bot
from database.main_db import admin_crud
from utils.unzip_test_files import save_test_files


class AdminState(StatesGroup):
    upload_test = State()


@bot.message_handler(is_admin=True, commands=["uptest"])
async def handle_upload_tests(message: Message):
    await _handle_upload_tests(message)


@bot.message_handler(is_admin=False, commands=["uptest"])
async def handle_no_upload_tests(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


async def _handle_upload_tests(message: Message):
    disciplines = admin_crud.get_all_disciplines()
    if len(disciplines) < 1:
        await bot.send_message(message.chat.id, "В БД отсутствуют данные по дисциплинам!")
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[InlineKeyboardButton(
            it.short_name,
            callback_data=f"upTest_{it.id}"
        ) for it in disciplines]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите дисциплину для загрузки тестов:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: "upTest_" in call.data)
async def callback_upload_tests(call: CallbackQuery):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "upTest":
            await bot.edit_message_text(
                "Загрузите архив с тестами",
                call.message.chat.id,
                call.message.id
            )
            await bot.set_state(
                call.from_user.id,
                AdminState.upload_test,
                call.message.chat.id
            )
            async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data["discipline_id"] = int(call.data.split("_")[1])
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )

@bot.message_handler(state=AdminState.upload_test, content_types=["document"])
async def handle_upload_zip_tests(message: Message):
    result_message = await start_upload_file_message(message)
    file_name = message.document.file_name
    if file_name[-4:] == ".zip":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            discipline_id = data["discipline_id"]
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        discipline = admin_crud.get_discipline(discipline_id)
        await save_test_files(discipline.path_to_test, downloaded_file)
        await finish_upload_file_message(
            message,
            result_message,
            f'<i>Тесты по дисциплине "{discipline.short_name}" загружены!</i>'
        )
        await bot.delete_state(
            message.from_user.id,
            message.chat.id
        )
    else:
        await bot.reply_to(message, "Неверный тип файла")
