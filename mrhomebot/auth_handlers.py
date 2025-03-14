from telebot.apihelper import ApiTelegramException
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from mrhomebot.configuration import bot
from mrhomebot.admin_handlers import admin_keyboard

import database.main_db.common_crud as common_crud
import database.main_db.student_crud as student_crud
from database.main_db.common_crud import UserEnum
from mrhomebot.student_handlers.student_menu import student_keyboard
from mrhomebot.teacher_handlers.teacher_menu import create_teacher_keyboard


class AuthStates(StatesGroup):
    full_name = State()


async def is_subscribed(chat_id: int, user_id: int) -> bool:
    try:
        response = await bot.get_chat_member(chat_id, user_id)
        if response.status == "left":
            return False
        else:
            return True
    except ApiTelegramException as ex:
        if ex.result_json["description"] == "Bad Request: user is not subscribed":
            return False

@bot.message_handler(commands=["start"])
async def handle_start(message: Message):
    user = common_crud.user_verification(message.from_user.id)
    match user:
        case UserEnum.Admin:
            await bot.send_message(
                message.chat.id,
                "<b>Hello, Admin!</b>",
                parse_mode="HTML",
                reply_markup=admin_keyboard(message)
            )
        case UserEnum.Teacher:
            await bot.send_message(
                message.chat.id,
                "<i>Hello, Teacher!</i>",
                parse_mode="HTML",
                reply_markup=create_teacher_keyboard(message)
            )
        case UserEnum.Student:
            await bot.send_message(
                message.chat.id,
                "Hello, Student!",
                parse_mode="HTML",
                reply_markup=student_keyboard(message)
            )
        case _:
            chats = common_crud.get_chats()
            user_in_chat = False
            for chat_id in chats:
                user_in_chat = await is_subscribed(chat_id, message.from_user.id)
                if user_in_chat:
                    break

            if user_in_chat:
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("Да", callback_data="start_yes"),
                    InlineKeyboardButton("Нет", callback_data="start_no"),
                )
                text = """
                    Бот осуществляет хранение и обработку персональных данных
                    \nна российских серверах. К таким данным относятся: \n
                    - ФИО\n
                    - Успеваемость по предмету\n
                    - Telegram ID\n
                    Вы даёте разрешение на обработку персональных данных?
                    """
                await bot.send_message(
                    message.chat.id,
                    text,
                    reply_markup=markup,
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    "Пожалуйста, подпишитесь на канал!!!",
                )

@bot.callback_query_handler(func=lambda call: "start_" in call.data)
async def callback_auth_query(call: CallbackQuery):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "start":
            if call.data == "start_yes":
                text = "Спасибо! Удачной учёбы!\n"
                text += "Введите ваше ФИО:"
                await bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.id,
                )
                await bot.set_state(
                    call.from_user.id, AuthStates.full_name, call.message.chat.id
                )
            if call.data == "start_no":
                await bot.edit_message_text(
                    "Жаль. Если передумаете - перезапустите бота!",
                    call.message.chat.id,
                    call.message.id,
                )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных!",
                call.message.chat.id,
                call.message.id,
            )

@bot.message_handler(state=AuthStates.full_name)
async def input_full_name(message: Message):
    full_name = message.text
    if len(full_name.split(" ")) != 3:
        await bot.send_message(
            message.chat.id,
            'Пожалуйста, введите полное ФИО! Например: Иванов Иван Иванович',
        )
    else:
        if student_crud.has_student(full_name):
            student_crud.set_telegram_id(full_name, message.from_user.id)
            await bot.send_message(
                message.chat.id,
                "Вы успешно авторизовались!",
                reply_markup=student_keyboard(message)
            )
        else:
            await bot.send_message(
                message.chat.id,
                'Пожалуйста, проверьте корректность ввода ФИО или свяжитесь с преподавателем'
            )
