from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message

from mrhomebot.configuration import bot
from database.main_db import admin_crud


class AdminStates(StatesGroup):
    teacher_name = State()
    teacher_tg_id = State()


@bot.message_handler(is_admin=True, commands=["addteacher"])
async def handle_add_teacher(message: Message):
    await _handle_add_teacher(message)


@bot.message_handler(is_admin=False, commands=["addteacher"])
async def handle_no_add_teacher(message: Message):
    await bot.send_message(
        message.chat.id,
        "Нет прав доступа!!!",
    )


async def _handle_add_teacher(message: Message):
    await bot.set_state(
        message.from_user.id,
        AdminStates.teacher_name,
        message.chat.id,
    )
    await bot.send_message(
        message.chat.id,
        "Введите ФИО преподавателя: (Иванов Иван Иванович)",
    )


@bot.message_handler(state=AdminStates.teacher_name)
async def teacher_name_correct(message: Message):
    if message.text == "stop":
        await bot.delete_state(message.from_user.id, message.chat.id)
        return

    if len(message.text.split(" ")) == 3:
        await bot.set_state(
            message.from_user.id,
            AdminStates.teacher_tg_id,
            message.chat.id
        )
        await bot.send_message(
            message.chat.id,
            "Введите telegram id преподавателя:",
        )
        async with bot.retrieve_data(
            message.from_user.id,
            message.chat.id 
        ) as data:
            data["teacher_name"] = message.text
    else:
        await bot.send_message(
            message.chat.id,
            "Проверьте корректность ввода ФИО!"
        )


@bot.message_handler(state=AdminStates.teacher_tg_id)
async def teacher_id_correct(message: Message):
    if message.text.isdigit():
        async with bot.retrieve_data(
            message.from_user.id,
            message.chat.id
        ) as data:
            admin_crud.add_teacher(data["teacher_name"], int(message.text))
        await bot.send_message(
            message.chat.id,
            "Преподаватель успешно добавлен!",
        )
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Пожалуйста, проверьте корректность ввода ID!")
