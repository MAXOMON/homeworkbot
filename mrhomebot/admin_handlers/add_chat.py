from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message

from mrhomebot.configuration import bot
from database.main_db import admin_crud


class AdminStates(StatesGroup):
    chat_id = State()


@bot.message_handler(is_admin=True, commands=["addchat"])
async def handle_add_chat(message: Message):
    await _handle_add_chat(message)


@bot.message_handler(is_admin=False, commands=["addchat"])
async def handle_no_add_chat(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


async def _handle_add_chat(message: Message) -> None:
    await bot.set_state(message.from_user.id, AdminStates.chat_id, message.chat.id)
    await bot.send_message(message.chat.id, "Введите telegram id добавляемого группового чата:")


@bot.message_handler(state=AdminStates.chat_id)
async def chat_correct(message: Message):
    msg = message.text
    if msg[0] == "-" and msg[1:].isdigit() and int(msg) < 0:
        admin_crud.add_chat(int(msg))
        await bot.send_message(message.chat.id, "Групповой чат успешно добавлен!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Введите корректный id группового чата!")
