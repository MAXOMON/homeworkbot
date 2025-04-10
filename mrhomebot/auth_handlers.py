"""
This module contains a handler for user authentication and authorization 
and the necessary functionality for it,
"""
from telebot.apihelper import ApiTelegramException
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup,\
    CallbackQuery
import database.main_db.common_crud as common_crud
import database.main_db.student_crud as student_crud
from database.main_db.common_crud import UserEnum
from mrhomebot.admin_handlers import admin_keyboard
from mrhomebot.configuration import bot
from mrhomebot.student_handlers.student_menu import student_keyboard
from mrhomebot.teacher_handlers.teacher_menu import create_teacher_keyboard


class AuthStates(StatesGroup):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg user authenticate.
    """
    full_name = State()


async def is_subscribed(chat_id: int, user_id: int) -> bool:
    """
    Check this user is subscribed

    :param chat_id: Telegram chat ID 
    :param user_id: Telegram user ID (message.from_user.id)

    :return bool: True IF is subscribed ELSE False
    """
    try:
        response = await bot.get_chat_member(chat_id, user_id)
        if response.status == "left":
            return False
        return True
    except ApiTelegramException as ex:
        if ex.result_json["description"] == "Bad Request: user \
            is not subscribed":
            return False

@bot.message_handler(commands=["start"])
async def handle_start(message: Message):
    """
    Check the user's status when receiving a 'start' command from him 
    in the Telegram bot chat, and provide him with 
    a keyboard with the functionality available to him, if, of course, 
    the user has passed the appropriate check.

    :param message: the object containing information about
        an incoming message from the user.
    """
    user = common_crud.user_verification(message.from_user.id)
    match user:
        case UserEnum.ADMIN:
            await bot.send_message(
                message.chat.id,
                "<b>Hello, Admin!</b>",
                parse_mode="HTML",
                reply_markup=admin_keyboard(message)
            )
        case UserEnum.TEACHER:
            await bot.send_message(
                message.chat.id,
                "<i>Hello, Teacher!</i>",
                parse_mode="HTML",
                reply_markup=create_teacher_keyboard(message)
            )
        case UserEnum.STUDENT:
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
                user_in_chat = await is_subscribed(
                    chat_id,
                    message.from_user.id
                    )
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
    """
    Set the state that is required for further registration of the user 
    in the system if the user agrees with the condition, otherwise - no.

    :param call: an object that extends the standard message.
        contains the start command and the answer to consent 
        to the processing of personal data (yes/no).
    """
    print(call, call.data, call.data.split("_"))
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
                    call.from_user.id,
                    AuthStates.full_name,
                    call.message.chat.id
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
    """
    Add the telegram ID of this student to the database 
    if the user entered the correct data regarding the full name, 
    and such a student exists in the educational system.

    :param message: the object containing information about
        an incoming message from the user, eg user full name
    """
    full_name = message.text
    if len(full_name.split(" ")) != 3:
        await bot.send_message(
            message.chat.id,
            'Пожалуйста, введите полное ФИО! Например: Иванов Иван Иванович',
        )
    else:
        if student_crud.has_more_students(full_name):
            groups = student_crud.get_groups_of_students_with_same_name(
                full_name)
            groups_inline_buttons = [
                InlineKeyboardButton(
                    it.group_name,
                    callback_data=f"FULL_NAME_WITH_{it.id}"
                ) for it in groups
            ]
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(*groups_inline_buttons)

            async with bot.retrieve_data(
                message.from_user.id, message.chat.id) as sel_data:
                sel_data['full_name'] = full_name

            await bot.send_message(
                message.chat.id,
                "Выберите группу, в которой вы учитесь:",
                reply_markup=markup
            )
        elif student_crud.has_student(full_name):
            student_crud.set_telegram_id(full_name, message.from_user.id)
            await bot.send_message(
                message.chat.id,
                "Вы успешно авторизовались!",
                reply_markup=student_keyboard(message)
            )
        else:
            await bot.send_message(
                message.chat.id,
                'Пожалуйста, проверьте корректность ввода ФИО \
                    или свяжитесь с преподавателем'
            )

@bot.callback_query_handler(func=lambda call: "FULL_NAME_WITH_" in call.data)
async def input_full_name_with_group(call: CallbackQuery):
    group_id = int(call.data.split('_')[-1])
    async with bot.retrieve_data(
        call.from_user.id,
        call.message.chat.id
    ) as sel_data:
        full_name = sel_data['full_name']
    telegram_id = call.from_user.id
    student_crud.set_telegram_id_on_group_id(full_name,
                                             group_id,
                                             telegram_id)
    await bot.send_message(
                call.message.chat.id,
                "Вы успешно авторизовались!",
                reply_markup=student_keyboard(call.message)
            )
