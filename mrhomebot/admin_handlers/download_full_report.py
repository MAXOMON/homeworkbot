from telebot.types import Message
from mrhomebot.admin_handlers.utils import create_groups_button
from mrhomebot.configuration import bot


@bot.message_handler(is_admin=True, commands=["fullrep"])
async def handle_download_full_report(message: Message):
    await create_groups_button(message, "fullReport")


@bot.message_handler(is_admin=False, commands=["fullrep"])
async def handle_no_download_full_report(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")
