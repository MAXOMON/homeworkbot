from enum import IntEnum

from telebot.asyncio_handler_backends import State, StatesGroup
from pydantic import BaseModel
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from mrhomebot.configuration import bot
from database.main_db import admin_crud
from mrhomebot.filters import add_student_factory


class AddStudentStep(IntEnum):
    SELECT_GROUP = 0
    SAVE = 1

class ProcessAddStudent(BaseModel):
    full_name: str = ""
    group_id: int = 0
    next_step: int = 0


class AdminStates(StatesGroup):
    student_name = State()


@bot.message_handler(is_admin=True, commands=["addstudent"])
async def handle_add_student(message: Message):
    await _handle_add_student(message)


@bot.message_handler(is_admin=False, commands=["addstudent"])
async def handle_no_add_student(message: Message):
    await bot.send_message(message.chat.id, "Нет прав доступа!!!")


async def _handle_add_student(message: Message):
    groups = admin_crud.get_all_groups()
    if len(groups) < 1:
        await bot.send_message(
            message.chat.id,
            "В БД отсутствуют группы, куда можно добавить студента!"
        )
        return

    group_inline_buttons = [
        InlineKeyboardButton(
            it.group_name,
            callback_data=add_student_factory.new(
                group_id=it.id,
                next_step=AddStudentStep.SAVE
            )
        ) for it in groups
    ]

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(*group_inline_buttons)

    await bot.send_message(
        message.chat.id,
        "Выберите группу для нового студента:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=None, addst_config=add_student_factory.filter())
async def callback_select_group(call: CallbackQuery):
    data = add_student_factory.parse(callback_data=call.data)
    selected_group_id = data["group_id"]

    await bot.set_state(call.from_user.id, AdminStates.student_name, call.message.chat.id)
    await bot.send_message(call.message.chat.id, "Введите ФИО студента:")

    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as selected_data:
        selected_data["selected_group_id"] = selected_group_id


@bot.message_handler(state=AdminStates.student_name)
async def student_name_correct(message: Message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as selected_data:
        selected_group_id = selected_data.get("selected_group_id")

    full_name = message.text.strip()

    if len(full_name.split(" ")) == 3:
        admin_crud.add_student(full_name, selected_group_id)
        await bot.send_message(message.chat.id, "Студент успешно добавлен!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Проверьте корректность ввода ФИО!")
