"""
This module contains all the necessary functionality 
to display the administrator's admin menu in the Telegram bot chat.
"""
import asyncio
from enum import Enum, auto
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Message
from database.main_db import admin_crud
from mrhomebot import bot
from mrhomebot.admin_handlers.add_chat import _handle_add_chat
from mrhomebot.admin_handlers.add_teacher import _handle_add_teacher
from mrhomebot.admin_handlers.utils import create_teachers_button,\
    create_groups_button, create_discipline_button
from mrhomebot.admin_handlers.add_student import _handle_add_student
from mrhomebot.admin_handlers.add_discipline import _handle_add_discipline
from mrhomebot.admin_handlers.add_students_group \
    import _handle_add_students_group
from mrhomebot.admin_handlers.unban_student import create_unban_student_buttons
from mrhomebot.admin_handlers.upload_tests import _handle_upload_tests
from mrhomebot.admin_handlers.upload_start_configuration \
    import _handle_upload_start_configuration
from mrhomebot.admin_handlers.download_all_test_and_answer \
    import _handle_download_all_test_and_answer
from mrhomebot.admin_handlers.reset_teacher_mode import __handle_reset
from mrhomebot.teacher_handlers.teacher_menu import create_teacher_keyboard


class AdminException(Exception):
    """Exception raised in admin menu"""


class AdminCommand(Enum):
    """
    Contains constants required for more convenient use 
    in the functions for creating and processing the admin menu
    """
    ADD_GROUP = auto()
    ADD_TEACHER = auto()
    ADD_STUDENT = auto()
    ADD_DISCIPLINE = auto()
    ADD_CHAT = auto()
    SET_TEACHER_TO_GROUP = auto()
    SET_TEACHER_TO_DISCIPLINE = auto()
    BAN_STUDENT = auto()
    UNBAN_STUDENT = auto()
    UPLOAD_CONFIGURATION = auto()
    UPLOAD_TESTS = auto()
    ADD_STUDENTS_GROUP = auto()
    NEXT = auto()
    BACK = auto()
    DELETE_STUDENT = auto()
    DELETE_TEACHER = auto()
    DELETE_GROUP = auto()
    DOWNLOAD_FULL_REPORT = auto()
    DOWNLOAD_SHORT_REPORT = auto()
    DOWNLOAD_FINISH_REPORT = auto()
    DOWNLOAD_ANSWER = auto()
    DOWNLOAD_ALL_ANSWER_WITH_TEST = auto()
    SWITCH_TO_TEACHER = auto()
    RESET = auto()


__admin_commands = {
    AdminCommand.UPLOAD_TESTS: "Загрузить тесты",
    AdminCommand.UPLOAD_CONFIGURATION: "Загрузить стартовую конфигурацию",
    AdminCommand.BAN_STUDENT: "Забанить",
    AdminCommand.UNBAN_STUDENT: "Разбанить",
    AdminCommand.SET_TEACHER_TO_DISCIPLINE: "Назначить преподу дисциплину",
    AdminCommand.SET_TEACHER_TO_GROUP: "Назначить преподу группу",
    AdminCommand.ADD_STUDENTS_GROUP: "Доб. гр. студентов",
    AdminCommand.ADD_STUDENT: "Добавить студента",
    AdminCommand.ADD_TEACHER: "Добавить препода",
    AdminCommand.ADD_DISCIPLINE: "Добавить дисциплину",
    AdminCommand.ADD_CHAT: "Добавить чат",
    AdminCommand.NEXT: "\u2192",
    AdminCommand.BACK: "\u2190",
    AdminCommand.DELETE_STUDENT: "Удал. студента",
    AdminCommand.DELETE_GROUP: "Удал. группу",
    AdminCommand.DELETE_TEACHER: "Удал. препода",
    AdminCommand.DOWNLOAD_ANSWER: "Скачать ответы",
    AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST: "Скачать все ответы",
    AdminCommand.DOWNLOAD_FULL_REPORT: "Полный отчёт",
    AdminCommand.DOWNLOAD_SHORT_REPORT: "Краткий отчёт",
    AdminCommand.DOWNLOAD_FINISH_REPORT: "Итоговый отчёт",
    AdminCommand.SWITCH_TO_TEACHER: "\U0001F468\U0000200D\U0001F3EB",
    AdminCommand.RESET: "Сброс ошибки"
}


async def first_admin_keyboard(message: Message) -> ReplyKeyboardMarkup:
    """
    the first list of the admin menu, 
    which will be displayed to the administrator in the telegram bot chat.

    :param message: the object containing information about
        an incoming message from the user.
    :return ReplyKeyboardMarkup: This object represents a custom keyboard 
        with reply options.
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.ADD_TEACHER]),
        KeyboardButton(__admin_commands[AdminCommand.ADD_CHAT])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.ADD_STUDENT]),
        KeyboardButton(__admin_commands[AdminCommand.ADD_DISCIPLINE]),
        KeyboardButton(__admin_commands[AdminCommand.ADD_STUDENTS_GROUP])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.SET_TEACHER_TO_DISCIPLINE]),
        KeyboardButton(__admin_commands[AdminCommand.SET_TEACHER_TO_GROUP])
    )
    footer_buttons = []
    is_teacher = await admin_crud.is_teacher(message.from_user.id)
    if is_teacher:
        footer_buttons.append(KeyboardButton(__admin_commands[AdminCommand.SWITCH_TO_TEACHER]))
    footer_buttons.append(KeyboardButton(__admin_commands[AdminCommand.NEXT]))
    markup.add(*footer_buttons)
    return markup


async def second_admin_keyboard(message: Message | None = None) -> ReplyKeyboardMarkup:
    """
    the second list of the admin menu, 
    which will be displayed to the administrator in the telegram bot chat.

    :param message: the object containing information about
        an incoming message from the user.
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.DOWNLOAD_ANSWER]),
        KeyboardButton(__admin_commands[AdminCommand.DOWNLOAD_FINISH_REPORT])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.DOWNLOAD_FULL_REPORT]),
        KeyboardButton(__admin_commands[AdminCommand.DOWNLOAD_SHORT_REPORT])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST]),
        KeyboardButton(__admin_commands[AdminCommand.BAN_STUDENT]),
        KeyboardButton(__admin_commands[AdminCommand.UNBAN_STUDENT])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.BACK]),
        KeyboardButton(__admin_commands[AdminCommand.NEXT])
    )
    await asyncio.sleep(0.0001)
    return markup


