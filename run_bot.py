"""
Telegram bot launch module in a separate process
Example:
    $ python run_bot.py
"""
import asyncio
from sys import platform
from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from utils.init_app import init_app


async def main():
    """running telegram bot in infinite loop"""

    await asyncio.gather(
        bot.infinity_polling(request_timeout=90),
        AnswerProcessing(bot).run()
    )


if __name__ == "__main__":
    if platform == 'win32':
        # IF OS == WINDOWS:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(init_app())
    finally:
        asyncio.run(main())
