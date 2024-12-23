
from mrhomebot.admin_handlers.utils import create_groups_button
from mrhomebot.configuration import bot
from telebot.types import Message


@bot.message_handler(is_admin=True, commands=["shortrep"])
async def handle_download_short_report(message: Message):
    await create_groups_button(message, "shortReport")


@bot.message_handler(is_admin=False, commands=["shortrep"])
async def handle_no_download_short_report(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")
