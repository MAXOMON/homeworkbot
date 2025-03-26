"""
This module is responsible for sending information to the Telegram bot chat 
to the user about completed/uncompleted work on his homework.
"""
import asyncio
import json
from telebot.async_telebot import AsyncTeleBot
from database.queue_db import queue_out_crud, rejected_crud
from model.pydantic.queue_out_raw import TestResult
from model.pydantic.test_rejected_files import TestRejectedFiles
from model.queue_db.queue_out import QueueOut


def _get_lab_number(name: str) -> int:
    """
    Returns the extracted lab work number from the work file name.

    :param name: name of the work file.

    :return int: lab work number
    """
    name = name.replace("-", "_")
    value = name.split("_")[-1]
    value = value.split(".")[0]
    return int(value)


class AnswerProcessing:
    """
    Class for polling the intermediate database 
    and sending results to the student
    """
    def __init__(self, bot: AsyncTeleBot,
                 amount_answer_process: int | None = None):
        """
        :param bot: link to bot instance
        :param amount_answer_process: number of records processed at a time.
            If set to None - everything is scraped from the DB table
        """
        self.slice_size = amount_answer_process
        self.bot = bot

    async def run(self):
        """
        Run an event listener that monitors the output and rejected tables 
        of the intermediate database. And send the results 
        from the output table for further processing, 
        and the results from the rejected table to the telegram bot chat.
        """
        while True:
            await asyncio.sleep(2)
            if queue_out_crud.is_not_empty():
                records = queue_out_crud.get_all_records()
                if self.slice_size is not None:
                    if self.slice_size < len(records):
                        records = records[:self.slice_size]
                await self.__processing_records(records)
            while rejected_crud.is_not_empty():
                record = rejected_crud.get_first_record()
                await asyncio.sleep(1)
                rejected = TestRejectedFiles(**json.loads(record.data))
                text = f"<i>{rejected.description}:</i>"
                for it in rejected.files:
                    text += f" \n<b>{it}</b>"
                await self.bot.send_message(
                    record.chat_id,
                    text,
                    parse_mode='HTML'
                )

    async def __processing_records(self, records: list[QueueOut]) -> None:
        """
        Prepare and submit a response based on the results 
        of checking your homework assignments.

        :param records: Result records

        :return None:
        """
        for record in records:
            test_result = TestResult(**json.loads(record.data))
            text = '<i>Результат тестирования:</i>\n'

            test_result.successful_task.sort(
                key=lambda x: _get_lab_number(x.file_name))
            test_result.failed_task.sort(
                key=lambda x: _get_lab_number(x.file_name))
            for it in test_result.successful_task:
                text += f'<b>✅ {it.file_name}</b>\n'
            for it in test_result.failed_task:
                text += f'<b>❌ {it.file_name}</b> {it.description}\n'
            await self.bot.send_message(
                record.chat_id,
                text=text,
                parse_mode='HTML'
            )
            queue_out_crud.delete_record(record.id)
