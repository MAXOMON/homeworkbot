"""
An auxiliary module with functions for creating 
various starting or intermediate InlineKeyboardButton
"""
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.main_db import student_crud
from mrhomebot import bot


async def create_student_disciplines_button(message: Message, prefix: str):
    """
    Generates a keyboard with the disciplines of the selected student, 
    with a callback function, for processing the selected discipline 
    in other functionality of the system.

    :param message: the object containing information about
        an incoming message from the user. 
    :param prefix: Text representation of a command that 
        is used in various handlers, eg 'nearestDeadline'...
    """
    disciplines = student_crud.get_assign_disciplines(message.from_user.id)
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
            callback_data=f"{prefix}_{it.id}"
        ) for it in disciplines]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите дисциплину:",
        parse_mode='HTML',
        reply_markup=markup
    )
