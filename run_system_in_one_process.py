"""
The module for launching both the bot 
and the testing verification system in one process.

Example:
    $ python run_system_in_one_process.py
"""
import asyncio
import os
from pathlib import Path
from sys import platform
from dotenv import load_dotenv
from testing_tools.answer.answer_processing import AnswerProcessing
from testing_tools.checker.task_processing import TaskProcessing
from utils.init_app import init_app
from mrhomebot import bot


async def main():
    """
    Launch a competitive telegram bot and testing verification system.
    """
    load_dotenv()

    temp_path = Path.cwd()
    temp_path = Path(temp_path.joinpath(os.getenv("TEMP_REPORT_DIR")))
    dockers_run = int(os.getenv("AMOUNT_DOKER_RUN"))
    await bot.delete_webhook()
    await asyncio.gather(
        bot.infinity_polling(request_timeout=190),
        AnswerProcessing(bot).run(),
        TaskProcessing(temp_path, dockers_run).run(),
    )



if __name__ == '__main__':
    if platform == 'win32':
        # IF OS == WINDOWS:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(init_app())
    finally:
        asyncio.run(main())