async def third_admin_keyboard(message: Message | None = None) -> ReplyKeyboardMarkup:
    """
    the third list of the admin menu, 
    which will be displayed to the administrator in the telegram bot chat.

    :param message: the object containing information about
        an incoming message from the user.
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.DELETE_GROUP]),
        KeyboardButton(__admin_commands[AdminCommand.DELETE_TEACHER]),
        KeyboardButton(__admin_commands[AdminCommand.DELETE_STUDENT])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.UPLOAD_TESTS]),
        KeyboardButton(__admin_commands[AdminCommand.UPLOAD_CONFIGURATION])
    )
    markup.add(
        KeyboardButton(__admin_commands[AdminCommand.BACK])
    )
    await asyncio.sleep(0.0001)
    return markup

def is_admin_command(command: str) -> bool:
    """
    Checks if the command is in the allowed list.

    :param command: a command sent by a user to a chat with a telegram bot 
        with admin status, for example /addstudent
    """
    for _, value in __admin_commands.items():
        if value == command:
            return True
    return False

def get_current_admin_command(command: str) -> AdminCommand:
    """
    Return the name of the menu button if there is one 
    in the list of admin menu commands

    :param command: a command sent by a user to a chat with a telegram bot 
        with admin status, for example /addstudent
    """
    for key, value in __admin_commands.items():
        if value == command:
            return key
    raise AdminException("Неизвестная команда")

__menu_index: dict[int, int] = {}
__menu_list = [
    first_admin_keyboard,
    second_admin_keyboard,
    third_admin_keyboard
]

async def switch_admin_to_teacher_menu(message: Message):
    """
    Switch from admin menu to teacher menu

    :param message: the object containing information about
        an incoming message from the user.
    """
    markup = await create_teacher_keyboard(message)
    await bot.send_message(
        message.chat.id,
        "Переключение в режим преподавателя",
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=markup
    )

@bot.message_handler(is_admin=True,
                     func=lambda message: is_admin_command(message.text))
async def handle_commands(message: Message):
    """
    Call the function according to the command passed by the administrator.

    :param message: the object containing information about
        an incoming message from the user.
    """
    command = get_current_admin_command(message.text)
    match command:
        case AdminCommand.ADD_CHAT:
            await _handle_add_chat(message)
        case AdminCommand.ADD_STUDENT:
            await _handle_add_student(message)
        case AdminCommand.ADD_TEACHER:
            await _handle_add_teacher(message)
        case AdminCommand.ADD_STUDENTS_GROUP:
            await _handle_add_students_group(message)
        case AdminCommand.ADD_DISCIPLINE:
            await _handle_add_discipline(message)
        case AdminCommand.BAN_STUDENT:
            await create_groups_button(message, "groupBan")
        case AdminCommand.UNBAN_STUDENT:
            await create_unban_student_buttons(message)
        case AdminCommand.NEXT:
            if message.from_user.id not in __menu_index:
                __menu_index[message.from_user.id] = 1
            else:
                __menu_index[message.from_user.id] += 1
            index = __menu_index[message.from_user.id]
            markup = await __menu_list[index](message)
            await bot.send_message(
                message.chat.id,
                "Смена меню",
                reply_markup=markup
            )
        case AdminCommand.BACK:
            if message.from_user.id not in __menu_index:
                __menu_index[message.from_user.id] = 0
            else:
                __menu_index[message.from_user.id] -= 1
            index = __menu_index[message.from_user.id]
            markup = await __menu_list[index](message)
            await bot.send_message(
                message.chat.id,
                "Смена меню",
                reply_markup=markup
            )
        case AdminCommand.SET_TEACHER_TO_GROUP:
            await create_teachers_button(message, "assignTeacherGR")
        case AdminCommand.SET_TEACHER_TO_DISCIPLINE:
            await create_teachers_button(message, "assignTeacherDis")
        case AdminCommand.DELETE_GROUP:
            await create_groups_button(message, "groupDel")
        case AdminCommand.DELETE_STUDENT:
            await create_groups_button(message, "groupStudDel")
        case AdminCommand.DELETE_TEACHER:
            await create_teachers_button(message, "delTeacher")
        case AdminCommand.UPLOAD_TESTS:
            await _handle_upload_tests(message)
        case AdminCommand.UPLOAD_CONFIGURATION:
            await _handle_upload_start_configuration(message)
        case AdminCommand.SWITCH_TO_TEACHER:
            await admin_crud.switch_admin_mode_to_teacher(message.from_user.id)
            await switch_admin_to_teacher_menu(message)
        case AdminCommand.DOWNLOAD_FULL_REPORT:
            await create_groups_button(message, "fullReport")
        case AdminCommand.DOWNLOAD_ANSWER:
            await create_discipline_button(message, 'dowAnswersDis')
        case AdminCommand.DOWNLOAD_FINISH_REPORT:
            await create_groups_button(message, "finishReport")
        case AdminCommand.DOWNLOAD_SHORT_REPORT:
            await create_groups_button(message, "shortReport")
        case AdminCommand.DOWNLOAD_ALL_ANSWER_WITH_TEST:
            await _handle_download_all_test_and_answer(message)
        case AdminCommand.RESET:
            await __handle_reset(message)
