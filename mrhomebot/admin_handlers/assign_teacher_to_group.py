from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)

from mrhomebot.admin_handlers.utils import create_teachers_button
from mrhomebot.configuration import bot
from database.main_db import admin_crud


@bot.message_handler(is_admin=True, commands=["assigntgr"])
async def handle_assign_teacher_to_group(message: Message):
    await create_teachers_button(message, "assignTeacherGR")


@bot.message_handler(is_admin=False, commands=["assigntgr"])
async def handle_no_assign_teacher_to_group(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


@bot.callback_query_handler(func=lambda call: "assignTeacherGR_" in call.data or 
                            "assignGroupT_" in call.data)
async def callback_assign_teacher_to_group(call: CallbackQuery):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "assignTeacherGR":
            teacher_id = int(call.data.split("_")[1])
            groups = admin_crud.get_not_assign_teacher_groups(teacher_id)
            if len(groups) < 1:
                await bot.send_message(
                    call.message.chat.id,
                    "В БД отсутствуют группы, куда можно добавить студента!"
                )
                return
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[
                    InlineKeyboardButton(
                        it.group_name,
                        callback_data=f"assignGroupT_{it.id}_{teacher_id}"
                    ) for it in groups
                ]
            )
            await bot.edit_message_text(
                "Выберите группу, которой назначается преподаватель:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case "assignGroupT":
            group_id = call.data.split("_")[1]
            teacher_id = call.data.split("_")[2]
            admin_crud.assign_teacher_to_group(int(teacher_id), int(group_id))
            await bot.edit_message_text(
                "Преподаватель назначен группе",
                call.message.chat.id,
                call.message.id
            )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )
