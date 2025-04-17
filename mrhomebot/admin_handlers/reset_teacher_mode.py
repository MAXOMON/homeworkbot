"""
This module resets the teacher mode for the system administrator 
if an error occurs in the bot.
"""
from telebot.types import Message
from database.main_db import teacher_crud
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["reset"])
async def handle_reset_with_admin(message: Message):
    """
    Call the teacher mode reset function 
    if the command is received from the administrator!

    :param message: the object containing information about
        an incoming message from the user.
    """
    await __handle_reset(message)

@bot.message_handler(is_teacher=True, commands=["reset"])
async def handle_reset_with_teacher(message: Message):
    """
    Call the teacher mode reset function 
    if the command is received from the teacher!

    :param message: the object containing information about
        an incoming message from the user.
    """
    await __handle_reset(message)

async def __handle_reset(message: Message):
    """
    Turn off teacher mode if the menu in the telegram bot is buggy.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await teacher_crud.switch_teacher_mode_to_admin(message.from_user.id)
    await bot.send_message(
        message.chat.id,
        "Teacher-mode is off"
    )
