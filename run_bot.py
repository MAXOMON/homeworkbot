"""
Telegram bot launch module in a separate process
Example:
    $ python run_bot.py
"""
import asyncio

from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from utils.init_app import init_app
from mrhomebot.configuration import DOMAIN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV


async def main():
    """running telegram bot in infinite loop"""

    await asyncio.gather(
        bot.infinity_polling(request_timeout=90),
        AnswerProcessing(bot).run()
    )


if __name__ == "__main__":
    init_app()
    asyncio.run(main())
