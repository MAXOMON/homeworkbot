from enum import IntEnum

from telebot.asyncio_handler_backends import State, StatesGroup
from pydantic import BaseModel
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from mrhomebot.configuration import bot
from database.main_db import admin_crud, common_crud
from mrhomebot.filters import add_student_factory


class AddStudentStep(IntEnum):
    SAVE = 1
    DISCIPLINE = 2


class ProcessAddStudent(BaseModel):
    full_name: str = ""
    discipline_id: int = 0
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
    await bot.set_state(message.from_user.id, AdminStates.student_name, message.chat.id)
    await bot.send_message(message.chat.id, "Введите ФИО студента: ")


@bot.message_handler(state=AdminStates.student_name)
async def student_name_correct(message: Message):
    if message.text == "stop":
        await bot.delete_state(message.from_user.id, message.chat.id)
        return
    
    if len(message.text.split(" ")) == 3:
        groups = admin_crud.get_all_groups()
        if len(groups) < 1:
            await bot.send_message(message.chat.id, "В БД отсутствуют группы, куда можно добавить студента!")
            return
        group_inline_button = []
        for it in groups:
            group_inline_button.append(
                InlineKeyboardButton(
                    it.group_name,
                    callback_data=add_student_factory.new(
                        full_name=message.text,
                        group_id=it.id,
                        discipline_id=-1,
                        next_step=(AddStudentStep.DISCIPLINE),
                    )
                )
            )
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(*group_inline_button)
        await bot.send_message(
            message.chat.id,
            "Выберите группу студента:",
            reply_markup=markup
        )
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Проверьте корректность ввода ФИО!")


@bot.callback_query_handler(func=None, addst_config=add_student_factory.filter())
async def callback_add_student(call: CallbackQuery):
    student_data = ProcessAddStudent(
        **add_student_factory.parse(callback_data=call.data)
    )
    match student_data.next_step:
        case AddStudentStep.DISCIPLINE:
            disciplines = common_crud.get_group_disciplines(student_data.group_id)
            if len(disciplines) < 1:
                await bot.send_message(
                    call.message.chat.id,
                    "В БД отсутствуют данные по дисциплинам!"
                )
                return
            discipline_inline_button = []
            for it in disciplines:
                discipline_inline_button.append(
                    InlineKeyboardButton(
                        it.short_name,
                        callback_data=add_student_factory.new(
                            full_name=student_data.full_name,
                            group_id=student_data.group_id,
                            discipline_id=it.id,
                            next_step=int(AddStudentStep.SAVE)
                        )
                    )
                )
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(*discipline_inline_button)
            await bot.edit_message_text(
                "Выберите дисциплину по которой обучается студент:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case AddStudentStep.SAVE:
            admin_crud.add_student(
                student_data.full_name,
                student_data.group_id,
                student_data.discipline_id
            )
            await bot.edit_message_text(
                "Студент успешно добавлен!",
                call.message.chat.id,
                call.message.id
            )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных!",
                call.message.chat.id,
                call.message.id
            )
