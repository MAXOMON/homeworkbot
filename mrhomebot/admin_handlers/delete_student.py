"""Contains the necessary functionality for deleting students by a bot"""
from telebot.types import Message, CallbackQuery
from database.main_db import admin_crud, common_crud
from mrhomebot.admin_handlers.utils import create_groups_button,\
    create_callback_students_button
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["delstudent"])
async def handle_del_student(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "delete student"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await create_groups_button(message, "groupStudDel")


@bot.message_handler(is_admin=False, commands=["delstudent"])
async def handle_no_del_student(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


@bot.callback_query_handler(func=lambda call: "groupStudDel_" in call.data \
                            or "studDel_" in call.data)
async def callback_del_student(call: CallbackQuery):
    """
    Delete the selected student.

    :param call: an object that extends the standard message.
        Contains information about the student group from 
        which the student needs to be removed, 
        as well as the ID of the selected student.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "groupStudDel":
            group_id = int(call.data.split("_")[1])
            students = await common_crud.get_students_from_group(group_id)
            await create_callback_students_button(call,
                                                  students,
                                                  "studDel",
                                                  True)
        case "studDel":
            student_id = int(call.data.split("_")[1])
            await admin_crud.delete_student(student_id)
            await bot.edit_message_text(
                "Студент успешно удалён",
                call.message.chat.id,
                call.message.id
            )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )
