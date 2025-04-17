"""
An intermediary module that establishes additional control over the user 
to prevent unauthorized access and flooding.
"""
from enum import Enum, auto
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from telebot.types import Message
from database.main_db import common_crud, student_crud


class BanMiddleware(BaseMiddleware):
    """
    A class of middleware that is implemented into a bot 
    to exclude banned students from the system functionality
    """
    def __init__(self, bot: AsyncTeleBot) -> None:
        """
        :param bot: bot instance
        """
        self.update_types = ["message"]
        self.bot = bot

    async def pre_process(self, message: Message, data):
        """
        Before serving this user, check if this user is banned.

        :param message: the object containing information about
            an incoming message from the user.
        :param data: Any
        """
        if await common_crud.is_ban(message.from_user.id):
            await self.bot.send_message(
                message.chat.id,
                "Функциональность бота недоступна для \
                    забаненных пользователей\n" +
                "Для разблокировки обратитесь к своему преподавателю"
            )
            return CancelUpdate()


    async def post_process(self, message, data, exception):
        ...


class FloodMiddlewareState(Enum):
    """
    To manage the current state, which is necessary to restrict/grant access
    to certain system functions, eg upload answers.
    """
    UPLOAD_ANSWER = auto()
    WAIT_UPLOAD_ANSWER = auto()


class StudentFloodMiddleware(BaseMiddleware):
    """
    A class of middleware implemented in a bot to limit requests
    from students to download answers to homework (lab work)
    and commands to check the academic performance.
    """
    def __init__(self,
                 bot: AsyncTeleBot,
                 load_answers_limit: int,
                 commands_limit: int):
        """
        :param bot: link to initialized bot
        :param load_answers_limit: limit (in minutes)
            for the period of loading answers
        :param commands_limit: limit (in minutes)
            for the period of requests for academic performance data
        """
        self.last_answer_time = {}
        self.last_command_time = {}
        self.state = {}
        self.bot = bot
        self.load_answers_limit = load_answers_limit * 60
        self.commands_limit = commands_limit * 60
        self.update_types = ['message']

    async def pre_process(self, message: Message, data):
        """
        Before servicing a user, check whether enough time has passed since 
        his last request (to avoid flooding).
        
        :param message: the object containing information about
            an incoming message from the user.
        :param data: Any
        """
        if await student_crud.is_student(message.from_user.id):
            if message.text in ["Загрузить ответ",
                                "Ближайший дедлайн",
                                "Успеваемость"]:
                if (message.from_user.id not in self.last_answer_time and
                     message.text == "Загрузить ответ"):
                    self.state[
                        message.from_user.id
                        ] = FloodMiddlewareState.WAIT_UPLOAD_ANSWER
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
                        if (message.date - self.last_answer_time[
                            message.from_user.id
                            ] < self.load_answers_limit):
                            last_time = self.load_answers_limit
                            last_time -= message.date - \
                                self.last_answer_time.get(message.from_user.id)
                            is_flood = True
                        else:
                            self.state[message.from_user.id] = \
                                FloodMiddlewareState.WAIT_UPLOAD_ANSWER
                        self.last_answer_time[message.from_user.id] = \
                            message.date
                    case _:
                        if (message.date - self.last_command_time[
                            message.from_user.id
                            ] < self.commands_limit):
                            last_time = self.commands_limit
                            last_time -= message.date - \
                                self.last_command_time.get(
                                    message.from_user.id
                                    )
                            is_flood = True
                        self.last_command_time[message.from_user.id] = \
                            message.date
                if is_flood:
                    await self.bot.send_message(
                        message.chat.id,
                        "Лимит до следующего обращения к боту \
                            еще не истек!!!" +
                        f"Обратитесь к боту через {last_time // 60} минут..."
                    )
                    return CancelUpdate()

            elif message.text == "/start":
                return
            else:
                if (self.state[message.from_user.id] == \
                    FloodMiddlewareState.WAIT_UPLOAD_ANSWER and
                        message.content_type == "document"):
                    self.state[message.from_user.id] = \
                        FloodMiddlewareState.UPLOAD_ANSWER
                else:
                    return CancelUpdate()

    async def post_process(self, message, data, exception):
        ...
