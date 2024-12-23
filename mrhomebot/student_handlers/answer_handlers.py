from telebot.asyncio_handler_backends import State, StatesGroup

from database.main_db import common_crud
from database.queue_db import queue_in_crud
from model.pydantic.queue_in_raw import QueueInRaw


from telebot.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from utils.check_exist_test_folder import is_test_folder_exist
from utils.unzip_homework_files import save_homework_file
from mrhomebot import bot


class StudentStates(StatesGroup):
    upload_answer = State()


@bot.callback_query_handler(
        func=lambda call: "uploadAnswer_" in call.data or "labNumber_" in call.data
        )
async def handle_upload_answer(call: CallbackQuery):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "uploadAnswer":
            discipline_id = int(call.data.split("_")[1])
            discipline = common_crud.get_discipline(discipline_id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[InlineKeyboardButton(
                    f"Лаб. раб. № {it}",
                    callback_data=f"labNumber_{it}_{discipline_id}"
                ) for it in range(1, discipline.max_home_works + 1)]
            )
            await bot.edit_message_text(
                "Выберите номер лабораторной работы",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case "labNumber":
            number = int(call.data.split("_")[1])
            if not is_test_folder_exist(int(call.data.split("_")[2]), number):
                await bot.edit_message_text(
                    "Тесты для этой работы не готовы",
                    call.message.chat.id,
                    call.message.id
                )
                return
            await bot.edit_message_text(
                "Загрузите ответы в zip-файле",
                call.message.chat.id,
                call.message.id
            )
            await bot.set_state(
                call.from_user.id,
                StudentStates.upload_answer,
                call.message.chat.id
            )
            async with bot.retrieve_data(
                call.from_user.id, call.message.chat.id
            ) as data:
                data["labNumber"] = number
                data["discipline_id"] = int(call.data.split("_")[2])
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработка данных",
                call.message.chat.id,
                call.message.id
            )


@bot.message_handler(state=StudentStates.upload_answer, content_types=['document'])
async def handle_student_docs(message: Message):
    result_message = await bot.send_message(
        message.chat.id,
        "<i>Загружаем ваш файл</i>",
        parse_mode='HTML',
        disable_web_page_preview=True
    )

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lab_num = data["labNumber"]
        discipline_id = data["discipline_id"]
    
    discipline = common_crud.get_discipline(discipline_id)

    file_name = message.document.file_name
    if file_name[-4:] == ".zip":
        if message.document.file_size > 10000:
            await bot.edit_message_text(
                "<i>Архив превысил разрешённый к загрузке размер!!!</i>",
                message.chat.id,
                message.id,
                parse_mode='HTML'
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
            return
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        filelist = await save_homework_file(
            file_name,
            downloaded_file,
            message.forum_user.id,
            lab_num,
            discipline.path_to_answer
        )

        queue_in_crud.add_record(
            message.from_user.id,
            message.chat.id,
            QueueInRaw(
                discipline_id,
                lab_num,
                filelist
            )
        )
        
        await bot.send_message(message.chat.id, "Задания отправлены на проверку")

    else:
        await bot.reply_to(message, "Неверный тип файла")
    
    await bot.edit_message_text(
        "<i>Файл загружен</i>",
        message.chat.id,
        result_message.id,
        parse_mode="HTML"
    )
    await bot.delete_state(message.from_user.id, message.chat.id)
