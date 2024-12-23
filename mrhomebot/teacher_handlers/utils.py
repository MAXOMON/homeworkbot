from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from mrhomebot import bot
from database.main_db import teacher_crud


async def create_teacher_groups_button(message: Message, callback_prefix: str):
    groups = teacher_crud.get_assign_groups(message.from_user.id)
    if len(groups) < 1:
        await bot.send_message(message.chat.id, "В БД отсутствуют группы!")
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
        parse_mode='HTML',
        reply_markup=markup
    )


async def create_teacher_discipline_button(message: Message, callback_prefix: str):
    disciplines = teacher_crud.get_teacher_disciplines(message.from_user.id)
    if len(disciplines) < 1:
        await bot.send_message(message.chat.id, "В БД отсутствуют дисциплины!")
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
        reply_markup=markup
    )
