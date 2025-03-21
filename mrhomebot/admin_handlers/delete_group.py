"""
Contains the necessary functionality for the bot to delete a group of students.
"""
from telebot.types import Message, CallbackQuery
from database.main_db import admin_crud
from mrhomebot.admin_handlers.utils import create_groups_button
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["delgroup"])
async def handle_delete_group(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "delete group"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await create_groups_button(message, "groupDel")


@bot.message_handler(is_admin=False, commands=["delgroup"])
async def handle_no_delete_group(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


@bot.callback_query_handler(func=lambda call: "groupDel_" in call.data)
async def callback_delete_group(call: CallbackQuery):
    """
    Delete the selected group of students from the database.

    :param call: an object that extends the standard message.
        Contains the ID of the group to be deleted.
    """
    group_id = int(call.data.split("_")[1])
    admin_crud.delete_group(group_id)
    await bot.edit_message_text(
        "Выбранная группа успешно удалена", 
        call.message.chat.id, 
        call.message.id
    )
