"""
Module for processing the administrator's command 
to download the short report for a specific discipline.
"""
from telebot.types import Message
from mrhomebot.admin_handlers.utils import create_groups_button
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["shortrep"])
async def handle_download_short_report(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "download short report"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await create_groups_button(message, "shortReport")

@bot.message_handler(is_admin=False, commands=["shortrep"])
async def handle_no_download_short_report(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")
