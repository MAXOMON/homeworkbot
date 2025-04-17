"""
This module contains the basic operations with incoming data 
for their subsequent entry/extraction into the queue database output table.
"""
import json
from database.queue_db.database import Session
from model.pydantic.queue_out_raw import TestResult
from model.queue_db.queue_out import QueueOut
from pydantic.json import pydantic_encoder
from sqlalchemy.future import select


async def is_empty() -> bool:
    """
    Check if output table is empty

    :param None:

    :return bool: True IF is empty ELSE False
    """
    async with Session() as session:
        data = await session.scalar(select(QueueOut))
        return data is None

async def is_not_empty() -> bool:
    """
    Check if output table is not empty

    :param None:

    :return bool: True IF is not empty ELSE False
    """
    async with Session() as session:
        data = await session.scalar(select(QueueOut))
        return data is not None

async def get_all_records() -> list[QueueOut]:
    """
    Get all records from the output table

    :param None:

    :return list[QueueOut]: list of output table records in the format 
        of objects of the QueueOut class
    """
    async with Session() as session:
        data = await session.scalars(select(QueueOut))
        return data.all()

async def delete_record(record_id: int) -> None:
    """
    Delete this record from output table

    :param record_id: record ID

    :return None:
    """
    async with Session() as session:
        data = await session.scalar(
            select(QueueOut).where(QueueOut.id == record_id)
        )
        await session.delete(data)
        await session.commit()

async def add_record(user_tg_id: int, chat_id: int, data: TestResult) -> None:
    """
    Add the check result to the output table

    :param user_tg_id: user Telegran ID
    :param chat_id: chat ID 
    :param data: eg telegram_id, chat_id, result_report

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            json_data = json.dumps(
                data,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
                separators=(',', ': '),
                default=pydantic_encoder
            )
            session.add(
                QueueOut(
                    telegram_id=user_tg_id,
                    chat_id=chat_id,
                    data=json_data
                )
            )
            await session.commit()
