"""
This module contains all the necessary functionality to 
add a teacher to the database.
"""
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message
from database.main_db import admin_crud
from mrhomebot.configuration import bot


class AdminStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg add a teacher.
    """
    teacher_name = State()
    teacher_tg_id = State()


@bot.message_handler(is_admin=True, commands=["addteacher"])
async def handle_add_teacher(message: Message):
    """
    Call the next level function for further processing
    if the command received from the user is "add teacher"
    and if this user is an administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await _handle_add_teacher(message)

@bot.message_handler(is_admin=False, commands=["addteacher"])
async def handle_no_add_teacher(message: Message):
    """
    Deny the user his request, since (based on the verification results)
    he is not an administrator and is prohibited from using this functionality.

    :param message: the object containing information about
        an incoming message from the user.
    """
    await bot.send_message(
        message.chat.id,
        "Нет прав доступа!!!",
    )

async def _handle_add_teacher(message: Message):
    """
    Sets the user to a special state that 
    grants access to the admin function of adding a teacher.

    :param message: the object containing information about
        an incoming message from the user.
    """
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
    """
    Check the correctness of the transmitted information about the teacher,
    set an additional state for transmitting the next function.

    :param message: the object containing information about
        an incoming message from the user.
    """
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
    """
    Add a teacher to the database if the check for the correctness 
    of the transmitted information about 
    the teacher's telegram ID is successfully passed.

    :param message: the object containing information about
        an incoming message from the user.
    """
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
        await bot.send_message(message.chat.id,
                               "Пожалуйста, проверьте корректность ввода ID!")
