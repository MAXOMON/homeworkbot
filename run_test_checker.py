"""
Модуль запуска подсистемы проверки ответов в отдельном процессе
Example:
    $ python run_test_checker.py
"""
import asyncio
import os
from pathlib import Path

from testing_tools.checker.task_processing import TaskProcessing
from utils.init_app import init_app

if __name__ == "__main__":
    init_app()

    temp_path = Path.cwd()
    temp_path = Path(temp_path.joinpath(os.getenv("TEMP_REPORT_DIR")))
    dockers_run = int(os.getenv("AMOUNT_DOKER_RUN"))

    asyncio.run(TaskProcessing(temp_path, dockers_run).run())