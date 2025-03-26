"""The module contains various utilities for administrator command handlers"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message,\
    CallbackQuery
from database.main_db import admin_crud
from model.main_db.student import Student
from mrhomebot import bot


async def create_teachers_button(message: Message, callback_prefix: str):
    """
    Generates a keyboard for selecting a teacher from the list of teachers.

    :param message: the object containing information about
        an incoming message from the user.
    :param callback_prefix: Typically, some administrative command 
        from the list of administrator command handlers.
    """
    teachers = admin_crud.get_teachers()
    if len(teachers) < 1:
        await bot.send_message(message.chat.id,
                               "В БД отсутствуют преподаватели!")
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                it.full_name,
                callback_data=f"{callback_prefix}_{it.id}"
            ) for it in teachers
        ]
    )
    await bot.send_message(
        message.chat.id, 
        "Выберите преподавателя: ",
        reply_markup=markup
        )

async def start_upload_file_message(message: Message) -> Message:
    """
    Display a message in the Telegram bot chat 
    about the start of file download.

    :param message: the object containing information about
        an incoming message from the user.
    
    :return Message: We send this object so that 
        it can be used in the next function, eg 'finish_upload_file_message'
    """
    return await bot.send_message(
        message.chat.id,
        "<i>Загружаем ваш файл...</i>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def finish_upload_file_message(message: Message,
                                     result_message: Message,
                                     text: str = "<i>Файл загружен!</i>"):
    """
    Display a message in the Telegram bot chat 
    about the successful file download.

    :param message: the object containing information about
        an incoming message from the user.
    :param result_message: the object from 'start_upload_file_message' 
        contains the original string we want to change
    :param text: Text that should be replaced in the telegram bot chat.
    """
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=result_message.id,
        text=text,
        parse_mode="HTML"
    )

async def create_groups_button(message: Message, callback_prefix: str):
    """
    The function creates a keyboard for selecting groups.

    :param message: the object containing information about
        an incoming message from the user.
    :param callback_prefix: Typically, some administrative command 
        from the list of administrator command handlers.
    """
    groups = admin_crud.get_all_groups()
    if len(groups) < 1:
        await bot.send_message(
            message.chat.id,
            "В БД отсутствуют группы!"
        )
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[InlineKeyboardButton(
            it.group_name,
            callback_data=f"{callback_prefix}_{it.id}"
        ) for it in groups]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите группу, в которой учится студент:",
        reply_markup=markup
    )

async def create_callback_students_button(
        call: CallbackQuery,
        students: list[Student],
        callback_prefix: str,
        id_flag: bool = False):
    """
    The function creates a keyboard for selecting students

    :param call: an object that extends the standard message.
    :param students: list of students
    :param callback_prefix: Typically, some administrative command 
        from the list of administrator command handlers.
    :param id_flag: True IF hasn`t telegram_id ELSE False
    """
    if len(students) < 1:
        await bot.send_message(
            call.message.chat.id,
            "В группе нет студентов"
        )
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[InlineKeyboardButton(
            it.full_name,
            callback_data=f"{callback_prefix}_\
                {it.telegram_id if not id_flag else it.id}"
        ) for it in students]
    )
    await bot.edit_message_text(
        "Выберите студента:",
        call.message.chat.id,
        call.message.id,
        reply_markup=markup
    )

async def create_discipline_button(message: Message, callback_prefix: str):
    """
    The function creates a keyboard for selecting discipline

    :param message: the object containing information about
        an incoming message from the user.
    :param callback_prefix: Typically, some administrative command 
        from the list of administrator command handlers.
    """
    disciplines = admin_crud.get_all_disciplines()
    if len(disciplines) < 1:
        await bot.send_message(
            message.chat.id,
            "В БД отсутствуют дисциплины!"
        )
        return
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[InlineKeyboardButton(
            it.short_name,
            callback_data=f"{callback_prefix}_{it.id}"
        ) for it in disciplines]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите дисциплину:",
        parse_mode='HTML',
        reply_markup=markup
    )
