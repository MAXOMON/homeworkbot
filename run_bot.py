"""
Модуль запуска телеграм-бота в отдельном процессе
Example:
    $ python run_bot.py
"""
import asyncio

from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from utils.init_app import init_app


async def main():
    await asyncio.gather(
        bot.infinity_polling(request_timeout=90),
        AnswerProcessing(bot).run()
    )


if __name__ == "__main__":
    init_app()
    asyncio.run(main())