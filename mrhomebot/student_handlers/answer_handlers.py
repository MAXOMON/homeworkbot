"""Student Command Processing Module for loading answers from a student"""
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import CallbackQuery, Message, InlineKeyboardButton,\
    InlineKeyboardMarkup
from database.main_db import common_crud
from database.queue_db import queue_in_crud
from model.pydantic.queue_in_raw import QueueInRaw
from mrhomebot.configuration import bot
from utils.check_exist_test_folder import is_test_folder_exist
from utils.unzip_homework_files import save_homework_file


class StudentStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg upload answer.
    """
    upload_answer = State()


PAGINATOR = 5


@bot.callback_query_handler(
    func=lambda call: ("uploadAnswer_" in call.data) or
                    ("labNumber_" in call.data))
async def handle_upload_answer(call: CallbackQuery):
    """
    Pass to the next function, responsible for loading the answers 
    from the student, after collecting 
    (the buttons in the telegram chat are formed, with a callback function) 
    all the necessary information about the group number, 
    its discipline and the laboratory work number.

    :param call: an object that extends a standard message.
        may contain information about the discipline,
        lab assignment number, etc.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "uploadAnswer":
            paginator = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            discipline = await common_crud.get_discipline(discipline_id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            lab_list = [f"Лаб. раб. № {it}"
                        for it in range(1, discipline.max_home_works + 1)]
            markup.add(
                *[InlineKeyboardButton(
                    it,
                    callback_data=f"labNumber_{it.split()[-1]}_{discipline_id}"
                ) for it in lab_list[
                    PAGINATOR * paginator:PAGINATOR * (paginator + 1)]]
            )
            if paginator == 0:
                markup.add(
                    InlineKeyboardButton(
                        "➡",
                        callback_data=f"uploadAnswer_{paginator + 1}_\
                            {discipline_id}"
                    )
                )
            elif len(lab_list) > PAGINATOR * (paginator + 1):
                markup.add(
                    InlineKeyboardButton(
                        "⬅",
                        callback_data=f"uploadAnswer_{paginator - 1}_\
                            {discipline_id}"
                    ),
                    InlineKeyboardButton(
                        "➡",
                        callback_data=f"uploadAnswer_{paginator + 1}_\
                            {discipline_id}"
                    ),
                    row_width=2
                )
            else:
                markup.add(
                    InlineKeyboardButton(
                        "⬅",
                        callback_data=f"uploadAnswer_{paginator - 1}_\
                            {discipline_id}"
                    )
                )

            await bot.edit_message_text(
                "Выберите номер лабораторной работы",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case "labNumber":
            number = int(call.data.split("_")[1])
            if not await is_test_folder_exist(int(call.data.split("_")[2]), number):
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
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )

@bot.message_handler(
        content_types=['document'], state=StudentStates.upload_answer
        )
async def handle_student_docs(message: Message):
    """
    Add a record with the student's answers 
    to the input table of the intermediate database.

    :param message: the object containing information about 
        an incoming message from a user. In this case, 
        it is an archive with ready-made responses from a student, 
        which further require separate verification.
    """
    result_message = await bot.send_message(
        message.chat.id,
        "<i>Загружаем ваш файл</i>",
        parse_mode='HTML',
        disable_web_page_preview=True
    )

    async with bot.retrieve_data(
        message.from_user.id,
        message.chat.id) as data:
        lab_num = data["labNumber"]
        discipline_id = data["discipline_id"]

    discipline = await common_crud.get_discipline(discipline_id)

    file_name = message.document.file_name
    if file_name[-4:] == ".zip":
        if message.document.file_size > 10000:
            await bot.edit_message_text(
                text="<i>Архив превысил разрешённый к загрузке размер!!!</i>",
                chat_id=message.chat.id,
                message_id=result_message.id,
                parse_mode='HTML'
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
            return
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        filelist = await save_homework_file(
            file_name,
            downloaded_file,
            message.from_user.id,
            lab_num,
            discipline.path_to_answer
        )

        await queue_in_crud.add_record(
            message.from_user.id,
            message.chat.id,
            QueueInRaw(
                discipline_id=discipline_id,
                lab_number=lab_num,
                files_path=filelist
            )
        )

        await bot.send_message(message.chat.id,
                               "Задания отправлены на проверку")

    else:
        await bot.reply_to(message, "Неверный тип файла")

    await bot.edit_message_text(
        text="<i>Файл загружен</i>",
        chat_id=message.chat.id,
        message_id=result_message.id,
        parse_mode="HTML"
    )
    await bot.delete_state(message.from_user.id, message.chat.id)
