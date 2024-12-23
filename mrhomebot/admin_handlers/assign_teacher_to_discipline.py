from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from mrhomebot.admin_handlers.utils import create_teachers_button
from mrhomebot.configuration import bot
from database.main_db import admin_crud


@bot.message_handler(is_admin=True, commands=["assigntd"])
async def handle_assign_teacher_to_discipline(message: Message):
    await create_teachers_button(message, "assignTeacherDis")


@bot.message_handler(is_admin=False, commands=["assigntd"])
async def handle_no_assign_teacher_to_discipline(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


@bot.callback_query_handler(func=lambda call: "assignTeacherDis_" in call.data or 
                            "assignDiscT_" in call.data)
async def callback_assign_teacher_to_discipline(call: CallbackQuery):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "assignTeacherDis":
            teacher_id = int(call.data.split("_")[1])
            disciplines = admin_crud.get_not_assign_teacher_discipline(teacher_id)
            if len(disciplines) < 1:
                await bot.send_message(call.message.chat.id, "В БД отсутствуют данные по дисциплинам!")
                return
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[InlineKeyboardButton(
                    it.short_name,
                    callback_data=f"assignDiscT_{it.id}_{teacher_id}"
                ) for it in disciplines]
            )
            await bot.edit_message_text(
                "Выберите дисциплину, которой назначается преподаватель:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case "assignDiscT":
            discipline_id = int(call.data.split("_")[1])
            teacher_id = int(call.data.split("_")[2])
            admin_crud.assign_teacher_to_discipline(teacher_id, discipline_id)
            await bot.edit_message_text(
                "Дисциплина назначена преподавателю",
                call.message.chat.id,
                call.message.id
            )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных!",
                call.message.chat.id,
                call.message.id
            )
