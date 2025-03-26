"""Contains the necessary functionality to delete a teacher"""
from telebot.types import Message, CallbackQuery
from database.main_db import admin_crud
from mrhomebot.admin_handlers.utils import create_teachers_button
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["delteacher"])
async def handle_delete_teacher(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "delete teacher"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await create_teachers_button(message, "delTeacher")


@bot.message_handler(is_admin=False, commands=["delteacher"])
async def handle_no_delete_teacher(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


@bot.callback_query_handler(func=lambda call: "delTeacher_" in call.data)
async def callback_delete_teacher(call: CallbackQuery):
    """
    Remove the selected teacher from the system.

    :param call: an object that extends the standard message.
        Contains information about the teacher ID to be deleted.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "delTeacher":
            teacher_id = int(call.data.split("_")[1])
            admin_crud.delete_teacher(teacher_id)
            await bot.edit_message_text(
                "Преподаватель успешно удалён",
                call.message.chat.id,
                call.message.id
            )
        case _:
            await bot.edit_message_text(
                f"Ошибка admin_delete_teacher{call.data=}",
                call.message.chat.id,
                call.message.id
            )
