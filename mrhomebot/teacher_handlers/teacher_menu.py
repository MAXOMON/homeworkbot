"""Module for processing various teacher commands"""
from enum import Enum, auto
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database.main_db.admin_crud import is_admin
from database.main_db import teacher_crud
from mrhomebot.admin_handlers import admin_menu
from mrhomebot.admin_handlers.unban_student import create_unban_student_buttons
from mrhomebot.configuration import bot
from mrhomebot.teacher_handlers.utils import create_teacher_groups_button, \
    create_teacher_discipline_button


class TeacherException(Exception):
    """Exception raised in teacher command handler."""


class TeacherCommand(Enum):
    """
    Contains constants required for more convenient use 
    in the functions for creating and processing the teacher menu
    """
    BAN_STUDENT = auto()
    UNBAN_STUDENT = auto()
    DOWNLOAD_FULL_REPORT = auto()
    DOWNLOAD_SHORT_REPORT = auto()
    DOWNLOAD_FINISH_REPORT = auto()
    DOWNLOAD_ANSWER = auto()
    INTERACTIVE_REPORT = auto()
    SWITCH_TO_ADMIN = auto()


__teacher_commands = {
    TeacherCommand.BAN_STUDENT: "Забанить",
    TeacherCommand.UNBAN_STUDENT: "Разбанить",
    TeacherCommand.DOWNLOAD_ANSWER: "Скачать ответы",
    TeacherCommand.INTERACTIVE_REPORT: "Интерактивный отчёт",
    TeacherCommand.DOWNLOAD_FULL_REPORT: "Полный отчёт",
    TeacherCommand.DOWNLOAD_SHORT_REPORT: "Короткий отчёт",
    TeacherCommand.DOWNLOAD_FINISH_REPORT: "Итоговый отчёт",
    TeacherCommand.SWITCH_TO_ADMIN: "\U0001F977"
}

def create_teacher_keyboard(
        message: Message | None = None) -> ReplyKeyboardMarkup:
    """
    Generates a teacher menu list,
    which will be displayed to the teacher/admin with teacher_mode 
    in the Telegram bot chat.

    :param message: the object containing information about 
        an incoming message from a user.

    :return ReplyKeyboardMarkup: This object represents 
        a custom keyboard with reply options
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(__teacher_commands[TeacherCommand.DOWNLOAD_ANSWER]),
        KeyboardButton(__teacher_commands[TeacherCommand.DOWNLOAD_FINISH_REPORT])
    )
    markup.add(
        KeyboardButton(__teacher_commands[TeacherCommand.DOWNLOAD_FULL_REPORT]),
        KeyboardButton(__teacher_commands[TeacherCommand.DOWNLOAD_SHORT_REPORT])
    )
    markup.add(
        KeyboardButton(__teacher_commands[TeacherCommand.INTERACTIVE_REPORT])
    )
    footer_buttons = [
        KeyboardButton(__teacher_commands[TeacherCommand.BAN_STUDENT]),
        KeyboardButton(__teacher_commands[TeacherCommand.UNBAN_STUDENT])
    ]
    if is_admin(message.from_user.id):
        footer_buttons.append(
            KeyboardButton(__teacher_commands[TeacherCommand.SWITCH_TO_ADMIN])
        )
    markup.add(*footer_buttons)
    return markup


def is_teacher_command(command: str) -> bool:
    """
    Check if the command you sent is in the teacher's list of allowed commands.

    :param command: eg message.text
    
    :return bool: True IF is a command ELSE False
    """
    for _, value in __teacher_commands.items():
        if value == command:
            return True
    return False

def get_current_teacher_command(command: str) -> TeacherCommand:
    """
    Return the key of this command, if any.

    :param command: eg message.text

    :return TeacherCommand: object of a class TeacherCommand 
        for other processing
    """
    for key, value in __teacher_commands.items():
        if value == command:
            return key
    raise TeacherException('Неизвестная команда')

async def switch_teacher_to_admin_menu(message: Message):
    """
    Switch the teacher menu to the administrator menu

    :param message: the object containing information about
        an incoming message from the user.
    """
    teacher_crud.switch_teacher_mode_to_admin(message.from_user.id)
    await bot.send_message(
        message.chat.id,
        "Переключение в режим админа",
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=admin_menu.first_admin_keyboard(message)
    )

@bot.message_handler(
    is_teacher=True, func=lambda message: is_teacher_command(message.text)
)
async def handle_commands(message: Message):
    """
    Check if the given message is a teacher command and call 
    the functionality corresponding to this command.

    :param message: the object containing information about
        an incoming message from the user.
    """
    command = get_current_teacher_command(message.text)
    match command:
        case TeacherCommand.SWITCH_TO_ADMIN:
            await switch_teacher_to_admin_menu(message)
        case TeacherCommand.DOWNLOAD_FULL_REPORT:
            await create_teacher_groups_button(message, 'fullReport')
        case TeacherCommand.DOWNLOAD_FINISH_REPORT:
            await create_teacher_groups_button(message, 'finishReport')
        case TeacherCommand.DOWNLOAD_SHORT_REPORT:
            await create_teacher_groups_button(message, 'shortReport')
        case TeacherCommand.BAN_STUDENT:
            await create_teacher_groups_button(message, 'groupBan')
        case TeacherCommand.UNBAN_STUDENT:
            await create_unban_student_buttons(message)
        case TeacherCommand.INTERACTIVE_REPORT:
            await create_teacher_groups_button(message, 'interactiveGrRep')
        case TeacherCommand.DOWNLOAD_ANSWER:
            await create_teacher_discipline_button(message, 'dowTAnswersDis')
