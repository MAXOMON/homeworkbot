"""
This module contains all the necessary functionality to 
add a Telegram chat to the database so that 
the bot functionality becomes available in this chat.
"""
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message
from database.main_db import admin_crud
from mrhomebot.configuration import bot


class AdminStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg add telegram chat.
    """
    chat_id = State()


@bot.message_handler(is_admin=True, commands=["addchat"])
async def handle_add_chat(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "add chat"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await _handle_add_chat(message)

@bot.message_handler(is_admin=False, commands=["addchat"])
async def handle_no_add_chat(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")

async def _handle_add_chat(message: Message) -> None:
    """
    Sets the user to a special state that 
    grants access to the admin function of adding a chat.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.set_state(
        message.from_user.id, AdminStates.chat_id, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Введите telegram id добавляемого группового чата:")

@bot.message_handler(state=AdminStates.chat_id)
async def chat_correct(message: Message):
    """
    Adds a chat to the database,
    provided that the passed parameter matches the chat number.

    :param message: the object containing information about
        an incoming message from the user.
    """
    msg = message.text
    if msg[0] == "-" and msg[1:].isdigit() and int(msg) < 0:
        try:
            await admin_crud.add_chat(int(msg))
            await bot.send_message(message.chat.id,
                               "Групповой чат успешно добавлен!")
            await bot.delete_state(message.from_user.id, message.chat.id)
        except:
            await bot.send_message(message.chat.id,
                               "Чат уже существует!")
            await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id,
                               "Введите корректный id группового чата!")
