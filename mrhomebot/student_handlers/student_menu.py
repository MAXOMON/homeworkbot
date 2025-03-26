"""Module for processing various student commands"""
from enum import Enum, auto
from telebot.types import KeyboardButton, Message, ReplyKeyboardMarkup
from mrhomebot import bot
from mrhomebot.student_handlers.utils import create_student_disciplines_button


class StudentException(Exception):
    """Exceptions that occur when working in the student menu."""


class StudentCommand(Enum):
    """
    Contains constants required for more convenient use 
    in the functions for creating and processing the student menu
    """
    UPLOAD_ANSWER = auto()
    NEAREST_DEADLINE = auto()
    ACADEMIC_PERFORMANCE = auto()


__student_commands = {
    StudentCommand.UPLOAD_ANSWER: "Загрузить ответ",
    StudentCommand.NEAREST_DEADLINE: "Ближайший дедлайн",
    StudentCommand.ACADEMIC_PERFORMANCE: "Успеваемость"
}

def is_student_command(command: str) -> bool:
    """
    Check if such a team is on the list of student commands.

    :param command: eg message.text from user TG

    :return bool: True IF is a command ELSE False
    """
    for _, value in __student_commands.items():
        if value == command:
            return True
    return False

def get_current_student_command(command: str) -> StudentCommand:
    """
    Return the key of the given team, if it is in the list of student teams.

    :param command: eg message.text

    :return StudentCommand: an object of the StudentCommand class, 
        representing one of its values. By this value, 
        in other student command processing functionality, 
        it will be easier to compare and implement the necessary logic.
    """
    for key, value in __student_commands.items():
        if value == command:
            return key
    raise StudentException('Неизвестная команда')

def student_keyboard(message: Message | None = None) -> ReplyKeyboardMarkup:
    """
    Generates a student menu list,
    which will be displayed to the student in the Telegram bot chat.

    :param message: the object containing information about
        an incoming message from the user.

    :return ReplyKeyboardMarkup: This object represents a custom keyboard 
        with reply options.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(__student_commands[StudentCommand.UPLOAD_ANSWER])
    )
    markup.add(
        KeyboardButton(__student_commands[StudentCommand.NEAREST_DEADLINE]),
        KeyboardButton(__student_commands[StudentCommand.ACADEMIC_PERFORMANCE])
    )
    return markup

@bot.message_handler(
        is_student=True, func=lambda message: is_student_command(message.text)
)
async def handle_commands(message: Message):
    """
    Check if the given message is a student command and call 
    the functionality corresponding to this command.

    :param message: the object containing information about
        an incoming message from the user. 
    """
    command = get_current_student_command(message.text)
    match command:
        case StudentCommand.UPLOAD_ANSWER:
            await create_student_disciplines_button(message, "uploadAnswer_0")
        case StudentCommand.NEAREST_DEADLINE:
            await create_student_disciplines_button(message, "nearestDeadline")
        case StudentCommand.ACADEMIC_PERFORMANCE:
            await create_student_disciplines_button(message, 'academicPerf')
