"""
Вспомогательный модуль с функциями по созданию различных стартовых
или промежуточных InlineKeyboardButton
"""
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from mrhomebot import bot
from database.main_db import student_crud


async def create_student_disciplines_button(message: Message, prefix: str):
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
