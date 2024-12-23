from enum import Enum, auto

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from telebot.types import Message

from database.main_db import common_crud, student_crud


class BanMiddleware(BaseMiddleware):
    """
    Класс промежуточного ПО, внедряемого в бота для отсечения забаненных
    студентов от функциональности системы
    """
    def __init__(self, bot: AsyncTeleBot) -> None:
        self.update_types = ["message"]
        self.bot = bot

    async def pre_process(self, message: Message, data):
        if common_crud.is_ban(message.from_user.id):
            await self.bot.send_message(
                message.chat.id,
                f"Функциональность бота недоступна для забаненных пользователей" \
                f"Для разблокировки обратитесь к своему преподавателю"
            )
            return CancelUpdate

    async def post_process(self, message, data, exception):
        ...


class FloodMiddlewareState(Enum):
    UPLOAD_ANSWER = auto()
    WAIT_UPLOAD_ANSWER = auto()


class StudentFloodMiddleware(BaseMiddleware):
    """
    Класс промежуточного ПО, внедряемого в бота для лимитирования запросов
    студентов на загрузку ответов на л/р (д/р) и команд на проверку успеваемости
    """
    def __init__(self, bot: AsyncTeleBot, load_answers_limit: int, commands_limit: int) -> None:
        """
        :param bot: ссылка на инициализированного бота
        :param load_answers_limit: ограничение (в минутах) на период загрузки ответов
        :param commands_limit: ограничение (в минутах) на период запросов данных об успеваемости

        :return:
        """
        self.last_answer_time = {}
        self.last_command_time = {}
        self.state = {}
        self.bot = bot
        self.load_answers_limit = load_answers_limit * 60
        self.commands_limit = commands_limit * 60
        self.update_types = ['message']

    async def pre_process(self, message: Message, data):
        print(message.date)
        if student_crud.is_student(message.from_user.id):
            if message.text in ["Загрузить ответ", "Ближайший дедлайн", "Успеваемость"]:
                if (message.from_user.id not in self.last_answer_time and
                     message.text == "Загрузить ответ"):
                    self.state[message.from_user.id] = FloodMiddlewareState.WAIT_UPLOAD_ANSWER
                    self.last_answer_time[message.from_user.id] = message.date
                    return
                
                if (message.from_user.id not in self.last_command_time and
                        message.text in ["Ближайший дедлайн", "Успеваемость"]):
                    self.last_command_time[message.from_user.id] = message.date
                    return
                
                is_flood = False
                last_time = 0
                match message.text:
                    case "Загрузить ответ":
                        if (message.date - self.last_answer_time[message.from_user.id] < 
                                self.load_answers_limit):
                            last_time = self.load_answers_limit
                            last_time -= message.date - self.last_command_time[message.from_user.id]
                            is_flood = True
                        self.last_command_time[message.from_user.id] = message.date
                    case _:
                        ...

            elif message.text == "/start":
                return
            else:
                if (self.state[message.from_user.id] == FloodMiddlewareState.WAIT_UPLOAD_ANSWER and
                        message.content_type == "document"):
                    self.state[message.from_user.id] = FloodMiddlewareState.UPLOAD_ANSWER
                else:
                    return CancelUpdate()


    async def post_process(self):
        ...


